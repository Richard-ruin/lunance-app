# scripts/data_seeds/seed_categories.py
"""
Seeding script untuk kategori global default.
Script ini akan membuat kategori-kategori default yang diperlukan sistem.
"""

import asyncio
import sys
import os
from datetime import datetime
import logging

# Tambahkan path root project
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from app.config.database import connect_to_mongo, close_mongo_connection, get_database
from app.models.category import DEFAULT_GLOBAL_CATEGORIES, CategoryInDB
from app.services.category_service import category_service

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class CategorySeeder:
    """Seeder untuk kategori global."""
    
    def __init__(self):
        self.collection_name = "categories"
        self.created_count = 0
        self.existing_count = 0
    
    async def seed_categories(self):
        """Seed kategori global default."""
        try:
            db = await get_database()
            collection = db[self.collection_name]
            
            logger.info("🌱 Mulai seeding kategori global...")
            
            for category_data in DEFAULT_GLOBAL_CATEGORIES:
                # Cek apakah kategori sudah ada
                existing = await collection.find_one({
                    "name": category_data["name"],
                    "is_global": True
                })
                
                if existing:
                    logger.info(f"✅ Kategori '{category_data['name']}' sudah ada, dilewati")
                    self.existing_count += 1
                else:
                    # Buat kategori baru
                    category_doc = CategoryInDB(
                        name=category_data["name"],
                        icon=category_data["icon"],
                        color=category_data["color"],
                        is_global=category_data["is_global"],
                        user_id=category_data["user_id"],
                        created_at=datetime.utcnow(),
                        updated_at=datetime.utcnow()
                    )
                    
                    result = await collection.insert_one(
                        category_doc.model_dump(by_alias=True, exclude={"id"})
                    )
                    
                    logger.info(f"✨ Kategori '{category_data['name']}' berhasil dibuat dengan ID: {result.inserted_id}")
                    self.created_count += 1
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error saat seeding kategori: {e}")
            return False
    
    async def print_summary(self):
        """Cetak ringkasan hasil seeding."""
        logger.info("\n" + "="*50)
        logger.info("📊 RINGKASAN SEEDING KATEGORI")
        logger.info("="*50)
        logger.info(f"✨ Kategori baru dibuat: {self.created_count}")
        logger.info(f"✅ Kategori sudah ada: {self.existing_count}")
        logger.info(f"📝 Total kategori diproses: {self.created_count + self.existing_count}")
        logger.info("="*50)
    
    async def list_all_categories(self):
        """Tampilkan semua kategori yang ada."""
        try:
            db = await get_database()
            collection = db[self.collection_name]
            
            # Ambil semua kategori global
            cursor = collection.find({"is_global": True}).sort("name", 1)
            categories = await cursor.to_list(length=None)
            
            logger.info("\n📋 DAFTAR KATEGORI GLOBAL:")
            logger.info("-" * 40)
            
            for i, category in enumerate(categories, 1):
                logger.info(f"{i:2d}. {category['name']:<20} | {category['icon']:<15} | {category['color']}")
            
            logger.info(f"\n📊 Total: {len(categories)} kategori global")
            
        except Exception as e:
            logger.error(f"❌ Error saat menampilkan kategori: {e}")


async def main():
    """Fungsi utama untuk menjalankan seeding."""
    seeder = CategorySeeder()
    
    try:
        # Koneksi ke database
        await connect_to_mongo()
        logger.info("🔗 Berhasil terhubung ke MongoDB")
        
        # Jalankan seeding
        success = await seeder.seed_categories()
        
        if success:
            # Tampilkan ringkasan
            await seeder.print_summary()
            
            # Tampilkan daftar kategori
            await seeder.list_all_categories()
            
            logger.info("\n🎉 Seeding kategori berhasil!")
        else:
            logger.error("❌ Seeding kategori gagal!")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"❌ Error utama: {e}")
        sys.exit(1)
    finally:
        # Tutup koneksi database
        await close_mongo_connection()
        logger.info("🔌 Koneksi database ditutup")


if __name__ == "__main__":
    # Jalankan seeding
    asyncio.run(main())