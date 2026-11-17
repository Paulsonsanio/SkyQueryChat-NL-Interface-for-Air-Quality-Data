"""Fetch the latest available NASA OMI/Aura OMNO2d data for India.

Requires an Earthdata Login token in EARTHDATA_TOKEN (loaded from the project .env).
Install with: pip install earthaccess h5py
"""
from __future__ import annotations

import argparse
import os
import re
import sys
import tempfile
from datetime import date, timedelta
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from skyquery import config  # noqa: E402

BBOX = (68.0, 6.0, 98.0, 38.0)
PRODUCT = "OMNO2d"
SOURCE = "NASA OMI/Aura NO2, 0.25 deg"
OUTPUT = config.REAL_DATA_PATH
GRID_PATH = "/HDFEOS/GRIDS/ColumnAmountNO2"
FIELD = f"{GRID_PATH}/Data_Fields/ColumnAmountNO2TropCloudScreened"


def _granule_date(granule) -> date:
    name = str(granule)
    if isinstance(granule, dict):
        name = str(granule.get("umm", {}).get(
            "GranuleUR", granule.get("meta", {}).get("native-id", name)
        ))
    match = re.search(r"OMNO2d_(\d{4})m(\d{2})(\d{2})", name)
    if match is None:
        raise ValueError(f"Could not determine observation date from granule name: {name}")
    return date(int(match.group(1)), int(match.group(2)), int(match.group(3)))


def _read_grid(path: Path) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    import h5py

    with h5py.File(path, "r") as source:
        dataset = source[FIELD]
        data = np.asarray(dataset[...], dtype=np.float64).squeeze()
        attrs = dataset.attrs
        fill = attrs.get("_FillValue", attrs.get("bad_value_scaled", None))
        if fill is not None:
            data[data == fill] = np.nan
        for key in ("scale_factor", "ScaleFactor", "Scale"):
            if key in attrs:
                data *= float(attrs[key])
                break
        for key in ("add_offset", "Offset"):
            if key in attrs:
                data += float(attrs[key])
                break
        data[~np.isfinite(data) | (np.abs(data) > 1e30)] = np.nan

    if data.shape != (720, 1440):
        raise ValueError(f"Unexpected OMNO2d grid shape: {data.shape}; expected (720, 1440)")
    lat_axis = np.linspace(89.875, -89.875, 720)
    lon_axis = np.linspace(-179.875, 179.875, 1440)
    lat_grid, lon_grid = np.meshgrid(lat_axis, lon_axis, indexing="ij")
    return lat_grid, lon_grid, data


def _crop(lat: np.ndarray, lon: np.ndarray, values: np.ndarray):
    west, south, east, north = BBOX
    keep = (
        np.isfinite(lat)
        & np.isfinite(lon)
        & (lat >= south)
        & (lat <= north)
        & (lon >= west)
        & (lon <= east)
    )
    if not keep.any():
        raise ValueError("OMI grid has no cells inside the requested India bounding box")

    row_mask = keep.any(axis=1)
    col_mask = keep.any(axis=0)
    lat_counts = keep.sum(axis=1)
    lon_counts = keep.sum(axis=0)
    lat_sums = np.where(keep, lat, 0).sum(axis=1)
    lon_sums = np.where(keep, lon, 0).sum(axis=0)
    lat_axis = np.divide(
        lat_sums, lat_counts, out=np.zeros_like(lat_sums), where=row_mask
    )[row_mask]
    lon_axis = np.divide(
        lon_sums, lon_counts, out=np.zeros_like(lon_sums), where=col_mask
    )[col_mask]
    cropped = values[np.ix_(row_mask, col_mask)].copy()
    cropped[~keep[np.ix_(row_mask, col_mask)]] = np.nan

    if lat_axis[0] > lat_axis[-1]:
        lat_axis = lat_axis[::-1]
        cropped = cropped[::-1]
    if lon_axis[0] > lon_axis[-1]:
        lon_axis = lon_axis[::-1]
        cropped = cropped[:, ::-1]

    # OMNO2d stores ColumnAmountNO2TropCloudScreened in molecules/cm2.
    # Preserve these raw units because the engine formats values by dividing by 1e15.
    return lat_axis.astype(np.float64), lon_axis.astype(np.float64), cropped.astype(np.float32)


def fetch(start: date, end: date, out: Path = OUTPUT) -> None:
    import earthaccess

    if not os.environ.get("EARTHDATA_TOKEN"):
        raise RuntimeError("EARTHDATA_TOKEN is not set; add it to the project .env before downloading.")
    earthaccess.login(strategy="environment")

    granules = earthaccess.search_data(
        short_name=PRODUCT,
        provider="GES_DISC",
        temporal=(start.isoformat(), end.isoformat()),
        bounding_box=BBOX,
        count=-1,
    )
    by_date = {}
    for granule in granules:
        day = _granule_date(granule)
        by_date[day] = granule
    available = sorted(by_date)
    if not available:
        raise RuntimeError(f"NASA GES DISC has no {PRODUCT} granules from {start} through {end}.")

    selected_dates = available[-120:]
    print(f"Found {len(available)} available days; selecting {len(selected_dates)}.")
    print(f"Real data date range: {selected_dates[0]} to {selected_dates[-1]}")
    cube, lat_axis, lon_axis = [], None, None
    with tempfile.TemporaryDirectory(prefix="skyquery-omno2d-") as temp_dir:
        downloaded = earthaccess.download(
            [by_date[day] for day in selected_dates],
            temp_dir,
            threads=4,
        )
        files_by_day = {_granule_date(path): Path(path) for path in downloaded}
        for day in selected_dates:
            lat, lon, values = _read_grid(files_by_day[day])
            this_lat, this_lon, cropped = _crop(lat, lon, values)
            if lat_axis is None:
                lat_axis, lon_axis = this_lat, this_lon
            elif not (np.array_equal(lat_axis, this_lat) and np.array_equal(lon_axis, this_lon)):
                raise ValueError(f"Grid coordinates changed in OMI granule for {day}")
            cube.append(cropped)

    data = np.stack(cube).astype(np.float32)
    if not np.isfinite(data).any():
        raise RuntimeError("Downloaded OMI granules contain no valid cloud-screened tropospheric NO2 cells.")
    out.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(
        out,
        time=np.array([day.isoformat() for day in selected_dates]),
        lat=lat_axis,
        lon=lon_axis,
        no2=data,
        source=np.array(SOURCE),
    )
    print(f"Saved {out}")
    print(f"Date range: {selected_dates[0]} to {selected_dates[-1]}")
    print(f"Grid shape: {data.shape}; valid cells: {np.isfinite(data).any(axis=0).sum()}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--end", type=date.fromisoformat, default=date.today())
    parser.add_argument("--days", type=int, default=240, help="search window; latest 120 available days are used")
    parser.add_argument("--out", type=Path, default=OUTPUT)
    args = parser.parse_args()
    if args.days < 1:
        parser.error("--days must be positive")
    fetch(args.end - timedelta(days=args.days - 1), args.end, args.out)


if __name__ == "__main__":
    main()
