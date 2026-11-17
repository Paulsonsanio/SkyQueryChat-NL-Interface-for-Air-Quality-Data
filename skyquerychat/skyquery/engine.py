"""Query engine: executes a validated plan against the raw grid. All numbers in answers come from here."""
from __future__ import annotations
from dataclasses import dataclass
from datetime import date, timedelta

import numpy as np

from . import config, gazetteer
from .schema import QueryPlan, UserFacingError, SUPPORTED_POLLUTANTS
from .store import GridStore


@dataclass
class Location:
    name: str
    lat: float
    lon: float
    source: str  # "gazetteer" | "llm" | "user"


@dataclass
class Resolved:
    intent: str
    locations: list[Location]
    start: date
    end: date
    relative: bool          # True if period was relative ("last week"), anchored to latest data day
    notes: list[str]
    top_n: int
    order: str


_PRETTY = {"pm25": "PM2.5", "pm10": "PM10", "o3": "ozone (O₃)", "so2": "SO₂", "co": "CO",
           "hcho": "formaldehyde (HCHO)", "aqi": "AQI", "aerosol": "aerosol"}


# ---------------------------------------------------------------- resolution / validation
def resolve(plan: QueryPlan, store: GridStore) -> Resolved:
    notes: list[str] = []
    if plan.pollutant not in SUPPORTED_POLLUTANTS:
        raise UserFacingError(
            "unsupported",
            f"This build answers questions about tropospheric nitrogen dioxide (NO₂) only, "
            f"which is what the loaded dataset contains. I can't give {_PRETTY.get(plan.pollutant, plan.pollutant.upper())} "
            f"values without inventing them. Try asking about NO₂ or 'air pollution' instead.")

    locs: list[Location] = []
    for ref in plan.locations:
        hit = gazetteer.lookup(ref.name)
        if hit:
            canon, lat, lon = hit
            locs.append(Location(canon, lat, lon, "gazetteer"))
        elif ref.lat is not None and ref.lon is not None and ref.name.startswith("("):
            locs.append(Location(ref.name, ref.lat, ref.lon, "user"))   # coordinates typed by the user
        elif ref.lat is not None and ref.lon is not None:
            locs.append(Location(ref.name.title(), ref.lat, ref.lon, "llm"))
            notes.append(f"Coordinates for {ref.name} ({ref.lat:.2f}, {ref.lon:.2f}) were supplied by the "
                         f"language model, not looked up in a verified gazetteer.")
        else:
            raise UserFacingError(
                "unknown_location",
                f"I don't have coordinates for “{ref.name}”. Try an Indian state (e.g. Punjab, Maharashtra) "
                f"or city (e.g. Delhi, Mumbai, Bengaluru) or give latitude/longitude.")

    for loc in locs:
        if not store.covers(loc.lat, loc.lon):
            raise UserFacingError(
                "out_of_coverage",
                f"{loc.name} is outside the area covered by the loaded satellite data "
                f"({store.bounds_text()}). The dataset observes the India region.")

    # intent-specific requirements
    if plan.intent == "rank":
        if not locs:
            locs = [Location(n, *gazetteer.CITIES[n], "gazetteer")
                    for n in gazetteer.CITIES if store.covers(*gazetteer.CITIES[n])]
    elif plan.intent == "compare":
        if len(locs) < 2:
            raise UserFacingError("clarify", "Which two (or more) places should I compare? "
                                  "For example: “Compare NO₂ in Delhi and Mumbai last month”.")
    elif not locs:
        raise UserFacingError("clarify", "Which city do you mean? For example: "
                              "“What is the NO₂ level in Delhi?”")

    # period
    relative = False
    first, last = store.first_date, store.last_date
    if plan.start_date or plan.end_date:
        start = date.fromisoformat(plan.start_date) if plan.start_date else first
        end = date.fromisoformat(plan.end_date) if plan.end_date else (
            start if plan.intent == "current" else last)
        if plan.intent == "current" and plan.start_date and not plan.end_date:
            end = start
    elif plan.last_n_days:
        end, start, relative = last, last - timedelta(days=plan.last_n_days - 1), True
    elif plan.intent == "current":
        end, start, relative = last, last - timedelta(days=config.CURRENT_LOOKBACK_DAYS - 1), True
    else:
        end, start, relative = last, last - timedelta(days=config.DEFAULT_WINDOW_DAYS - 1), True

    if end < first or start > last:
        raise UserFacingError(
            "bad_period", f"The loaded data covers {first} to {last}; nothing is available for "
            f"{start} to {end}. Ask about a date inside that range.")
    if start < first:
        notes.append(f"Data starts on {first}; the period was shortened accordingly.")
        start = first
    if end > last:
        notes.append(f"Data ends on {last}; the period was shortened accordingly.")
        end = last
    return Resolved(plan.intent, locs, start, end, relative, notes, plan.top_n, plan.order)


