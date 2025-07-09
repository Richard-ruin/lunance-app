# scripts/test_login_request.py
"""
Script untuk test login dengan requests library (tanpa import app).
"""

import requests
import json
import sys
import os

def test_server_reachability():
    """Test apakah server bisa dijangkau."""
    base_url = "http://localhost:8000"
    
    print("🔍 TESTING SERVER REACHABILITY")
    print("=" * 35)
    
    endpoints_to_test = [
        "/",
        "/docs",
        "/health",
        "/api/v1/",
    ]
    
    for endpoint in endpoints_to_test:
        try:
            url = f"{base_url}{endpoint}"
            print(f"\n   Testing: {url}")
            
            response = requests.get(url, timeout=5)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                print(f"   ✅ Reachable!")
                return True
            else:
                print(f"   ⚠️ Status: {response.status_code}")
                
        except requests.exceptions.ConnectionError:
            print(f"   ❌ Connection refused")
        except requests.exceptions.Timeout:
            print(f"   ⏰ Timeout")
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    return False

def test_auth_endpoints():
    """Test berbagai kemungkinan auth endpoint."""
    base_url = "http://localhost:8000"
    
    # Berbagai kemungkinan endpoint
    auth_endpoints = [
        "/api/v1/auth/login",
        "/api/v1/login", 
        "/auth/login",
        "/login",
        "/api/auth/login",
        "/v1/auth/login"
    ]
    
    # Test data
    login_data = {
        "email": "admin@lunance.ac.id",
        "password": "AdminPassword123!"
    }
    
    print(f"\n🔐 TESTING AUTH ENDPOINTS")
    print("=" * 30)
    
    for endpoint in auth_endpoints:
        try:
            url = f"{base_url}{endpoint}"
            print(f"\n   POST {endpoint}")
            
            response = requests.post(
                url,
                json=login_data,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                print(f"   ✅ SUCCESS!")
                try:
                    data = response.json()
                    print(f"   Token: {data.get('access_token', 'N/A')[:50]}...")
                    print(f"   User: {data.get('user', {}).get('email', 'N/A')}")
                    return endpoint, data
                except:
                    print(f"   ⚠️ Success but no JSON response")
                    
            elif response.status_code == 404:
                print(f"   ❌ Not Found")
            elif response.status_code == 422:
                print(f"   ❌ Validation Error")
                try:
                    error = response.json()
                    print(f"   Detail: {error}")
                except:
                    pass
            elif response.status_code == 401:
                print(f"   ❌ Unauthorized (credentials invalid)")
                try:
                    error = response.json()
                    print(f"   Detail: {error}")
                except:
                    pass
            else:
                print(f"   ⚠️ Other: {response.status_code}")
                try:
                    print(f"   Response: {response.text[:200]}")
                except:
                    pass
                
        except requests.exceptions.ConnectionError:
            print(f"   ❌ Connection Error")
        except requests.exceptions.Timeout:
            print(f"   ⏰ Timeout")
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    return None, None

def test_different_credentials():
    """Test dengan kredensial yang berbeda."""
    base_url = "http://localhost:8000"
    endpoint = "/api/v1/auth/login"  # Default endpoint
    
    print(f"\n🔑 TESTING DIFFERENT CREDENTIALS")
    print("=" * 35)
    
    test_credentials = [
        {
            "name": "Admin Default",
            "email": "admin@lunance.ac.id",
            "password": "AdminPassword123!"
        },
        {
            "name": "Admin Simple",
            "email": "admin@lunance.ac.id", 
            "password": "admin123"
        },
        {
            "name": "Admin Alternative",
            "email": "admin@lunance.ac.id",
            "password": "password123"
        },
        {
            "name": "Test Student",
            "email": "test@ui.ac.id",
            "password": "Password123!"
        }
    ]
    
    for cred in test_credentials:
        try:
            print(f"\n   Testing: {cred['name']}")
            print(f"   Email: {cred['email']}")
            print(f"   Password: {cred['password']}")
            
            response = requests.post(
                f"{base_url}{endpoint}",
                json={
                    "email": cred['email'],
                    "password": cred['password']
                },
                headers={"Content-Type": "application/json"},
                timeout=5
            )
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                print(f"   ✅ SUCCESS!")
                data = response.json()
                print(f"   User: {data.get('user', {}).get('full_name', 'N/A')}")
                return cred, data
            else:
                try:
                    error = response.json()
                    print(f"   Error: {error.get('detail', error)}")
                except:
                    print(f"   Error: {response.text[:100]}")
                    
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    return None, None

def main():
    """Main function."""
    print("🚀 LOGIN REQUEST TESTER")
    print("=" * 25)
    
    # 1. Test server reachability
    print("\n1️⃣ TESTING SERVER...")
    server_ok = test_server_reachability()
    
    if not server_ok:
        print("\n❌ SERVER TIDAK DAPAT DIJANGKAU!")
        print("💡 Pastikan:")
        print("   - FastAPI server sedang running")
        print("   - Port 8000 tidak terblokir")
        print("   - Tidak ada error di server logs")
        print("\n🚀 Untuk menjalankan server:")
        print("   cd lunance-backend")
        print("   python -m uvicorn app.main:app --reload --port 8000")
        return
    
    # 2. Test auth endpoints
    print("\n2️⃣ TESTING AUTH ENDPOINTS...")
    working_endpoint, success_data = test_auth_endpoints()
    
    if working_endpoint:
        print(f"\n✅ WORKING ENDPOINT FOUND: {working_endpoint}")
        print(f"🎉 LOGIN BERHASIL!")
        return
    
    # 3. Test different credentials
    print("\n3️⃣ TESTING DIFFERENT CREDENTIALS...")
    working_cred, success_data = test_different_credentials()
    
    if working_cred:
        print(f"\n✅ WORKING CREDENTIALS:")
        print(f"   Email: {working_cred['email']}")
        print(f"   Password: {working_cred['password']}")
        return
    
    # 4. Final diagnosis
    print(f"\n❌ SEMUA TEST GAGAL!")
    print(f"\n🔍 KEMUNGKINAN MASALAH:")
    print(f"   1. Database: Users belum ada atau password salah")
    print(f"   2. Server: Auth endpoint belum diimplementasi")
    print(f"   3. Logic: Ada bug di authentication service")
    print(f"   4. Config: Environment variables salah")
    
    print(f"\n💡 LANGKAH SELANJUTNYA:")
    print(f"   1. Jalankan: python scripts/debug_login.py")
    print(f"   2. Cek server logs untuk error")
    print(f"   3. Pastikan seeding berhasil")
    print(f"   4. Cek file .env configuration")

if __name__ == "__main__":
    main()