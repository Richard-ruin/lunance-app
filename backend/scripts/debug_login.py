# scripts/debug_login.py
"""
Script untuk debug masalah login.
"""

import asyncio
import sys
import os
from datetime import datetime

# Fix path - tambahkan root directory ke Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

# Sekarang import akan berfungsi
from app.config.database import connect_to_mongo, close_mongo_connection, get_database
from app.utils.password import verify_password, hash_password

async def debug_login_issue():
    """Debug masalah login."""
    try:
        await connect_to_mongo()
        db = await get_database()
        collection = db.users
        
        print("🔍 DEBUGGING LOGIN ISSUE")
        print("=" * 50)
        
        # 1. Cek apakah admin ada
        admin = await collection.find_one({"email": "admin@lunance.ac.id"})
        if not admin:
            print("❌ Admin user tidak ditemukan!")
            print("💡 Mungkin seeding belum berhasil atau email berbeda")
            
            # Cek users yang ada
            all_users = await collection.find({}, {"email": 1, "role": 1}).limit(5).to_list(length=5)
            print(f"\n📋 Users yang ada di database:")
            for user in all_users:
                print(f"   - {user.get('email', 'N/A')} ({user.get('role', 'N/A')})")
            
            return False
        
        print("✅ Admin user ditemukan:")
        print(f"   ID: {admin.get('_id')}")
        print(f"   Email: {admin.get('email')}")
        print(f"   Full Name: {admin.get('full_name')}")
        print(f"   Role: {admin.get('role')}")
        print(f"   Is Active: {admin.get('is_active')}")
        print(f"   Is Verified: {admin.get('is_verified')}")
        print(f"   Password Hash exists: {'password_hash' in admin}")
        print(f"   Password Hash length: {len(admin.get('password_hash', ''))}")
        
        # 2. Test password verification
        stored_hash = admin.get('password_hash')
        test_password = "AdminPassword123!"
        
        if stored_hash:
            print(f"\n🔐 TESTING PASSWORD VERIFICATION:")
            print(f"   Stored hash: {stored_hash[:50]}...")
            print(f"   Test password: {test_password}")
            
            try:
                # Test dengan password yang benar
                is_valid = verify_password(test_password, stored_hash)
                print(f"   Password verification result: {is_valid}")
                
                if not is_valid:
                    print("⚠️ Password verification gagal! Akan memperbaiki...")
                    # Generate hash baru
                    new_hash = hash_password(test_password)
                    
                    # Update di database
                    result = await collection.update_one(
                        {"_id": admin["_id"]},
                        {"$set": {"password_hash": new_hash, "updated_at": datetime.utcnow()}}
                    )
                    
                    if result.modified_count > 0:
                        print("✅ Password hash berhasil diperbaiki!")
                        # Test lagi
                        is_valid_new = verify_password(test_password, new_hash)
                        print(f"   New verification result: {is_valid_new}")
                    else:
                        print("❌ Gagal memperbaiki password hash")
                
            except Exception as pwd_error:
                print(f"❌ Error saat verify password: {pwd_error}")
                return False
                
        else:
            print("❌ Password hash tidak ada!")
            # Generate password hash baru
            new_hash = hash_password(test_password)
            result = await collection.update_one(
                {"_id": admin["_id"]},
                {"$set": {"password_hash": new_hash}}
            )
            if result.modified_count > 0:
                print("✅ Password hash baru berhasil ditambahkan!")
            return False
        
        # 3. Cek mahasiswa sample
        print(f"\n👤 CHECKING STUDENT SAMPLE:")
        student = await collection.find_one({"role": "STUDENT"})
        if student:
            print(f"   Email: {student.get('email')}")
            print(f"   Full Name: {student.get('full_name')}")
            print(f"   Is Active: {student.get('is_active')}")
            print(f"   Password Hash exists: {'password_hash' in student}")
            
            if 'password_hash' in student:
                student_hash = student['password_hash']
                student_password = "Password123!"
                
                try:
                    is_valid_student = verify_password(student_password, student_hash)
                    print(f"   Student password verification: {is_valid_student}")
                    
                    if not is_valid_student:
                        print("⚠️ Student password perlu diperbaiki!")
                        new_student_hash = hash_password(student_password)
                        await collection.update_many(
                            {"role": "STUDENT"},
                            {"$set": {"password_hash": new_student_hash}}
                        )
                        print("✅ All student passwords fixed!")
                        
                except Exception as e:
                    print(f"❌ Error verifying student password: {e}")
        else:
            print("⚠️ Tidak ada student ditemukan")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during debugging: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        await close_mongo_connection()

