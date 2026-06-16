import requests
import os

# Configuration
API_URL = "http://localhost:8000"
EMAIL = "argonuser@example.com"
PASSWORD = "argonpassword"
IMAGE_PATH = "test_imagen798x1200.jpg"

def verify_upload():
    # 1. Login
    print(f"Logging in as {EMAIL}...")
    try:
        res = requests.post(f"{API_URL}/auth/login", json={"email": EMAIL, "password": PASSWORD})
        res.raise_for_status()
        token = res.json()["access_token"]
        print("Login successful. Token acquired.")
    except Exception as e:
        print(f"Login failed: {e}")
        if res: print(res.text)
        return

    # 2. Upload
    print(f"Uploading {IMAGE_PATH}...")
    if not os.path.exists(IMAGE_PATH):
        print(f"Error: File {IMAGE_PATH} not found.")
        # Create a dummy one if missing for some reason
        with open(IMAGE_PATH, "wb") as f:
            f.write(os.urandom(1024))
        print("Created dummy file.")
    
    headers = {"Authorization": f"Bearer {token}"}
    files = {"file": (IMAGE_PATH, open(IMAGE_PATH, "rb"), "image/jpeg")}
    
    try:
        res = requests.post(f"{API_URL}/upload/", headers=headers, files=files)
        print(f"Status Code: {res.status_code}")
        print(f"Response: {res.json()}")
    except Exception as e:
        print(f"Upload failed: {e}")
        if res: print(res.text)

if __name__ == "__main__":
    verify_upload()
