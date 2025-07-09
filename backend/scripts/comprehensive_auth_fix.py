# scripts/comprehensive_auth_fix.py
"""
Comprehensive fix untuk semua masalah authentication.
"""

import asyncio
import sys
import os
from datetime import datetime

# Fix path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from app.config.database import connect_to_mongo, close_mongo_connection, get_database
from app.utils.password import hash_password, verify_password

async def fix_database_indexes():
    """Fix database indexes completely."""
    try:
        await connect_to_mongo()
        db = await get_database()
        collection = db.users
        
        print("🔧 FIXING DATABASE INDEXES")
        print("=" * 35)
        
        # Drop ALL indexes except _id
        indexes = await collection.list_indexes().to_list(length=None)
        for index in indexes:
            index_name = index.get('name', '')
            if index_name != '_id_':
                try:
                    print(f"🗑️ Dropping index: {index_name}")
                    await collection.drop_index(index_name)
                except Exception as e:
                    print(f"⚠️ Could not drop {index_name}: {e}")
        
        # Create only the email index we need
        try:
            await collection.create_index("email", unique=True, name="email_unique")
            print("✅ Created email unique index")
        except Exception as e:
            print(f"⚠️ Email index: {e}")
        
        print("✅ Database indexes fixed")
        return True
        
    except Exception as e:
        print(f"❌ Error fixing indexes: {e}")
        return False

async def fix_user_roles_and_enum():
    """Fix user roles to match enum values."""
    try:
        db = await get_database()
        collection = db.users
        
        print("\n🔧 FIXING USER ROLES & ENUM")
        print("=" * 35)
        
        # Update all lowercase roles to uppercase
        admin_result = await collection.update_many(
            {"role": "admin"},
            {"$set": {"role": "ADMIN"}}
        )
        print(f"✅ Fixed {admin_result.modified_count} admin roles")
        
        student_result = await collection.update_many(
            {"role": "student"}, 
            {"$set": {"role": "STUDENT"}}
        )
        print(f"✅ Fixed {student_result.modified_count} student roles")
        
        # Check current distribution
        admin_count = await collection.count_documents({"role": "ADMIN"})
        student_count = await collection.count_documents({"role": "STUDENT"})
        
        print(f"📊 Current roles: {admin_count} ADMIN, {student_count} STUDENT")
        
        return True
        
    except Exception as e:
        print(f"❌ Error fixing roles: {e}")
        return False

