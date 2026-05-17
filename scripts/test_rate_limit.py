import requests

API_URL = "http://localhost:8000/api/auth/forgot-password"

def test_rate_limit():
    print("--- INICIANDO PRUEBA DE RATE LIMITING ---")
    
    # El endpoint de forgot-password permite 3/minute
    limit = 3
    email = "rate_limit_test@example.com"
    
    print(f"\nEnviando {limit + 2} peticiones al endpoint (límite es {limit} por minuto)...")
    
    success_count = 0
    blocked = False
    
    for i in range(limit + 2):
        res = requests.post(API_URL, json={"email": email})
        
        if res.status_code == 200:
            success_count += 1
            print(f"    [{i+1}] Éxito (HTTP 200)")
        elif res.status_code == 429:
            print(f"    [{i+1}] BLOQUEADO correctamente por Rate Limit (HTTP 429)")
            blocked = True
        else:
            print(f"    [{i+1}] Código inesperado:", res.status_code)
            
    if blocked and success_count == limit:
        print("\n[EXITO] Rate Limiting funciona correctamente. Bloqueo exactamente a partir del limite.")
    else:
        print(f"\n[PELIGRO] Rate Limiting fallo. Exitos: {success_count}, Bloqueado: {blocked}")

if __name__ == "__main__":
    test_rate_limit()
