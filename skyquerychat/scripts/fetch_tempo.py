"""Download NASA TEMPO NO2 (Level-3, V03) and convert it to the project's grid format.

This optional fetcher is for North America only. For India, use scripts/fetch_real_data.py.

    pip install earthaccess xarray h5netcdf
    # one-time: free account at https://urs.earthdata.nasa.gov  (then either set env vars
    #   EARTHDATA_USERNAME / EARTHDATA_PASSWORD, or let earthaccess prompt you)
    python scripts/fetch_tempo.py --start 2025-10-01 --end 2025-10-14 --dry-run   # just check access
    python scripts/fetch_tempo.py --start 2025-10-01 --end 2025-10-14             # build the real cube

Output goes to data/tempo_no2_grid.npz by default, so run_demo.py / app.py / cli.py then use REAL data
with zero code changes. Per scan: tropospheric column (product/vertical_column_troposphere), pixels with
main_data_quality_flag != 0 or fill values dropped, block-averaged to a 0.25 degree grid; each day is the
mean of up to --max-per-day daytime scans. Files are read by streaming only the requested bounding box.

NOTE: written from NASA ASDC's documented layout (collection TEMPO_NO2_L3, group 'product', coordinates in the
root group). It needs Earthdata credentials + internet, so it could not be executed in the sandbox where
this project was generated - run it once with --dry-run, then a 2-3 day range, before relying on it.
"""
from __future__ import annotations
import argparse
import os
from datetime import date, timedelta
from pathlib import Path

import numpy as np

STEP = 0.25


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--start", required=True)
    ap.add_argument("--end", required=True)
    ap.add_argument("--bbox", nargs=4, type=float, default=[-125.0, 15.0, -65.0, 55.0],
                    metavar=("W", "S", "E", "N"))
    ap.add_argument("--max-per-day", type=int, default=4, help="max daytime scans averaged per day")
    ap.add_argument("--out", default=str(Path(__file__).resolve().parent.parent / "data" / "tempo_no2_grid.npz"))
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    import earthaccess
    import xarray as xr

    strategy = "environment" if os.environ.get("EARTHDATA_USERNAME") else "interactive"
    earthaccess.login(strategy=strategy, persist=True)

    W, S, E, N = a.bbox
    lat_t = np.arange(S, N + 1e-9, STEP)
    lon_t = np.arange(W, E + 1e-9, STEP)
    NY, NX = len(lat_t), len(lon_t)
    d0, d1 = date.fromisoformat(a.start), date.fromisoformat(a.end)
    days = [d0 + timedelta(days=i) for i in range((d1 - d0).days + 1)]
    cube = np.full((len(days), NY, NX), np.nan, dtype=np.float32)

    for k, day in enumerate(days):
        granules = earthaccess.search_data(short_name="TEMPO_NO2_L3", version="V03",
                                           temporal=(f"{day} 00:00:00", f"{day} 23:59:59"),
                                           bounding_box=(W, S, E, N))
        print(f"{day}: {len(granules)} granule(s)")
        if a.dry_run or not granules:
            continue
        pick = np.unique(np.linspace(0, len(granules) - 1, min(a.max_per_day, len(granules))).round().astype(int))
        sums = np.zeros(NY * NX)
        cnts = np.zeros(NY * NX)
        for f in earthaccess.open([granules[i] for i in pick]):
            try:
                root = xr.open_dataset(f, engine="h5netcdf")
                prod = xr.open_dataset(f, engine="h5netcdf", group="product")
                lat, lon = root["latitude"].values, root["longitude"].values
                li = np.where((lat >= S - STEP) & (lat <= N + STEP))[0]
                lj = np.where((lon >= W - STEP) & (lon <= E + STEP))[0]
                col = prod["vertical_column_troposphere"].isel(latitude=li, longitude=lj).values
                qa = prod["main_data_quality_flag"].isel(latitude=li, longitude=lj).values
                col = np.squeeze(col).astype(np.float64)
                qa = np.squeeze(qa)
                col[(qa != 0) | ~np.isfinite(col) | (col < -1e29) | (col > 1e20)] = np.nan
                ti = np.clip(np.round((lat[li] - S) / STEP).astype(int), 0, NY - 1)
                tj = np.clip(np.round((lon[lj] - W) / STEP).astype(int), 0, NX - 1)
                tgt = ti[:, None] * NX + tj[None, :]
                ok = np.isfinite(col)
                sums += np.bincount(tgt[ok], weights=col[ok], minlength=NY * NX)
                cnts += np.bincount(tgt[ok], minlength=NY * NX)
            except Exception as e:  # one bad granule must not kill the whole download
                print(f"  skipped a granule: {type(e).__name__}: {e}")
        with np.errstate(invalid="ignore", divide="ignore"):
            cube[k] = np.where(cnts > 0, sums / np.maximum(cnts, 1), np.nan).reshape(NY, NX)

    if a.dry_run:
        print("dry run finished: access works.")
        return
    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(out, no2=cube, lat=lat_t, lon=lon_t, dates=np.array([d.isoformat() for d in days]),
                        source=np.array("NASA TEMPO NO2 L3 V03 (ASDC), tropospheric column, QA=0, "
                                        "0.25deg block mean, daily mean of daytime scans"))
    print(f"wrote {out}  valid fraction = {np.isfinite(cube).mean():.1%}")


if __name__ == "__main__":
    main()
