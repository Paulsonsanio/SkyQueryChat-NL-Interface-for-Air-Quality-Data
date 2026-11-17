"""Central configuration. Everything can be overridden with environment variables / a .env file."""
from __future__ import annotations
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def load_dotenv(path: Path | None = None) -> None:
    """Tiny .env loader (no extra dependency). Existing environment variables win."""
    path = path or ROOT / ".env"
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


load_dotenv()

REAL_DATA_PATH = ROOT / "data" / "no2_grid.npz"
SYNTHETIC_DATA_PATH = Path(os.environ.get("SKYQUERY_DATA", ROOT / "data" / "tempo_no2_grid.npz"))
DATA_PATH = Path(os.environ.get("SKYQUERY_DATA", REAL_DATA_PATH))
OUTPUT_DIR = ROOT / "outputs"

RADIUS_KM = float(os.environ.get("SKYQUERY_RADIUS_KM", 25.0))  # area averaged around a city centre
MIN_VALID_FRAC = 0.30       # a city-day needs >=30% valid cells, else it counts as "no observation"
MIN_TREND_POINTS = 5        # minimum valid days needed to report a trend
FLAT_THRESHOLD_PCT = 5.0    # |change| below this is called "roughly flat"
DEFAULT_WINDOW_DAYS = 30    # default period for trend / average / ranking
CURRENT_LOOKBACK_DAYS = 7   # "latest value" searches back this far for a cloud-free day
MAX_QUESTION_CHARS = 500
UNIT = "molecules/cm²"
UNIT_SCALE = 1e15           # values are displayed in units of 10^15 molecules/cm²

# Heuristic plain-English bands for the tropospheric NO2 column (NOT an official AQI).
LEVELS = [
    (1.0e15, "very low (near clean-background levels)"),
    (2.5e15, "low"),
    (5.0e15, "moderate (typical of a busy urban area)"),
    (8.0e15, "elevated"),
    (float("inf"), "high (heavy traffic/industrial emissions)"),
]
