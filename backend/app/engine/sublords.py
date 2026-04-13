"""
KP Sub-Lord resolution using the 249-entry pre-computed table.

Given any sidereal longitude, returns the star lord (nakshatra lord)
and sub lord via binary search — O(log 249) ≈ O(1) effectively.
"""
from __future__ import annotations

import bisect

from app.engine.constants import KP_SUBLORD_TABLE, NAKSHATRA_SPAN, VIMSHOTTARI_ORDER, SUBLORD_SPANS_DEG

# Pre-compute start_deg list for binary search
_TABLE_STARTS: list[float] = [entry["start_deg"] for entry in KP_SUBLORD_TABLE]


def _find_entry(longitude: float) -> dict:
    """Return the KP_SUBLORD_TABLE entry for the given sidereal longitude."""
    lon = longitude % 360.0
    # bisect_right gives us the insertion point; subtract 1 for the containing entry
    idx = bisect.bisect_right(_TABLE_STARTS, lon) - 1
    idx = max(0, min(idx, len(KP_SUBLORD_TABLE) - 1))
    return KP_SUBLORD_TABLE[idx]


def get_star_lord(longitude: float) -> str:
    """Return the nakshatra (star) lord for a given sidereal longitude."""
    return _find_entry(longitude)["nak_lord"]


def get_sub_lord(longitude: float) -> str:
    """Return the KP sub lord for a given sidereal longitude."""
    return _find_entry(longitude)["sub_lord"]


def get_sub_sub_lord(longitude: float) -> str:
    """
    Return the KP sub-sub lord (Sub of Sub).
    The sub-lord's span is itself divided by Vimshottari proportions,
    starting from the sub-lord itself.
    """
    entry = _find_entry(longitude)
    sub_lord = entry["sub_lord"]
    sub_start = entry["start_deg"]
    sub_end = entry["end_deg"]
    sub_span = sub_end - sub_start

    # Position within the sub-lord span
    lon = longitude % 360.0
    position_in_sub = lon - sub_start

    # Divide the sub-span by Vimshottari proportions
    sub_start_idx = VIMSHOTTARI_ORDER.index(sub_lord)
    current = 0.0
    for i in range(9):
        planet = VIMSHOTTARI_ORDER[(sub_start_idx + i) % 9]
        planet_span = (SUBLORD_SPANS_DEG[planet] / NAKSHATRA_SPAN) * sub_span
        if position_in_sub < current + planet_span:
            return planet
        current += planet_span

    # Fallback — should not reach here with valid longitude
    return VIMSHOTTARI_ORDER[(sub_start_idx + 8) % 9]


def get_lords(longitude: float) -> tuple[str, str, str]:
    """
    Return (star_lord, sub_lord, sub_sub_lord) for a sidereal longitude.
    Most efficient — single table lookup + one pass.
    """
    entry = _find_entry(longitude)
    star_lord = entry["nak_lord"]
    sub_lord = entry["sub_lord"]
    sub_sub_lord = get_sub_sub_lord(longitude)
    return star_lord, sub_lord, sub_sub_lord
