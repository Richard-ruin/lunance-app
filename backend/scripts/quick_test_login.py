# scripts/quick_test_login.py
import requests
import json

def test_login():
    url = "http://localhost:8000/api/v1/auth/login"
    
    # Test admin
    admin_data = {
        "email": "admin@lunance.ac.id",
        "password": "AdminPassword123!"
    }
    
    print("🧪 Testing Admin Login...")
    try:
        response = requests.post(url, json=admin_data, timeout=10)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ SUCCESS!")
            print(f"User: {data.get('user', {}).get('full_name')}")
            print(f"Role: {data.get('user', {}).get('role')}")
            print(f"Token: {data.get('access_token', 'N/A')[:50]}...")
        else:
            print("❌ FAILED!")
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Request failed: {e}")

if __name__ == "__main__":
    test_login()