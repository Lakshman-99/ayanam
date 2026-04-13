"""
Vimshottari Dasha Calculator

Computes the dasha balance at birth from Moon's nakshatra position,
then generates the full dasha/bhukti/antara sequence.

Algorithm:
1. Determine Moon's nakshatra at birth
2. That nakshatra's lord = current Mahadasha lord
3. Fraction elapsed in nakshatra = fraction elapsed in Mahadasha
4. Remaining balance = first dasha period
5. Subsequent dashas follow VIMSHOTTARI_ORDER cyclically
6. Each dasha is subdivided into bhuktis using the same proportional logic
7. Each bhukti is subdivided into antaras
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta

from app.engine.constants import (
    VIMSHOTTARI_ORDER,
    VIMSHOTTARI_TOTAL_YEARS,
    VIMSHOTTARI_YEARS,
)
from app.engine.nakshatras import nakshatra_balance_elapsed

# Gregorian days in a Vimshottari year (used for date arithmetic)
DAYS_PER_YEAR = 365.25


@dataclass
class DashaPeriod:
    """A single dasha/bhukti/antara period."""

    level: int          # 1 = Mahadasha, 2 = Bhukti, 3 = Antara
    lord: str           # Planet name
    parent_lord: str | None  # Parent period's lord (None for Mahadasha)
    start_date: date
    end_date: date

    @property
    def duration_days(self) -> int:
        return (self.end_date - self.start_date).days


def _years_to_days(years: float) -> int:
    return round(years * DAYS_PER_YEAR)


def compute_dasha_balance(moon_longitude: float, birth_date: date) -> tuple[str, date]:
    """
    Compute the remaining balance of the current Mahadasha at birth.

    Returns:
        (dasha_lord, dasha_end_date)

    The fraction elapsed in the nakshatra gives the fraction elapsed in the dasha.
    Remaining fraction × dasha years = remaining dasha balance.
    """
    fraction_elapsed = nakshatra_balance_elapsed(moon_longitude)
    fraction_remaining = 1.0 - fraction_elapsed

    from app.engine.nakshatras import get_nakshatra
    nak = get_nakshatra(moon_longitude)
    dasha_lord = nak["ruler"]

    total_years = VIMSHOTTARI_YEARS[dasha_lord]
    remaining_years = fraction_remaining * total_years
    remaining_days = _years_to_days(remaining_years)

    dasha_end = birth_date + timedelta(days=remaining_days)
    return dasha_lord, dasha_end


def generate_dasha_periods(
    birth_date: date,
    moon_longitude: float,
    levels: int = 3,
    years_forward: int = 120,
) -> list[DashaPeriod]:
    """
    Generate the complete Vimshottari dasha sequence.

    Args:
        birth_date: Date of birth (local date, day-accurate)
        moon_longitude: Sidereal longitude of Moon at birth
        levels: 1 = Mahadasha only, 2 = +Bhukti, 3 = +Antara
        years_forward: How many years ahead to generate

    Returns:
        Flat list of DashaPeriod ordered by start_date.
    """
    from app.engine.nakshatras import get_nakshatra
    nak = get_nakshatra(moon_longitude)
    first_lord = nak["ruler"]
    first_lord_idx = VIMSHOTTARI_ORDER.index(first_lord)

    fraction_elapsed = nakshatra_balance_elapsed(moon_longitude)

    cutoff_date = birth_date + timedelta(days=_years_to_days(years_forward))
    all_periods: list[DashaPeriod] = []

    # --- Mahadasha sequence ---
    maha_start = birth_date

    for maha_offset in range(9):
        maha_lord = VIMSHOTTARI_ORDER[(first_lord_idx + maha_offset) % 9]
        maha_years_full = VIMSHOTTARI_YEARS[maha_lord]

        if maha_offset == 0:
            # First dasha: only the remaining fraction
            maha_years = (1.0 - fraction_elapsed) * maha_years_full
        else:
            maha_years = float(maha_years_full)

        maha_days = _years_to_days(maha_years)
        maha_end = maha_start + timedelta(days=maha_days)

        if maha_start > cutoff_date:
            break

        maha_period = DashaPeriod(
            level=1,
            lord=maha_lord,
            parent_lord=None,
            start_date=maha_start,
            end_date=maha_end,
        )
        all_periods.append(maha_period)

        if levels >= 2:
            all_periods.extend(
                _generate_bhuktis(maha_lord, maha_start, maha_end, levels, cutoff_date)
            )

        maha_start = maha_end

        # After first dasha, restart the sequence for subsequent dashas
        if maha_offset == 0:
            first_lord_idx = first_lord_idx  # next iteration picks (first_lord_idx + 1) % 9
        else:
            pass

    return all_periods


def _generate_bhuktis(
    maha_lord: str,
    maha_start: date,
    maha_end: date,
    levels: int,
    cutoff_date: date,
) -> list[DashaPeriod]:
    """Generate bhukti sub-periods within a Mahadasha."""
    maha_years_full = float(VIMSHOTTARI_YEARS[maha_lord])
    maha_lord_idx = VIMSHOTTARI_ORDER.index(maha_lord)
    maha_total_days = (maha_end - maha_start).days

    bhuktis: list[DashaPeriod] = []
    bhukti_start = maha_start

    for bhukti_offset in range(9):
        bhukti_lord = VIMSHOTTARI_ORDER[(maha_lord_idx + bhukti_offset) % 9]
        bhukti_years = VIMSHOTTARI_YEARS[bhukti_lord]

        # Bhukti duration = (bhukti_years / 120) * maha_total_days
        bhukti_days = round((bhukti_years / VIMSHOTTARI_TOTAL_YEARS) * maha_total_days)
        bhukti_end = bhukti_start + timedelta(days=bhukti_days)

        # Clamp last bhukti to maha_end
        if bhukti_offset == 8:
            bhukti_end = maha_end

        if bhukti_start > cutoff_date:
            break

        bhukti_period = DashaPeriod(
            level=2,
            lord=bhukti_lord,
            parent_lord=maha_lord,
            start_date=bhukti_start,
            end_date=bhukti_end,
        )
        bhuktis.append(bhukti_period)

        if levels >= 3:
            bhuktis.extend(
                _generate_antaras(
                    maha_lord, bhukti_lord, bhukti_start, bhukti_end, cutoff_date
                )
            )

        bhukti_start = bhukti_end

    return bhuktis


def _generate_antaras(
    maha_lord: str,
    bhukti_lord: str,
    bhukti_start: date,
    bhukti_end: date,
    cutoff_date: date,
) -> list[DashaPeriod]:
    """Generate antara sub-sub-periods within a Bhukti."""
    bhukti_years = float(VIMSHOTTARI_YEARS[bhukti_lord])
    bhukti_lord_idx = VIMSHOTTARI_ORDER.index(bhukti_lord)
    bhukti_total_days = (bhukti_end - bhukti_start).days

    antaras: list[DashaPeriod] = []
    antara_start = bhukti_start

    for antara_offset in range(9):
        antara_lord = VIMSHOTTARI_ORDER[(bhukti_lord_idx + antara_offset) % 9]
        antara_years = VIMSHOTTARI_YEARS[antara_lord]

        antara_days = round(
            (antara_years / VIMSHOTTARI_TOTAL_YEARS) * bhukti_total_days
        )
        antara_end = antara_start + timedelta(days=antara_days)

        if antara_offset == 8:
            antara_end = bhukti_end

        if antara_start > cutoff_date:
            break

        antaras.append(DashaPeriod(
            level=3,
            lord=antara_lord,
            parent_lord=bhukti_lord,
            start_date=antara_start,
            end_date=antara_end,
        ))

        antara_start = antara_end

    return antaras


def get_current_dasha(periods: list[DashaPeriod], on_date: date) -> dict:
    """
    Return the current running Maha/Bhukti/Antara for a given date.
    Returns dict with keys: mahadasha, bhukti, antara (planet names).
    """
    result = {"mahadasha": None, "bhukti": None, "antara": None}
    for p in periods:
        if p.start_date <= on_date < p.end_date:
            if p.level == 1:
                result["mahadasha"] = p.lord
            elif p.level == 2:
                result["bhukti"] = p.lord
            elif p.level == 3:
                result["antara"] = p.lord
    return result
