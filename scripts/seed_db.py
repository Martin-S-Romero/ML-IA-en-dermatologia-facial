"""
Seed script: crea usuarios de prueba y verifica que la API funciona.
Uso: python scripts/seed_db.py
Requiere: pip install requests
"""
import sys
import requests

BASE = "http://localhost:8000"

USERS = [
    {
        "register": {
            "full_name": "Ana García",
            "email": "ana.garcia@prueba.com",
            "password": "Test1234!",
            "gdpr_accepted": True,
        },
        "profile": {
            "age": 27,
            "gender": "femenino",
            "fitzpatrick": "III",
            "skin_type": "mixta",
            "skin_conditions": ["acne", "poros_dilatados"],
            "allergies": ["fragancia"],
            "country": "España",
            "city": "Madrid",
        },
    },
    {
        "register": {
            "full_name": "Carlos López",
            "email": "carlos.lopez@prueba.com",
            "password": "Test1234!",
            "gdpr_accepted": True,
        },
        "profile": {
            "age": 35,
            "gender": "masculino",
            "fitzpatrick": "II",
            "skin_type": "grasa",
            "skin_conditions": ["rosácea"],
            "allergies": [],
            "country": "México",
            "city": "Ciudad de México",
        },
    },
]


def check(label, r):
    ok = r.status_code < 400
    symbol = "OK" if ok else "ERROR"
    print(f"  [{symbol}] {label} → {r.status_code}")
    if not ok:
        print(f"         {r.text[:200]}")
    return ok


def main():
    print("=== Comprobando conexión ===")
    try:
        r = requests.get(f"{BASE}/", timeout=5)
        check("GET /", r)
        r = requests.get(f"{BASE}/health/db", timeout=5)
        check("GET /health/db", r)
        if r.json().get("status") != "ok":
            print("\nERROR: La base de datos no responde. Asegúrate de que el backend está corriendo.")
            sys.exit(1)
    except requests.exceptions.ConnectionError:
        print("\nERROR: No se puede conectar a http://localhost:8000")
        print("Arranca el backend primero: docker-compose up -d backend db redis")
        sys.exit(1)

    print("\n=== Creando usuarios de prueba ===")
    for u in USERS:
        name = u["register"]["full_name"]
        print(f"\n--- {name} ---")

        # Registro
        r = requests.post(f"{BASE}/api/auth/register", json=u["register"], timeout=10)
        if r.status_code == 400 and "registrado" in r.text:
            print(f"  [INFO] Usuario ya existe, haciendo login...")
            r = requests.post(f"{BASE}/api/auth/login", json={
                "email": u["register"]["email"],
                "password": u["register"]["password"],
            }, timeout=10)
            if not check("POST /api/auth/login", r):
                continue
        else:
            if not check("POST /api/auth/register", r):
                continue

        token = r.json().get("access_token")
        if not token:
            print("  [ERROR] No se obtuvo token")
            continue

        headers = {"Authorization": f"Bearer {token}"}

        # Perfil de piel
        r = requests.post(f"{BASE}/api/users/profile", json=u["profile"], headers=headers, timeout=10)
        check("POST /api/users/profile", r)

        # Verificar datos guardados
        r = requests.get(f"{BASE}/api/users/me", headers=headers, timeout=10)
        check("GET /api/users/me", r)

        r = requests.get(f"{BASE}/api/users/profile", headers=headers, timeout=10)
        check("GET /api/users/profile", r)
        if r.status_code == 200:
            p = r.json()
            print(f"  Piel: {p.get('skin_type')} | Fitzpatrick: {p.get('fitzpatrick')} | Condiciones: {p.get('skin_conditions')}")

    print("\n=== Resumen ===")
    print(f"Swagger UI:  http://localhost:8000/docs")
    print(f"API base:    {BASE}")
    print(f"Credenciales de prueba:")
    for u in USERS:
        print(f"  {u['register']['email']} / {u['register']['password']}")


if __name__ == "__main__":
    main()
