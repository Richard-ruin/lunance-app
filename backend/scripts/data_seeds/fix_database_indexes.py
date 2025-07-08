# scripts/data_seeds/fix_database_indexes.py
"""
Script untuk memperbaiki database indexes yang menyebabkan error.
Mengatasi masalah index username_1 yang tidak diperlukan.
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


class DatabaseIndexFixer:
    """Memperbaiki database indexes yang bermasalah."""
    
    def __init__(self):
        self.fixed_indexes = []
        self.errors = []
    
    async def list_current_indexes(self, collection_name: str):
        """List semua indexes di collection."""
        try:
            db = await get_database()
            collection = db[collection_name]
            
            indexes = await collection.list_indexes().to_list(length=None)
            
            logger.info(f"\n📋 INDEXES di collection '{collection_name}':")
            logger.info("-" * 50)
            
            for index in indexes:
                logger.info(f"  • {index['name']}: {index.get('key', {})}")
                if index.get('unique'):
                    logger.info(f"    (UNIQUE)")
            
            return indexes
            
        except Exception as e:
            logger.error(f"❌ Error listing indexes untuk {collection_name}: {e}")
            return []
    
    async def drop_problematic_indexes(self):
        """Drop indexes yang menyebabkan masalah."""
        try:
            db = await get_database()
            users_collection = db.users
            
            logger.info("🔍 Mengecek indexes yang bermasalah...")
            
            # List current indexes
            indexes = await self.list_current_indexes("users")
            
            # Cari dan drop index username_1 jika ada
            username_index_found = False
            for index in indexes:
                if index["name"] == "username_1":
                    username_index_found = True
                    logger.info("🗑️ Menghapus index 'username_1' yang bermasalah...")
                    
                    try:
                        await users_collection.drop_index("username_1")
                        logger.info("✅ Index 'username_1' berhasil dihapus")
                        self.fixed_indexes.append("username_1")
                    except Exception as e:
                        logger.error(f"❌ Error menghapus index username_1: {e}")
                        self.errors.append(f"Drop username_1: {e}")
            
            if not username_index_found:
                logger.info("✅ Index 'username_1' tidak ditemukan, tidak perlu dihapus")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error saat memperbaiki indexes: {e}")
            self.errors.append(f"General error: {e}")
            return False
    
    async def create_correct_indexes(self):
        """Buat indexes yang benar sesuai model."""
        try:
            db = await get_database()
            users_collection = db.users
            
            logger.info("🔧 Membuat indexes yang benar...")
            
            # Index untuk email (unique)
            try:
                await users_collection.create_index("email", unique=True)
                logger.info("✅ Index email (unique) berhasil dibuat")
                self.fixed_indexes.append("email_unique")
            except Exception as e:
                if "already exists" in str(e).lower():
                    logger.info("✅ Index email sudah ada")
                else:
                    logger.error(f"❌ Error membuat index email: {e}")
                    self.errors.append(f"Create email index: {e}")
            
            # Index untuk created_at
            try:
                await users_collection.create_index("created_at")
                logger.info("✅ Index created_at berhasil dibuat")
                self.fixed_indexes.append("created_at")
            except Exception as e:
                if "already exists" in str(e).lower():
                    logger.info("✅ Index created_at sudah ada")
                else:
                    logger.error(f"❌ Error membuat index created_at: {e}")
                    self.errors.append(f"Create created_at index: {e}")
            
            # Index untuk university_id
            try:
                await users_collection.create_index("university_id")
                logger.info("✅ Index university_id berhasil dibuat")
                self.fixed_indexes.append("university_id")
            except Exception as e:
                if "already exists" in str(e).lower():
                    logger.info("✅ Index university_id sudah ada")
                else:
                    logger.error(f"❌ Error membuat index university_id: {e}")
                    self.errors.append(f"Create university_id index: {e}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error saat membuat indexes: {e}")
            self.errors.append(f"Create indexes error: {e}")
            return False
    
    async def check_and_clean_duplicate_data(self):
        """Cek dan bersihkan data duplikat jika ada."""
        try:
            db = await get_database()
            users_collection = db.users
            
            logger.info("🔍 Mengecek data duplikat...")
            
            # Cek apakah ada documents dengan email yang sama
            pipeline = [
                {"$group": {
                    "_id": "$email",
                    "count": {"$sum": 1},
                    "docs": {"$push": "$_id"}
                }},
                {"$match": {"count": {"$gt": 1}}}
            ]
            
            duplicates = await users_collection.aggregate(pipeline).to_list(length=None)
            
            if duplicates:
                logger.warning(f"⚠️ Ditemukan {len(duplicates)} email duplikat")
                
                for dup in duplicates:
                    email = dup["_id"]
                    doc_ids = dup["docs"]
                    logger.warning(f"  Email '{email}': {len(doc_ids)} duplikat")
                    
                    # Hapus duplikat, sisakan yang pertama
                    if len(doc_ids) > 1:
                        ids_to_delete = doc_ids[1:]  # Hapus semua kecuali yang pertama
                        result = await users_collection.delete_many({
                            "_id": {"$in": ids_to_delete}
                        })
                        logger.info(f"  🗑️ Menghapus {result.deleted_count} duplikat untuk email '{email}'")
            else:
                logger.info("✅ Tidak ada data duplikat ditemukan")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error saat cek duplikat: {e}")
            return False
    
    async def print_summary(self):
        """Cetak ringkasan perbaikan."""
        logger.info("\n" + "="*60)
        logger.info("📊 RINGKASAN PERBAIKAN DATABASE")
        logger.info("="*60)
        logger.info(f"✅ Indexes yang diperbaiki: {len(self.fixed_indexes)}")
        logger.info(f"❌ Errors yang terjadi: {len(self.errors)}")
        
        if self.fixed_indexes:
            logger.info("\n🔧 INDEXES YANG DIPERBAIKI:")
            for index in self.fixed_indexes:
                logger.info(f"  • {index}")
        
        if self.errors:
            logger.info("\n❌ ERRORS:")
            for error in self.errors:
                logger.info(f"  • {error}")
        
        logger.info("="*60)
        
        if len(self.errors) == 0:
            logger.info("🎉 Database berhasil diperbaiki!")
            logger.info("💡 Sekarang coba jalankan seeding ulang")
        else:
            logger.warning("⚠️ Ada beberapa error, cek detail di atas")


async def main():
    """Fungsi utama."""
    fixer = DatabaseIndexFixer()
    
    try:
        # Koneksi ke database
        await connect_to_mongo()
        logger.info("🔗 Berhasil terhubung ke MongoDB")
        
        logger.info("\n🔧 MEMULAI PERBAIKAN DATABASE INDEXES")
        logger.info("="*60)
        
        # List indexes saat ini
        await fixer.list_current_indexes("users")
        
        # Bersihkan data duplikat
        await fixer.check_and_clean_duplicate_data()
        
        # Drop indexes bermasalah
        await fixer.drop_problematic_indexes()
        
        # Buat indexes yang benar
        await fixer.create_correct_indexes()
        
        # List indexes setelah perbaikan
        logger.info("\n📋 INDEXES SETELAH PERBAIKAN:")
        await fixer.list_current_indexes("users")
        
        # Tampilkan ringkasan
        await fixer.print_summary()
        
    except Exception as e:
        logger.error(f"❌ Error utama: {e}")
        sys.exit(1)
    finally:
        # Tutup koneksi database
        await close_mongo_connection()
        logger.info("\n🔌 Koneksi database ditutup")


if __name__ == "__main__":
    print("🔧 DATABASE INDEX FIXER")
    print("Script untuk memperbaiki indexes yang menyebabkan error seeding")
    
    # Jalankan perbaikan
    asyncio.run(main())