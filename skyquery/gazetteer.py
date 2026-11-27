"""Offline gazetteer for the India region (name -> lat/lon).

Covers:
  - All 28 Indian States & 8 Union Territories
  - Major Indian metropolitan areas, industrial belts, and cities
  - Common colloquial aliases (e.g. Bombay -> Mumbai, Bangalore -> Bengaluru)
  - Key international cities outside coverage (so the bot gives an informed 'out of coverage' answer)
"""
from __future__ import annotations
import re
from pathlib import Path

INDIAN_STATES_AND_UTS = (
    "Punjab", "Delhi", "Haryana", "Rajasthan", "Uttar Pradesh", "Bihar",
    "Madhya Pradesh", "Gujarat", "Maharashtra", "West Bengal", "Odisha",
    "Jharkhand", "Chhattisgarh", "Andhra Pradesh", "Telangana", "Karnataka",
    "Tamil Nadu", "Kerala", "Goa", "Himachal Pradesh", "Uttarakhand",
    "Jammu and Kashmir", "Ladakh", "Assam", "Sikkim", "Arunachal Pradesh",
    "Nagaland", "Manipur", "Mizoram", "Tripura", "Meghalaya", "Chandigarh",
    "Puducherry", "Andaman and Nicobar", "Lakshadweep",
    "Dadra and Nagar Haveli and Daman and Diu",
)

