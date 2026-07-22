"""
Simple database seeding script.
Creates the 3 roles (admin, student, instructor) and one admin user.

Run with:  python -m app.seed.seed_data

Safe to run multiple times — checks before inserting, won't create duplicates.
"""
from app.db.database import SessionLocal
from app.models.role import Role
from app.models.user import User
from app.core.security import hash_password


def run():
    db = SessionLocal()
    try:
        # ---------- Roles ----------
        role_names = ["admin", "student", "instructor"]
        roles = {}
        for name in role_names:
            role = db.query(Role).filter(Role.name == name).first()
            if not role:
                role = Role(name=name)
                db.add(role)
                db.commit()
                db.refresh(role)
                print(f"Created role: {name}")
            else:
                print(f"Role already exists, skipping: {name}")
            roles[name] = role

        # ---------- Admin user ----------
        admin_user = db.query(User).filter(User.email == "admin@edugen.com").first()
        if not admin_user:
            admin_user = User(
                username="admin",
                email="admin@edugen.com",
                password_hash=hash_password("Admin@123"),
                role_id=roles["admin"].id,
                is_active=True,
            )
            db.add(admin_user)
            db.commit()
            db.refresh(admin_user)
            print(f"Created admin user: {admin_user.email}")
        else:
            print("Admin user already exists, skipping")

        print("\n✅ Seeding complete.")
        print(f"   admin login  -> email: {admin_user.email}  password: Admin@123")

    finally:
        db.close()


if __name__ == "__main__":
    run()