import requests

API_URL = "http://localhost:8000/api/health/db"  # Un endpoint simple para probar

def test_cors():
    print("--- INICIANDO PRUEBA DE ATAQUES CORS ---")
    
    # 1. Solicitud Legítima (Desde nuestro frontend React/Vite)
    print("\n[+] PRUEBA 1: Solicitud desde el Frontend Legítimo (http://localhost:3000)")
    headers_legit = {"Origin": "http://localhost:3000"}
    res_legit = requests.options(API_URL, headers=headers_legit)
    
    # Verificamos si el servidor responde con el header de CORS permitiendo el acceso
    cors_header = res_legit.headers.get("Access-Control-Allow-Origin")
    if cors_header == "http://localhost:3000":
        print("    [EXITO] El servidor permitio la conexion. (Header: Access-Control-Allow-Origin presente)")
    else:
        print(f"    [ERROR] El servidor no envio el header correcto. Headers recibidos: {res_legit.headers}")

    # 2. Solicitud Maliciosa (Desde un dominio no autorizado, ej. sitio de phishing)
    print("\n[*] ATAQUE 1: Solicitud desde sitio de Phishing (http://maliciou-site.com)")
    headers_malicious = {"Origin": "http://maliciou-site.com"}
    res_malicious = requests.options(API_URL, headers=headers_malicious)
    
    # Si el CORS está bien configurado, el servidor NO DEBE devolver el header permitiendo a ese dominio
    cors_header_malicious = res_malicious.headers.get("Access-Control-Allow-Origin")
    if not cors_header_malicious:
        print("    [EXITO] Defensa CORS exitosa! El servidor rechazo el Origin malicioso.")
        print("            (El navegador del usuario bloqueara la solicitud)")
    else:
        print(f"    [PELIGRO] Falla de seguridad! CORS permitio el acceso al dominio malicioso: {cors_header_malicious}")
        
    print("\n--- PRUEBA FINALIZADA ---")

if __name__ == "__main__":
    test_cors()
