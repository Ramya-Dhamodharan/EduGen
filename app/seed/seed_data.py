"""
Simple database seeding script — seeds only the roles table.
Run with:  python -m app.seed.seed_data
"""
from app.db.database import SessionLocal
from app.models.role import Role


def run():
    db = SessionLocal()
    try:
        roles_to_create = ["admin", "student", "instructor"]

        for role_name in roles_to_create:
            existing = db.query(Role).filter(Role.name == role_name).first()
            if not existing:
                db.add(Role(name=role_name))
                print(f"Created role: {role_name}")
            else:
                print(f"Role already exists, skipping: {role_name}")

        db.commit()
        print("\n✅ Role seeding complete.")

    finally:
        db.close()


if __name__ == "__main__":
    run()