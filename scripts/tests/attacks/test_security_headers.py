import requests

API_URL = "http://localhost:8000/"

def test_security_headers():
    print("--- INICIANDO PRUEBA DE SECURITY HEADERS ---")
    
    res = requests.get(API_URL)
    headers = res.headers
    
    expected_headers = {
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        "X-XSS-Protection": "1; mode=block",
        "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
        "Content-Security-Policy": "frame-ancestors 'none';",
        "Referrer-Policy": "strict-origin-when-cross-origin"
    }
    
    all_passed = True
    
    for header, expected_value in expected_headers.items():
        actual_value = headers.get(header)
        if actual_value == expected_value:
            print(f"    [EXITO] Header '{header}' está presente y correcto.")
        else:
            print(f"    [ERROR] Header '{header}' falta o es incorrecto. Recibido: {actual_value}")
            all_passed = False
            
    if all_passed:
        print("\n[EXITO] Defensa HTTP Header exitosa! La aplicacion esta protegida.")
    else:
        print("\n[PELIGRO] Falla en la validacion de Security Headers.")

if __name__ == "__main__":
    test_security_headers()
