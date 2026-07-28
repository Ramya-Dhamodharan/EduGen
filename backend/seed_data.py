"""
Simple database seeding script.
Creates the 3 roles (admin, student, instructor) and one admin user.

Run with: python -m app.seed.seed_data

Safe to run multiple times — checks before inserting, won't create duplicates.
"""

import asyncio

from sqlalchemy import select

from app.core.security import hash_password
from app.db.database import SessionLocal
from app.models.role import Role
from app.models.user import User


async def run():
    async with SessionLocal() as db:
        # ---------- Roles ----------
        role_names = ["admin", "student", "instructor"]
        roles = {}

        for name in role_names:
            result = await db.execute(
                select(Role).where(Role.name == name)
            )
            role = result.scalar_one_or_none()

            if not role:
                role = Role(name=name)
                db.add(role)

                await db.commit()
                await db.refresh(role)

                print(f"Created role: {name}")
            else:
                print(f"Role already exists, skipping: {name}")

            roles[name] = role

        # ---------- Admin user ----------
        result = await db.execute(
            select(User).where(User.email == "admin@edugen.com")
        )
        admin_user = result.scalar_one_or_none()

        if not admin_user:
            admin_user = User(
                username="admin",
                email="admin@edugen.com",
                password_hash=hash_password("Admin@123"),
                role_id=roles["admin"].id,
                is_active=True,
            )

            db.add(admin_user)

            await db.commit()
            await db.refresh(admin_user)

            print(f"Created admin user: {admin_user.email}")
        else:
            print("Admin user already exists, skipping")

        print("\n✅ Seeding complete.")
        print(
            f"   admin login -> email: {admin_user.email}  password: Admin@123"
        )


if __name__ == "__main__":
    asyncio.run(run())