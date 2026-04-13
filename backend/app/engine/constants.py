"""
KP Astrology Constants

This module defines all static reference data used by the KP calculation engine.
No imports from the app layer — this is pure domain data.
"""
from __future__ import annotations

# =============================================================================
# Engine metadata
# =============================================================================
ENGINE_VERSION = "1.0.0"

# =============================================================================
# Planet definitions
# =============================================================================

# Short IDs used throughout the engine and in output JSON
PLANET_NAMES = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]

PLANET_SHORT = {
    "Sun": "Su", "Moon": "Mo", "Mars": "Ma",
    "Mercury": "Me", "Jupiter": "Ju", "Venus": "Ve",
    "Saturn": "Sa", "Rahu": "Ra", "Ketu": "Ke",
}

PLANET_FULL = {v: k for k, v in PLANET_SHORT.items()}

# pyswisseph planet IDs — imported lazily to avoid loading C extension at import time
# Use ephemeris.py functions to access these values
SWE_PLANET_IDS = {
    "Sun": 0,       # swe.SUN
    "Moon": 1,      # swe.MOON
    "Mercury": 2,   # swe.MERCURY
    "Venus": 3,     # swe.VENUS
    "Mars": 4,      # swe.MARS
    "Jupiter": 5,   # swe.JUPITER
    "Saturn": 6,    # swe.SATURN
    "Rahu": 11,     # swe.MEAN_NODE (KP uses mean node)
    # Ketu is not a pyswisseph planet — computed as Rahu + 180
}

# =============================================================================
# Zodiac signs
# =============================================================================

SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer",
    "Leo", "Virgo", "Libra", "Scorpio",
    "Sagittarius", "Capricorn", "Aquarius", "Pisces",
]

# Sign lords (KP uses the same as traditional Jyotish)
SIGN_LORDS = {
    "Aries": "Mars",        "Taurus": "Venus",      "Gemini": "Mercury",
    "Cancer": "Moon",       "Leo": "Sun",            "Virgo": "Mercury",
    "Libra": "Venus",       "Scorpio": "Mars",       "Sagittarius": "Jupiter",
    "Capricorn": "Saturn",  "Aquarius": "Saturn",    "Pisces": "Jupiter",
}

# =============================================================================
# 27 Nakshatras
# Each nakshatra = 13°20' = 800' arc-minutes
# Vimshottari lords cycle in the order defined by VIMSHOTTARI_ORDER
# =============================================================================

NAKSHATRA_SPAN = 360.0 / 27  # 13.333... degrees

NAKSHATRAS = [
    {"index": 0,  "name": "Ashwini",       "ruler": "Ketu"},
    {"index": 1,  "name": "Bharani",       "ruler": "Venus"},
    {"index": 2,  "name": "Krittika",      "ruler": "Sun"},
    {"index": 3,  "name": "Rohini",        "ruler": "Moon"},
    {"index": 4,  "name": "Mrigashira",    "ruler": "Mars"},
    {"index": 5,  "name": "Ardra",         "ruler": "Rahu"},
    {"index": 6,  "name": "Punarvasu",     "ruler": "Jupiter"},
    {"index": 7,  "name": "Pushya",        "ruler": "Saturn"},
    {"index": 8,  "name": "Ashlesha",      "ruler": "Mercury"},
    {"index": 9,  "name": "Magha",         "ruler": "Ketu"},
    {"index": 10, "name": "Purva Phalguni","ruler": "Venus"},
    {"index": 11, "name": "Uttara Phalguni","ruler": "Sun"},
    {"index": 12, "name": "Hasta",         "ruler": "Moon"},
    {"index": 13, "name": "Chitra",        "ruler": "Mars"},
    {"index": 14, "name": "Swati",         "ruler": "Rahu"},
    {"index": 15, "name": "Vishakha",      "ruler": "Jupiter"},
    {"index": 16, "name": "Anuradha",      "ruler": "Saturn"},
    {"index": 17, "name": "Jyeshtha",      "ruler": "Mercury"},
    {"index": 18, "name": "Mula",          "ruler": "Ketu"},
    {"index": 19, "name": "Purva Ashadha", "ruler": "Venus"},
    {"index": 20, "name": "Uttara Ashadha","ruler": "Sun"},
    {"index": 21, "name": "Shravana",      "ruler": "Moon"},
    {"index": 22, "name": "Dhanishta",     "ruler": "Mars"},
    {"index": 23, "name": "Shatabhisha",   "ruler": "Rahu"},
    {"index": 24, "name": "Purva Bhadra",  "ruler": "Jupiter"},
    {"index": 25, "name": "Uttara Bhadra", "ruler": "Saturn"},
    {"index": 26, "name": "Revati",        "ruler": "Mercury"},
]

