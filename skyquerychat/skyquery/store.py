"""Raw-data layer: a gridded daily tropospheric-NO2 cube.

File format (.npz):  no2[T,Y,X] float32 (molecules/cm2, NaN = no valid retrieval),
                     lat[Y], lon[X], time[T] or dates[T] ('YYYY-MM-DD'), source (str).
`scripts/make_sample_data.py` writes a synthetic cube; `scripts/fetch_real_data.py` writes a real India-region cube.
"""
from __future__ import annotations
import math
import os
from datetime import date, timedelta
from pathlib import Path

import numpy as np

from . import config

R_EARTH_KM = 6371.0088


def haversine_km(lat1, lon1, lat2, lon2):
    """Vectorised great-circle distance in km (numpy broadcasting)."""
    p1, p2 = np.radians(lat1), np.radians(lat2)
    dphi = p2 - p1
    dlmb = np.radians(lon2) - np.radians(lon1)
    a = np.sin(dphi / 2) ** 2 + np.cos(p1) * np.cos(p2) * np.sin(dlmb / 2) ** 2
    return 2 * R_EARTH_KM * np.arcsin(np.sqrt(a))


class DataError(RuntimeError):
    pass


class GridStore:
    def __init__(self, path: Path | str | None = None):
        path = Path(path or ensure_data())
        if not path.exists():
            raise DataError(f"Data file not found: {path}. Run: python scripts/make_sample_data.py")
        try:
            z = np.load(path, allow_pickle=False)
            self.no2 = np.asarray(z["no2"], dtype=np.float32)
            self.lat = np.asarray(z["lat"], dtype=np.float64)
            self.lon = np.asarray(z["lon"], dtype=np.float64)
            time_values = z["time"] if "time" in z.files else z["dates"]
            self.dates = [date.fromisoformat(str(s)[:10]) for s in time_values]
            self.source = str(z["source"]) if "source" in z.files else "unknown"
        except Exception as e:  # corrupt / wrong file -> clear message instead of a stack trace
            raise DataError(f"Could not read {path}: {e}") from e
        if self.no2.shape != (len(self.dates), len(self.lat), len(self.lon)):
            raise DataError("Data cube shape does not match (dates, lat, lon).")
        self.is_synthetic = self.source.upper().startswith("SYNTHETIC")
        self._series_cache: dict[tuple, tuple[np.ndarray, int]] = {}

    # ---- basic facts -------------------------------------------------
    @property
    def first_date(self) -> date:
        return self.dates[0]

    @property
    def last_date(self) -> date:
        return self.dates[-1]

    @property
    def valid_cell_count(self) -> int:
        return int(np.isfinite(self.no2).any(axis=0).sum())

    @property
    def _dlat(self) -> float:
        return float(abs(self.lat[1] - self.lat[0])) if len(self.lat) > 1 else 0.25

    @property
    def _dlon(self) -> float:
        return float(abs(self.lon[1] - self.lon[0])) if len(self.lon) > 1 else 0.25

    def covers(self, lat: float, lon: float) -> bool:
        return (self.lat.min() - self._dlat / 2 <= lat <= self.lat.max() + self._dlat / 2 and
                self.lon.min() - self._dlon / 2 <= lon <= self.lon.max() + self._dlon / 2)

    def bounds_text(self) -> str:
        return (f"{self.lat.min():.1f}°–{self.lat.max():.1f}° lat, "
                f"{self.lon.min():.1f}°–{self.lon.max():.1f}° lon")

    def date_index(self, d: date) -> int | None:
        try:
            return self.dates.index(d)
        except ValueError:
            return None

    # ---- area-averaged series ---------------------------------------
    def cell_mask(self, lat0: float, lon0: float, radius_km: float) -> np.ndarray:
        LAT, LON = np.meshgrid(self.lat, self.lon, indexing="ij")
        dist = haversine_km(lat0, lon0, LAT, LON)
        mask = dist <= radius_km
        if not mask.any():  # radius smaller than a cell -> use the nearest cell
            mask[np.unravel_index(np.argmin(dist), dist.shape)] = True
        return mask

    def series(self, lat0: float, lon0: float, radius_km: float | None = None) -> tuple[np.ndarray, int]:
        """Daily mean over valid cells within radius. Days with < MIN_VALID_FRAC valid cells -> NaN."""
        radius_km = radius_km or config.RADIUS_KM
        key = (round(lat0, 4), round(lon0, 4), radius_km)
        if key in self._series_cache:
            return self._series_cache[key]
        mask = self.cell_mask(lat0, lon0, radius_km)
        n_cells = int(mask.sum())
        cells = self.no2[:, mask]                        # (T, n_cells)
        valid = np.isfinite(cells)
        n_valid = valid.sum(axis=1)
        with np.errstate(invalid="ignore", divide="ignore"):
            mean = np.where(valid, cells, 0.0).sum(axis=1) / np.maximum(n_valid, 1)
        mean = np.where(n_valid / n_cells >= config.MIN_VALID_FRAC, mean, np.nan)
        out = (mean.astype(np.float64), n_cells)
        self._series_cache[key] = out
        return out

    def slice_dates(self, start: date, end: date) -> list[int]:
        return [i for i, d in enumerate(self.dates) if start <= d <= end]


def ensure_data(path: Path | str | None = None) -> Path:
    """Prefer a downloaded real grid; otherwise use the existing synthetic demo cube."""
    if path is None:
        if os.environ.get("SKYQUERY_DATA"):
            path = config.DATA_PATH
        elif config.REAL_DATA_PATH.exists():
            return config.REAL_DATA_PATH
        else:
            path = config.SYNTHETIC_DATA_PATH
    path = Path(path)
    if path.exists():
        return path
    from .scripts_bridge import generate  # local import to avoid import cost
    generate(path)
    return path
