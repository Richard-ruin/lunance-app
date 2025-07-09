# scripts/check_auth_implementation.py
"""
Script untuk memeriksa implementasi auth endpoint.
"""

import os
import sys

def check_auth_files():
    """Cek file-file authentication."""
    print("🔍 CHECKING AUTH IMPLEMENTATION")
    print("=" * 35)
    
    # Path yang perlu dicek
    auth_files = [
        "app/api/v1/endpoints/auth.py",
        "app/services/auth_service.py", 
        "app/models/auth.py",
        "app/utils/jwt.py",
        "app/utils/password.py"
    ]
    
    for file_path in auth_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path} exists")
            
            # Cek isi file
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                if 'login' in content.lower():
                    print(f"   📋 Contains login logic")
                    
                    # Cek specific patterns
                    if 'Invalid email or password' in content:
                        print(f"   ⚠️ Found error message: 'Invalid email or password'")
                    if 'verify_password' in content:
                        print(f"   ✅ Uses verify_password function")
                    if 'role' in content.lower():
                        print(f"   ✅ Handles user roles")
                        
            except Exception as e:
                print(f"   ❌ Could not read file: {e}")
        else:
            print(f"❌ {file_path} missing")
    
    # Cek main.py untuk routing
    print(f"\n🔗 CHECKING ROUTING:")
    main_file = "app/main.py"
    if os.path.exists(main_file):
        with open(main_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        if '/auth' in content:
            print(f"✅ Auth routes included in main.py")
        else:
            print(f"⚠️ Auth routes might not be included")
            
        if 'api/v1' in content:
            print(f"✅ API v1 routes included")
    else:
        print(f"❌ main.py not found")

def check_env_config():
    """Cek konfigurasi environment."""
    print(f"\n🔧 CHECKING ENVIRONMENT CONFIG:")
    
    env_files = [".env", ".env.example"]
    
    for env_file in env_files:
        if os.path.exists(env_file):
            print(f"✅ {env_file} exists")
            
            try:
                with open(env_file, 'r') as f:
                    content = f.read()
                    
                # Cek JWT config
                if 'JWT' in content:
                    print(f"   ✅ JWT configuration found")
                if 'SECRET' in content:
                    print(f"   ✅ SECRET key configuration found")
                if 'MONGO' in content:
                    print(f"   ✅ MongoDB configuration found")
                    
            except Exception as e:
                print(f"   ❌ Could not read {env_file}: {e}")
        else:
            print(f"⚠️ {env_file} not found")

if __name__ == "__main__":
    check_auth_files()
    check_env_config()
    
    print(f"\n💡 NEXT STEPS:")
    print(f"   1. Run: python scripts/fix_auth_issues.py")
    print(f"   2. Restart FastAPI server")
    print(f"   3. Test login in Postman")