async def test_manual_auth():
    """Test manual authentication logic."""
    try:
        await connect_to_mongo()
        db = await get_database()
        collection = db.users
        
        print(f"\n🧪 MANUAL AUTH TEST")
        print("=" * 30)
        
        email = "admin@lunance.ac.id"
        password = "AdminPassword123!"
        
        # Step 1: Find user
        print(f"1️⃣ Searching for user: {email}")
        user = await collection.find_one({"email": email})
        if not user:
            print(f"❌ User not found with email: {email}")
            return False
        
        print(f"✅ User found: {user.get('full_name')}")
        
        # Step 2: Check if active
        print(f"2️⃣ Checking if user is active...")
        is_active = user.get('is_active', False)
        print(f"   is_active field: {is_active}")
        
        if not is_active:
            print(f"⚠️ User is not active, fixing...")
            await collection.update_one(
                {"_id": user["_id"]},
                {"$set": {"is_active": True}}
            )
            print(f"✅ User activated!")
        else:
            print(f"✅ User is active")
        
        # Step 3: Verify password
        print(f"3️⃣ Verifying password...")
        stored_hash = user.get('password_hash')
        if not stored_hash:
            print(f"❌ No password hash found")
            return False
        
        print(f"   Password hash exists: {len(stored_hash)} chars")
        
        try:
            is_valid = verify_password(password, stored_hash)
            print(f"   Password verification: {is_valid}")
            
            if not is_valid:
                print(f"❌ Password verification failed")
                return False
        except Exception as e:
            print(f"❌ Password verification error: {e}")
            return False
        
        print(f"✅ Password verification successful")
        
        # Step 4: Simulate successful auth
        print(f"4️⃣ Auth simulation...")
        print(f"✅ MANUAL AUTH SUCCESSFUL!")
        print(f"   User ID: {user.get('_id')}")
        print(f"   Email: {user.get('email')}")
        print(f"   Role: {user.get('role')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during manual auth test: {e}")
        import traceback
        traceback.print_exc()
        return False

async def check_database_connection():
    """Cek koneksi database."""
    try:
        print("🔌 CHECKING DATABASE CONNECTION")
        print("=" * 35)
        
        await connect_to_mongo()
        db = await get_database()
        
        # Test connection
        server_info = await db.command("ping")
        print(f"✅ Database ping successful: {server_info}")
        
        # Check collections
        collections = await db.list_collection_names()
        print(f"📋 Collections available: {collections}")
        
        # Check users collection
        if 'users' in collections:
            user_count = await db.users.count_documents({})
            admin_count = await db.users.count_documents({"role": "ADMIN"})
            student_count = await db.users.count_documents({"role": "STUDENT"})
            
            print(f"👥 User statistics:")
            print(f"   Total users: {user_count}")
            print(f"   Admins: {admin_count}")
            print(f"   Students: {student_count}")
        else:
            print(f"❌ Users collection not found!")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Database connection error: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Main function."""
    print("🚀 LUNANCE LOGIN DEBUG TOOL")
    print("=" * 40)
    
    # 0. Check database connection
    print("\n0️⃣ CHECKING DATABASE CONNECTION...")
    db_ok = await check_database_connection()
    if not db_ok:
        print("❌ Database connection failed!")
        return
    
    # 1. Debug login issue
    print("\n1️⃣ DEBUGGING LOGIN ISSUE...")
    success = await debug_login_issue()
    if not success:
        print("❌ Debug menemukan masalah yang perlu diperbaiki")
        
        # Coba perbaiki dan test lagi
        print("\n🔧 Mencoba perbaikan otomatis...")
        await debug_login_issue()  # Run again after fixes
    
    # 2. Test manual auth
    print("\n2️⃣ TESTING MANUAL AUTH...")
    success = await test_manual_auth()
    if success:
        print("\n🎉 LOGIN DEBUG SELESAI - MASALAH SUDAH DIPERBAIKI!")
        print("\n💡 CREDENTIALS UNTUK TESTING:")
        print("   👑 Admin: admin@lunance.ac.id / AdminPassword123!")
        print("   👤 Student: [any student email] / Password123!")
        print("\n📡 TEST DI POSTMAN:")
        print("   POST http://localhost:8000/api/v1/auth/login")
        print("   Content-Type: application/json")
        print('   Body: {"email": "admin@lunance.ac.id", "password": "AdminPassword123!"}')
    else:
        print("\n❌ Masih ada masalah setelah debug")
        print("💡 Kemungkinan masalah:")
        print("   1. Auth endpoint tidak ada atau berbeda")
        print("   2. Server FastAPI tidak running")
        print("   3. Ada masalah di auth service logic")

if __name__ == "__main__":
    print("📍 Current working directory:", os.getcwd())
    print("📁 Script location:", os.path.dirname(os.path.abspath(__file__)))
    print("📂 Parent directory:", os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⚠️ Script dihentikan oleh user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()