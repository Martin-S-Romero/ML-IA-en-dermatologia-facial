import requests
import uuid

API_URL = "http://localhost:8000/api"

def get_auth_token():
    user_id = str(uuid.uuid4())[:8]
    email = f"user_{user_id}@example.com"
    password = "SecurePassword123!"
    
    requests.post(f"{API_URL}/auth/register", json={
        "email": email, "password": password, "full_name": "Product Test", "gdpr_accepted": True
    })
    res = requests.post(f"{API_URL}/auth/login", json={"email": email, "password": password})
    return res.json()["access_token"]

def test_products_endpoints():
    print("--- INICIANDO PRUEBAS DE PRODUCTOS ---")
    token = get_auth_token()
    headers = {"Authorization": f"Bearer {token}"}
    
    # 1. Búsqueda de productos (puede devolver vacío si no hay datos en la BD, pero no debe fallar)
    print("\n[1] GET /products/search")
    res = requests.get(f"{API_URL}/products/search?q=cerave&category=cleanser", headers=headers)
    if res.status_code == 200:
        products = res.json()
        print(f"    [EXITO] Búsqueda ejecutada correctamente. Encontró {len(products)} productos.")
    else:
        print("    [ERROR]", res.text)
        
    # 2. Obtener recomendaciones
    print("\n[2] GET /products/recommended")
    res = requests.get(f"{API_URL}/products/recommended", headers=headers)
    if res.status_code == 200:
        recommended = res.json()
        print(f"    [EXITO] Recomendaciones obtenidas: {len(recommended)} productos.")
    else:
        print("    [ERROR]", res.text)
        
    # 3. Detalles de un producto
    if products:
        product_id = products[0]["id"]
        print(f"\n[3] GET /products/{product_id}")
        res = requests.get(f"{API_URL}/products/{product_id}", headers=headers)
        if res.status_code == 200:
            print("    [EXITO] Detalles del producto leídos correctamente.")
        else:
            print("    [ERROR]", res.text)
    else:
        print("\n[3] (Omitido) GET /products/{id} - No hay productos en la BD de prueba para consultar ID.")

if __name__ == "__main__":
    test_products_endpoints()
