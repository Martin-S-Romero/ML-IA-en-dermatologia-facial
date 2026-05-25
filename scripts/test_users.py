import requests
import uuid

API_URL = "http://localhost:8000/api"

def get_auth_token():
    user_id = str(uuid.uuid4())[:8]
    email = f"user_{user_id}@example.com"
    password = "SecurePassword123!"
    
    requests.post(f"{API_URL}/auth/register", json={
        "email": email, "password": password, "full_name": "Test User", "gdpr_accepted": True
    })
    res = requests.post(f"{API_URL}/auth/login", json={"email": email, "password": password})
    return res.json()["access_token"]

def test_users_endpoints():
    print("--- INICIANDO PRUEBAS DE USUARIOS Y PERFILES ---")
    token = get_auth_token()
    headers = {"Authorization": f"Bearer {token}"}
    
    # 1. Obtener mi perfil
    print("\n[1] GET /users/me")
    res = requests.get(f"{API_URL}/users/me", headers=headers)
    if res.status_code == 200:
        print("    [EXITO] Información de usuario obtenida:", res.json()["email"])
    else:
        print("    [ERROR]", res.text)
        
    # 2. Crear/Actualizar Perfil de Piel
    print("\n[2] PUT /users/profile")
    profile_data = {
        "age": 25,
        "gender": "femenino",
        "fitzpatrick": "III",
        "skin_type": "mixta",
        "skin_conditions": ["acne"],
        "allergies": [],
        "country": "Ecuador",
        "city": "Quito"
    }
    res = requests.put(f"{API_URL}/users/profile", json=profile_data, headers=headers)
    if res.status_code == 200:
        print("    [EXITO] Perfil de piel creado correctamente.")
    else:
        print("    [ERROR]", res.text)
        
    # 3. Leer Perfil de Piel
    print("\n[3] GET /users/profile")
    res = requests.get(f"{API_URL}/users/profile", headers=headers)
    if res.status_code == 200 and res.json()["skin_type"] == "mixta":
        print("    [EXITO] Perfil leído correctamente y coincide.")
    else:
        print("    [ERROR]", res.text)
        
    # 4. Actualizar nombre de usuario
    print("\n[4] PUT /users/me")
    update_data = {
        "full_name": "Nombre Actualizado"
    }
    res = requests.put(f"{API_URL}/users/me", json=update_data, headers=headers)
    if res.status_code == 200:
        print("    [EXITO] Nombre de usuario actualizado correctamente.")
    else:
        print("    [ERROR]", res.text)

    # 5. Actualizar perfil de piel
    print("\n[5] PUT /users/profile (actualización)")
    profile_update = {
        "skin_type": "grasa"
    }
    res = requests.put(f"{API_URL}/users/profile", json=profile_update, headers=headers)
    if res.status_code == 200:
        # Verificar que se actualizó el perfil
        res_profile = requests.get(f"{API_URL}/users/profile", headers=headers)
        if res_profile.json()["skin_type"] == "grasa":
            print("    [EXITO] Tipo de piel actualizado correctamente.")
        else:
            print("    [ERROR] El tipo de piel no se actualizó.")
    else:
        print("    [ERROR]", res.text)

if __name__ == "__main__":
    test_users_endpoints()
