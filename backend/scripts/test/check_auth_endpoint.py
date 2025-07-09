# scripts/check_auth_endpoint.py
"""
Script untuk mengecek apakah auth endpoint berfungsi dengan benar.
"""

import requests
import json
import sys

def test_auth_endpoint():
    """Test auth endpoint secara langsung."""
    
    base_url = "http://localhost:8000"
    
    print("🔍 TESTING AUTH ENDPOINT")
    print("=" * 30)
    
    # Test 1: Health check
    try:
        response = requests.get(f"{base_url}/")
        print(f"✅ Server reachable: {response.status_code}")
    except Exception as e:
        print(f"❌ Server tidak dapat dijangkau: {e}")
        return False
    
    # Test 2: Login admin
    login_data = {
        "email": "admin@lunance.ac.id",
        "password": "AdminPassword123!"
    }
    
    try:
        print(f"\n🔐 Testing Admin Login...")
        print(f"   URL: {base_url}/api/v1/auth/login")
        print(f"   Data: {json.dumps(login_data, indent=2)}")
        
        response = requests.post(
            f"{base_url}/api/v1/auth/login",
            json=login_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"   Status Code: {response.status_code}")
        print(f"   Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Login berhasil!")
            print(f"   Access Token: {data.get('access_token', 'N/A')[:50]}...")
            print(f"   User: {data.get('user', {}).get('email', 'N/A')}")
        else:
            print(f"❌ Login gagal!")
            try:
                error_data = response.json()
                print(f"   Error: {json.dumps(error_data, indent=2)}")
            except:
                print(f"   Error Text: {response.text}")
        
        return response.status_code == 200
        
    except Exception as e:
        print(f"❌ Error testing login: {e}")
        return False

def test_different_endpoints():
    """Test berbagai variasi endpoint."""
    
    base_url = "http://localhost:8000"
    endpoints_to_test = [
        "/api/v1/auth/login",
        "/auth/login", 
        "/login",
        "/api/auth/login"
    ]
    
    login_data = {
        "email": "admin@lunance.ac.id",
        "password": "AdminPassword123!"
    }
    
    print(f"\n🔍 TESTING DIFFERENT ENDPOINTS")
    print("=" * 35)
    
    for endpoint in endpoints_to_test:
        try:
            url = f"{base_url}{endpoint}"
            print(f"\n   Testing: {url}")
            
            response = requests.post(
                url,
                json=login_data,
                headers={"Content-Type": "application/json"},
                timeout=5
            )
            
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                print(f"   ✅ SUCCESS!")
                return endpoint
            elif response.status_code == 404:
                print(f"   ❌ Not Found")
            else:
                print(f"   ⚠️ Other: {response.status_code}")
                
        except requests.exceptions.Timeout:
            print(f"   ⏰ Timeout")
        except requests.exceptions.ConnectionError:
            print(f"   🔌 Connection Error")
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    return None

if __name__ == "__main__":
    print("🚀 AUTH ENDPOINT CHECKER")
    print("=" * 25)
    
    # Test main endpoint
    success = test_auth_endpoint()
    
    if not success:
        print("\n⚠️ Main endpoint gagal, mencoba endpoint lain...")
        working_endpoint = test_different_endpoints()
        
        if working_endpoint:
            print(f"\n✅ Working endpoint found: {working_endpoint}")
        else:
            print(f"\n❌ Tidak ada endpoint yang bekerja")
            print(f"\n💡 Kemungkinan masalah:")
            print(f"   1. Server FastAPI tidak running")
            print(f"   2. Port bukan 8000")
            print(f"   3. Endpoint path berbeda")
            print(f"   4. CORS issue")