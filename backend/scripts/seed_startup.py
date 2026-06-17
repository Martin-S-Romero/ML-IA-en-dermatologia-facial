"""
seed_startup.py
Corre una sola vez al inicio del contenedor, después de las migraciones.
- Si la tabla products está vacía, restaura el dump de productos.
- Crea un usuario demo si no existe ningún usuario.
"""

import os
import sys
import subprocess

sys.path.insert(0, "/app")

from sqlalchemy import text
from app.core.database import SessionLocal

DB_HOST     = "db"
DB_USER     = "postgres"
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "password")
DB_NAME     = "tesis_db"
DUMP_FILE   = "/app/data/products_seed.dump"

DEMO_EMAIL    = "demo@skinai.com"
DEMO_PASSWORD = "skinai2024"
DEMO_NAME     = "Usuario Demo"


def seed_products(db):
    count = db.execute(text("SELECT COUNT(*) FROM products")).scalar()
    if count > 0:
        print(f"  ✅ Productos ya en BD: {count:,} — skip")
        return

    if not os.path.exists(DUMP_FILE):
        print(f"  ⚠️  Archivo de seed no encontrado: {DUMP_FILE}")
        print("      Puedes cargarlo manualmente más tarde.")
        return

    print(f"  📦 Cargando productos desde {DUMP_FILE}...")
    env = {**os.environ, "PGPASSWORD": DB_PASSWORD}
    result = subprocess.run(
        [
            "pg_restore",
            "-U", DB_USER,
            "-h", DB_HOST,
            "-d", DB_NAME,
            "--data-only",
            "--no-privileges",
            "--no-owner",
            DUMP_FILE,
        ],
        env=env,
        capture_output=True,
        text=True,
    )
    if result.returncode == 0:
        count_after = db.execute(text("SELECT COUNT(*) FROM products")).scalar()
        print(f"  ✅ Productos cargados: {count_after:,}")
    else:
        # pg_restore puede devolver warnings (código 1) aunque haya insertado todo
        count_after = db.execute(text("SELECT COUNT(*) FROM products")).scalar()
        if count_after > 0:
            print(f"  ✅ Productos cargados con advertencias: {count_after:,}")
        else:
            print(f"  ❌ Error cargando productos:\n{result.stderr[:800]}")


def seed_demo_user(db):
    existing = db.execute(
        text("SELECT id FROM users WHERE email = :email"),
        {"email": DEMO_EMAIL}
    ).fetchone()

    if existing:
        print(f"  ✅ Usuario demo ya existe ({DEMO_EMAIL}) — skip")
        return

    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["argon2"])
    hashed = pwd_context.hash(DEMO_PASSWORD)

    db.execute(
        text("""
            INSERT INTO users (email, hashed_password, full_name, gdpr_accepted, is_active)
            VALUES (:email, :pwd, :name, true, true)
        """),
        {"email": DEMO_EMAIL, "pwd": hashed, "name": DEMO_NAME},
    )
    db.commit()
    print(f"  ✅ Usuario demo creado:")
    print(f"     Email:    {DEMO_EMAIL}")
    print(f"     Password: {DEMO_PASSWORD}")


if __name__ == "__main__":
    db = SessionLocal()
    try:
        print("→ Seed productos...")
        seed_products(db)
        print("→ Seed usuario demo...")
        seed_demo_user(db)
    finally:
        db.close()

    print("✅ Seed completado")
