"""
Oracle Benchmark Dataset Generator for JyotishOS (Phase 2 Task P2-T1).
Generates an authoritative, deterministic reference dataset of 100 benchmark charts
using Swiss Ephemeris (`swisseph`) across:
1. 20 Historical Benchmark Charts (BC to Modern)
2. 40 Modern Diverse Global Charts (Equator, Southern Hemisphere, Americas, Europe, Asia)
3. 20 Temporal Edge Dates (Leap years, J2000 epoch, Indian War Time +6:30, 1962/65/71 DST, Pre-1906 LMT)
4. 20 Circumpolar Polar Latitude Charts (65° to 78° N/S across Solstices/Equinoxes)

Serializes reference data to `tests/golden/oracle_100_benchmarks.json`.
"""

import os
import sys
import json
from datetime import datetime, date, time, timezone

# Ensure project root is in sys.path
curr_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(curr_dir, "..", ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.jyotish.core.models import BirthData
from src.jyotish.core.ephemeris import SwissEphemerisProvider
from src.jyotish.core.calculator import ChartCalculator
from src.jyotish.core.ashtakavarga import AshtakavargaCalculator
from src.jyotish.core.jaimini import default_jaimini_calculator
from src.jyotish.dasha.vimshottari import default_dasha_engine


# 1. 20 Historical Benchmark Cases
HISTORICAL_SPECS = [
    {"id": "HIST_01_SRI_RAMA", "name": "Sri Rama", "year": 100, "month": 4, "day": 10, "hour": 12, "min": 0, "lat": 26.7922, "lon": 82.1998, "city": "Ayodhya", "tz": "Asia/Kolkata"},
    {"id": "HIST_02_SRI_KRISHNA", "name": "Sri Krishna", "year": 200, "month": 7, "day": 19, "hour": 0, "min": 0, "lat": 27.4924, "lon": 77.6737, "city": "Mathura", "tz": "Asia/Kolkata"},
    {"id": "HIST_03_BUDDHA", "name": "Gautama Buddha", "year": 563, "month": 5, "day": 15, "hour": 12, "min": 0, "lat": 27.4705, "lon": 83.2755, "city": "Lumbini", "tz": "Asia/Kolkata"},
    {"id": "HIST_04_ADI_SHANKARA", "name": "Adi Shankara", "year": 788, "month": 4, "day": 12, "hour": 11, "min": 0, "lat": 10.1667, "lon": 76.4333, "city": "Kalady", "tz": "Asia/Kolkata"},
    {"id": "HIST_05_VARAHAMIHIRA", "name": "Varahamihira", "year": 505, "month": 3, "day": 20, "hour": 12, "min": 0, "lat": 23.1765, "lon": 75.7885, "city": "Ujjain", "tz": "Asia/Kolkata"},
    {"id": "HIST_06_CHAITANYA", "name": "Sri Chaitanya Mahaprabhu", "year": 1486, "month": 2, "day": 18, "hour": 18, "min": 15, "lat": 23.4064, "lon": 88.3658, "city": "Navadvipa", "tz": "Asia/Kolkata"},
    {"id": "HIST_07_AKBAR", "name": "Emperor Akbar", "year": 1542, "month": 10, "day": 15, "hour": 2, "min": 15, "lat": 25.3549, "lon": 69.7376, "city": "Umerkot", "tz": "Asia/Kolkata"},
    {"id": "HIST_08_SHIVAJI", "name": "Chhatrapati Shivaji Maharaj", "year": 1630, "month": 2, "day": 19, "hour": 18, "min": 30, "lat": 19.2064, "lon": 73.8606, "city": "Shivneri", "tz": "Asia/Kolkata"},
    {"id": "HIST_09_NEWTON", "name": "Sir Isaac Newton", "year": 1643, "month": 1, "day": 4, "hour": 1, "min": 30, "lat": 52.8090, "lon": -0.6300, "city": "Woolsthorpe", "tz": "Europe/London"},
    {"id": "HIST_10_GOETHE", "name": "Johann Wolfgang von Goethe", "year": 1749, "month": 8, "day": 28, "hour": 12, "min": 0, "lat": 50.1109, "lon": 8.6821, "city": "Frankfurt", "tz": "Europe/Berlin"},
    {"id": "HIST_11_LINCOLN", "name": "Abraham Lincoln", "year": 1809, "month": 2, "day": 12, "hour": 6, "min": 54, "lat": 37.5739, "lon": -85.7405, "city": "Hodgenville", "tz": "America/New_York"},
    {"id": "HIST_12_VIVEKANANDA", "name": "Swami Vivekananda", "year": 1863, "month": 1, "day": 12, "hour": 6, "min": 33, "lat": 22.5726, "lon": 88.3639, "city": "Kolkata", "tz": "Asia/Kolkata"},
    {"id": "HIST_13_GANDHI", "name": "Mahatma Gandhi", "year": 1869, "month": 10, "day": 2, "hour": 7, "min": 12, "lat": 21.6417, "lon": 69.6293, "city": "Porbandar", "tz": "Asia/Kolkata"},
    {"id": "HIST_14_EINSTEIN", "name": "Albert Einstein", "year": 1879, "month": 3, "day": 14, "hour": 11, "min": 30, "lat": 48.4011, "lon": 9.9876, "city": "Ulm", "tz": "Europe/Berlin"},
    {"id": "HIST_15_RAMANA_MAHARSHI", "name": "Sri Ramana Maharshi", "year": 1879, "month": 12, "day": 30, "hour": 1, "min": 0, "lat": 9.5333, "lon": 78.2000, "city": "Tiruchuzhi", "tz": "Asia/Kolkata"},
    {"id": "HIST_16_YOGANANDA", "name": "Paramahansa Yogananda", "year": 1893, "month": 1, "day": 5, "hour": 20, "min": 38, "lat": 26.7606, "lon": 83.3732, "city": "Gorakhpur", "tz": "Asia/Kolkata"},
    {"id": "HIST_17_PRABHUPADA", "name": "A.C. Bhaktivedanta Swami", "year": 1896, "month": 9, "day": 1, "hour": 16, "min": 0, "lat": 22.5726, "lon": 88.3639, "city": "Kolkata", "tz": "Asia/Kolkata"},
    {"id": "HIST_18_BOSE", "name": "Subhas Chandra Bose", "year": 1897, "month": 1, "day": 23, "hour": 12, "min": 15, "lat": 20.4625, "lon": 85.8828, "city": "Cuttack", "tz": "Asia/Kolkata"},
    {"id": "HIST_19_BV_RAMAN", "name": "Dr. B.V. Raman", "year": 1912, "month": 8, "day": 8, "hour": 19, "min": 43, "lat": 12.9716, "lon": 77.5946, "city": "Bangalore", "tz": "Asia/Kolkata"},
    {"id": "HIST_20_MANDELA", "name": "Nelson Mandela", "year": 1918, "month": 7, "day": 18, "hour": 14, "min": 30, "lat": -31.9544, "lon": 28.5133, "city": "Mvezo", "tz": "Africa/Johannesburg"},
]

# 2. 40 Modern Global Cities Specifications (Deterministic grid across world latitudes)
MODERN_CITIES = [
    ("Quito", -0.1807, -78.4678, "America/Guayaquil"),           # Equator
    ("Pontianak", -0.0263, 109.3425, "Asia/Pontianak"),          # Equator
    ("Nairobi", -1.2921, 36.8219, "Africa/Nairobi"),             # Near Equator
    ("Singapore", 1.3521, 103.8198, "Asia/Singapore"),           # Near Equator
    ("Macapa", 0.0389, -51.0664, "America/Belem"),               # Exact Equator
    ("Sydney", -33.8688, 151.2093, "Australia/Sydney"),          # Southern Mid
    ("Melbourne", -37.8136, 144.9631, "Australia/Melbourne"),    # Southern Mid
    ("Auckland", -36.8485, 174.7633, "Pacific/Auckland"),        # Southern Mid
    ("Buenos Aires", -34.6037, -58.3816, "America/Argentina/Buenos_Aires"), # Southern Mid
    ("Santiago", -33.4489, -70.6693, "America/Santiago"),        # Southern Mid
    ("Cape Town", -33.9249, 18.4241, "Africa/Johannesburg"),     # Southern Mid
    ("Rio de Janeiro", -22.9068, -43.1729, "America/Sao_Paulo"), # Southern Tropic
    ("Johannesburg", -26.2041, 28.0473, "Africa/Johannesburg"),  # Southern Tropic
    ("Lima", -12.0464, -77.0428, "America/Lima"),                # Southern Tropic
    ("Perth", -31.9505, 115.8605, "Australia/Perth"),            # Southern Mid
    ("Tokyo", 35.6762, 139.6503, "Asia/Tokyo"),                  # Northern Mid
    ("Beijing", 39.9042, 116.4074, "Asia/Shanghai"),             # Northern Mid
    ("Seoul", 37.5665, 126.9780, "Asia/Seoul"),                  # Northern Mid
    ("New Delhi", 28.6139, 77.2090, "Asia/Kolkata"),             # Northern Mid
    ("Mumbai", 19.0760, 72.8777, "Asia/Kolkata"),                # Northern Tropic
    ("Kolkata", 22.5726, 88.3639, "Asia/Kolkata"),               # Northern Tropic
    ("Chennai", 13.0827, 80.2707, "Asia/Kolkata"),               # Northern Tropic
    ("Bangalore", 12.9716, 77.5946, "Asia/Kolkata"),             # Northern Tropic
    ("Cairo", 30.0444, 31.2357, "Africa/Cairo"),                 # Northern Mid
    ("Dubai", 25.2048, 55.2708, "Asia/Dubai"),                   # Northern Tropic
    ("Riyadh", 24.7136, 46.6753, "Asia/Riyadh"),                 # Northern Tropic
    ("Bangkok", 13.7563, 100.5018, "Asia/Bangkok"),              # Northern Tropic
    ("London", 51.5074, -0.1278, "Europe/London"),               # Northern High
    ("Paris", 48.8566, 2.3522, "Europe/Paris"),                  # Northern Mid
    ("Berlin", 52.5200, 13.4050, "Europe/Berlin"),               # Northern Mid
    ("Rome", 41.9028, 12.4964, "Europe/Rome"),                   # Northern Mid
    ("Madrid", 40.4168, -3.7038, "Europe/Madrid"),               # Northern Mid
    ("Moscow", 55.7558, 37.6173, "Europe/Moscow"),               # Northern High
    ("New York", 40.7128, -74.0060, "America/New_York"),         # Northern Mid
    ("Los Angeles", 34.0522, -118.2437, "America/Los_Angeles"),  # Northern Mid
    ("Chicago", 41.8781, -87.6298, "America/Chicago"),           # Northern Mid
    ("Toronto", 43.6532, -79.3832, "America/Toronto"),           # Northern Mid
    ("Vancouver", 49.2827, -123.1207, "America/Vancouver"),      # Northern Mid
    ("Mexico City", 19.4326, -99.1332, "America/Mexico_City"),   # Northern Tropic
    ("Honolulu", 21.3069, -157.8583, "Pacific/Honolulu"),        # Northern Island
]

# 3. 20 Temporal Edge Cases
EDGE_SPECS = [
    {"id": "EDGE_01_J2000_EPOCH", "name": "J2000 Epoch", "year": 2000, "month": 1, "day": 1, "hour": 12, "min": 0, "lat": 0.0, "lon": 0.0, "city": "Greenwich Prime", "tz": "UTC"},
    {"id": "EDGE_02_CENTURY_LEAP", "name": "Century Leap 2000", "year": 2000, "month": 2, "day": 29, "hour": 23, "min": 59, "lat": 28.6139, "lon": 77.2090, "city": "Delhi", "tz": "Asia/Kolkata"},
    {"id": "EDGE_03_NON_LEAP_1900", "name": "Non-Leap 1900", "year": 1900, "month": 2, "day": 28, "hour": 12, "min": 0, "lat": 28.6139, "lon": 77.2090, "city": "Delhi", "tz": "Asia/Kolkata"},
    {"id": "EDGE_04_LEAP_2024", "name": "Leap 2024", "year": 2024, "month": 2, "day": 29, "hour": 15, "min": 30, "lat": 19.0760, "lon": 72.8777, "city": "Mumbai", "tz": "Asia/Kolkata"},
    {"id": "EDGE_05_WAR_TIME_1943", "name": "Indian War Time 1943", "year": 1943, "month": 6, "day": 15, "hour": 10, "min": 30, "lat": 26.8467, "lon": 80.9462, "city": "Lucknow", "tz": "Asia/Kolkata"},
    {"id": "EDGE_06_WAR_TIME_1944", "name": "Indian War Time 1944", "year": 1944, "month": 8, "day": 20, "hour": 16, "min": 45, "lat": 22.5726, "lon": 88.3639, "city": "Kolkata", "tz": "Asia/Kolkata"},
    {"id": "EDGE_07_WAR_TIME_1945", "name": "Indian War Time 1945", "year": 1945, "month": 9, "day": 1, "hour": 8, "min": 0, "lat": 13.0827, "lon": 80.2707, "city": "Chennai", "tz": "Asia/Kolkata"},
    {"id": "EDGE_08_DST_1962", "name": "Sino-Indian War DST 1962", "year": 1962, "month": 11, "day": 1, "hour": 11, "min": 0, "lat": 26.1445, "lon": 91.7362, "city": "Guwahati", "tz": "Asia/Kolkata"},
    {"id": "EDGE_09_DST_1965", "name": "Indo-Pak War DST 1965", "year": 1965, "month": 9, "day": 15, "hour": 14, "min": 0, "lat": 30.7333, "lon": 76.7794, "city": "Chandigarh", "tz": "Asia/Kolkata"},
    {"id": "EDGE_10_DST_1971", "name": "Indo-Pak War DST 1971", "year": 1971, "month": 12, "day": 10, "hour": 9, "min": 30, "lat": 28.6139, "lon": 77.2090, "city": "Delhi", "tz": "Asia/Kolkata"},
    {"id": "EDGE_11_LMT_1885", "name": "Pre-1906 LMT 1885", "year": 1885, "month": 5, "day": 15, "hour": 12, "min": 0, "lat": 22.5726, "lon": 88.3639, "city": "Kolkata", "tz": "Asia/Kolkata"},
    {"id": "EDGE_12_LMT_1900", "name": "Pre-1906 LMT 1900", "year": 1900, "month": 1, "day": 1, "hour": 6, "min": 0, "lat": 19.0760, "lon": 72.8777, "city": "Mumbai", "tz": "Asia/Kolkata"},
    {"id": "EDGE_13_LMT_1905", "name": "Pre-1906 Eve 1905", "year": 1905, "month": 12, "day": 31, "hour": 18, "min": 0, "lat": 26.8467, "lon": 80.9462, "city": "Lucknow", "tz": "Asia/Kolkata"},
    {"id": "EDGE_14_Y2K_EVE", "name": "Y2K Eve", "year": 1999, "month": 12, "day": 31, "hour": 23, "min": 59, "lat": 51.5074, "lon": -0.1278, "city": "London", "tz": "Europe/London"},
    {"id": "EDGE_15_MID_CENTURY_2050", "name": "Mid-Century 2050", "year": 2050, "month": 1, "day": 1, "hour": 0, "min": 1, "lat": 28.6139, "lon": 77.2090, "city": "Delhi", "tz": "Asia/Kolkata"},
    {"id": "EDGE_16_DST_FALL_FOLD0", "name": "US DST Fall-Back Fold 0", "year": 2023, "month": 11, "day": 5, "hour": 1, "min": 30, "lat": 40.7128, "lon": -74.0060, "city": "New York", "tz": "America/New_York", "fold": 0},
    {"id": "EDGE_17_DST_FALL_FOLD1", "name": "US DST Fall-Back Fold 1", "year": 2023, "month": 11, "day": 5, "hour": 1, "min": 30, "lat": 40.7128, "lon": -74.0060, "city": "New York", "tz": "America/New_York", "fold": 1},
    {"id": "EDGE_18_SUMMER_SOLSTICE", "name": "Summer Solstice 2024", "year": 2024, "month": 6, "day": 20, "hour": 20, "min": 51, "lat": 23.4372, "lon": 77.0000, "city": "Tropic of Cancer", "tz": "Asia/Kolkata"},
    {"id": "EDGE_19_WINTER_SOLSTICE", "name": "Winter Solstice 2024", "year": 2024, "month": 12, "day": 21, "hour": 9, "min": 20, "lat": -23.4372, "lon": 25.0000, "city": "Tropic of Capricorn", "tz": "Africa/Johannesburg"},
    {"id": "EDGE_20_EQUINOX_2024", "name": "Spring Equinox 2024", "year": 2024, "month": 3, "day": 20, "hour": 3, "min": 6, "lat": 0.0, "lon": 0.0, "city": "Equator Meridan", "tz": "UTC"},
]

# 4. 20 Polar Latitude Cases (65° to 78° N/S)
POLAR_SPECS = [
    {"id": "POLAR_01_TROMSO_SUMMER", "name": "Tromso Midnight Sun", "year": 2024, "month": 6, "day": 21, "hour": 0, "min": 0, "lat": 69.6492, "lon": 18.9553, "city": "Tromso", "tz": "Europe/Oslo"},
    {"id": "POLAR_02_TROMSO_WINTER", "name": "Tromso Polar Night", "year": 2024, "month": 12, "day": 21, "hour": 12, "min": 0, "lat": 69.6492, "lon": 18.9553, "city": "Tromso", "tz": "Europe/Oslo"},
    {"id": "POLAR_03_SVALBARD_SUMMER", "name": "Longyearbyen Svalbard Summer", "year": 2024, "month": 7, "day": 1, "hour": 14, "min": 0, "lat": 78.2232, "lon": 15.6267, "city": "Longyearbyen", "tz": "Europe/Oslo"},
    {"id": "POLAR_04_SVALBARD_WINTER", "name": "Longyearbyen Svalbard Winter", "year": 2024, "month": 1, "day": 15, "hour": 10, "min": 0, "lat": 78.2232, "lon": 15.6267, "city": "Longyearbyen", "tz": "Europe/Oslo"},
    {"id": "POLAR_05_MURMANSK_SPRING", "name": "Murmansk Spring Equinox", "year": 2024, "month": 3, "day": 20, "hour": 12, "min": 0, "lat": 68.9585, "lon": 33.0827, "city": "Murmansk", "tz": "Europe/Moscow"},
    {"id": "POLAR_06_MURMANSK_AUTUMN", "name": "Murmansk Autumn Equinox", "year": 2024, "month": 9, "day": 22, "hour": 15, "min": 30, "lat": 68.9585, "lon": 33.0827, "city": "Murmansk", "tz": "Europe/Moscow"},
    {"id": "POLAR_07_NORILSK_SOLSTICE", "name": "Norilsk Summer", "year": 2023, "month": 6, "day": 22, "hour": 18, "min": 0, "lat": 69.3558, "lon": 88.1893, "city": "Norilsk", "tz": "Asia/Krasnoyarsk"},
    {"id": "POLAR_08_NORILSK_WINTER", "name": "Norilsk Winter", "year": 2023, "month": 12, "day": 22, "hour": 6, "min": 0, "lat": 69.3558, "lon": 88.1893, "city": "Norilsk", "tz": "Asia/Krasnoyarsk"},
    {"id": "POLAR_09_BARROW_SUMMER", "name": "Utqiagvik Alaska Summer", "year": 2024, "month": 6, "day": 21, "hour": 12, "min": 0, "lat": 71.2906, "lon": -156.7886, "city": "Utqiagvik", "tz": "America/Anchorage"},
    {"id": "POLAR_10_BARROW_WINTER", "name": "Utqiagvik Alaska Winter", "year": 2024, "month": 12, "day": 21, "hour": 12, "min": 0, "lat": 71.2906, "lon": -156.7886, "city": "Utqiagvik", "tz": "America/Anchorage"},
    {"id": "POLAR_11_FAIRBANKS_SUMMER", "name": "Fairbanks Alaska Midsummer", "year": 2024, "month": 6, "day": 21, "hour": 23, "min": 0, "lat": 64.8378, "lon": -147.7164, "city": "Fairbanks", "tz": "America/Anchorage"},
    {"id": "POLAR_12_NUUK_WINTER", "name": "Nuuk Greenland Midwinter", "year": 2024, "month": 12, "day": 21, "hour": 13, "min": 0, "lat": 64.1814, "lon": -51.6941, "city": "Nuuk", "tz": "America/Nuuk"},
    {"id": "POLAR_13_OULU_SPRING", "name": "Oulu Finland Spring", "year": 2024, "month": 4, "day": 10, "hour": 9, "min": 0, "lat": 65.0121, "lon": 25.4651, "city": "Oulu", "tz": "Europe/Helsinki"},
    {"id": "POLAR_14_REYKJAVIK_EQUINOX", "name": "Reykjavik Iceland Equinox", "year": 2024, "month": 3, "day": 20, "hour": 12, "min": 0, "lat": 64.1466, "lon": -21.9426, "city": "Reykjavik", "tz": "Atlantic/Reykjavik"},
    {"id": "POLAR_15_ANTARCTIC_MCMURDO_SUMMER", "name": "McMurdo Antarctica Summer", "year": 2024, "month": 1, "day": 1, "hour": 12, "min": 0, "lat": -77.8419, "lon": 166.6863, "city": "McMurdo", "tz": "Pacific/Auckland"},
    {"id": "POLAR_16_ANTARCTIC_MCMURDO_WINTER", "name": "McMurdo Antarctica Winter", "year": 2024, "month": 6, "day": 21, "hour": 12, "min": 0, "lat": -77.8419, "lon": 166.6863, "city": "McMurdo", "tz": "Pacific/Auckland"},
    {"id": "POLAR_17_ANTARCTIC_PALMER", "name": "Palmer Station Antarctica", "year": 2024, "month": 11, "day": 15, "hour": 16, "min": 30, "lat": -64.7742, "lon": -64.0531, "city": "Palmer", "tz": "America/Punta_Arenas"},
    {"id": "POLAR_18_KIRUNA_SOLSTICE", "name": "Kiruna Sweden Summer", "year": 2024, "month": 6, "day": 21, "hour": 1, "min": 0, "lat": 67.8558, "lon": 20.2253, "city": "Kiruna", "tz": "Europe/Stockholm"},
    {"id": "POLAR_19_ALTA_WINTER", "name": "Alta Norway Polar Night", "year": 2023, "month": 12, "day": 25, "hour": 14, "min": 0, "lat": 69.9689, "lon": 23.2717, "city": "Alta", "tz": "Europe/Oslo"},
    {"id": "POLAR_20_INUVIK_ARCTIC", "name": "Inuvik Canada Arctic", "year": 2024, "month": 7, "day": 10, "hour": 17, "min": 0, "lat": 68.3607, "lon": -133.7230, "city": "Inuvik", "tz": "America/Inuvik"},
]


def build_all_100_case_specs():
    specs = []
    # 1. Historical 20
    for s in HISTORICAL_SPECS:
        specs.append({**s, "category": "historical"})

    # 2. Modern 40
    # Deterministic generation across 1950 - 2030
    for i, (c_name, c_lat, c_lon, c_tz) in enumerate(MODERN_CITIES):
        # Deterministic calendar spread: year = 1950 + (i * 2), month = (i % 12) + 1, day = ((i * 3) % 28) + 1
        y = 1950 + (i * 2)
        m = (i % 12) + 1
        d = ((i * 3) % 28) + 1
        h = (i * 5) % 24
        minute = (i * 13) % 60
        specs.append({
            "id": f"MODERN_{i+1:02d}_{c_name.upper().replace(' ', '_')}",
            "name": f"Modern {c_name} Native",
            "year": y,
            "month": m,
            "day": d,
            "hour": h,
            "min": minute,
            "lat": c_lat,
            "lon": c_lon,
            "city": c_name,
            "tz": c_tz,
            "category": "modern"
        })

    # 3. Edge 20
    for s in EDGE_SPECS:
        specs.append({**s, "category": "edge_dates"})

    # 4. Polar 20
    for s in POLAR_SPECS:
        specs.append({**s, "category": "polar_latitudes"})

    return specs


def generate_oracle_dataset():
    """Generates exact Swiss Ephemeris reference data for all 100 benchmark charts."""
    calc = ChartCalculator(SwissEphemerisProvider())
    specs = build_all_100_case_specs()
    assert len(specs) == 100, f"Expected exactly 100 benchmark cases, found {len(specs)}"

    oracle_db = {
        "metadata": {
            "version": "2.0.0",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "engine": "Swiss Ephemeris (swisseph)",
            "ayanamsa": "Lahiri (SIDM_LAHIRI = 1)",
            "total_benchmarks": 100,
            "categories": {
                "historical": 20,
                "modern": 40,
                "edge_dates": 20,
                "polar_latitudes": 20
            },
            "tolerances": {
                "graha_longitude_degrees": 0.001,       # <= 3.6 arcsec (Moshier) / <= 1 arcsec (.se1)
                "lagna_longitude_arcmin": 1.0,          # <= 0.0167 deg
                "house_cusp_arcmin": 1.0,               # <= 0.0167 deg
                "dasha_balance_years": 0.0001,          # <= ~1 hour
                "ashtakavarga_sav_sum": 337             # exact integer invariant
            }
        },
        "benchmarks": {}
    }

    print(f"Generating authoritative Swiss Ephemeris oracle for {len(specs)} benchmark charts...")

    for spec in specs:
        case_id = spec["id"]
        b_d = date(spec["year"], spec["month"], spec["day"])
        b_t = time(spec["hour"], spec["min"], 0)
        fold_val = spec.get("fold")

        # Determine house system: polar latitude uses Equal if requested or Placidus with polar safeguard
        hsys = "Whole Sign" if spec["category"] != "polar_latitudes" else "Equal"

        b_obj = BirthData(
            name=spec["name"],
            birth_date=b_d,
            birth_time=b_t,
            latitude=spec["lat"],
            longitude=spec["lon"],
            timezone=spec["tz"],
            city=spec["city"],
            fold=fold_val,
            house_system=hsys,
            birth_time_confidence="exact"
        )

        chart = calc.calculate_full_chart(b_obj, house_system=hsys)

        # 1. Planetary reference
        planets_ref = {}
        for p_name, p_pos in chart.planets.items():
            planets_ref[p_name] = {
                "longitude": round(p_pos.longitude, 6),
                "latitude": round(p_pos.latitude, 6),
                "speed": round(p_pos.speed, 6),
                "is_retrograde": p_pos.is_retrograde,
                "is_combust": p_pos.is_combust,
                "sign_id": p_pos.sign_id,
                "sign_name": p_pos.sign_name,
                "sign_degree": round(p_pos.sign_degree, 6),
                "nakshatra_name": p_pos.nakshatra_name,
                "nakshatra_pada": p_pos.nakshatra_pada,
            }

        # 2. Houses reference
        houses_ref = []
        for h in chart.houses:
            houses_ref.append({
                "house_number": h.house_number,
                "cusp_longitude": round(h.cusp_longitude, 6),
                "sign_id": h.sign_id,
                "sign_name": h.sign_name,
                "bhava_madhya": round(h.bhava_madhya, 6) if h.bhava_madhya is not None else None,
            })

        # 3. Ashtakavarga reference
        av = AshtakavargaCalculator.calculate(chart)
        assert av.total_bindus == 337, f"Invariant violated for {case_id}: SAV sum {av.total_bindus} != 337"

        # 4. Jaimini reference
        jaimini = default_jaimini_calculator.calculate(chart)

        # 5. Vimshottari dasha balance
        moon_lon = chart.planets["Moon"].longitude
        balance_lord, frac_elapsed, balance_years = default_dasha_engine.calculate_birth_balance(moon_lon)

        oracle_db["benchmarks"][case_id] = {
            "case_id": case_id,
            "category": spec["category"],
            "input": {
                "name": spec["name"],
                "birth_date": b_d.isoformat(),
                "birth_time": b_t.strftime("%H:%M:%S"),
                "latitude": spec["lat"],
                "longitude": spec["lon"],
                "timezone": spec["tz"],
                "city": spec["city"],
                "fold": fold_val,
                "house_system": hsys
            },
            "astronomical": {
                "jd_ut": round(chart.metadata.jd_ut, 6),
                "delta_t_seconds": round(chart.metadata.delta_t_seconds, 4),
                "ayanamsa_name": chart.metadata.ayanamsa_name,
                "ayanamsa_value": round(chart.metadata.ayanamsa_value, 6),
                "utc_datetime": chart.metadata.utc_datetime.isoformat() if chart.metadata.utc_datetime else None,
                "polar_latitude_adjusted": chart.metadata.polar_latitude_adjusted,
            },
            "lagna": {
                "sign_id": chart.lagna_sign_id,
                "sign_name": chart.lagna_sign_name,
                "degree": round(chart.lagna_degree, 6),
                "longitude": round(chart.lagna_longitude, 6)
            },
            "planets": planets_ref,
            "houses": houses_ref,
            "ashtakavarga": {
                "total_sav_bindus": av.total_bindus,
                "sav_signs": av.sav,
                "bav_totals": {p: sum(av.bav[p]) for p in av.bav}
            },
            "jaimini": {
                "chara_karakas_7": jaimini.karakas_7,
                "karakamsha_sign_name": jaimini.karakamsha_sign_name
            },
            "dasha_balance": {
                "lord": balance_lord,
                "balance_years": round(balance_years, 6)
            }
        }

    output_path = os.path.join(curr_dir, "oracle_100_benchmarks.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(oracle_db, f, indent=2)

    print(f"Successfully generated 100-chart Oracle snapshot -> {output_path}")
    return output_path


if __name__ == "__main__":
    generate_oracle_dataset()
