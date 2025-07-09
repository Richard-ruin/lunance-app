# scripts/deep_debug_auth.py
"""
Deep debugging untuk masalah authentication yang persisten.
"""

import asyncio
import sys
import os
from datetime import datetime
import json

# Fix path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from app.config.database import connect_to_mongo, close_mongo_connection, get_database
from app.utils.password import hash_password, verify_password
from app.services.auth_service import AuthService, AuthenticationError
from app.models.auth import LoginRequest

async def debug_auth_service_directly():
    """Debug auth service secara langsung."""
    try:
        await connect_to_mongo()
        
        print("🔍 DEBUGGING AUTH SERVICE DIRECTLY")
        print("=" * 40)
        
        # Create auth service instance
        auth_service = AuthService()
        
        # Create login request
        login_data = LoginRequest(
            email="admin@lunance.ac.id",
            password="AdminPassword123!"
        )
        
        print(f"📧 Email: {login_data.email}")
        print(f"🔐 Password: {login_data.password}")
        print(f"📝 Remember me: {login_data.remember_me}")
        
        # Step by step debugging
        print(f"\n1️⃣ CHECKING USER IN DATABASE...")
        db = await get_database()
        users_collection = db.users
        
        user_doc = await users_collection.find_one({"email": login_data.email})
        if not user_doc:
            print("❌ User not found in database!")
            return False
        
        print(f"✅ User found in database:")
        print(f"   ID: {user_doc.get('_id')}")
        print(f"   Email: {user_doc.get('email')}")
        print(f"   Role: {user_doc.get('role')}")
        print(f"   Is Active: {user_doc.get('is_active')}")
        print(f"   Is Verified: {user_doc.get('is_verified')}")
        print(f"   Has Password Hash: {'password_hash' in user_doc}")
        
        if 'password_hash' in user_doc:
            stored_hash = user_doc['password_hash']
            print(f"   Password Hash Length: {len(stored_hash)}")
            print(f"   Password Hash Preview: {stored_hash[:30]}...")
            
            # Test password verification manually
            print(f"\n2️⃣ TESTING PASSWORD VERIFICATION...")
            is_valid = verify_password(login_data.password, stored_hash)
            print(f"   Manual verification: {'✅ PASS' if is_valid else '❌ FAIL'}")
            
            if not is_valid:
                print("   🔧 Trying to fix password...")
                new_hash = hash_password(login_data.password)
                await users_collection.update_one(
                    {"_id": user_doc["_id"]},
                    {"$set": {"password_hash": new_hash}}
                )
                print("   ✅ Password hash updated")
                
                # Test again
                is_valid_new = verify_password(login_data.password, new_hash)
                print(f"   New verification: {'✅ PASS' if is_valid_new else '❌ FAIL'}")
        
        print(f"\n3️⃣ TESTING AUTH SERVICE LOGIN...")
        try:
            result = await auth_service.login_user(login_data)
            print(f"✅ AUTH SERVICE SUCCESS!")
            print(f"   User: {result.user.get('full_name')}")
            print(f"   Token: {result.tokens.access_token[:50]}...")
            return True
            
        except AuthenticationError as auth_error:
            print(f"❌ AUTH SERVICE FAILED: {auth_error}")
            return False
        except Exception as e:
            print(f"❌ UNEXPECTED ERROR: {e}")
            import traceback
            traceback.print_exc()
            return False
        
    except Exception as e:
        print(f"❌ Error in debug: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_with_curl_equivalent():
    """Test dengan menggunakan requests library."""
    import requests
    
    print(f"\n🌐 TESTING WITH HTTP REQUEST")
    print("=" * 35)
    
    url = "http://localhost:8000/api/v1/auth/login"
    data = {
        "email": "admin@lunance.ac.id",
        "password": "AdminPassword123!"
    }
    headers = {
        "Content-Type": "application/json"
    }
    
    print(f"📡 URL: {url}")
    print(f"📝 Data: {json.dumps(data, indent=2)}")
    print(f"📋 Headers: {json.dumps(headers, indent=2)}")
    
    try:
        print(f"\n🚀 Sending request...")
        response = requests.post(url, json=data, headers=headers, timeout=10)
        
        print(f"📊 Response Status: {response.status_code}")
        print(f"📋 Response Headers: {dict(response.headers)}")
        
        try:
            response_data = response.json()
            print(f"📄 Response Body: {json.dumps(response_data, indent=2)}")
        except:
            print(f"📄 Response Text: {response.text}")
        
        if response.status_code == 200:
            print(f"✅ HTTP REQUEST SUCCESS!")
            return True
        else:
            print(f"❌ HTTP REQUEST FAILED!")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"❌ CONNECTION ERROR - Server not running?")
        return False
    except Exception as e:
        print(f"❌ HTTP REQUEST ERROR: {e}")
        return False

