"""seed plan features

Revision ID: 0003
Revises: 0002
Create Date: 2026-04-25 00:00:00.000000

Seeds the Plan.features dict with the canonical entitlement keys.
Idempotent — safe to run on databases that already have plans seeded
with the old (boolean-only) feature shape.
"""
from __future__ import annotations

import json
from alembic import op


revision = "0003"
down_revision = "0002"
branch_labels = None
depends_on = None


PLAN_FEATURES = {
    "free": {
        "astrology": True,
        "numerology": False,
        "vastu": False,
        "panchang": True,
        "horary": False,
        "matching": False,
        "api_access": False,
    },
    "starter": {
        "astrology": True,
        "numerology": True,
        "vastu": False,
        "panchang": True,
        "horary": True,
        "matching": True,
        "api_access": False,
    },
    "pro": {
        "astrology": True,
        "numerology": True,
        "vastu": True,
        "panchang": True,
        "horary": True,
        "matching": True,
        "api_access": True,
    },
    "enterprise": {
        "astrology": True,
        "numerology": True,
        "vastu": True,
        "panchang": True,
        "horary": True,
        "matching": True,
        "api_access": True,
        "white_label": True,
    },
}


def upgrade() -> None:
    # Normalize any legacy uppercase tier values from buggy installs
    op.execute("UPDATE plans SET tier = LOWER(tier) WHERE tier <> LOWER(tier)")

    # Seed features for every known tier
    for tier, features in PLAN_FEATURES.items():
        features_json = json.dumps(features)
        op.execute(
            f"UPDATE plans SET features = '{features_json}'::jsonb WHERE tier = '{tier}'"
        )


def downgrade() -> None:
    # Revert to the original empty-features state
    op.execute("UPDATE plans SET features = '{}'::jsonb")