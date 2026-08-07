from sqlalchemy import select

from app.core.security import hash_password
from app.db.database import SessionLocal
from app.models.role import Role
from app.models.user import User


async def seed_database():
    async with SessionLocal() as db:
        # ---------- Roles ----------
        role_names = ["admin", "student", "instructor"]
        roles = {}

        for name in role_names:
            result = await db.execute(select(Role).where(Role.name == name))
            role = result.scalar_one_or_none()

            if role is None:
                role = Role(name=name)
                db.add(role)

                await db.commit()
                await db.refresh(role)

                print(f"Created role: {name}")
            else:
                print(f"Role already exists: {name}")

            roles[name] = role

        # ---------- Admin ----------
        result = await db.execute(select(User).where(User.email == "admin@edugen.com"))
        admin = result.scalar_one_or_none()

        if admin is None:
            admin = User(
                username="admin",
                email="admin@edugen.com",
                password_hash=hash_password("Admin@123"),
                role_id=roles["admin"].id,
                is_active=True,
            )

            db.add(admin)

            await db.commit()
            await db.refresh(admin)

            print("Created admin user.")
        else:
            print("Admin user already exists.")

        print("Database seeding completed.")