async def check_auth_endpoint_implementation():
    """Check implementasi auth endpoint."""
    print(f"\n🔍 CHECKING AUTH ENDPOINT IMPLEMENTATION")
    print("=" * 45)
    
    # Check if auth endpoint file exists and is correct
    auth_file = "app/api/v1/endpoints/auth.py"
    
    try:
        with open(auth_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print(f"✅ Auth endpoint file exists")
        
        # Check for key patterns
        if 'async def login_user' in content:
            print(f"✅ Login function found")
        else:
            print(f"❌ Login function not found")
        
        if 'AuthService' in content:
            print(f"✅ AuthService import found")
        else:
            print(f"❌ AuthService import not found")
        
        if 'LoginRequest' in content:
            print(f"✅ LoginRequest import found")
        else:
            print(f"❌ LoginRequest import not found")
        
        if 'HTTPException' in content:
            print(f"✅ HTTPException import found")
        else:
            print(f"❌ HTTPException import not found")
        
        # Look for the actual login endpoint
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if '@router.post("/login"' in line:
                print(f"✅ Login endpoint found at line {i+1}")
                break
        else:
            print(f"❌ Login endpoint not found")
        
        # Check error handling
        if 'Login failed' in content:
            print(f"✅ 'Login failed' error message found")
            
            # Find the context
            for i, line in enumerate(lines):
                if 'Login failed' in line:
                    print(f"   Found at line {i+1}: {line.strip()}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error checking auth endpoint: {e}")
        return False

async def test_server_logs():
    """Test dan tampilkan server logs."""
    print(f"\n📝 SERVER LOG ANALYSIS")
    print("=" * 25)
    
    log_files = ["app.log", "logs/app.log", "app/app.log"]
    
    for log_file in log_files:
        if os.path.exists(log_file):
            print(f"📄 Found log file: {log_file}")
            
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                
                # Show last 20 lines
                print(f"📋 Last 20 lines:")
                for line in lines[-20:]:
                    if 'login' in line.lower() or 'auth' in line.lower() or 'error' in line.lower():
                        print(f"   {line.strip()}")
                
            except Exception as e:
                print(f"❌ Error reading log file: {e}")
            
            break
    else:
        print(f"⚠️ No log files found")

async def check_dependencies():
    """Check dependencies yang mungkin missing."""
    print(f"\n🔧 CHECKING DEPENDENCIES")
    print("=" * 28)
    
    try:
        # Check imports
        from app.services.auth_service import AuthService
        print(f"✅ AuthService import OK")
        
        from app.models.auth import LoginRequest, LoginResponse
        print(f"✅ Auth models import OK")
        
        from app.utils.password import verify_password, hash_password
        print(f"✅ Password utils import OK")
        
        from app.utils.jwt import create_token_pair
        print(f"✅ JWT utils import OK")
        
        from app.config.database import get_database
        print(f"✅ Database config import OK")
        
        # Test creating instances
        auth_service = AuthService()
        print(f"✅ AuthService instantiation OK")
        
        login_req = LoginRequest(email="test@ac.id", password="test123")
        print(f"✅ LoginRequest creation OK")
        
        return True
        
    except Exception as e:
        print(f"❌ Dependency error: {e}")
        import traceback
        traceback.print_exc()
        return False

async def create_minimal_test_user():
    """Create minimal test user untuk debugging."""
    try:
        db = await get_database()
        collection = db.users
        
        print(f"\n🧪 CREATING MINIMAL TEST USER")
        print("=" * 35)
        
        # Delete existing test user
        await collection.delete_many({"email": "test@ac.id"})
        
        # Create minimal user
        test_password = "test123"
        test_hash = hash_password(test_password)
        
        minimal_user = {
            "email": "test@ac.id",
            "full_name": "Test User",
            "phone_number": "628123456789",
            "role": "STUDENT",
            "initial_savings": 0.0,
            "password_hash": test_hash,
            "is_active": True,
            "is_verified": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        result = await collection.insert_one(minimal_user)
        print(f"✅ Test user created: {result.inserted_id}")
        
        # Test password immediately
        is_valid = verify_password(test_password, test_hash)
        print(f"✅ Password verification: {'PASS' if is_valid else 'FAIL'}")
        
        # Test auth service with this user
        print(f"\n🧪 Testing auth service with test user...")
        auth_service = AuthService()
        login_data = LoginRequest(email="test@ac.id", password="test123")
        
        try:
            result = await auth_service.login_user(login_data)
            print(f"✅ AUTH SERVICE SUCCESS with test user!")
            
            # Now test HTTP request
            print(f"\n🌐 Testing HTTP request with test user...")
            import requests
            
            response = requests.post(
                "http://localhost:8000/api/v1/auth/login",
                json={"email": "test@ac.id", "password": "test123"},
                headers={"Content-Type": "application/json"}
            )
            
            print(f"📊 HTTP Response: {response.status_code}")
            if response.status_code == 200:
                print(f"✅ HTTP REQUEST SUCCESS with test user!")
                return True
            else:
                print(f"❌ HTTP REQUEST FAILED: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Auth service failed with test user: {e}")
            return False
        
    except Exception as e:
        print(f"❌ Error creating test user: {e}")
        return False

async def main():
    """Main debug function."""
    print("🚀 DEEP AUTHENTICATION DEBUG")
    print("=" * 35)
    
    try:
        # 1. Check dependencies
        print(f"\n1️⃣ CHECKING DEPENDENCIES...")
        success = await check_dependencies()
        if not success:
            print(f"❌ Dependencies failed!")
            return
        
        # 2. Check auth endpoint implementation
        print(f"\n2️⃣ CHECKING AUTH ENDPOINT...")
        await check_auth_endpoint_implementation()
        
        # 3. Debug auth service directly
        print(f"\n3️⃣ DEBUGGING AUTH SERVICE...")
        success = await debug_auth_service_directly()
        
        # 4. Test HTTP request
        print(f"\n4️⃣ TESTING HTTP REQUEST...")
        success = await test_with_curl_equivalent()
        
        # 5. Create and test minimal user
        print(f"\n5️⃣ TESTING WITH MINIMAL USER...")
        success = await create_minimal_test_user()
        
        # 6. Check server logs
        print(f"\n6️⃣ CHECKING SERVER LOGS...")
        await test_server_logs()
        
        if success:
            print(f"\n🎉 DEBUGGING COMPLETED!")
            print(f"\nTEST CREDENTIALS AVAILABLE:")
            print(f"   👑 Admin: admin@lunance.ac.id / AdminPassword123!")
            print(f"   🧪 Test: test@ac.id / test123")
        else:
            print(f"\n❌ DEBUGGING FOUND ISSUES!")
        
    except Exception as e:
        print(f"❌ Debug error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await close_mongo_connection()

if __name__ == "__main__":
    asyncio.run(main())