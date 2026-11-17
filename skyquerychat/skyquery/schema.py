"""Strict query-plan schema. Whatever the LLM (or the rule parser) produces must pass through here."""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import date

INTENTS = ("current", "average", "trend", "compare", "rank", "peak", "out_of_domain")
SUPPORTED_POLLUTANTS = ("no2",)

_POLLUTANT_SYNONYMS = {
    "no2": "no2", "no₂": "no2", "nitrogen dioxide": "no2", "nitrogen_dioxide": "no2",
    "nox": "no2", "air quality": "no2", "air_quality": "no2", "pollution": "no2",
    "hcho": "hcho", "formaldehyde": "hcho", "o3": "o3", "ozone": "o3", "so2": "so2",
    "co": "co", "pm2.5": "pm25", "pm25": "pm25", "pm10": "pm10", "aqi": "aqi",
    "aerosol": "aerosol", "aod": "aerosol",
}


class PlanError(ValueError):
    """Raised when a plan is malformed. The message is fed back to the LLM for one repair attempt."""


class UserFacingError(Exception):
    """A normal, expected outcome the user should be told about (not a crash)."""

    def __init__(self, kind: str, message: str):
        super().__init__(message)
        self.kind = kind
        self.message = message


@dataclass
class LocationRef:
    name: str
    lat: float | None = None
    lon: float | None = None


@dataclass
class QueryPlan:
    intent: str
    pollutant: str = "no2"
    locations: list[LocationRef] = field(default_factory=list)
    start_date: str | None = None     # ISO yyyy-mm-dd
    end_date: str | None = None
    last_n_days: int | None = None
    top_n: int = 5
    order: str = "highest"            # for rank: highest | lowest

    @classmethod
    def from_dict(cls, d: object) -> "QueryPlan":
        if not isinstance(d, dict):
            raise PlanError("plan must be a JSON object")
        intent = str(d.get("intent", "")).strip().lower()
        if intent not in INTENTS:
            raise PlanError(f"intent must be one of {INTENTS}, got {intent!r}")

        raw_pol = str(d.get("pollutant") or "no2").strip().lower()
        pollutant = _POLLUTANT_SYNONYMS.get(raw_pol, "other")

        locs: list[LocationRef] = []
        raw_locs = d.get("locations") or []
        if isinstance(raw_locs, (str, dict)):
            raw_locs = [raw_locs]
        if not isinstance(raw_locs, list):
            raise PlanError("locations must be a list")
        for item in raw_locs[:10]:
            if isinstance(item, str):
                name, lat, lon = item, None, None
            elif isinstance(item, dict):
                name, lat, lon = item.get("name"), item.get("lat"), item.get("lon")
            else:
                raise PlanError("each location must be a string or {name, lat, lon}")
            name = str(name or "").strip()[:80]
            if not name:
                continue
            try:
                lat = None if lat is None else float(lat)
                lon = None if lon is None else float(lon)
            except (TypeError, ValueError):
                raise PlanError(f"lat/lon for {name!r} must be numbers")
            if lat is not None and not -90 <= lat <= 90:
                raise PlanError(f"lat {lat} out of range")
            if lon is not None and not -180 <= lon <= 180:
                raise PlanError(f"lon {lon} out of range")
            locs.append(LocationRef(name, lat, lon))

        def _date(key: str) -> str | None:
            v = d.get(key)
            if v in (None, "", "null"):
                return None
            try:
                return date.fromisoformat(str(v)[:10]).isoformat()
            except ValueError:
                raise PlanError(f"{key} must be ISO yyyy-mm-dd, got {v!r}")

        start, end = _date("start_date"), _date("end_date")
        if start and end and start > end:
            start, end = end, start

        n = d.get("last_n_days")
        if n in (None, "", "null"):
            n = None
        else:
            try:
                n = int(n)
            except (TypeError, ValueError):
                raise PlanError("last_n_days must be an integer")
            if not 1 <= n <= 3650:
                raise PlanError("last_n_days must be between 1 and 3650")

        try:
            top_n = int(d.get("top_n") or 5)
        except (TypeError, ValueError):
            top_n = 5
        top_n = max(1, min(20, top_n))
        order = str(d.get("order") or "highest").lower()
        order = "lowest" if order.startswith("low") else "highest"

        return cls(intent, pollutant, locs, start, end, n, top_n, order)

    def to_dict(self) -> dict:
        return {
            "intent": self.intent, "pollutant": self.pollutant,
            "locations": [{"name": l.name, "lat": l.lat, "lon": l.lon} for l in self.locations],
            "start_date": self.start_date, "end_date": self.end_date,
            "last_n_days": self.last_n_days, "top_n": self.top_n, "order": self.order,
        }


# JSON schema handed to the LLM (Anthropic tool input_schema / OpenAI-style prompt).
PLAN_JSON_SCHEMA = {
    "type": "object",
    "properties": {
        "intent": {"type": "string", "enum": list(INTENTS),
                   "description": "current=latest/one-day value, average=mean over a period, "
                                  "trend=change over time, compare=2+ places side by side, "
                                  "rank=which cities are highest/lowest, peak=worst/best day, "
                                  "out_of_domain=general or meta question not asking for a satellite query"},
        "pollutant": {"type": "string",
                      "description": "no2 (supported). Use the real pollutant asked about, e.g. pm25, o3, aqi."},
        "locations": {"type": "array", "items": {"type": "object", "properties": {
            "name": {"type": "string"},
            "lat": {"type": ["number", "null"], "description": "only if you are confident"},
            "lon": {"type": ["number", "null"]}}, "required": ["name"]}},
        "start_date": {"type": ["string", "null"], "description": "ISO date or null"},
        "end_date": {"type": ["string", "null"], "description": "ISO date or null"},
        "last_n_days": {"type": ["integer", "null"], "description": "for 'last week' use 7, 'last month' 30"},
        "top_n": {"type": "integer"},
        "order": {"type": "string", "enum": ["highest", "lowest"]},
    },
    "required": ["intent"],
}
