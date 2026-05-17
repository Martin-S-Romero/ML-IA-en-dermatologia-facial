import requests
import time
import os

API_URL = "http://localhost:8000/api"
EMAIL = "argonuser@example.com"
PASSWORD = "argonpassword"
IMAGE_PATH = r"c:\Users\Sheen\Downloads\Tesis 2.0\image\test_imagen798x1200.jpg"

def test_mock():
    # 0. Register (in case db was cleared)
    reg_payload = {
        "email": EMAIL, 
        "password": PASSWORD,
        "full_name": "Argon User",
        "gdpr_accepted": True
    }
    reg_res = requests.post(f"{API_URL}/auth/register", json=reg_payload)
    print("Registration response:", reg_res.text)

    # 1. Login
    res = requests.post(f"{API_URL}/auth/login", json={"email": EMAIL, "password": PASSWORD})
    if res.status_code != 200:
        print("Login failed:", res.text)
        return
    token = res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # 2. Upload and start analysis
    print(f"Uploading {IMAGE_PATH}...")
    files = {"file": (IMAGE_PATH, open(IMAGE_PATH, "rb"), "image/jpeg")}
    res = requests.post(f"{API_URL}/analysis/upload", headers=headers, files=files)
    if res.status_code != 202:
        print("Upload failed:", res.text)
        return
        
    analysis_data = res.json()
    analysis_id = analysis_data["analysis_id"]
    print(f"Analysis started! ID: {analysis_id}")
    
    # 3. Poll for status
    for i in range(15):
        time.sleep(2)
        res = requests.get(f"{API_URL}/analysis/{analysis_id}/status", headers=headers)
        if res.status_code == 200:
            status = res.json()["status"]
            print(f"Status check {i+1}: {status}")
            if status == "completed":
                print("Analysis complete!")
                break
            elif status == "failed":
                print("Analysis failed!")
                break
        else:
            print(f"Failed to get status: {res.text}")
            
    # 4. Get full result
    res = requests.get(f"{API_URL}/analysis/{analysis_id}", headers=headers)
    if res.status_code == 200:
        print("\nFull Analysis Result:")
        print(res.json())

if __name__ == "__main__":
    if os.path.exists(IMAGE_PATH):
        test_mock()
    else:
        print(f"Image {IMAGE_PATH} not found. Ensure you are in the correct directory.")
