# scripts/fix_auth_issues.py
"""
Script untuk memperbaiki semua masalah authentication.
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
from app.utils.password import hash_password

async def fix_username_index_completely():
    """Hapus username index secara paksa."""
    try:
        await connect_to_mongo()
        db = await get_database()
        collection = db.users
        
        print("🔧 FIXING USERNAME INDEX ISSUE")
        print("=" * 35)
        
        # Get all indexes
        indexes = await collection.list_indexes().to_list(length=None)
        
        # Drop username index
        for index in indexes:
            index_name = index.get('name', '')
            index_key = index.get('key', {})
            
            if 'username' in index_key and index_name != '_id_':
                try:
                    print(f"🗑️ Dropping index: {index_name}")
                    await collection.drop_index(index_name)
                    print(f"✅ Index {index_name} dropped successfully")
                except Exception as e:
                    print(f"⚠️ Could not drop {index_name}: {e}")
        
        # Verify no username indexes remain
        indexes_after = await collection.list_indexes().to_list(length=None)
        username_indexes = [idx['name'] for idx in indexes_after if 'username' in idx.get('key', {})]
        
        if username_indexes:
            print(f"⚠️ Still have username indexes: {username_indexes}")
            return False
        else:
            print(f"✅ All username indexes removed")
            return True
            
    except Exception as e:
        print(f"❌ Error fixing username index: {e}")
        return False

async def fix_user_roles():
    """Perbaiki role field untuk semua users."""
    try:
        await connect_to_mongo()
        db = await get_database()
        collection = db.users
        
        print(f"\n🔧 FIXING USER ROLES")
        print("=" * 25)
        
        # Fix admin role
        admin_result = await collection.update_many(
            {"role": "admin"},
            {"$set": {"role": "ADMIN"}}
        )
        print(f"✅ Fixed {admin_result.modified_count} admin roles")
        
        # Fix student role
        student_result = await collection.update_many(
            {"role": "student"},
            {"$set": {"role": "STUDENT"}}
        )
        print(f"✅ Fixed {student_result.modified_count} student roles")
        
        # Check current roles
        role_stats = await collection.aggregate([
            {"$group": {"_id": "$role", "count": {"$sum": 1}}}
        ]).to_list(length=None)
        
        print(f"📊 Current role distribution:")
        for stat in role_stats:
            print(f"   {stat['_id']}: {stat['count']} users")
        
        return True
        
    except Exception as e:
        print(f"❌ Error fixing user roles: {e}")
        return False

async def create_missing_students():
    """Buat student users yang hilang."""
    try:
        await connect_to_mongo()
        db = await get_database()
        users_collection = db.users
        universities_collection = db.universities
        
        print(f"\n👥 CREATING MISSING STUDENTS")
        print("=" * 30)
        
        # Check if we have students
        student_count = await users_collection.count_documents({"role": "STUDENT"})
        print(f"Current students: {student_count}")
        
        if student_count >= 10:
            print(f"✅ Enough students exist")
            return True
        
        # Get universities for reference
        universities = await universities_collection.find({"is_active": True}).to_list(length=None)
        if not universities:
            print(f"❌ No universities found!")
            return False
        
        print(f"📚 Found {len(universities)} universities")
        
        # Create sample students
        import random
        from faker import Faker
        fake = Faker('id_ID')
        
        students_to_create = 10 - student_count
        print(f"🔨 Creating {students_to_create} students...")
        
        for i in range(students_to_create):
            try:
                name = fake.name()
                university = random.choice(universities)
                
                # Simple email generation
                username = name.lower().replace(" ", "").replace(".", "")[:10]
                email = f"{username}{i}@test.ac.id"
                
                student_data = {
                    "email": email,
                    "full_name": name,
                    "phone_number": f"628{random.randint(10000000, 99999999)}",
                    "university_id": str(university["_id"]),
                    "faculty_id": None,
                    "major_id": None,
                    "role": "STUDENT",
                    "initial_savings": random.uniform(500000, 5000000),
                    "password_hash": hash_password("Password123!"),
                    "is_active": True,
                    "is_verified": True,
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                }
                
                result = await users_collection.insert_one(student_data)
                print(f"   ✅ Created student: {email}")
                
            except Exception as e:
                print(f"   ⚠️ Failed to create student {i}: {e}")
        
        # Final count
        final_count = await users_collection.count_documents({"role": "STUDENT"})
        print(f"✅ Total students now: {final_count}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating students: {e}")
        return False

async def test_fixed_auth():
    """Test authentication setelah diperbaiki."""
    try:
        await connect_to_mongo()
        db = await get_database()
        collection = db.users
        
        print(f"\n🧪 TESTING FIXED AUTH")
        print("=" * 25)
        
        # Test admin
        admin = await collection.find_one({"email": "admin@lunance.ac.id"})
        if admin:
            print(f"✅ Admin found:")
            print(f"   Email: {admin['email']}")
            print(f"   Role: {admin['role']}")
            print(f"   Is Active: {admin['is_active']}")
            print(f"   Has Password: {'password_hash' in admin}")
        else:
            print(f"❌ Admin not found!")
            return False
        
        # Test student
        student = await collection.find_one({"role": "STUDENT"})
        if student:
            print(f"✅ Student sample found:")
            print(f"   Email: {student['email']}")
            print(f"   Role: {student['role']}")
            print(f"   Is Active: {student['is_active']}")
            print(f"   Has Password: {'password_hash' in student}")
        else:
            print(f"❌ No students found!")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing auth: {e}")
        return False

async def main():
    """Main function."""
    print("🚀 COMPREHENSIVE AUTH FIX")
    print("=" * 30)
    
    try:
        # 1. Fix username index
        print("\n1️⃣ FIXING USERNAME INDEX...")
        success = await fix_username_index_completely()
        if not success:
            print("⚠️ Username index fix failed, continuing...")
        
        # 2. Fix user roles
        print("\n2️⃣ FIXING USER ROLES...")
        success = await fix_user_roles()
        if not success:
            print("❌ Role fix failed!")
            return
        
        # 3. Create missing students
        print("\n3️⃣ CREATING MISSING STUDENTS...")
        success = await create_missing_students()
        if not success:
            print("⚠️ Student creation failed, continuing...")
        
        # 4. Test fixed auth
        print("\n4️⃣ TESTING FIXED AUTH...")
        success = await test_fixed_auth()
        if success:
            print(f"\n🎉 AUTH FIX COMPLETED SUCCESSFULLY!")
            print(f"\n💡 CREDENTIALS TO TEST:")
            print(f"   👑 Admin: admin@lunance.ac.id / AdminPassword123!")
            
            # Show student emails
            db = await get_database()
            students = await db.users.find({"role": "STUDENT"}, {"email": 1}).limit(3).to_list(length=3)
            print(f"   👤 Students:")
            for student in students:
                print(f"      {student['email']} / Password123!")
            
            print(f"\n📡 TEST IN POSTMAN:")
            print(f"   POST http://localhost:8000/api/v1/auth/login")
            print(f"   Content-Type: application/json")
            print(f'   Body: {{"email": "admin@lunance.ac.id", "password": "AdminPassword123!"}}')
        else:
            print(f"\n❌ Auth test failed after fixes")
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await close_mongo_connection()

if __name__ == "__main__":
    asyncio.run(main())