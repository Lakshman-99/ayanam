"""One-shot: add top-level domain entitlements to existing plans."""
import asyncio
from sqlalchemy import select
from app.dependencies import get_session_factory
from app.models.subscription import Plan, PlanTier

PLAN_FEATURES = {
    PlanTier.FREE: {
        "astrology": True,
        "numerology": False,
        "vastu": False,
        "panchang": True,
        "horary": False,
        "matching": False,
        "api_access": False,
    },
    PlanTier.STARTER: {
        "astrology": True,
        "numerology": True,
        "vastu": False,
        "panchang": True,
        "horary": True,
        "matching": True,
        "api_access": False,
    },
    PlanTier.PRO: {
        "astrology": True,
        "numerology": True,
        "vastu": True,
        "panchang": True,
        "horary": True,
        "matching": True,
        "api_access": True,
    },
    PlanTier.ENTERPRISE: {
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


async def main():
    factory = get_session_factory()
    async with factory() as db:
        for tier, features in PLAN_FEATURES.items():
            plan = await db.scalar(select(Plan).where(Plan.tier == tier))
            if plan:
                plan.features = features
                print(f"Updated {tier.value}: {features}")
        await db.commit()


if __name__ == "__main__":
    asyncio.run(main())