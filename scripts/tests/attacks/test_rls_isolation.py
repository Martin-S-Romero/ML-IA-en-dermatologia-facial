import requests
import uuid

API_URL = "http://localhost:8000/api"

def generate_user():
    user_id = str(uuid.uuid4())[:8]
    return {
        "email": f"attacker_{user_id}@example.com",
        "password": "password123",
        "full_name": f"Attacker {user_id}",
        "gdpr_accepted": True
    }

def test_rls():
    print("--- INICIANDO PRUEBA DE ATAQUES RLS ---")
    
    # 1. Crear Usuario A (Víctima)
    user_a = generate_user()
    requests.post(f"{API_URL}/auth/register", json=user_a)
    token_a = requests.post(f"{API_URL}/auth/login", json=user_a).json()["access_token"]
    headers_a = {"Authorization": f"Bearer {token_a}"}
    print(f"[+] Usuario A (Víctima) creado: {user_a['email']}")
    
    # 2. Usuario A crea un análisis (Mocked, no necesitamos imagen real si falla, pero RLS inserta el record)
    # RLS allows insert because user_id matches.
    # We will upload a fake file or just use the test image.
    image_path = r"c:\Users\Sheen\Downloads\Tesis 2.0\image\test_imagen798x1200.jpg"
    files = {"file": ("test.jpg", open(image_path, "rb"), "image/jpeg")}
    res_upload = requests.post(f"{API_URL}/analysis/upload", headers=headers_a, files=files)
    
    if res_upload.status_code != 202:
        print("Error subiendo imagen para Usuario A:", res_upload.text)
        return
        
    analysis_id = res_upload.json()["analysis_id"]
    print(f"[+] Usuario A creó el análisis ID: {analysis_id}")
    
    # 3. Crear Usuario B (Atacante)
    user_b = generate_user()
    requests.post(f"{API_URL}/auth/register", json=user_b)
    token_b = requests.post(f"{API_URL}/auth/login", json=user_b).json()["access_token"]
    headers_b = {"Authorization": f"Bearer {token_b}"}
    print(f"[+] Usuario B (Atacante) creado: {user_b['email']}")
    
    # -------------------------------------------------------------
    # ATAQUE 1: Usuario B intenta ver el análisis del Usuario A
    # (A nivel de aplicación puede estar protegido, pero RLS garantiza que la BD devuelve NULL)
    print(f"\n[*] ATAQUE 1: Usuario B solicita GET /analysis/{analysis_id} (Data del Usuario A)")
    res_attack_1 = requests.get(f"{API_URL}/analysis/{analysis_id}", headers=headers_b)
    print(f"    Resultado HTTP: {res_attack_1.status_code}")
    if res_attack_1.status_code == 404:
        print("    [EXITO] Defensa exitosa! RLS y App bloquearon el acceso.")
    else:
        print("    [PELIGRO] Falla de seguridad! Acceso permitido:", res_attack_1.text)
        
    # -------------------------------------------------------------
    # ATAQUE 2: Intento sin autenticación en un endpoint no protegido (Bypassing App logic)
    # El endpoint /{analysis_id}/image no tiene Depends(get_current_user).
    # Antes de RLS, este endpoint devolvía la imagen a CUALQUIERA que tuviera el ID.
    # Ahora, como RLS evalúa la política y 'app.current_user_id' está vacío, la BD filtra la fila.
    print(f"\n[*] ATAQUE 2: Solicitud sin autenticación a GET /analysis/{analysis_id}/image")
    res_attack_2 = requests.get(f"{API_URL}/analysis/{analysis_id}/image")
    print(f"    Resultado HTTP: {res_attack_2.status_code}")
    if res_attack_2.status_code in [401, 404]:
        print(f"    [EXITO] Defensa exitosa! Acceso bloqueado con HTTP {res_attack_2.status_code}.")
        if res_attack_2.status_code == 404:
            print("        (Nota: RLS oculto el registro a nivel de Base de Datos).")
        else:
            print("        (Nota: FastAPI bloqueo la solicitud a nivel de aplicacion).")
    else:
        print("    [PELIGRO] Falla de seguridad! Imagen expuesta:", res_attack_2.status_code)

if __name__ == "__main__":
    test_rls()
