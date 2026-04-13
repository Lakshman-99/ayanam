"""
Nakshatra, Sign, and Pada calculations.
All pure functions — no async, no external dependencies.
"""
from __future__ import annotations

import math

from app.engine.constants import (
    NAKSHATRA_SPAN,
    NAKSHATRAS,
    SIGNS,
    SIGN_LORDS,
)

# Each pada = 1/4 of a nakshatra = 13°20' / 4 = 3°20'
PADA_SPAN = NAKSHATRA_SPAN / 4


def get_nakshatra_index(longitude: float) -> int:
    """Return 0-based nakshatra index for a sidereal longitude."""
    lon = longitude % 360.0
    return int(lon / NAKSHATRA_SPAN)


def get_nakshatra(longitude: float) -> dict:
    """Return the nakshatra dict for a given sidereal longitude."""
    return NAKSHATRAS[get_nakshatra_index(longitude)]


def get_nakshatra_pada(longitude: float) -> int:
    """Return pada (1-4) within the nakshatra for a given sidereal longitude."""
    lon = longitude % 360.0
    position_in_nak = lon % NAKSHATRA_SPAN
    pada = int(position_in_nak / PADA_SPAN) + 1
    return min(pada, 4)  # clamp to 4 for exact boundary


def get_nakshatra_lord(longitude: float) -> str:
    """Return the Vimshottari dasha lord of the nakshatra at a given longitude."""
    return get_nakshatra(longitude)["ruler"]


def get_sign_index(longitude: float) -> int:
    """Return 0-based sign index (0 = Aries, 11 = Pisces)."""
    return int((longitude % 360.0) / 30.0)


def get_sign(longitude: float) -> str:
    """Return the zodiac sign name for a given sidereal longitude."""
    return SIGNS[get_sign_index(longitude)]


def get_sign_lord(longitude: float) -> str:
    """Return the sign lord (planetary ruler) for a given longitude."""
    return SIGN_LORDS[get_sign(longitude)]


def format_dms(longitude: float) -> str:
    """
    Format a longitude as D°M'S\" within its sign.
    e.g. 345.394° → '15°23'38\"'  (within Pisces)
    """
    degrees_in_sign = longitude % 30.0
    d = int(degrees_in_sign)
    m_total = (degrees_in_sign - d) * 60
    m = int(m_total)
    s = int((m_total - m) * 60)
    return f"{d:02d}°{m:02d}'{s:02d}\""


def nakshatra_balance_elapsed(longitude: float) -> float:
    """
    Return the fraction of the current nakshatra already elapsed (0.0 – 1.0).
    Used to compute dasha balance at birth.
    """
    lon = longitude % 360.0
    position_in_nak = lon % NAKSHATRA_SPAN
    return position_in_nak / NAKSHATRA_SPAN
