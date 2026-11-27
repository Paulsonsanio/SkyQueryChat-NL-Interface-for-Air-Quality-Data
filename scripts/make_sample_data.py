"""Generate a SYNTHETIC daily tropospheric-NO2 grid for the INDIA region.

Layout:
  - Latitude:  6.0°N to 38.0°N (step 0.25°, 129 points)
  - Longitude: 68.0°E to 98.0°E (step 0.25°, 121 points)
  - Days:      120 days starting 2025-07-01
  - Sensor:    Sentinel-5P / INSAT layout (molecules/cm2)

Usage:
  python scripts/make_sample_data.py [output.npz]
"""
from __future__ import annotations
import sys
from datetime import date, timedelta
from pathlib import Path

import numpy as np

START = date(2025, 7, 1)
N_DAYS = 120
LAT = np.arange(6.0, 38.0001, 0.25)
LON = np.arange(68.0, 98.0001, 0.25)

# city/state: (lat, lon, peak NO2 in 1e15 molecules/cm2, drift in % per 30 days)
CITY_PLUMES = {
    # Northern Plains & NCR (High emission corridor)
    "Delhi": (28.6139, 77.2090, 42.0, +10),
    "Punjab": (31.1471, 75.3412, 34.0, +8),
    "Ludhiana": (30.9010, 75.8573, 38.0, +7),
    "Amritsar": (31.6340, 74.8723, 32.0, +5),
    "Jalandhar": (31.3260, 75.5762, 30.0, +6),
    "Chandigarh": (30.7333, 76.7794, 26.0, +4),
    "Haryana": (29.0588, 76.0856, 33.0, +7),
    "Faridabad": (28.4089, 77.3178, 36.0, +8),
    "Gurugram": (28.4595, 77.0266, 35.0, +7),
    "Noida": (28.5355, 77.3910, 36.0, +8),
    "Ghaziabad": (28.6692, 77.4538, 37.0, +8),
    "Meerut": (28.9845, 77.7064, 32.0, +6),
    "Agra": (27.1767, 78.0081, 31.0, +5),
    "Kanpur": (26.4499, 80.3319, 35.0, +7),
    "Lucknow": (26.8467, 80.9462, 33.0, +7),
    "Varanasi": (25.3176, 82.9739, 30.0, +6),
    "Prayagraj": (25.4358, 81.8463, 29.0, +5),
    "Patna": (25.5941, 85.1376, 36.0, +8),
    "Bihar": (25.0961, 85.3131, 34.0, +7),
    "Uttar Pradesh": (26.8467, 80.9462, 32.0, +6),

    # Western India
    "Mumbai": (19.0760, 72.8777, 28.0, +2),
    "Thane": (19.2183, 72.9781, 26.0, +2),
    "Pune": (18.5204, 73.8567, 22.0, +1),
    "Nashik": (19.9975, 73.7898, 20.0, +1),
    "Nagpur": (21.1458, 79.0882, 21.0, +2),
    "Maharashtra": (19.7515, 75.7139, 23.0, +2),
    "Ahmedabad": (23.0225, 72.5714, 29.0, +4),
    "Surat": (21.1702, 72.8311, 27.0, +3),
    "Vadodara": (22.3072, 73.1812, 25.0, +3),
    "Rajkot": (22.3039, 70.8022, 21.0, +2),
    "Gujarat": (22.2587, 71.1924, 24.0, +3),
    "Jaipur": (26.9124, 75.7873, 24.0, +3),
    "Jodhpur": (26.2389, 73.0243, 19.0, +2),
    "Kota": (25.2138, 75.8648, 23.0, +3),
    "Rajasthan": (27.0238, 74.2179, 21.0, +2),
    "Goa": (15.2993, 74.1240, 14.0, 0),

    # Eastern & Central India
    "Kolkata": (22.5726, 88.3639, 31.0, +6),
    "Howrah": (22.5958, 88.2636, 30.0, +6),
    "West Bengal": (22.9868, 87.8550, 28.0, +5),
    "Ranchi": (23.3441, 85.3096, 23.0, +4),
    "Dhanbad": (23.7957, 86.4304, 28.0, +5),
    "Jharkhand": (23.6102, 85.2799, 24.0, +4),
    "Bhopal": (23.2599, 77.4126, 19.0, +2),
    "Indore": (22.7196, 75.8577, 23.0, +3),
    "Gwalior": (26.2183, 78.1828, 26.0, +4),
    "Madhya Pradesh": (22.9734, 78.6569, 20.0, +2),
    "Raipur": (21.2514, 81.6296, 25.0, +4),
    "Chhattisgarh": (21.2787, 81.8661, 23.0, +3),
    "Bhubaneswar": (20.2961, 85.8245, 22.0, +3),
    "Odisha": (20.9517, 85.0985, 21.0, +3),

    # Southern India
    "Bengaluru": (12.9716, 77.5946, 18.0, -2),
    "Mysore": (12.2958, 76.6394, 13.0, -1),
    "Hubli": (15.3647, 75.1240, 15.0, 0),
    "Karnataka": (15.3173, 75.7139, 17.0, -1),
    "Chennai": (13.0827, 80.2707, 17.0, -1),
    "Coimbatore": (11.0168, 76.9558, 15.0, -1),
    "Madurai": (9.9252, 78.1198, 14.0, -1),
    "Tamil Nadu": (11.1271, 78.6569, 16.0, -1),
    "Hyderabad": (17.3850, 78.4867, 21.0, +3),
    "Telangana": (18.1124, 79.0193, 20.0, +2),
    "Visakhapatnam": (17.6868, 83.2185, 19.0, +2),
    "Vijayawada": (16.5062, 80.6480, 18.0, +1),
    "Andhra Pradesh": (15.9129, 79.7400, 18.0, +1),
    "Kochi": (9.9312, 76.2673, 14.0, -3),
    "Thiruvananthapuram": (8.5241, 76.9366, 12.0, -2),
    "Kerala": (10.8505, 76.2711, 13.0, -2),

    # Northern & North-Eastern Hill Regions
    "Dehradun": (30.3165, 78.0322, 15.0, +2),
    "Uttarakhand": (30.0668, 79.0193, 14.0, +1),
    "Shimla": (31.1048, 77.1734, 8.0, -1),
    "Himachal Pradesh": (31.1048, 77.1734, 9.0, -1),
    "Srinagar": (34.0837, 74.7973, 11.0, -2),
    "Jammu and Kashmir": (33.7782, 76.5762, 12.0, -2),
    "Guwahati": (26.1445, 91.7362, 16.0, +1),
    "Assam": (26.2006, 92.9376, 15.0, +1),
}
BACKGROUND = 1.2  # x1e15 molecules/cm2


