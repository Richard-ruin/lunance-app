# scripts/data_seeds/fix_username_index.py
"""
Script untuk memperbaiki masalah index username yang menyebabkan E11000 error.
"""

import asyncio
import sys
import os
import logging

# Tambahkan path root project
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from app.config.database import connect_to_mongo, close_mongo_connection, get_database

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


async def diagnose_username_issue():
    """Diagnose masalah username index."""
    try:
        db = await get_database()
        collection = db.users
        
        logger.info("🔍 DIAGNOSA MASALAH USERNAME INDEX")
        logger.info("=" * 50)
        
        # 1. Cek semua indexes yang ada
        indexes = await collection.list_indexes().to_list(length=None)
        
        logger.info("📋 INDEX YANG ADA SAAT INI:")
        username_indexes = []
        for index in indexes:
            index_name = index.get('name', '')
            index_key = index.get('key', {})
            index_unique = index.get('unique', False)
            
            logger.info(f"   - {index_name}: {index_key} (unique: {index_unique})")
            
            if 'username' in index_key:
                username_indexes.append(index_name)
        
        # 2. Cek users yang ada
        user_count = await collection.count_documents({})
        users_with_username = await collection.count_documents({"username": {"$exists": True, "$ne": None}})
        users_with_null_username = await collection.count_documents({"username": None})
        users_without_username_field = await collection.count_documents({"username": {"$exists": False}})
        
        logger.info(f"\n📊 STATISTIK USERS:")
        logger.info(f"   - Total users: {user_count}")
        logger.info(f"   - Users dengan username: {users_with_username}")
        logger.info(f"   - Users dengan username null: {users_with_null_username}")
        logger.info(f"   - Users tanpa field username: {users_without_username_field}")
        
        # 3. Identifikasi masalah
        if username_indexes:
            logger.warning(f"\n⚠️ MASALAH DITEMUKAN:")
            logger.warning(f"   - Index username ditemukan: {username_indexes}")
            logger.warning(f"   - Index ini menyebabkan error karena multiple null values")
            logger.warning(f"   - Solusi: Hapus index username atau isi field username")
        
        return username_indexes
        
    except Exception as e:
        logger.error(f"❌ Error diagnosing username issue: {e}")
        return []


async def fix_username_index_issue():
    """Perbaiki masalah username index."""
    try:
        db = await get_database()
        collection = db.users
        
        logger.info("🔧 MEMPERBAIKI MASALAH USERNAME INDEX")
        logger.info("=" * 50)
        
        # 1. Hapus semua index username
        indexes = await collection.list_indexes().to_list(length=None)
        
        for index in indexes:
            index_name = index.get('name', '')
            index_key = index.get('key', {})
            
            if 'username' in index_key and index_name != '_id_':
                try:
                    logger.info(f"🗑️ Menghapus index: {index_name}")
                    await collection.drop_index(index_name)
                    logger.info(f"✅ Index {index_name} berhasil dihapus")
                except Exception as e:
                    logger.error(f"❌ Gagal menghapus index {index_name}: {e}")
        
        # 2. Verifikasi tidak ada index username lagi
        indexes_after = await collection.list_indexes().to_list(length=None)
        remaining_username_indexes = []
        
        for index in indexes_after:
            if 'username' in index.get('key', {}):
                remaining_username_indexes.append(index.get('name'))
        
        if remaining_username_indexes:
            logger.warning(f"⚠️ Masih ada index username: {remaining_username_indexes}")
            return False
        else:
            logger.info("✅ Semua index username berhasil dihapus")
        
        # 3. Pastikan index yang diperlukan masih ada
        essential_indexes = ['email_unique', 'email_1']
        
        for index in indexes_after:
            index_name = index.get('name', '')
            index_key = index.get('key', {})
            
            if 'email' in index_key:
                logger.info(f"✅ Index email masih ada: {index_name}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error fixing username index: {e}")
        return False


async def clean_user_data():
    """Bersihkan data user yang bermasalah."""
    try:
        db = await get_database()
        collection = db.users
        
        logger.info("🧹 MEMBERSIHKAN DATA USER")
        logger.info("=" * 30)
        
        # 1. Hapus field username yang null atau undefined
        result = await collection.update_many(
            {"username": None},
            {"$unset": {"username": ""}}
        )
        
        logger.info(f"🗑️ Menghapus field username null dari {result.modified_count} users")
        
        # 2. Hapus field username yang kosong
        result = await collection.update_many(
            {"username": ""},
            {"$unset": {"username": ""}}
        )
        
        logger.info(f"🗑️ Menghapus field username kosong dari {result.modified_count} users")
        
        # 3. Verifikasi pembersihan
        users_with_username = await collection.count_documents({"username": {"$exists": True}})
        logger.info(f"✅ Users dengan field username setelah pembersihan: {users_with_username}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error cleaning user data: {e}")
        return False


async def verify_fix():
    """Verifikasi bahwa masalah sudah teratasi."""
    try:
        db = await get_database()
        collection = db.users
        
        logger.info("✅ VERIFIKASI PERBAIKAN")
        logger.info("=" * 30)
        
        # Test insert user baru
        test_user = {
            "email": f"test.verification.{int(asyncio.get_event_loop().time())}@test.ac.id",
            "full_name": "Test User Verification",
            "phone_number": "628999999999",
            "role": "STUDENT",
            "initial_savings": 0.0,
            "password_hash": "test_hash",
            "is_active": True,
            "is_verified": False
        }
        
        try:
            result = await collection.insert_one(test_user)
            logger.info(f"✅ Test insert berhasil: {result.inserted_id}")
            
            # Hapus test user
            await collection.delete_one({"_id": result.inserted_id})
            logger.info("🗑️ Test user dihapus")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Test insert gagal: {e}")
            return False
        
    except Exception as e:
        logger.error(f"❌ Error verifying fix: {e}")
        return False


async def main():
    """Fungsi utama untuk memperbaiki masalah username."""
    try:
        # Koneksi ke database
        await connect_to_mongo()
        logger.info("🔗 Berhasil terhubung ke MongoDB")
        
        # 1. Diagnose masalah
        username_indexes = await diagnose_username_issue()
        
        if not username_indexes:
            logger.info("✅ Tidak ada masalah username index ditemukan")
            return
        
        # 2. Perbaiki index
        success = await fix_username_index_issue()
        if not success:
            logger.error("❌ Gagal memperbaiki username index!")
            sys.exit(1)
        
        # 3. Bersihkan data
        success = await clean_user_data()
        if not success:
            logger.error("❌ Gagal membersihkan data user!")
            sys.exit(1)
        
        # 4. Verifikasi perbaikan
        success = await verify_fix()
        if success:
            logger.info("\n🎉 MASALAH USERNAME INDEX BERHASIL DIPERBAIKI!")
            logger.info("💡 Sekarang Anda bisa menjalankan seeding ulang")
        else:
            logger.error("\n❌ Masalah belum sepenuhnya teratasi")
            sys.exit(1)
        
    except Exception as e:
        logger.error(f"❌ Error utama: {e}")
        sys.exit(1)
    finally:
        # Tutup koneksi database
        await close_mongo_connection()
        logger.info("🔌 Koneksi database ditutup")


if __name__ == "__main__":
    asyncio.run(main())