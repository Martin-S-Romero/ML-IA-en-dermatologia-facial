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

TEST_EMAIL = "testanalysis@example.com"
TEST_PASS  = "TestPass123!"
TEST_NAME  = "Test Analysis User"

# Usuarios de ejemplo con análisis reales de distintas condiciones
EJEMPLO_USERS = [
    {"email": "ejemplo1@example.com", "password": "EjemploPass1!", "name": "Ejemplo Acné Excoriado"},
    {"email": "ejemplo3@example.com", "password": "EjemploPass3!", "name": "Ejemplo Rosácea ETR"},
    {"email": "ejemplo7@example.com", "password": "EjemploPass7!", "name": "Ejemplo Multi-condición"},
]

# Análisis reales (formato fiel al que genera el pipeline IA)
EJEMPLO_ANALYSES = [
    {
        "user_email": "ejemplo1@example.com",
        "original_filename": "1a116d78-c1aa-41ef-a8ae-52abfde29dcf.jpg",
        "censored_filename": "002d7099-ac0d-45fc-9347-faa3948fa77f_censored.jpg",
        "top1_label": "acne-excoriated",
        "top1_confidence": 0.427128,
        "model_version": "efficientnet_b3_v1",
        "face_censored": True,
        "result": {
            "compute": "cpu",
            "all_scores": {
                "rosacea-etr": 0.030196,
                "acne-comedonal": 0.005075,
                "acne-excoriated": 0.427128,
                "acne-inflammatory": 0.10797,
                "perioral-dermatitis": 0.00668,
                "rosacea-inflammatory": 0.182366,
                "seborrheic-dermatitis": 0.240585,
            },
            "top1_label": "acne-excoriated",
            "tta_passes": 5,
            "model_version": "efficientnet_b3_v1",
            "top1_confidence": 0.427128,
        },
    },
    {
        "user_email": "ejemplo3@example.com",
        "original_filename": "58fede2b-de80-4fd0-b079-a075077de8a2.jpg",
        "censored_filename": "be9f158a-aaed-46aa-a43e-978becee9411_censored.jpg",
        "top1_label": "rosacea-etr",
        "top1_confidence": 0.542984,
        "model_version": "efficientnet_b3_v1",
        "face_censored": True,
        "result": {
            "compute": "cpu",
            "all_scores": {
                "rosacea-etr": 0.542984,
                "acne-comedonal": 0.022386,
                "acne-excoriated": 0.249576,
                "acne-inflammatory": 0.007145,
                "perioral-dermatitis": 0.00625,
                "rosacea-inflammatory": 0.120578,
                "seborrheic-dermatitis": 0.051081,
            },
            "top1_label": "rosacea-etr",
            "tta_passes": 5,
            "model_version": "efficientnet_b3_v1",
            "top1_confidence": 0.542984,
        },
    },
    {
        "user_email": "ejemplo7@example.com",
        "original_filename": "a2872796-8042-4c59-82b8-a21fc39d4003.jpg",
        "censored_filename": "832c0b80-8d8b-49cf-86b9-b9c2c727b945_censored.jpg",
        "top1_label": "rosacea-inflammatory",
        "top1_confidence": 0.3188,
        "model_version": "efficientnet_b3_v3",
        "face_censored": True,
        "result": {
            "model": "efficientnet_b3",
            "top_n": [
                {"prob": 0.3188, "label": "rosacea-inflammatory"},
                {"prob": 0.2482, "label": "acne-excoriated"},
                {"prob": 0.1325, "label": "seborrheic-dermatitis"},
                {"prob": 0.1182, "label": "rosacea-etr"},
            ],
            "condition": "rosacea-inflammatory",
            "timestamp": "2026-06-09T05:12:48.101028",
            "confidence": 0.3188,
            "tta_passes": 5,
            "worst_zone": "mejilla_der",
            "model_version": "efficientnet_b3_v3",
            "zones_display": {
                "nariz":       {"scales": 0.1674, "erythema": 0.2916, "severity": 0.1985, "comedones": 0.0641},
                "frente":      {"scales": 0.2522, "erythema": 0.2947, "severity": 0.2298, "comedones": 0.1069},
                "menton":      {"scales": 0.5188, "erythema": 0.4681, "severity": 0.3751, "comedones": 0.1243},
                "mejilla_der": {"scales": 0.6965, "erythema": 0.5204, "severity": 0.4423, "comedones": 0.1427},
                "mejilla_izq": {"scales": 0.3697, "erythema": 0.4227, "severity": 0.3259, "comedones": 0.1354},
            },
            "severity_score": 0.3703,
            "zones_diagnostic": {
                "ceja_der":      {"scales": 1.0,    "erythema": 0.3568, "severity": 0.514,  "comedones": 0.4521},
                "ceja_izq":      {"scales": 1.0,    "erythema": 0.2676, "severity": 0.4874, "comedones": 0.5119},
                "mandibula_der": {"scales": 1.0,    "erythema": 0.5644, "severity": 0.5488, "comedones": 0.2221},
                "mandibula_izq": {"scales": 0.4735, "erythema": 0.4211, "severity": 0.3582, "comedones": 0.1764},
                "nariz_lat_der": {"scales": 1.0,    "erythema": 0.6164, "severity": 0.646,  "comedones": 0.4594},
                "nariz_lat_izq": {"scales": 0.4083, "erythema": 0.4748, "severity": 0.4056, "comedones": 0.2885},
                "zona_perioral": {"scales": 1.0,    "erythema": 0.6461, "severity": 0.6757, "comedones": 0.5086},
            },
            "profile_consistency": 0.2482,
            "zone_schema_version": "v3",
            "affected_zones_count": 12,
            "historical_consistency": 0.0,
        },
    },
    {
        "user_email": "ejemplo7@example.com",
        "original_filename": "b4f50506-fe68-4b48-943a-667448e2ff5f.jpg",
        "censored_filename": "835e4a3e-f30e-4e88-98f7-0d1a7a16635c_censored.jpg",
        "top1_label": "healthy-skin",
        "top1_confidence": 0.2898,
        "model_version": "efficientnet_b3_v3",
        "face_censored": True,
        "result": {
            "delta": {
                "zones": {
                    "nariz":       {"erythema_pct": 70.37, "scales_delta": 0.175,   "erythema_delta": 0.2052,  "comedones_delta": -0.0089},
                    "frente":      {"erythema_pct": 60.23, "scales_delta": 0.2757,  "erythema_delta": 0.1775,  "comedones_delta": 0.0066},
                    "menton":      {"erythema_pct": 29.93, "scales_delta": -0.032,  "erythema_delta": 0.1401,  "comedones_delta": 0.0341},
                    "mejilla_der": {"erythema_pct": 7.57,  "scales_delta": -0.2005, "erythema_delta": 0.0394,  "comedones_delta": -0.0718},
                    "mejilla_izq": {"erythema_pct": 38.11, "scales_delta": 0.2514,  "erythema_delta": 0.1611,  "comedones_delta": 0.0062},
                },
                "condition_curr": "healthy-skin",
                "condition_prev": "rosacea-inflammatory",
                "severity_delta": 0.0887,
                "severity_trend": "worsening",
                "condition_changed": True,
                "severity_delta_pct": 23.95,
                "affected_zones_delta": 0,
            },
            "model": "efficientnet_b3",
            "top_n": [
                {"prob": 0.2898, "label": "healthy-skin"},
                {"prob": 0.1651, "label": "rosacea-inflammatory"},
                {"prob": 0.1543, "label": "rosacea-etr"},
                {"prob": 0.1364, "label": "seborrheic-dermatitis"},
                {"prob": 0.1308, "label": "acne-excoriated"},
            ],
            "condition": "healthy-skin",
            "timestamp": "2026-06-09T05:24:11.298956",
            "confidence": 0.2898,
            "tta_passes": 5,
            "worst_zone": "mejilla_izq",
            "model_version": "efficientnet_b3_v3",
            "zones_display": {
                "nariz":       {"scales": 0.3424, "erythema": 0.4968, "severity": 0.3335, "comedones": 0.0552},
                "frente":      {"scales": 0.5279, "erythema": 0.4722, "severity": 0.3757, "comedones": 0.1135},
                "menton":      {"scales": 0.4868, "erythema": 0.6082, "severity": 0.449,  "comedones": 0.1584},
                "mejilla_der": {"scales": 0.496,  "erythema": 0.5598, "severity": 0.4004, "comedones": 0.0709},
                "mejilla_izq": {"scales": 0.6211, "erythema": 0.5838, "severity": 0.4586, "comedones": 0.1416},
            },
            "severity_score": 0.459,
            "zones_diagnostic": {
                "ceja_der":      {"scales": 1.0,    "erythema": 0.4936, "severity": 0.5915, "comedones": 0.4824},
                "ceja_izq":      {"scales": 1.0,    "erythema": 0.4928, "severity": 0.6211, "comedones": 0.5824},
                "mandibula_der": {"scales": 0.6008, "erythema": 0.57,   "severity": 0.4566, "comedones": 0.1716},
                "mandibula_izq": {"scales": 0.5991, "erythema": 0.5852, "severity": 0.4883, "comedones": 0.2528},
                "nariz_lat_der": {"scales": 1.0,    "erythema": 0.6551, "severity": 0.6359, "comedones": 0.3611},
                "nariz_lat_izq": {"scales": 0.9212, "erythema": 0.6694, "severity": 0.6093, "comedones": 0.301},
                "zona_perioral": {"scales": 1.0,    "erythema": 0.9851, "severity": 0.7718, "comedones": 0.2642},
            },
            "profile_consistency": 0.1308,
            "zone_schema_version": "v3",
            "affected_zones_count": 12,
            "historical_consistency": 0.0526,
        },
    },
]


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


