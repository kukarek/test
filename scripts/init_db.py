import asyncio
import json
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database.connection import async_session_maker, init_db
from app.common.models.models import Plan, User, UserPlanEnum
from app.core.security.auth import hash_password


async def seed_plans():
    async with async_session_maker() as session:
        try:
            from sqlalchemy import select
            result = await session.execute(select(Plan))
            existing = result.scalars().all()

            if existing:
                print("Plans already exist, skipping seed...")
                return

            free_plan = Plan(
                name="Free",
                plan_type=UserPlanEnum.FREE,
                daily_search_limit=10,
                price_monthly=0.0,
                price_annual=0.0,
                features=json.dumps([
                    "10 searches per day",
                    "Access to all marketplaces",
                    "Basic analytics"
                ]),
                is_active=True
            )

            pro_plan = Plan(
                name="Pro",
                plan_type=UserPlanEnum.PRO,
                daily_search_limit=1000,
                price_monthly=9.99,
                price_annual=99.99,
                features=json.dumps([
                    "1000 searches per day",
                    "AI-powered routing",
                    "Advanced analytics"
                ]),
                is_active=True
            )

            session.add(free_plan)
            session.add(pro_plan)

            await session.commit()
            print("✓ Plans seeded successfully")

        except Exception as e:
            print(f"✗ Error seeding plans: {e}")
            await session.rollback()


async def main():
    print("Initializing database...")
    try:
        await init_db()
        print("✓ Database tables created")
        await seed_plans()
        print("\n✓ Database initialization completed successfully!")
    except Exception as e:
        print(f"\n✗ Database initialization failed: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
