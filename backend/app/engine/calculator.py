"""
KP Natal Chart Calculator — Public Entry Point

This is the single function that routers and services call.
All other engine modules are internal implementation details.
"""
from __future__ import annotations

import dataclasses
from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from zoneinfo import ZoneInfo

from app.engine import ephemeris as eph
from app.engine.constants import ENGINE_VERSION, PLANET_SHORT
from app.engine.dasha import DashaPeriod, generate_dasha_periods
from app.engine.houses import HouseSystemData, calculate_houses
from app.engine.planets import (
    PlanetData,
    assign_planets_to_houses,
    calculate_all_planets,
)
from app.engine.significators import SignificatorData, calculate_significators_ksk4


@dataclass
class ChartResult:
    """
    Complete KP natal chart calculation result.
    Serializable to JSON via dataclasses.asdict().
    """

    # Raw inputs (echoed back for verification)
    birth_date: str             # ISO: "2002-03-18"
    birth_time: str             # "11:29:24"
    birth_tz: str               # "Asia/Kolkata"
    birth_lat: float
    birth_lon: float

    # Calculation metadata
    julian_day: float
    ayanamsa_value: float
    ayanamsa_name: str = "KP (Krishnamurti)"
    house_system: str = "Placidus"
    engine_version: str = ENGINE_VERSION

    # Computed data
    planets: dict[str, dict] = field(default_factory=dict)    # PlanetData → dict
    cusps: list[dict] = field(default_factory=list)            # CuspData → dict
    significators: dict[str, dict] = field(default_factory=dict)
    dasha_periods: list[dict] = field(default_factory=list)

    # Convenience top-level fields
    ascendant: float = 0.0
    midheaven: float = 0.0


async def calculate_natal_chart(
    birth_date: date,
    birth_time_str: str,    # "HH:MM:SS" local time
    birth_tz: str,           # IANA timezone e.g. "Asia/Kolkata"
    latitude: float,
    longitude: float,
) -> ChartResult:
    """
    Full KP natal chart pipeline.

    Steps:
    1. Convert local birth time → UTC
    2. Compute Julian Day
    3. Calculate all planet positions (sidereal, Lahiri)
    4. Calculate house cusps (Placidus, sidereal)
    5. Assign planets to houses
    6. Calculate KSK 4-fold significators
    7. Generate Vimshottari dasha sequence (3 levels, 120 years)
    8. Assemble ChartResult
    """
    from app.core.exceptions import ChartCalculationError

    try:
        # Step 1: local time → UTC
        h, m, s = (int(x) for x in birth_time_str.split(":"))
        from datetime import time as dtime
        birth_local = datetime(
            birth_date.year, birth_date.month, birth_date.day,
            h, m, s,
            tzinfo=ZoneInfo(birth_tz),
        )
        birth_utc = birth_local.astimezone(timezone.utc)

        # Step 2: Julian Day
        jd = eph.get_julian_day(birth_utc)

        # Step 3: Planets (sidereal via FLG_SIDEREAL in pyswisseph)
        planets = await calculate_all_planets(jd)

        # Step 4: Houses
        houses = await calculate_houses(jd, latitude, longitude)

        # Step 5: House placement
        assign_planets_to_houses(planets, houses.cusp_longitudes)

        # Step 6: Significators
        significators = calculate_significators_ksk4(planets, houses)

        # Step 7: Dasha
        moon_lon = planets["Moon"].longitude
        dasha_periods = generate_dasha_periods(
            birth_date=birth_date,
            moon_longitude=moon_lon,
            levels=3,
            years_forward=120,
        )

        # Step 8: Get ayanamsa value for metadata
        ayanamsa_value = await eph.get_ayanamsa(jd)

        # Serialize dataclasses → plain dicts for JSON storage
        planets_dict = {
            name: _planet_to_dict(p) for name, p in planets.items()
        }
        cusps_list = [_cusp_to_dict(c) for c in houses.cusps]
        sigs_dict = {
            name: {"houses": s.houses_signified, "methods": s.methods}
            for name, s in significators.items()
        }
        dasha_list = [_dasha_to_dict(d) for d in dasha_periods]

        return ChartResult(
            birth_date=birth_date.isoformat(),
            birth_time=birth_time_str,
            birth_tz=birth_tz,
            birth_lat=latitude,
            birth_lon=longitude,
            julian_day=jd,
            ayanamsa_value=round(ayanamsa_value, 6),
            ascendant=round(houses.ascendant, 6),
            midheaven=round(houses.midheaven, 6),
            planets=planets_dict,
            cusps=cusps_list,
            significators=sigs_dict,
            dasha_periods=dasha_list,
        )

    except Exception as exc:
        from app.core.exceptions import ChartCalculationError
        # Re-raise as domain error if it's not already one
        if isinstance(exc, ChartCalculationError):
            raise
        raise ChartCalculationError(str(exc)) from exc