def seed_test_analysis(db):
    """Crea un usuario de prueba con un análisis completado para los tests de Fase 2."""
    import json

    row = db.execute(
        text("SELECT id FROM users WHERE email = :email"),
        {"email": TEST_EMAIL}
    ).fetchone()

    if row:
        count = db.execute(
            text("SELECT COUNT(*) FROM analyses WHERE user_id = :uid AND status = 'completed'"),
            {"uid": row[0]}
        ).scalar()
        if count > 0:
            print(f"  ✅ Usuario de prueba con análisis ya existe ({TEST_EMAIL}) — skip")
            return

    if not row:
        from passlib.context import CryptContext
        pwd_context = CryptContext(schemes=["argon2"])
        hashed = pwd_context.hash(TEST_PASS)
        db.execute(
            text("""
                INSERT INTO users (email, hashed_password, full_name, gdpr_accepted, is_active)
                VALUES (:email, :pwd, :name, true, true)
            """),
            {"email": TEST_EMAIL, "pwd": hashed, "name": TEST_NAME},
        )
        db.commit()
        row = db.execute(
            text("SELECT id FROM users WHERE email = :email"),
            {"email": TEST_EMAIL}
        ).fetchone()

    result_json = json.dumps({
        "condition":              "acne-comedonal",
        "confidence":             0.82,
        "top_n": [
            {"label": "acne-comedonal", "prob": 0.82},
            {"label": "rosacea-etr",    "prob": 0.12},
            {"label": "healthy-skin",   "prob": 0.06},
        ],
        "severity_score":         0.70,
        "worst_zone":             "forehead",
        "affected_zones_count":   2,
        "zones_display":          {},
        "zones_diagnostic":       {},
        "profile_consistency":    0.90,
        "historical_consistency": 1.0,
        "model":                  "efficientnet_b2",
        "tta_passes":             5,
        "zone_schema_version":    "v12",
        "timestamp":              "2026-01-01T00:00:00",
    })

    db.execute(
        text("""
            INSERT INTO analyses
                (user_id, status, top1_label, top1_confidence,
                 model_version, result, face_censored, completed_at)
            VALUES
                (:uid, 'completed', 'acne-comedonal', 0.82,
                 'efficientnet_b2', CAST(:result AS jsonb), false, NOW())
        """),
        {"uid": row[0], "result": result_json},
    )
    db.commit()
    print(f"  ✅ Usuario de prueba con análisis creado:")
    print(f"     Email:    {TEST_EMAIL}")
    print(f"     Password: {TEST_PASS}")
    print(f"     Análisis: acne-comedonal (severity 0.70, secondary: rosacea-etr 0.12)")


