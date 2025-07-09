# scripts/data_seeds/fix_database_indexes.py
"""
Script untuk memperbaiki database indexes yang bermasalah.
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


async def fix_user_indexes():
    """Perbaiki indexes pada collection users."""
    try:
        db = await get_database()
        collection = db.users
        
        logger.info("🔧 Memperbaiki indexes pada collection users...")
        
        # Ambil semua index yang ada
        indexes = await collection.list_indexes().to_list(length=None)
        
        logger.info("📋 Index yang ada saat ini:")
        for index in indexes:
            logger.info(f"   - {index.get('name', '')}: {index.get('key', {})}")
        
        # Hapus index username jika ada
        for index in indexes:
            index_name = index.get('name', '')
            index_key = index.get('key', {})
            
            if 'username' in index_key and index_name != '_id_':
                logger.warning(f"⚠️ Menghapus index yang bermasalah: {index_name}")
                try:
                    await collection.drop_index(index_name)
                    logger.info(f"✅ Index {index_name} berhasil dihapus")
                except Exception as e:
                    logger.error(f"❌ Gagal menghapus index {index_name}: {e}")
        
        # Pastikan index email yang benar ada
        try:
            await collection.create_index("email", unique=True, name="email_1")
            logger.info("✅ Index email unik berhasil dibuat/dipastikan")
        except Exception as e:
            if "already exists" in str(e):
                logger.info("✅ Index email sudah ada")
            else:
                logger.warning(f"⚠️ Warning saat membuat index email: {e}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error fixing user indexes: {e}")
        return False


async def main():
    """Fungsi utama."""
    try:
        # Koneksi ke database
        await connect_to_mongo()
        logger.info("🔗 Berhasil terhubung ke MongoDB")
        
        # Fix user indexes
        success = await fix_user_indexes()
        
        if success:
            logger.info("🎉 Berhasil memperbaiki database indexes!")
        else:
            logger.error("❌ Gagal memperbaiki database indexes!")
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