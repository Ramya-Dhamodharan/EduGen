"""
Seed the database with the three roles and one test user per role.

Run from the project root (where app/ lives):

    uv run python seed.py
    # or:  python seed.py

Safe to re-run: existing rows are reused, not duplicated.
"""

from app.db.database import SessionLocal
import app.models  # registers every mapper
from app.models.role import Role
from app.models.user import User
from app.core.security import hash_password

ROLES = ["Admin", "Instructor", "Student"]

USERS = [
    # (username,        email,                     password,        role)
    ("admin",      "admin@edugen.com",      "Admin@12345",      "Admin"),
    ("instructor", "instructor@edugen.com", "Instructor@12345", "Instructor"),
    ("student",    "student@edugen.com",    "Student@12345",    "Student"),
]


def main() -> None:
    db = SessionLocal()
    try:
        # ---- roles ----
        role_map = {}
        for name in ROLES:
            role = db.query(Role).filter(Role.name == name).first()
            if not role:
                role = Role(name=name)
                db.add(role)
                db.flush()
                print(f"  + created role {name} (id={role.id})")
            else:
                print(f"  = role {name} already exists (id={role.id})")
            role_map[name] = role

        # ---- users ----
        for username, email, password, role_name in USERS:
            user = db.query(User).filter(User.email == email).first()
            if user:
                # keep the role correct even if the user already existed
                user.role_id = role_map[role_name].id
                print(f"  = user {email} already exists -> role set to {role_name}")
                continue

            user = User(
                username=username,
                email=email,
                password_hash=hash_password(password),
                role_id=role_map[role_name].id,
                is_active=True,
            )
            db.add(user)
            db.flush()
            # self-referencing audit column
            user.created_by = user.id
            print(f"  + created {role_name}: {email} / {password}")

        db.commit()

        print("\nSeed complete. Login credentials:")
        for username, email, password, role_name in USERS:
            print(f"  {role_name:<11} {email:<26} {password}")
        print("\nRole ids (needed for POST /api/users):")
        for name, role in role_map.items():
            print(f"  {name:<11} role_id = {role.id}")

    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()