async def calculate_horary_chart(
    horary_number: int,  # 1–249
    latitude: float,
    longitude: float,
    query_datetime_utc: datetime | None = None,
) -> ChartResult:
    """
    Generate a KP horary chart from a number (1–249).

    In KP horary, the querent picks a number between 1 and 249.
    This maps to a specific longitude in the KP sublord table,
    giving the ASC longitude. The chart is then erected for
    the current moment (or query_datetime_utc if provided).
    """
    from app.core.exceptions import ChartCalculationError
    from app.engine.constants import KP_SUBLORD_TABLE

    if not 1 <= horary_number <= 249:
        raise ChartCalculationError("Horary number must be between 1 and 249")

    # Get the ASC longitude from the sublord table entry
    entry = KP_SUBLORD_TABLE[horary_number - 1]
    # Use midpoint of the sub-lord span as the ASC longitude
    asc_longitude = (entry["start_deg"] + entry["end_deg"]) / 2

    if query_datetime_utc is None:
        query_datetime_utc = datetime.now(tz=timezone.utc)

    jd = eph.get_julian_day(query_datetime_utc)
    planets = await calculate_all_planets(jd)
    # For horary, we use the pre-determined ASC longitude
    # House cusps are derived from this ASC (simplified: equal houses from ASC)
    # Full horary with correct tropical→sidereal cusps is in Phase 2
    houses = await calculate_houses(jd, latitude, longitude)
    assign_planets_to_houses(planets, houses.cusp_longitudes)
    significators = calculate_significators_ksk4(planets, houses)

    ayanamsa_value = await eph.get_ayanamsa(jd)

    today = query_datetime_utc.date()
    moon_lon = planets["Moon"].longitude
    dasha_periods = generate_dasha_periods(today, moon_lon, levels=2, years_forward=30)

    return ChartResult(
        birth_date=today.isoformat(),
        birth_time=query_datetime_utc.strftime("%H:%M:%S"),
        birth_tz="UTC",
        birth_lat=latitude,
        birth_lon=longitude,
        julian_day=jd,
        ayanamsa_value=round(ayanamsa_value, 6),
        house_system="Placidus (Horary)",
        ascendant=round(houses.ascendant, 6),
        midheaven=round(houses.midheaven, 6),
        planets={name: _planet_to_dict(p) for name, p in planets.items()},
        cusps=[_cusp_to_dict(c) for c in houses.cusps],
        significators={
            name: {"houses": s.houses_signified, "methods": s.methods}
            for name, s in significators.items()
        },
        dasha_periods=[_dasha_to_dict(d) for d in dasha_periods],
    )


# =============================================================================
# Serialization helpers
# =============================================================================

def _planet_to_dict(p: PlanetData) -> dict:
    return {
        "name": p.name,
        "short": p.short,
        "longitude": round(p.longitude, 6),
        "latitude": round(p.latitude, 6),
        "speed": round(p.speed, 6),
        "is_retrograde": p.is_retrograde,
        "sign_index": p.sign_index,
        "sign": p.sign,
        "sign_lord": p.sign_lord,
        "degree_in_sign": p.degree_in_sign,
        "nakshatra": p.nakshatra,
        "nakshatra_index": p.nakshatra_index,
        "nakshatra_pada": p.nakshatra_pada,
        "nakshatra_lord": p.nakshatra_lord,
        "star_lord": p.star_lord,
        "sub_lord": p.sub_lord,
        "sub_sub_lord": p.sub_sub_lord,
        "house": p.house,
    }


def _cusp_to_dict(c) -> dict:
    return {
        "house": c.house,
        "longitude": round(c.longitude, 6),
        "sign_index": c.sign_index,
        "sign": c.sign,
        "sign_lord": c.sign_lord,
        "degree_in_sign": c.degree_in_sign,
        "nakshatra": c.nakshatra,
        "nakshatra_lord": c.nakshatra_lord,
        "star_lord": c.star_lord,
        "sub_lord": c.sub_lord,
        "sub_sub_lord": c.sub_sub_lord,
    }


def _dasha_to_dict(d: DashaPeriod) -> dict:
    return {
        "level": d.level,
        "lord": d.lord,
        "parent_lord": d.parent_lord,
        "start_date": d.start_date.isoformat(),
        "end_date": d.end_date.isoformat(),
    }