# ---------------------------------------------------------------- computation
def level_label(v: float) -> str:
    for limit, label in config.LEVELS:
        if v < limit:
            return label
    return config.LEVELS[-1][1]


def _linear_trend(x: np.ndarray, y: np.ndarray, span_days: int) -> dict:
    if len(x) < config.MIN_TREND_POINTS:
        return {"slope_per_day": None, "change_pct": None, "r2": None, "direction": "insufficient data"}
    slope, intercept = np.polyfit(x, y, 1)
    fit_start, fit_end = intercept, intercept + slope * span_days
    pred = intercept + slope * x
    ss_res, ss_tot = float(np.sum((y - pred) ** 2)), float(np.sum((y - y.mean()) ** 2))
    r2 = 1 - ss_res / ss_tot if ss_tot > 0 else 0.0
    pct = (fit_end - fit_start) / fit_start * 100 if fit_start > 0 else None
    if pct is None:
        direction = "insufficient data"
    elif pct >= config.FLAT_THRESHOLD_PCT:
        direction = "increasing"
    elif pct <= -config.FLAT_THRESHOLD_PCT:
        direction = "decreasing"
    else:
        direction = "roughly flat"
    return {"slope_per_day": float(slope), "change_pct": None if pct is None else float(pct),
            "r2": float(r2), "direction": direction}


def _row(store: GridStore, loc: Location, start: date, end: date, intent: str) -> dict:
    series, n_cells = store.series(loc.lat, loc.lon)
    idx = store.slice_dates(start, end)
    vals = series[idx]
    dates = [store.dates[i] for i in idx]
    ok = np.isfinite(vals)
    row: dict = {
        "location": loc.name, "lat": loc.lat, "lon": loc.lon, "n_cells": n_cells,
        "n_total": len(idx), "n_valid": int(ok.sum()),
        "series": [[d.isoformat(), (float(v) if np.isfinite(v) else None)] for d, v in zip(dates, vals)],
        "mean": float(np.mean(vals[ok])) if ok.any() else None,
        "min": float(np.min(vals[ok])) if ok.any() else None,
        "max": float(np.max(vals[ok])) if ok.any() else None,
    }
    if ok.any():
        k = int(np.nanargmax(np.where(ok, vals, -np.inf)))
        row["peak_date"], row["peak_value"] = dates[k].isoformat(), float(vals[k])
        k = int(np.nanargmin(np.where(ok, vals, np.inf)))
        row["low_date"], row["low_value"] = dates[k].isoformat(), float(vals[k])
        last_ok = np.where(ok)[0][-1]
        row["latest_date"], row["latest_value"] = dates[last_ok].isoformat(), float(vals[last_ok])
        x = np.array([(d - start).days for d, o in zip(dates, ok) if o], dtype=float)
        row.update(_linear_trend(x, vals[ok], (end - start).days))
        # context for "current": mean of the 30 days ending on the latest valid day
        ctx_end = dates[last_ok]
        cidx = store.slice_dates(ctx_end - timedelta(days=config.DEFAULT_WINDOW_DAYS - 1), ctx_end)
        cv = series[cidx]
        row["context_mean"] = float(np.nanmean(cv)) if np.isfinite(cv).any() else None
        row["context_window"] = [(ctx_end - timedelta(days=config.DEFAULT_WINDOW_DAYS - 1)).isoformat(),
                                 ctx_end.isoformat()]
        row["context_series"] = [
            [store.dates[i].isoformat(), (float(series[i]) if np.isfinite(series[i]) else None)]
            for i in cidx
        ]
    else:
        row.update({"slope_per_day": None, "change_pct": None, "r2": None, "direction": "no data",
                    "context_mean": None})
    return row


def execute(res: Resolved, store: GridStore) -> dict:
    rows = [_row(store, loc, res.start, res.end, res.intent) for loc in res.locations]
    result: dict = {
        "intent": res.intent, "unit": config.UNIT, "start": res.start.isoformat(),
        "end": res.end.isoformat(), "relative_period": res.relative, "notes": list(res.notes),
        "source": store.source, "synthetic": store.is_synthetic, "rows": rows,
        "radius_km": config.RADIUS_KM, "order": res.order, "top_n": res.top_n,
    }
    if res.intent in ("rank", "compare"):
        have = [r for r in rows if r["mean"] is not None]
        have.sort(key=lambda r: r["mean"], reverse=(res.order == "highest" or res.intent == "compare"))
        result["ranking"] = [r["location"] for r in have]
        if res.intent == "rank":
            result["ranking"] = result["ranking"][: res.top_n]
    if all(r["n_valid"] == 0 for r in rows):
        name = rows[0]["location"] if rows else "this location"
        raise UserFacingError(
            "no_data", f"No valid satellite data for this location ({name}) from "
            f"{res.start} to {res.end}. The selected grid cells contain no usable observations.")
    return result
