"""
Unit tests for Vimshottari dasha calculator.
"""
from __future__ import annotations

from datetime import date

import pytest

from app.engine.constants import VIMSHOTTARI_ORDER, VIMSHOTTARI_YEARS
from app.engine.dasha import compute_dasha_balance, generate_dasha_periods


class TestDashaBalance:
    def test_at_nakshatra_start_full_period_remains(self):
        """Moon at exact nakshatra start → 100% of that dasha remains."""
        # Longitude 0.0 = start of Ashwini (lord = Ketu, 7 years)
        lord, end_date = compute_dasha_balance(0.0, date(2000, 1, 1))
        assert lord == "Ketu"
        expected_days = round(7 * 365.25)
        actual_days = (end_date - date(2000, 1, 1)).days
        # Allow ±2 days tolerance for rounding
        assert abs(actual_days - expected_days) <= 2

    def test_at_nakshatra_midpoint_half_period_remains(self):
        from app.engine.constants import NAKSHATRA_SPAN
        # Moon at midpoint of Ashwini = 50% elapsed → 50% of Ketu dasha remains
        lord, end_date = compute_dasha_balance(NAKSHATRA_SPAN / 2, date(2000, 1, 1))
        assert lord == "Ketu"
        expected_days = round(7 * 365.25 / 2)
        actual_days = (end_date - date(2000, 1, 1)).days
        assert abs(actual_days - expected_days) <= 2

    def test_returns_valid_lord(self):
        from app.engine.constants import NAKSHATRA_SPAN
        valid_lords = set(VIMSHOTTARI_ORDER)
        # Test all 27 nakshatra starting points
        for i in range(27):
            lon = i * NAKSHATRA_SPAN
            lord, _ = compute_dasha_balance(lon, date(2000, 1, 1))
            assert lord in valid_lords


class TestDashaGeneration:
    def setup_method(self):
        # Use Moon at 0° (start of Ashwini = Ketu dasha)
        self.moon_lon = 0.0
        self.birth_date = date(2000, 1, 1)

    def test_generates_mahadashas(self):
        periods = generate_dasha_periods(self.birth_date, self.moon_lon, levels=1)
        maha_periods = [p for p in periods if p.level == 1]
        assert len(maha_periods) >= 9  # at least one full cycle

    def test_first_dasha_lord_matches_moon_nakshatra(self):
        periods = generate_dasha_periods(self.birth_date, self.moon_lon, levels=1)
        first_maha = [p for p in periods if p.level == 1][0]
        assert first_maha.lord == "Ketu"  # Moon at 0° = Ashwini = Ketu

    def test_periods_are_continuous(self):
        periods = generate_dasha_periods(self.birth_date, self.moon_lon, levels=1)
        maha = [p for p in periods if p.level == 1]
        for i in range(1, len(maha)):
            assert maha[i].start_date == maha[i - 1].end_date, (
                f"Gap between period {i-1} and {i}: "
                f"{maha[i-1].end_date} != {maha[i].start_date}"
            )

    def test_mahadasha_start_is_birth_date(self):
        periods = generate_dasha_periods(self.birth_date, self.moon_lon, levels=1)
        first = [p for p in periods if p.level == 1][0]
        assert first.start_date == self.birth_date

    def test_bhukti_count_per_mahadasha(self):
        # Use a range that covers exactly one complete mahadasha (Ketu = 7 years)
        periods = generate_dasha_periods(self.birth_date, self.moon_lon, levels=2, years_forward=8)
        ketu_bhuktis = [p for p in periods if p.level == 2 and p.parent_lord == "Ketu"]
        # The Ketu mahadasha (7 years) fits entirely within 8 years → 9 bhuktis
        assert len(ketu_bhuktis) == 9

    def test_all_lords_are_valid(self):
        valid = set(VIMSHOTTARI_ORDER)
        periods = generate_dasha_periods(self.birth_date, self.moon_lon, levels=3, years_forward=10)
        for p in periods:
            assert p.lord in valid
            if p.parent_lord:
                assert p.parent_lord in valid

    def test_no_future_start_before_birth(self):
        periods = generate_dasha_periods(self.birth_date, self.moon_lon, levels=3)
        for p in periods:
            assert p.start_date >= self.birth_date