def seed_example_analyses(db):
    """Crea 3 usuarios de ejemplo con análisis reales de distintas condiciones.

    Usuarios y contraseñas:
      ejemplo1@example.com / EjemploPass1!  — acne-excoriated (formato v1)
      ejemplo3@example.com / EjemploPass3!  — rosacea-etr     (formato v1)
      ejemplo7@example.com / EjemploPass7!  — rosacea-inflammatory + healthy-skin (formato v3)
    """
    import json
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["argon2"])

    # Crear / recuperar usuarios
    user_ids: dict[str, int] = {}
    for u in EJEMPLO_USERS:
        row = db.execute(
            text("SELECT id FROM users WHERE email = :email"),
            {"email": u["email"]}
        ).fetchone()
        if not row:
            hashed = pwd_context.hash(u["password"])
            db.execute(
                text("""
                    INSERT INTO users (email, hashed_password, full_name, gdpr_accepted, is_active)
                    VALUES (:email, :pwd, :name, true, true)
                """),
                {"email": u["email"], "pwd": hashed, "name": u["name"]},
            )
            db.commit()
            row = db.execute(
                text("SELECT id FROM users WHERE email = :email"),
                {"email": u["email"]}
            ).fetchone()
        user_ids[u["email"]] = row[0]

    # Insertar análisis (idempotente: comprueba por user_id + original_filename)
    inserted = 0
    for a in EJEMPLO_ANALYSES:
        uid = user_ids[a["user_email"]]
        exists = db.execute(
            text("SELECT 1 FROM analyses WHERE user_id = :uid AND original_filename = :fname"),
            {"uid": uid, "fname": a["original_filename"]}
        ).fetchone()
        if exists:
            continue

        db.execute(
            text("""
                INSERT INTO analyses
                    (user_id, original_filename, censored_filename, status,
                     face_censored, top1_label, top1_confidence, model_version,
                     result, completed_at)
                VALUES
                    (:uid, :orig, :cens, 'completed',
                     :face_censored, :top1_label, :top1_confidence, :model_version,
                     CAST(:result AS jsonb), NOW())
            """),
            {
                "uid":             uid,
                "orig":            a["original_filename"],
                "cens":            a["censored_filename"],
                "face_censored":   a["face_censored"],
                "top1_label":      a["top1_label"],
                "top1_confidence": a["top1_confidence"],
                "model_version":   a["model_version"],
                "result":          json.dumps(a["result"]),
            },
        )
        inserted += 1

    db.commit()

    if inserted > 0:
        print(f"  ✅ {inserted} análisis de ejemplo insertados")
        for u in EJEMPLO_USERS:
            pw = next(x["password"] for x in EJEMPLO_USERS if x["email"] == u["email"])
            print(f"     {u['email']} / {pw}")
    else:
        print(f"  ✅ Análisis de ejemplo ya existen — skip")


if __name__ == "__main__":
    db = SessionLocal()
    try:
        print("→ Seed productos...")
        seed_products(db)
        print("→ Seed usuario demo...")
        seed_demo_user(db)
        print("→ Seed análisis de prueba...")
        seed_test_analysis(db)
        print("→ Seed análisis de ejemplo...")
        seed_example_analyses(db)
    finally:
        db.close()

    print("✅ Seed completado")