CITIES: dict[str, tuple[float, float]] = {
    # -------------------------------------------------------------------------
    # States & Union Territories of India
    # -------------------------------------------------------------------------
    "Punjab": (31.1471, 75.3412),
    "Delhi": (28.6139, 77.2090),
    "Haryana": (29.0588, 76.0856),
    "Rajasthan": (27.0238, 74.2179),
    "Uttar Pradesh": (26.8467, 80.9462),
    "Bihar": (25.0961, 85.3131),
    "Madhya Pradesh": (22.9734, 78.6569),
    "Gujarat": (22.2587, 71.1924),
    "Maharashtra": (19.7515, 75.7139),
    "West Bengal": (22.9868, 87.8550),
    "Odisha": (20.9517, 85.0985),
    "Jharkhand": (23.6102, 85.2799),
    "Chhattisgarh": (21.2787, 81.8661),
    "Andhra Pradesh": (15.9129, 79.7400),
    "Telangana": (18.1124, 79.0193),
    "Karnataka": (15.3173, 75.7139),
    "Tamil Nadu": (11.1271, 78.6569),
    "Kerala": (10.8505, 76.2711),
    "Goa": (15.2993, 74.1240),
    "Himachal Pradesh": (31.1048, 77.1734),
    "Uttarakhand": (30.0668, 79.0193),
    "Jammu and Kashmir": (33.7782, 76.5762),
    "Ladakh": (34.1526, 77.5771),
    "Assam": (26.2006, 92.9376),
    "Sikkim": (27.5330, 88.5122),
    "Arunachal Pradesh": (28.2180, 94.7278),
    "Nagaland": (26.1584, 94.5624),
    "Manipur": (24.6637, 93.9063),
    "Mizoram": (23.1645, 92.9376),
    "Tripura": (23.9408, 91.9882),
    "Meghalaya": (25.4670, 91.3662),
    "Chandigarh": (30.7333, 76.7794),
    "Puducherry": (11.9416, 79.8083),
    "Andaman and Nicobar": (11.7401, 92.6586),
    "Lakshadweep": (10.5667, 72.6417),

    # -------------------------------------------------------------------------
    # Major Indian Cities & Industrial Districts
    # -------------------------------------------------------------------------
    "Mumbai": (19.0760, 72.8777),
    "Bengaluru": (12.9716, 77.5946),
    "Kolkata": (22.5726, 88.3639),
    "Chennai": (13.0827, 80.2707),
    "Hyderabad": (17.3850, 78.4867),
    "Ahmedabad": (23.0225, 72.5714),
    "Pune": (18.5204, 73.8567),
    "Surat": (21.1702, 72.8311),
    "Jaipur": (26.9124, 75.7873),
    "Lucknow": (26.8467, 80.9462),
    "Kanpur": (26.4499, 80.3319),
    "Nagpur": (21.1458, 79.0882),
    "Indore": (22.7196, 75.8577),
    "Thane": (19.2183, 72.9781),
    "Bhopal": (23.2599, 77.4126),
    "Visakhapatnam": (17.6868, 83.2185),
    "Patna": (25.5941, 85.1376),
    "Vadodara": (22.3072, 73.1812),
    "Ghaziabad": (28.6692, 77.4538),
    "Ludhiana": (30.9010, 75.8573),
    "Agra": (27.1767, 78.0081),
    "Nashik": (19.9975, 73.7898),
    "Faridabad": (28.4089, 77.3178),
    "Meerut": (28.9845, 77.7064),
    "Rajkot": (22.3039, 70.8022),
    "Varanasi": (25.3176, 82.9739),
    "Srinagar": (34.0837, 74.7973),
    "Aurangabad": (19.8762, 75.3433),
    "Dhanbad": (23.7957, 86.4304),
    "Amritsar": (31.6340, 74.8723),
    "Navi Mumbai": (19.0330, 73.0297),
    "Prayagraj": (25.4358, 81.8463),
    "Ranchi": (23.3441, 85.3096),
    "Howrah": (22.5958, 88.2636),
    "Coimbatore": (11.0168, 76.9558),
    "Jabalpur": (23.1815, 79.9864),
    "Gwalior": (26.2183, 78.1828),
    "Vijayawada": (16.5062, 80.6480),
    "Jodhpur": (26.2389, 73.0243),
    "Madurai": (9.9252, 78.1198),
    "Raipur": (21.2514, 81.6296),
    "Kota": (25.2138, 75.8648),
    "Guwahati": (26.1445, 91.7362),
    "Solapur": (17.6599, 75.9064),
    "Hubli": (15.3647, 75.1240),
    "Bareilly": (28.3670, 79.4304),
    "Moradabad": (28.8356, 78.7747),
    "Mysore": (12.2958, 76.6394),
    "Gurugram": (28.4595, 77.0266),
    "Noida": (28.5355, 77.3910),
    "Jalandhar": (31.3260, 75.5762),
    "Kochi": (9.9312, 76.2673),
    "Dehradun": (30.3165, 78.0322),
    "Shimla": (31.1048, 77.1734),
    "Bhubaneswar": (20.2961, 85.8245),
    "Thiruvananthapuram": (8.5241, 76.9366),
    "Bathinda": (30.2110, 74.9455),
    "Patiala": (30.3398, 76.3869),
    "Mohali": (30.7046, 76.7179),
    "Panaji": (15.4909, 73.8278),
    "Gandhinagar": (23.2156, 72.6369),
    "Amaravati": (16.5410, 80.5150),
    "Itanagar": (27.0844, 93.6053),
    "Dispur": (26.1433, 91.7898),
    "Shillong": (25.5788, 91.8933),
    "Kohima": (25.6751, 94.1086),
    "Imphal": (24.8170, 93.9368),
    "Aizawl": (23.7271, 92.7176),
    "Agartala": (23.8315, 91.2868),
    "Gangtok": (27.3389, 88.6065),
    "Port Blair": (11.6234, 92.7265),
    "Kavaratti": (10.5669, 72.6420),
    "Daman": (20.3974, 72.8328),
    "Silvassa": (20.2766, 73.0083),
    "Jammu": (32.7266, 74.8570),
    "Jamshedpur": (22.8046, 86.2029),
    "Cuttack": (20.4625, 85.8830),
    "Rourkela": (22.2604, 84.8536),
    "Ujjain": (23.1793, 75.7849),
    "Gorakhpur": (26.7606, 83.3732),
    "Gaya": (24.7955, 84.9994),
    "Muzaffarpur": (26.1209, 85.3647),
    "Mangaluru": (12.9141, 74.8560),
    "Kozhikode": (11.2588, 75.7804),
    "Thrissur": (10.5276, 76.2144),
    "Tiruchirappalli": (10.7905, 78.7047),
    "Salem": (11.6643, 78.1460),
    "Tiruppur": (11.1085, 77.3411),
    "Guntur": (16.3067, 80.4365),
    "Nellore": (14.4426, 79.9865),
    "Kurnool": (15.8281, 78.0373),
    "Tirupati": (13.6288, 79.4192),
    "Warangal": (17.9689, 79.5941),
    "Kolhapur": (16.7050, 74.2433),
    "Udaipur": (24.5854, 73.7125),
    "Ajmer": (26.4499, 74.6399),
    "Bikaner": (28.0229, 73.3119),
    "Dadra and Nagar Haveli and Daman and Diu": (20.18, 73.02),

    # -------------------------------------------------------------------------
    # Outside coverage (kept to provide explicit out-of-coverage refusals)
    # -------------------------------------------------------------------------
    "New York": (40.7128, -74.0060),
    "London": (51.5074, -0.1278),
    "Paris": (48.8566, 2.3522),
    "Tokyo": (35.6762, 139.6503),
    "Beijing": (39.9042, 116.4074),
    "Sydney": (-33.8688, 151.2093),
    "Houston": (29.7604, -95.3698),
    "Los Angeles": (34.0522, -118.2437),
    "Chicago": (41.8781, -87.6298),
}

