import requests
import uuid

API_URL = "http://localhost:8000/api/auth"

def test_auth():
    print("--- INICIANDO PRUEBAS DE AUTENTICACION ---")
    user_id = str(uuid.uuid4())[:8]
    email = f"test_{user_id}@example.com"
    password = "SecurePassword123!"
    
    # 1. Registro con datos incompletos (debería fallar)
    print("\n[1] Prueba: Registro sin aceptar GDPR")
    res = requests.post(f"{API_URL}/register", json={
        "email": email, "password": password, "full_name": "Test User", "gdpr_accepted": False
    })
    if res.status_code == 400:
        print("    [EXITO] Rechazado correctamente por falta de GDPR.")
    else:
        print("    [ERROR] Permitió registro sin GDPR:", res.status_code)

    # 2. Registro exitoso
    print("\n[2] Prueba: Registro exitoso")
    res = requests.post(f"{API_URL}/register", json={
        "email": email, "password": password, "full_name": "Test User", "gdpr_accepted": True
    })
    if res.status_code in [200, 201]:
        print("    [EXITO] Usuario registrado correctamente.")
    else:
        print("    [ERROR] Falló registro:", res.text)
        return

    # 3. Login incorrecto
    print("\n[3] Prueba: Login con contraseña incorrecta")
    res = requests.post(f"{API_URL}/login", json={"email": email, "password": "wrong"})
    if res.status_code == 401:
        print("    [EXITO] Rechazado correctamente.")
    else:
        print("    [ERROR] Login incorrecto exitoso:", res.status_code)

    # 4. Login exitoso
    print("\n[4] Prueba: Login exitoso")
    res = requests.post(f"{API_URL}/login", json={"email": email, "password": password})
    if res.status_code == 200 and "access_token" in res.json():
        print("    [EXITO] Token JWT generado correctamente.")
    else:
        print("    [ERROR] Falló login:", res.text)

if __name__ == "__main__":
    test_auth()