def build(seed: int = 42) -> tuple[np.ndarray, list[str]]:
    rng = np.random.default_rng(seed)
    T, Y, X = N_DAYS, len(LAT), len(LON)
    dates = [START + timedelta(days=i) for i in range(T)]
    t = np.arange(T)
    dow = np.array([d.weekday() for d in dates])
    weekly = np.where(dow == 5, 0.85, np.where(dow == 6, 0.75, 1.0))
    doy = np.array([d.timetuple().tm_yday for d in dates])
    seasonal = 1 + 0.25 * np.cos(2 * np.pi * (doy - 15) / 365)   # winter pollution peak
    weather = rng.lognormal(0, 0.12, T)                           # day-to-day meteorology
    LATG, LONG = np.meshgrid(LAT, LON, indexing="ij")

    cube = np.full((T, Y, X), BACKGROUND, dtype=np.float64)
    for lat0, lon0, peak, drift in CITY_PLUMES.values():
        sigma = 0.35 + 0.02 * peak                                # atmospheric dispersion
        win = (np.abs(LATG - lat0) < 3.5) & (np.abs(LONG - lon0) < 3.5)
        d2 = (LATG - lat0) ** 2 + ((LONG - lon0) * np.cos(np.radians(lat0))) ** 2
        plume = peak * np.exp(-d2 / (2 * sigma ** 2)) * win
        tf = (1 + drift / 100 * t / 30) * weekly * seasonal * weather
        cube += plume[None] * tf[:, None, None]
    cube *= rng.lognormal(0, 0.07, cube.shape)                    # instrument retrieval noise

    # clouds: spatially coherent blobs (~25% missing observations)
    coarse = rng.random((T, (Y + 7) // 8, (X + 7) // 8))
    cloud = np.repeat(np.repeat(coarse, 8, axis=1), 8, axis=2)[:, :Y, :X] > 0.74
    cloud |= rng.random(cube.shape) < 0.02
    cube = np.where(cloud, np.nan, cube) * 1e15
    return cube.astype(np.float32), [d.isoformat() for d in dates]


def main(out: str | None = None) -> None:
    out_path = Path(out or Path(__file__).resolve().parent.parent / "data" / "tempo_no2_grid.npz")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    cube, dates = build()
    np.savez_compressed(
        out_path,
        no2=cube,
        lat=LAT,
        lon=LON,
        dates=np.array(dates),
        source=np.array("SYNTHETIC satellite grid (Sentinel-5P / INSAT layout for India, molecules/cm2)"),
    )
    print(f"wrote {out_path} shape={cube.shape} size={out_path.stat().st_size/1e6:.1f} MB")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else None)
