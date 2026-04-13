"""
Swiss Ephemeris wrapper

This is the ONLY module that imports swisseph (pysweph package).
All other engine modules call functions from here.

Package: pysweph (community-maintained fork of pyswisseph)
  pip install pysweph
  import swisseph as swe  ← same API, same import name

Thread safety: Swiss Ephemeris C functions (especially swe.set_ephe_path and
swe.calc_ut) are not thread-safe. All calls are routed through
asyncio.to_thread() so the FastAPI event loop is never blocked and
only one thread accesses the library at a time per process.

Ayanamsa: KP system uses SE_SIDM_KRISHNAMURTI (value 5), NOT Lahiri.
  KP precession rate: 50.2388475 arcsec/year
  Lahiri precession rate: 50.2388475 arcsec/year (historically same, but
  the epoch/reference point differs by a small but significant amount).
  Using the wrong constant causes ~1–3 arcsec error in positions — enough
  to flip sub-lord assignments at cusps.
"""
from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from pathlib import Path

import swisseph as swe

from app.engine.constants import SWE_PLANET_IDS

# =============================================================================
# Module-level initialization
# =============================================================================

_ephe_initialized = False


def initialize_ephemeris(ephe_path: str | Path) -> None:
    """
    Must be called once at application startup (in lifespan handler).
    Sets the ephemeris file path and KP ayanamsa.

    KP ayanamsa = swe.SIDM_KRISHNAMURTI (constant 5 in Swiss Ephemeris).
    This is NOT the same as Lahiri (constant 1) — they share the same
    precession rate but differ in reference epoch. Always use KRISHNAMURTI
    for KP charts to match published KPAstro / Jagannatha Hora outputs.
    """
    global _ephe_initialized
    swe.set_ephe_path(str(ephe_path))
    # KP Ayanamsa — SE_SIDM_KRISHNAMURTI = 5
    swe.set_sid_mode(swe.SIDM_KRISHNAMURTI)
    _ephe_initialized = True


# =============================================================================
# Low-level synchronous helpers (private — not safe to call from async directly)
# =============================================================================

def _julian_day(dt_utc: datetime) -> float:
    """Convert a UTC datetime to Julian Day Number."""
    hour_decimal = dt_utc.hour + dt_utc.minute / 60.0 + dt_utc.second / 3600.0
    return swe.julday(dt_utc.year, dt_utc.month, dt_utc.day, hour_decimal)


def _calc_planet_sync(jd: float, planet_name: str) -> tuple[float, float, float]:
    """
    Compute sidereal position of a planet.
    Returns (longitude, latitude, speed_deg_per_day).
    Speed < 0 means retrograde.
    """
    planet_id = SWE_PLANET_IDS[planet_name]
    flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL | swe.FLG_SPEED
    result, *_ = swe.calc_ut(jd, planet_id, flags)
    # result layout: (lon, lat, dist_au, speed_lon, speed_lat, speed_dist)
    return result[0], result[1], result[3]


def _calc_ketu_sync(rahu_longitude: float) -> tuple[float, float, float]:
    """Ketu is always exactly opposite Rahu."""
    ketu_lon = (rahu_longitude + 180.0) % 360.0
    return ketu_lon, 0.0, 0.0  # Ketu has no independent speed/latitude


def _calc_houses_sync(
    jd: float,
    lat: float,
    lon: float,
    system: bytes = b"P",  # P = Placidus (KP standard)
) -> tuple[tuple[float, ...], tuple[float, ...]]:
    """
    Compute house cusps using Placidus division.
    Returns (cusps_12, ascmc_10) where:
      cusps_12[0] = unused (Swiss Eph is 1-indexed), cusps_12[1..12] = cusp longitudes
      ascmc_10[0] = ASC, ascmc_10[1] = MC
    All values are tropical — apply sidereal correction separately.
    """
    cusps, ascmc = swe.houses(jd, lat, lon, system)
    return cusps, ascmc


def _get_ayanamsa_sync(jd: float) -> float:
    """Return the KP ayanamsa value for a given Julian Day."""
    return swe.get_ayanamsa_ut(jd)


# =============================================================================
# Async public API
# =============================================================================

async def calc_planet(jd: float, planet_name: str) -> tuple[float, float, float]:
    """Async: compute sidereal planet position. Returns (lon, lat, speed)."""
    return await asyncio.to_thread(_calc_planet_sync, jd, planet_name)


async def calc_houses(
    jd: float, lat: float, lon: float
) -> tuple[tuple[float, ...], tuple[float, ...]]:
    """Async: compute Placidus house cusps. Returns (cusps, ascmc)."""
    return await asyncio.to_thread(_calc_houses_sync, jd, lat, lon)


async def get_ayanamsa(jd: float) -> float:
    """Async: get KP ayanamsa value."""
    return await asyncio.to_thread(_get_ayanamsa_sync, jd)


def get_julian_day(dt_utc: datetime) -> float:
    """Synchronous Julian Day conversion — safe to call anywhere."""
    return _julian_day(dt_utc)


def apply_sidereal_correction(tropical_lon: float, ayanamsa: float) -> float:
    """Convert tropical longitude to sidereal by subtracting ayanamsa."""
    return (tropical_lon - ayanamsa) % 360.0
