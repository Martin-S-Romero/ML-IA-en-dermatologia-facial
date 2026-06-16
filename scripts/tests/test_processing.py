import requests
import os

# Configuration
API_URL = "http://localhost:8000"
EMAIL = "argonuser@example.com"
PASSWORD = "argonpassword"
IMAGE_PATH = r"c:\Users\Sheen\Downloads\Tesis 2.0\image\test_imagen798x1200.jpg"

def test_processing():
    # 1. Login
    print(f"Logging in as {EMAIL}...")
    try:
        res = requests.post(f"{API_URL}/auth/login", json={"email": EMAIL, "password": PASSWORD})
        res.raise_for_status()
        token = res.json()["access_token"]
        print("[OK] Login successful. Token acquired.")
    except Exception as e:
        print(f"[FAIL] Login failed: {e}")
        return

    # 2. Upload
    print(f"\nUploading {IMAGE_PATH}...")
    if not os.path.exists(IMAGE_PATH):
        print(f"[FAIL] Error: File {IMAGE_PATH} not found.")
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    files = {"file": (IMAGE_PATH, open(IMAGE_PATH, "rb"), "image/jpeg")}
    
    try:
        res = requests.post(f"{API_URL}/upload/", headers=headers, files=files)
        print(f"Status Code: {res.status_code}")
        upload_data = res.json()
        print(f"Response: {upload_data}")
        filename = upload_data["filename"]
        print(f"[OK] Uploaded as: {filename}")
    except Exception as e:
        print(f"[FAIL] Upload failed: {e}")
        return

    # 3. Process with different modes
    modes = ["blur", "pixelate", "black"]
    
    for mode in modes:
        print(f"\n{'='*50}")
        print(f"Testing mode: {mode.upper()}")
        print(f"{'='*50}")
        
        try:
            res = requests.post(
                f"{API_URL}/process/{filename}",
                headers=headers,
                params={"mode": mode, "expand": 15, "blur_strength": 55, "pixel_size": 10}
            )
            print(f"Status Code: {res.status_code}")
            
            if res.status_code == 200:
                # Save processed image
                output_filename = f"test_processed_{mode}.jpg"
                with open(output_filename, "wb") as f:
                    f.write(res.content)
                print(f"[OK] Processed image saved as: {output_filename}")
                print(f"   Process ID: {res.headers.get('X-Process-ID', 'N/A')}")
                print(f"   Mode: {res.headers.get('X-Mode', 'N/A')}")
            else:
                print(f"[FAIL] Processing failed: {res.text}")
                
        except Exception as e:
            print(f"[FAIL] Error processing with mode '{mode}': {e}")

    print(f"\n{'='*50}")
    print("[OK] All tests completed!")
    print(f"{'='*50}")

if __name__ == "__main__":
    test_processing()
