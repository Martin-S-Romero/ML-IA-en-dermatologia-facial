import requests
import uuid

API_URL = "http://localhost:8000/api"

def get_auth_token():
    user_id = str(uuid.uuid4())[:8]
    email = f"user_{user_id}@example.com"
    password = "SecurePassword123!"
    
    requests.post(f"{API_URL}/auth/register", json={
        "email": email, "password": password, "full_name": "Routine Test", "gdpr_accepted": True
    })
    res = requests.post(f"{API_URL}/auth/login", json={"email": email, "password": password})
    return res.json()["access_token"]

def test_routines_endpoints():
    print("--- INICIANDO PRUEBAS DE RUTINAS ---")
    token = get_auth_token()
    headers = {"Authorization": f"Bearer {token}"}
    
    # 1. Crear Rutina
    print("\n[1] POST /routines/")
    routine_data = {
        "analysis_id": None,
        "steps": [
            {
                "step_order": 1,
                "time_of_day": "am",
                "product_name": "Limpiador Suave",
                "product_category": "cleanser",
                "reason": "Limpieza matutina"
            },
            {
                "step_order": 2,
                "time_of_day": "am",
                "product_name": "Protector Solar FPS 50",
                "product_category": "spf",
                "reason": "Proteccion solar"
            }
        ]
    }
    res = requests.post(f"{API_URL}/routines/", json=routine_data, headers=headers)
    if res.status_code == 201:
        print("    [EXITO] Rutina y pasos creados correctamente.")
        routine = res.json()
        step_id = routine["steps"][0]["id"]
    else:
        print("    [ERROR]", res.text)
        return
        
    # 2. Leer Rutina Activa
    print("\n[2] GET /routines/active")
    res = requests.get(f"{API_URL}/routines/active", headers=headers)
    if res.status_code == 200 and len(res.json()["steps"]) == 2:
        print("    [EXITO] Rutina activa leída correctamente con sus 2 pasos.")
    else:
        print("    [ERROR]", res.text)
        
    # 3. Actualizar paso de rutina
    print("\n[3] PATCH /routines/active/steps")
    update_data = {
        "steps": [
            {"step_id": step_id, "product_name": "Limpiador Fuerte"}
        ]
    }
    res = requests.patch(f"{API_URL}/routines/active/steps", json=update_data, headers=headers)
    if res.status_code == 200:
        print("    [EXITO] Paso de rutina actualizado correctamente.")
    else:
        print("    [ERROR]", res.text)
        
    # 4. Registrar chequeo (Skin Check)
    print("\n[4] POST /routines/check")
    check_data = {
        "followed_routine": True,
        "notes": "Me ardió un poco el limpiador"
    }
    res = requests.post(f"{API_URL}/routines/check", json=check_data, headers=headers)
    if res.status_code == 201:
        print("    [EXITO] Skin check registrado exitosamente.")
    else:
        print("    [ERROR]", res.text)

if __name__ == "__main__":
    test_routines_endpoints()
