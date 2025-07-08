# scripts/data_seeds/seed_all.py
"""
Master seeding script yang menjalankan semua seeders secara berurutan.
Script ini akan menjalankan seeding dalam urutan yang benar.
"""

import asyncio
import sys
import os
import logging
from datetime import datetime
import importlib.util

# Tambahkan path root project
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from app.config.database import connect_to_mongo, close_mongo_connection

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class MasterSeeder:
    """Master seeder untuk menjalankan semua seeders."""
    
    def __init__(self):
        self.seeders = [
            {
                "name": "Categories",
                "file": "seed_categories.py",
                "description": "Seeding kategori global default"
            },
            {
                "name": "Universities", 
                "file": "seed_universities.py",
                "description": "Seeding universitas, fakultas, dan jurusan"
            },
            {
                "name": "Demo Data",
                "file": "seed_demo_data.py", 
                "description": "Seeding users, transactions, dan savings targets demo"
            }
        ]
        self.start_time = None
        self.results = {}
    
    def _load_seeder_module(self, filename):
        """Load seeder module secara dinamis."""
        try:
            current_dir = os.path.dirname(__file__)
            file_path = os.path.join(current_dir, filename)
            
            if not os.path.exists(file_path):
                logger.error(f"❌ File {filename} tidak ditemukan di {current_dir}")
                return None
            
            spec = importlib.util.spec_from_file_location("seeder_module", file_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            return module
            
        except Exception as e:
            logger.error(f"❌ Error loading {filename}: {e}")
            return None
    
    async def run_seeder(self, seeder_info):
        """Jalankan seeder individual."""
        seeder_name = seeder_info["name"]
        seeder_file = seeder_info["file"]
        description = seeder_info["description"]
        
        logger.info(f"\n🚀 Memulai seeding: {seeder_name}")
        logger.info(f"📝 {description}")
        logger.info("─" * 60)
        
        start_time = datetime.now()
        
        try:
            # Load module seeder
            module = self._load_seeder_module(seeder_file)
            if not module:
                return False
            
            # Jalankan main function dari seeder
            if hasattr(module, 'main'):
                await module.main()
                
                duration = (datetime.now() - start_time).total_seconds()
                logger.info(f"✅ {seeder_name} selesai dalam {duration:.2f} detik")
                
                self.results[seeder_name] = {
                    "status": "success",
                    "duration": duration
                }
                return True
            else:
                logger.error(f"❌ Function 'main' tidak ditemukan di {seeder_file}")
                self.results[seeder_name] = {
                    "status": "error",
                    "error": "Main function not found"
                }
                return False
                
        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds()
            logger.error(f"❌ Error saat menjalankan {seeder_name}: {e}")
            
            self.results[seeder_name] = {
                "status": "error", 
                "error": str(e),
                "duration": duration
            }
            return False
    
    async def check_database_connection(self):
        """Cek koneksi database sebelum seeding."""
        try:
            await connect_to_mongo()
            logger.info("✅ Koneksi database berhasil")
            return True
        except Exception as e:
            logger.error(f"❌ Gagal terhubung ke database: {e}")
            return False
    
    async def run_all_seeders(self, skip_on_error=False):
        """Jalankan semua seeders secara berurutan."""
        self.start_time = datetime.now()
        
        logger.info("🌟 MEMULAI MASTER SEEDING PROCESS")
        logger.info("=" * 70)
        logger.info(f"📅 Waktu mulai: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"📋 Total seeders: {len(self.seeders)}")
        logger.info("=" * 70)
        
        # Cek koneksi database
        if not await self.check_database_connection():
            logger.error("❌ Tidak dapat melanjutkan tanpa koneksi database")
            return False
        
        success_count = 0
        error_count = 0
        
        for i, seeder_info in enumerate(self.seeders, 1):
            logger.info(f"\n🔄 STEP {i}/{len(self.seeders)}: {seeder_info['name']}")
            
            success = await self.run_seeder(seeder_info)
            
            if success:
                success_count += 1
                logger.info(f"✅ Step {i} berhasil")
            else:
                error_count += 1
                logger.error(f"❌ Step {i} gagal")
                
                if not skip_on_error:
                    logger.error("🛑 Menghentikan proses karena error (gunakan --skip-on-error untuk melanjutkan)")
                    break
                else:
                    logger.warning("⚠️ Melanjutkan ke step berikutnya...")
        
        # Tampilkan ringkasan final
        await self.print_final_summary(success_count, error_count)
        
        return error_count == 0
    
    async def print_final_summary(self, success_count, error_count):
        """Tampilkan ringkasan final."""
        end_time = datetime.now()
        total_duration = (end_time - self.start_time).total_seconds()
        
        logger.info("\n" + "=" * 70)
        logger.info("📊 RINGKASAN MASTER SEEDING")
        logger.info("=" * 70)
        logger.info(f"⏰ Waktu mulai: {self.start_time.strftime('%H:%M:%S')}")
        logger.info(f"⏰ Waktu selesai: {end_time.strftime('%H:%M:%S')}")
        logger.info(f"⌛ Total durasi: {total_duration:.2f} detik")
        logger.info(f"✅ Berhasil: {success_count} seeders")
        logger.info(f"❌ Gagal: {error_count} seeders")
        
        logger.info("\n📋 DETAIL HASIL:")
        logger.info("-" * 50)
        
        for seeder_name, result in self.results.items():
            status_icon = "✅" if result["status"] == "success" else "❌"
            duration = result.get("duration", 0)
            
            if result["status"] == "success":
                logger.info(f"{status_icon} {seeder_name:<20} | {duration:6.2f}s | Berhasil")
            else:
                error_msg = result.get("error", "Unknown error")[:30]
                logger.info(f"{status_icon} {seeder_name:<20} | {duration:6.2f}s | {error_msg}")
        
        logger.info("=" * 70)
        
        if error_count == 0:
            logger.info("🎉 SEMUA SEEDING BERHASIL!")
            logger.info("💡 Database siap digunakan untuk development dan testing")
        else:
            logger.warning(f"⚠️ {error_count} seeder gagal, periksa log di atas")
    
    async def run_specific_seeder(self, seeder_name):
        """Jalankan seeder spesifik."""
        # Cari seeder berdasarkan nama
        target_seeder = None
        for seeder in self.seeders:
            if seeder["name"].lower() == seeder_name.lower():
                target_seeder = seeder
                break
        
        if not target_seeder:
            logger.error(f"❌ Seeder '{seeder_name}' tidak ditemukan")
            logger.info("📋 Seeders yang tersedia:")
            for seeder in self.seeders:
                logger.info(f"   - {seeder['name']}")
            return False
        
        # Cek koneksi database
        if not await self.check_database_connection():
            return False
        
        self.start_time = datetime.now()
        
        success = await self.run_seeder(target_seeder)
        
        await self.print_final_summary(1 if success else 0, 0 if success else 1)
        
        return success
    
    def list_available_seeders(self):
        """Tampilkan daftar seeders yang tersedia."""
        logger.info("📋 DAFTAR SEEDERS YANG TERSEDIA:")
        logger.info("=" * 50)
        
        for i, seeder in enumerate(self.seeders, 1):
            logger.info(f"{i}. {seeder['name']}")
            logger.info(f"   📝 {seeder['description']}")
            logger.info(f"   📄 File: {seeder['file']}")
            logger.info("")


async def main():
    """Fungsi utama."""
    seeder = MasterSeeder()
    
    # Parse command line arguments
    import argparse
    parser = argparse.ArgumentParser(description="Master seeding script untuk Lunance Backend")
    parser.add_argument("--seeder", "-s", help="Jalankan seeder spesifik")
    parser.add_argument("--list", "-l", action="store_true", help="Tampilkan daftar seeders")
    parser.add_argument("--skip-on-error", action="store_true", help="Lanjutkan meskipun ada error")
    
    args = parser.parse_args()
    
    try:
        if args.list:
            seeder.list_available_seeders()
            return
        
        if args.seeder:
            success = await seeder.run_specific_seeder(args.seeder)
        else:
            success = await seeder.run_all_seeders(skip_on_error=args.skip_on_error)
        
        if not success:
            sys.exit(1)
            
    except KeyboardInterrupt:
        logger.info("\n⚠️ Proses dihentikan oleh user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Error tidak terduga: {e}")
        sys.exit(1)
    finally:
        # Tutup koneksi database
        await close_mongo_connection()
        logger.info("🔌 Koneksi database ditutup")


if __name__ == "__main__":
    # Jalankan master seeder
    asyncio.run(main())