# =============================================================================
# Vimshottari Dasha system
# Total = 120 years; proportions determine sub-lord spans
# =============================================================================

VIMSHOTTARI_TOTAL_YEARS = 120

VIMSHOTTARI_ORDER = [
    "Ketu", "Venus", "Sun", "Moon", "Mars",
    "Rahu", "Jupiter", "Saturn", "Mercury",
]

VIMSHOTTARI_YEARS: dict[str, int] = {
    "Ketu": 7, "Venus": 20, "Sun": 6, "Moon": 10, "Mars": 7,
    "Rahu": 18, "Jupiter": 16, "Saturn": 19, "Mercury": 17,
}

# Sub-lord span in degrees within a nakshatra (800' total per nak)
# Each planet gets: (years / 120) * 13.333...°
def _compute_sublord_spans() -> dict[str, float]:
    result = {}
    for planet, years in VIMSHOTTARI_YEARS.items():
        result[planet] = (years / VIMSHOTTARI_TOTAL_YEARS) * NAKSHATRA_SPAN
    return result

SUBLORD_SPANS_DEG: dict[str, float] = _compute_sublord_spans()

# =============================================================================
# KP 249 Sub-Lord Table
#
# The 360° zodiac is divided by 27 nakshatras × 9 sub-lords.
# 27 × 9 = 243 + 6 extra = 249 entries to cover exactly 360°.
# (The "extra 6" arise because the sub-lord sequence wraps around nakshatra
# boundaries, so some nakshatras have more than 9 sub-entries.)
#
# Each entry: {start_deg, end_deg, nak_index, nak_lord, sub_lord}
# =============================================================================

def _generate_kp_sublord_table() -> list[dict]:
    """
    Generate the complete 249-entry KP sub-lord table.
    Algorithm: iterate through all 27 nakshatras; within each nakshatra,
    iterate through 9 Vimshottari planets in sequence starting from the
    nakshatra's own lord, assigning sub-spans proportional to dasha years.
    """
    table = []
    current_deg = 0.0

    for nak in NAKSHATRAS:
        nak_start = current_deg
        nak_ruler = nak["ruler"]

        # Find starting sub-lord for this nakshatra (= nakshatra's own ruler)
        sub_start_idx = VIMSHOTTARI_ORDER.index(nak_ruler)

        nak_end = nak_start + NAKSHATRA_SPAN
        sub_current = nak_start

        for i in range(9):
            sub_planet = VIMSHOTTARI_ORDER[(sub_start_idx + i) % 9]
            sub_span = SUBLORD_SPANS_DEG[sub_planet]
            sub_end = sub_current + sub_span

            # Clamp to nakshatra boundary (handles floating-point accumulation)
            if i == 8:
                sub_end = nak_end

            table.append({
                "start_deg": sub_current,
                "end_deg": sub_end,
                "nak_index": nak["index"],
                "nak_lord": nak_ruler,
                "sub_lord": sub_planet,
            })
            sub_current = sub_end

        current_deg = nak_end

    return table


KP_SUBLORD_TABLE: list[dict] = _generate_kp_sublord_table()

# =============================================================================
# House natural significations (for reference / future use in rules engine)
# =============================================================================

HOUSE_SIGNIFICATIONS: dict[int, list[str]] = {
    1:  ["self", "health", "body", "personality", "longevity"],
    2:  ["wealth", "family", "speech", "food", "savings"],
    3:  ["siblings", "courage", "short_travel", "communication", "arts"],
    4:  ["mother", "home", "property", "vehicles", "education", "happiness"],
    5:  ["children", "intelligence", "speculation", "romance", "past_life"],
    6:  ["enemies", "disease", "debts", "service", "litigation"],
    7:  ["spouse", "partnership", "business", "foreign_travel"],
    8:  ["longevity", "occult", "inheritance", "surgery", "transformation"],
    9:  ["father", "guru", "higher_education", "long_travel", "luck", "dharma"],
    10: ["career", "profession", "reputation", "authority", "government"],
    11: ["gains", "income", "friends", "fulfillment", "elder_siblings"],
    12: ["losses", "expenses", "foreign_settlement", "moksha", "hospitalization"],
}

# =============================================================================
# KP Significator rules
# =============================================================================

# Planets and their natural significations (general)
NATURAL_SIGNIFICATIONS: dict[str, list[int]] = {
    "Sun":     [1, 9, 10],
    "Moon":    [2, 4],
    "Mars":    [3, 6, 8],
    "Mercury": [3, 6, 10],
    "Jupiter": [2, 5, 9, 11],
    "Venus":   [2, 4, 7, 12],
    "Saturn":  [6, 8, 10, 12],
    "Rahu":    [6, 8, 12],
    "Ketu":    [8, 12],
}
