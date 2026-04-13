"""
Planet position calculator.

Computes all 9 KP planets (Sun through Ketu) with full KP metadata:
sign, nakshatra, star lord, sub lord, sub-sub lord.
House assignment happens after house calculation in calculator.py.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from app.engine import ephemeris as eph
from app.engine.nakshatras import (
    format_dms,
    get_nakshatra,
    get_nakshatra_lord,
    get_nakshatra_pada,
    get_sign,
    get_sign_lord,
    get_sign_index,
)
from app.engine.sublords import get_lords


@dataclass
class PlanetData:
    """Full KP data for a single planet."""

    name: str           # Full name: "Sun", "Moon", etc.
    short: str          # Short ID: "Su", "Mo", etc.

    longitude: float    # Sidereal longitude 0–360
    latitude: float     # Ecliptic latitude
    speed: float        # Degrees/day; negative = retrograde
    is_retrograde: bool

    sign_index: int     # 0-based (0 = Aries)
    sign: str
    sign_lord: str
    degree_in_sign: str  # formatted DMS

    nakshatra: str
    nakshatra_index: int
    nakshatra_pada: int
    nakshatra_lord: str  # = star_lord

    star_lord: str
    sub_lord: str
    sub_sub_lord: str

    house: int = 0      # Set after house calculation; 0 = not yet assigned


async def calculate_all_planets(jd: float) -> dict[str, PlanetData]:
    """
    Compute sidereal positions for all 9 KP planets.
    Returns dict keyed by full planet name.
    """
    from app.engine.constants import PLANET_SHORT, SWE_PLANET_IDS

    # Get ayanamsa once — applied to all tropical positions from swe.houses()
    # Planet positions from swe.calc_ut with FLG_SIDEREAL are already sidereal
    # (ayanamsa applied internally by pyswisseph when SIDM_LAHIRI is set)

    results: dict[str, PlanetData] = {}

    # Compute planets that have direct pyswisseph IDs
    for planet_name in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu"]:
        lon, lat, speed = await eph.calc_planet(jd, planet_name)
        lon = lon % 360.0

        nak = get_nakshatra(lon)
        star_lord, sub_lord, sub_sub_lord = get_lords(lon)
        sign = get_sign(lon)
        sign_idx = get_sign_index(lon)

        results[planet_name] = PlanetData(
            name=planet_name,
            short=PLANET_SHORT[planet_name],
            longitude=lon,
            latitude=lat,
            speed=speed,
            is_retrograde=speed < 0,
            sign_index=sign_idx,
            sign=sign,
            sign_lord=get_sign_lord(lon),
            degree_in_sign=format_dms(lon),
            nakshatra=nak["name"],
            nakshatra_index=nak["index"],
            nakshatra_pada=get_nakshatra_pada(lon),
            nakshatra_lord=nak["ruler"],
            star_lord=star_lord,
            sub_lord=sub_lord,
            sub_sub_lord=sub_sub_lord,
        )

    # Ketu = Rahu + 180
    rahu = results["Rahu"]
    ketu_lon = (rahu.longitude + 180.0) % 360.0
    nak = get_nakshatra(ketu_lon)
    star_lord, sub_lord, sub_sub_lord = get_lords(ketu_lon)
    sign = get_sign(ketu_lon)
    sign_idx = get_sign_index(ketu_lon)

    results["Ketu"] = PlanetData(
        name="Ketu",
        short="Ke",
        longitude=ketu_lon,
        latitude=0.0,
        speed=0.0,
        is_retrograde=False,
        sign_index=sign_idx,
        sign=sign,
        sign_lord=get_sign_lord(ketu_lon),
        degree_in_sign=format_dms(ketu_lon),
        nakshatra=nak["name"],
        nakshatra_index=nak["index"],
        nakshatra_pada=get_nakshatra_pada(ketu_lon),
        nakshatra_lord=nak["ruler"],
        star_lord=star_lord,
        sub_lord=sub_lord,
        sub_sub_lord=sub_sub_lord,
    )

    return results


def assign_planets_to_houses(
    planets: dict[str, PlanetData],
    cusp_longitudes: list[float],  # 12 values, index 0 = house 1 cusp
) -> None:
    """
    Assign house numbers to each planet in-place.
    KP uses cusp-based house placement (NOT sign-based).

    A planet is in house N if its longitude falls between cusp N and cusp N+1.
    """
    n = len(cusp_longitudes)
    for planet in planets.values():
        lon = planet.longitude
        planet.house = _find_house(lon, cusp_longitudes)


def _find_house(longitude: float, cusps: list[float]) -> int:
    """Return house number (1-12) for a given longitude given 12 cusp longitudes."""
    for i in range(12):
        cusp_start = cusps[i]
        cusp_end = cusps[(i + 1) % 12]

        if cusp_start <= cusp_end:
            if cusp_start <= longitude < cusp_end:
                return i + 1
        else:
            # Wraps around 0°/360° boundary
            if longitude >= cusp_start or longitude < cusp_end:
                return i + 1

    return 1  # fallback
