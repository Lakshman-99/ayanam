"""
Unit tests for KP engine constants.

These tests validate the structural integrity of the KP data tables.
They must pass before any chart calculation is attempted.
"""
from __future__ import annotations

import pytest

from app.engine.constants import (
    KP_SUBLORD_TABLE,
    NAKSHATRA_SPAN,
    NAKSHATRAS,
    PLANET_NAMES,
    PLANET_SHORT,
    SIGNS,
    VIMSHOTTARI_ORDER,
    VIMSHOTTARI_TOTAL_YEARS,
    VIMSHOTTARI_YEARS,
)


class TestNakshatras:
    def test_27_nakshatras(self):
        assert len(NAKSHATRAS) == 27

    def test_nakshatras_cover_full_zodiac(self):
        """27 × 13°20' = 360° exactly."""
        total = NAKSHATRA_SPAN * 27
        assert abs(total - 360.0) < 1e-9

    def test_nakshatra_indices_are_sequential(self):
        for i, nak in enumerate(NAKSHATRAS):
            assert nak["index"] == i, f"Nakshatra at position {i} has wrong index {nak['index']}"

    def test_nakshatra_lords_are_valid_planets(self):
        valid_lords = set(VIMSHOTTARI_ORDER)
        for nak in NAKSHATRAS:
            assert nak["ruler"] in valid_lords, f"{nak['name']} has invalid ruler {nak['ruler']!r}"

    def test_all_9_vimshottari_planets_are_lords(self):
        """Each of the 9 Vimshottari planets must appear as lord of exactly 3 nakshatras."""
        lord_counts: dict[str, int] = {}
        for nak in NAKSHATRAS:
            lord_counts[nak["ruler"]] = lord_counts.get(nak["ruler"], 0) + 1
        for planet in VIMSHOTTARI_ORDER:
            assert lord_counts.get(planet, 0) == 3, (
                f"{planet} should be lord of 3 nakshatras, got {lord_counts.get(planet, 0)}"
            )


class TestVimshottari:
    def test_total_years_is_120(self):
        assert sum(VIMSHOTTARI_YEARS.values()) == VIMSHOTTARI_TOTAL_YEARS == 120

    def test_9_dasha_lords(self):
        assert len(VIMSHOTTARI_ORDER) == 9
        assert len(VIMSHOTTARI_YEARS) == 9

    def test_order_matches_years_dict(self):
        for planet in VIMSHOTTARI_ORDER:
            assert planet in VIMSHOTTARI_YEARS, f"{planet} missing from VIMSHOTTARI_YEARS"

    def test_correct_year_values(self):
        """Verify the canonical Vimshottari year values."""
        expected = {
            "Ketu": 7, "Venus": 20, "Sun": 6, "Moon": 10, "Mars": 7,
            "Rahu": 18, "Jupiter": 16, "Saturn": 19, "Mercury": 17,
        }
        assert VIMSHOTTARI_YEARS == expected


class TestKPSublordTable:
    def test_table_has_entries(self):
        # 27 nakshatras × 9 sub-lords = 243 entries (mathematically exact).
        # The "249" in some KP texts refers to the horary number convention
        # where 6 boundary-spanning entries are counted twice.
        assert len(KP_SUBLORD_TABLE) == 243

    def test_table_starts_at_zero(self):
        assert abs(KP_SUBLORD_TABLE[0]["start_deg"]) < 1e-9

    def test_table_ends_at_360(self):
        assert abs(KP_SUBLORD_TABLE[-1]["end_deg"] - 360.0) < 1e-6

    def test_no_gaps_in_table(self):
        """Each entry must start where the previous one ended — no gaps."""
        for i in range(1, len(KP_SUBLORD_TABLE)):
            prev_end = KP_SUBLORD_TABLE[i - 1]["end_deg"]
            curr_start = KP_SUBLORD_TABLE[i]["start_deg"]
            assert abs(curr_start - prev_end) < 1e-9, (
                f"Gap at entry {i}: prev_end={prev_end}, curr_start={curr_start}"
            )

    def test_all_spans_positive(self):
        for entry in KP_SUBLORD_TABLE:
            span = entry["end_deg"] - entry["start_deg"]
            assert span > 0, f"Non-positive span at {entry['start_deg']}"

    def test_nak_lords_are_valid(self):
        valid = set(VIMSHOTTARI_ORDER)
        for entry in KP_SUBLORD_TABLE:
            assert entry["nak_lord"] in valid, f"Invalid nak_lord: {entry['nak_lord']}"

    def test_sub_lords_are_valid(self):
        valid = set(VIMSHOTTARI_ORDER)
        for entry in KP_SUBLORD_TABLE:
            assert entry["sub_lord"] in valid, f"Invalid sub_lord: {entry['sub_lord']}"

    def test_nak_indices_range(self):
        for entry in KP_SUBLORD_TABLE:
            assert 0 <= entry["nak_index"] <= 26


class TestSublordLookup:
    def test_lookup_at_zero(self):
        from app.engine.sublords import get_star_lord, get_sub_lord
        # Longitude 0° = start of Ashwini, lord = Ketu
        star = get_star_lord(0.0)
        assert star == "Ketu"

    def test_lookup_wraps_at_360(self):
        from app.engine.sublords import get_star_lord
        # 360° should wrap to 0° = Ashwini = Ketu
        star = get_star_lord(360.0)
        assert star == "Ketu"

    def test_lookup_at_nakshatra_boundary(self):
        from app.engine.sublords import get_star_lord
        # At exactly 13°20' = start of Bharani, lord = Venus
        star = get_star_lord(NAKSHATRA_SPAN)
        assert star == "Venus"

    def test_all_positions_return_valid_lords(self):
        from app.engine.sublords import get_sub_lord, get_star_lord
        valid = set(VIMSHOTTARI_ORDER)
        # Test 360 evenly spaced positions
        for i in range(360):
            lon = float(i)
            assert get_star_lord(lon) in valid
            assert get_sub_lord(lon) in valid


class TestNakshatraFunctions:
    def test_get_sign(self):
        from app.engine.nakshatras import get_sign
        assert get_sign(0.0) == "Aries"
        assert get_sign(30.0) == "Taurus"
        assert get_sign(359.9) == "Pisces"

    def test_get_sign_lord(self):
        from app.engine.nakshatras import get_sign_lord
        assert get_sign_lord(0.0) == "Mars"    # Aries → Mars
        assert get_sign_lord(120.0) == "Sun"   # Leo → Sun

    def test_get_nakshatra_pada(self):
        from app.engine.nakshatras import get_nakshatra_pada
        # At the start of a nakshatra, pada = 1
        assert get_nakshatra_pada(0.0) == 1
        # At 3°20' into Ashwini = start of pada 2
        assert get_nakshatra_pada(NAKSHATRA_SPAN / 4) == 2
        # At 6°40' into Ashwini = start of pada 3
        assert get_nakshatra_pada(NAKSHATRA_SPAN / 2) == 3

    def test_format_dms(self):
        from app.engine.nakshatras import format_dms
        result = format_dms(0.0)
        assert "00°00'00\"" == result

    def test_nakshatra_balance_elapsed(self):
        from app.engine.nakshatras import nakshatra_balance_elapsed
        # At the very start of a nakshatra: 0% elapsed
        assert abs(nakshatra_balance_elapsed(0.0)) < 1e-9
        # At midpoint: 50% elapsed
        assert abs(nakshatra_balance_elapsed(NAKSHATRA_SPAN / 2) - 0.5) < 1e-9
