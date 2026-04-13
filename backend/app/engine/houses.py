"""
House cusp calculator (Placidus — KP standard).

Converts tropical house cusps from Swiss Ephemeris to sidereal
by applying the ayanamsa correction.
"""
from __future__ import annotations

from dataclasses import dataclass

from app.engine import ephemeris as eph
from app.engine.nakshatras import (
    format_dms,
    get_nakshatra,
    get_sign,
    get_sign_index,
    get_sign_lord,
)
from app.engine.sublords import get_lords


@dataclass
class CuspData:
    """KP data for a single house cusp."""

    house: int          # 1–12
    longitude: float    # Sidereal longitude

    sign_index: int
    sign: str
    sign_lord: str
    degree_in_sign: str

    nakshatra: str
    nakshatra_lord: str  # = star_lord

    star_lord: str
    sub_lord: str
    sub_sub_lord: str


@dataclass
class HouseSystemData:
    """Complete house system computation result."""

    cusps: list[CuspData]   # 12 entries, index 0 = house 1
    ascendant: float        # Sidereal ASC longitude
    midheaven: float        # Sidereal MC longitude

    # Convenience accessors
    @property
    def cusp_longitudes(self) -> list[float]:
        return [c.longitude for c in self.cusps]

    @property
    def asc_sign(self) -> str:
        return self.cusps[0].sign

    @property
    def asc_lord(self) -> str:
        return self.cusps[0].sign_lord

    @property
    def asc_star_lord(self) -> str:
        return self.cusps[0].star_lord

    @property
    def asc_sub_lord(self) -> str:
        return self.cusps[0].sub_lord


async def calculate_houses(
    jd: float,
    lat: float,
    lon: float,
) -> HouseSystemData:
    """
    Compute all 12 house cusps with full KP data.
    Uses Placidus division with Lahiri (KP) ayanamsa.
    """
    # Swiss Ephemeris returns tropical cusps from swe.houses()
    # We get ayanamsa separately and subtract it
    tropical_cusps, ascmc = await eph.calc_houses(jd, lat, lon)
    ayanamsa = await eph.get_ayanamsa(jd)

    # tropical_cusps is 1-indexed (index 0 unused in pyswisseph)
    # ascmc[0] = tropical ASC, ascmc[1] = tropical MC
    sidereal_cusps_raw = [
        eph.apply_sidereal_correction(tropical_cusps[i], ayanamsa)
        for i in range(1, 13)  # houses 1..12
    ]
    sidereal_asc = eph.apply_sidereal_correction(ascmc[0], ayanamsa)
    sidereal_mc = eph.apply_sidereal_correction(ascmc[1], ayanamsa)

    cusps: list[CuspData] = []
    for i, sidereal_lon in enumerate(sidereal_cusps_raw, start=1):
        nak = get_nakshatra(sidereal_lon)
        star_lord, sub_lord, sub_sub_lord = get_lords(sidereal_lon)
        sign = get_sign(sidereal_lon)

        cusps.append(CuspData(
            house=i,
            longitude=sidereal_lon,
            sign_index=get_sign_index(sidereal_lon),
            sign=sign,
            sign_lord=get_sign_lord(sidereal_lon),
            degree_in_sign=format_dms(sidereal_lon),
            nakshatra=nak["name"],
            nakshatra_lord=nak["ruler"],
            star_lord=star_lord,
            sub_lord=sub_lord,
            sub_sub_lord=sub_sub_lord,
        ))

    return HouseSystemData(
        cusps=cusps,
        ascendant=sidereal_asc,
        midheaven=sidereal_mc,
    )
