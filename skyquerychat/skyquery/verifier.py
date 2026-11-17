"""Independent re-computation ("validated against raw data").

Deliberately does NOT reuse the engine's maths: it walks the raw grid cell by cell with pure-Python
`math` (haversine, mean, closed-form least squares) and compares with the engine's numbers.
"""
from __future__ import annotations
import math
from datetime import date, timedelta

from . import config
from .store import GridStore, R_EARTH_KM

REL_TOL = 1e-5


def _hav(lat1, lon1, lat2, lon2) -> float:
    p1, p2 = math.radians(lat1), math.radians(lat2)
    a = (math.sin((p2 - p1) / 2) ** 2 +
         math.cos(p1) * math.cos(p2) * math.sin(math.radians(lon2 - lon1) / 2) ** 2)
    return 2 * R_EARTH_KM * math.asin(math.sqrt(a))


def _cells(store: GridStore, lat0: float, lon0: float, radius: float) -> list[tuple[int, int]]:
    lats, lons = store.lat.tolist(), store.lon.tolist()
    near = []
    best = (1e18, 0, 0)
    for i, la in enumerate(lats):
        if abs(la - lat0) > 3:
            continue
        for j, lo in enumerate(lons):
            if abs(lo - lon0) > 4:
                continue
            d = _hav(lat0, lon0, la, lo)
            if d <= radius:
                near.append((i, j))
            if d < best[0]:
                best = (d, i, j)
    return near or [(best[1], best[2])]


def _daily(store: GridStore, cells, t: int):
    vals = []
    for i, j in cells:
        v = float(store.no2[t, i, j])
        if not math.isnan(v):
            vals.append(v)
    if vals and len(vals) / len(cells) >= config.MIN_VALID_FRAC:
        return sum(vals) / len(vals)
    return None


def _series(store, cells, start: date, end: date):
    out = []
    for t, d in enumerate(store.dates):
        if start <= d <= end:
            out.append((d, _daily(store, cells, t)))
    return out


def _ols(points):
    n = len(points)
    mx = sum(p[0] for p in points) / n
    my = sum(p[1] for p in points) / n
    sxx = sum((p[0] - mx) ** 2 for p in points)
    sxy = sum((p[0] - mx) * (p[1] - my) for p in points)
    slope = sxy / sxx if sxx else 0.0
    return slope, my - slope * mx


def _close(a, b) -> bool:
    if a is None or b is None:
        return a is None and b is None
    return abs(a - b) <= REL_TOL * max(1.0, abs(a), abs(b))


def verify(result: dict, store: GridStore) -> dict:
    """Return {'passed': bool, 'checks': [{name, engine, independent, ok}]}."""
    checks: list[dict] = []

    def add(name, eng, ind):
        checks.append({"name": name, "engine": eng, "independent": ind, "ok": _close(eng, ind)})

    start, end = date.fromisoformat(result["start"]), date.fromisoformat(result["end"])
    intent = result["intent"]
    means: dict[str, float | None] = {}
    for row in result["rows"]:
        loc = row["location"]
        cells = _cells(store, row["lat"], row["lon"], result["radius_km"])
        ser = _series(store, cells, start, end)
        good = [(d, v) for d, v in ser if v is not None]
        mean = sum(v for _, v in good) / len(good) if good else None
        means[loc] = mean
        add(f"{loc}: valid days", float(row["n_valid"]), float(len(good)))
        add(f"{loc}: period mean", row["mean"], mean)
        if not good:
            continue
        if intent in ("current", "peak", "average", "compare", "rank"):
            pk = max(good, key=lambda p: p[1])
            add(f"{loc}: peak value", row["peak_value"], pk[1])
            checks[-1]["ok"] = checks[-1]["ok"] and row["peak_date"] == pk[0].isoformat()
        if intent == "current":
            last_d, last_v = good[-1]
            add(f"{loc}: latest value", row["latest_value"], last_v)
            checks[-1]["ok"] = checks[-1]["ok"] and row["latest_date"] == last_d.isoformat()
            cs = last_d - timedelta(days=config.DEFAULT_WINDOW_DAYS - 1)
            cser = [v for _, v in _series(store, cells, cs, last_d) if v is not None]
            add(f"{loc}: 30-day context mean", row["context_mean"], sum(cser) / len(cser) if cser else None)
        if intent == "trend" and len(good) >= config.MIN_TREND_POINTS:
            slope, icpt = _ols([((d - start).days, v) for d, v in good])
            span = (end - start).days
            add(f"{loc}: trend slope/day", row["slope_per_day"], slope)
            pct = (slope * span) / icpt * 100 if icpt > 0 else None
            add(f"{loc}: trend change %", row["change_pct"], pct)

    if intent in ("rank", "compare"):
        have = [(k, v) for k, v in means.items() if v is not None]
        reverse = result["order"] == "highest" or intent == "compare"
        have.sort(key=lambda kv: kv[1], reverse=reverse)
        expected = [k for k, _ in have]
        if intent == "rank":
            expected = expected[: result["top_n"]]
        checks.append({"name": "ranking order", "engine": result["ranking"], "independent": expected,
                       "ok": result["ranking"] == expected})
    return {"passed": all(c["ok"] for c in checks), "checks": checks}