OUTSIDE_COVERAGE_CITIES = (
    "New York", "London", "Paris", "Tokyo", "Beijing", "Sydney",
    "Houston", "Los Angeles", "Chicago",
)
INDIAN_CITY_COORDINATES: dict[str, tuple[float, float]] = {
    name: coordinates for name, coordinates in CITIES.items()
    if name not in INDIAN_STATES_AND_UTS and name not in OUTSIDE_COVERAGE_CITIES
}
_CITY_FILE = Path(__file__).resolve().parent.parent / "data" / "india_cities.tsv"
if _CITY_FILE.exists():
    for _line in _CITY_FILE.read_text(encoding="utf-8").splitlines():
        if _line and not _line.startswith("#"):
            _name, _lat, _lon = _line.split("\t")
            INDIAN_CITY_COORDINATES[_name] = (float(_lat), float(_lon))
            CITIES[_name] = INDIAN_CITY_COORDINATES[_name]

# (regex, canonical name, case_sensitive)
_ALIASES: list[tuple[str, str, bool]] = [
    (r"\bNew Delhi\b", "Delhi", False),
    (r"\bNCR\b", "Delhi", True),
    (r"\bBombay\b", "Mumbai", False),
    (r"\bBangalore\b", "Bengaluru", False),
    (r"\bCalcutta\b", "Kolkata", False),
    (r"\bMadras\b", "Chennai", False),
    (r"\bBenares\b", "Varanasi", False),
    (r"\bKashi\b", "Varanasi", False),
    (r"\bCochin\b", "Kochi", False),
    (r"\bTrivandrum\b", "Thiruvananthapuram", False),
    (r"\bAllahabad\b", "Prayagraj", False),
    (r"\bGurgaon\b", "Gurugram", False),
    (r"\bMysuru\b", "Mysore", False),
    (r"\bTrichy\b", "Tiruchirappalli", False),
    (r"\bMangalore\b", "Mangaluru", False),
    (r"\bBaroda\b", "Vadodara", False),
    (r"\bPoona\b", "Pune", False),
    (r"\bBanaras\b", "Varanasi", False),
    (r"\bNYC\b", "New York", False),
    (r"\bLA\b", "Los Angeles", True),
    (r"\bDC\b", "Delhi", True),
]


def _patterns() -> list[tuple[re.Pattern, str]]:
    pats: list[tuple[re.Pattern, str]] = []
    for name in CITIES:
        pats.append((re.compile(r"\b" + re.escape(name) + r"\b", re.I), name))
    for rx, canon, cs in _ALIASES:
        pats.append((re.compile(rx, 0 if cs else re.I), canon))
    pats.sort(key=lambda p: -len(p[0].pattern))
    return pats


_PATS = _patterns()


def find_in_text(text: str) -> list[str]:
    """Return canonical city names mentioned in text, in order of first appearance (no duplicates)."""
    taken: list[tuple[int, int]] = []
    hits: list[tuple[int, str]] = []
    for pat, canon in _PATS:
        for m in pat.finditer(text):
            s, e = m.span()
            if any(s < te and e > ts for ts, te in taken):
                continue
            taken.append((s, e))
            hits.append((s, canon))
    hits.sort()
    out: list[str] = []
    for _, c in hits:
        if c not in out:
            out.append(c)
    return out


def lookup(name: str) -> tuple[str, float, float] | None:
    """Case-insensitive lookup of a name / alias. Returns (canonical, lat, lon) or None."""
    found = find_in_text(name)
    if found:
        c = found[0]
        return c, CITIES[c][0], CITIES[c][1]
    return None