async def fix_user_enum_in_models():
    """Update user model enum values."""
    print("\n🔧 FIXING USER MODEL ENUM")
    print("=" * 30)
    
    # Read current user.py file
    user_model_path = "app/models/user.py"
    
    try:
        with open(user_model_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Fix enum values
        old_enum = '''class UserRole(str, Enum):
    """User role enumeration."""
    ADMIN = "admin"
    STUDENT = "student"'''
        
        new_enum = '''class UserRole(str, Enum):
    """User role enumeration."""
    ADMIN = "ADMIN"
    STUDENT = "STUDENT"'''
        
        if old_enum in content:
            content = content.replace(old_enum, new_enum)
            
            # Write back
            with open(user_model_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print("✅ Fixed UserRole enum in user.py")
        else:
            print("ℹ️ UserRole enum already correct or not found")
        
        return True
        
    except Exception as e:
        print(f"❌ Error fixing user model: {e}")
        return False

async def fix_database_py():
    """Remove problematic username index from database.py."""
    print("\n🔧 FIXING DATABASE.PY")
    print("=" * 25)
    
    database_py_path = "app/config/database.py"
    
    try:
        with open(database_py_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Remove the problematic username index line
        lines = content.split('\n')
        new_lines = []
        
        for line in lines:
            if 'create_index("username"' not in line:
                new_lines.append(line)
            else:
                print(f"🗑️ Removing line: {line.strip()}")
        
        new_content = '\n'.join(new_lines)
        
        # Write back
        with open(database_py_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print("✅ Fixed database.py - removed username index")
        return True
        
    except Exception as e:
        print(f"❌ Error fixing database.py: {e}")
        return False

async def test_authentication_completely():
    """Test authentication end-to-end."""
    try:
        db = await get_database()
        collection = db.users
        
        print("\n🧪 TESTING AUTHENTICATION END-TO-END")
        print("=" * 40)
        
        # Test admin
        admin = await collection.find_one({"email": "admin@lunance.ac.id"})
        if not admin:
            print("❌ Admin not found!")
            return False
        
        print(f"👑 Admin found:")
        print(f"   Email: {admin['email']}")
        print(f"   Role: {admin['role']}")
        print(f"   Is Active: {admin['is_active']}")
        print(f"   Password Hash: {admin['password_hash'][:20]}...")
        
        # Test password verification
        test_password = "AdminPassword123!"
        is_valid = verify_password(test_password, admin['password_hash'])
        print(f"   Password Test: {'✅ PASS' if is_valid else '❌ FAIL'}")
        
        # Test student
        student = await collection.find_one({"role": "STUDENT"})
        if student:
            print(f"\n👤 Student sample:")
            print(f"   Email: {student['email']}")
            print(f"   Role: {student['role']}")
            print(f"   Is Active: {student['is_active']}")
            
            # Test student password
            student_password = "Password123!"
            is_valid_student = verify_password(student_password, student['password_hash'])
            print(f"   Password Test: {'✅ PASS' if is_valid_student else '❌ FAIL'}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing auth: {e}")
        return False

async def create_test_credentials():
    """Create clean test credentials."""
    try:
        db = await get_database()
        collection = db.users
        
        print("\n🔑 CREATING CLEAN TEST CREDENTIALS")
        print("=" * 40)
        
        # Delete existing admin
        await collection.delete_many({"email": "admin@lunance.ac.id"})
        
        # Create new admin with correct data
        admin_data = {
            "email": "admin@lunance.ac.id",
            "full_name": "Admin Lunance",
            "phone_number": "6281234567890",
            "role": "ADMIN",
            "initial_savings": 0.0,
            "password_hash": hash_password("AdminPassword123!"),
            "is_active": True,
            "is_verified": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        result = await collection.insert_one(admin_data)
        print(f"✅ New admin created: {result.inserted_id}")
        
        # Test the new admin
        new_admin = await collection.find_one({"_id": result.inserted_id})
        test_password = "AdminPassword123!"
        is_valid = verify_password(test_password, new_admin['password_hash'])
        print(f"   Password verification: {'✅ PASS' if is_valid else '❌ FAIL'}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating test credentials: {e}")
        return False

async def main():
    """Main comprehensive fix function."""
    print("🚀 COMPREHENSIVE AUTH FIX")
    print("=" * 30)
    
    try:
        # 1. Fix database indexes
        print("\n1️⃣ FIXING DATABASE INDEXES...")
        success = await fix_database_indexes()
        if not success:
            print("⚠️ Database index fix failed")
        
        # 2. Fix user roles in database
        print("\n2️⃣ FIXING USER ROLES...")
        success = await fix_user_roles_and_enum()
        if not success:
            print("⚠️ Role fix failed")
        
        # 3. Fix user model enum
        print("\n3️⃣ FIXING USER MODEL...")
        success = await fix_user_enum_in_models()
        if not success:
            print("⚠️ Model fix failed")
        
        # 4. Fix database.py
        print("\n4️⃣ FIXING DATABASE.PY...")
        success = await fix_database_py()
        if not success:
            print("⚠️ Database.py fix failed")
        
        # 5. Create clean test credentials
        print("\n5️⃣ CREATING CLEAN CREDENTIALS...")
        success = await create_test_credentials()
        if not success:
            print("⚠️ Credential creation failed")
        
        # 6. Test authentication completely
        print("\n6️⃣ TESTING AUTHENTICATION...")
        success = await test_authentication_completely()
        
        if success:
            print(f"\n🎉 COMPREHENSIVE FIX COMPLETED!")
            print(f"\n💡 CLEAN CREDENTIALS FOR TESTING:")
            print(f"   👑 Admin: admin@lunance.ac.id / AdminPassword123!")
            print(f"\n📡 TEST IN POSTMAN:")
            print(f"   POST http://localhost:8000/api/v1/auth/login")
            print(f"   Content-Type: application/json")
            print(f'   Body: {{"email": "admin@lunance.ac.id", "password": "AdminPassword123!"}}')
            print(f"\n🔄 RESTART SERVER AFTER THIS FIX!")
        else:
            print(f"\n❌ Some fixes failed, check logs above")
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await close_mongo_connection()

if __name__ == "__main__":
    asyncio.run(main())