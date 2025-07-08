# scripts/data_seeds/seed_universities.py
"""
Seeding script untuk universitas, fakultas, dan jurusan.
Script ini akan membuat data universitas Indonesia yang umum.
"""

import asyncio
import sys
import os
from datetime import datetime
import logging
from bson import ObjectId

# Tambahkan path root project
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from app.config.database import connect_to_mongo, close_mongo_connection, get_database
from app.models.university import UniversityInDB, Faculty, Major

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


# Data universitas Indonesia
UNIVERSITIES_DATA = [
    {
        "name": "Universitas Indonesia",
        "faculties": [
            {
                "name": "Fakultas Ilmu Komputer",
                "majors": [
                    {"name": "Ilmu Komputer"},
                    {"name": "Sistem Informasi"},
                    {"name": "Teknologi Informasi"}
                ]
            },
            {
                "name": "Fakultas Ekonomi dan Bisnis",
                "majors": [
                    {"name": "Manajemen"},
                    {"name": "Akuntansi"},
                    {"name": "Ekonomi"},
                    {"name": "Ekonomi Islam"}
                ]
            },
            {
                "name": "Fakultas Teknik",
                "majors": [
                    {"name": "Teknik Elektro"},
                    {"name": "Teknik Mesin"},
                    {"name": "Teknik Sipil"},
                    {"name": "Teknik Informatika"},
                    {"name": "Teknik Industri"}
                ]
            }
        ]
    },
    {
        "name": "Institut Teknologi Bandung",
        "faculties": [
            {
                "name": "Sekolah Teknik Elektro dan Informatika",
                "majors": [
                    {"name": "Teknik Informatika"},
                    {"name": "Sistem dan Teknologi Informasi"},
                    {"name": "Teknik Elektro"},
                    {"name": "Teknik Telekomunikasi"}
                ]
            },
            {
                "name": "Fakultas Matematika dan Ilmu Pengetahuan Alam",
                "majors": [
                    {"name": "Matematika"},
                    {"name": "Fisika"},
                    {"name": "Kimia"},
                    {"name": "Astronomi"}
                ]
            },
            {
                "name": "Sekolah Bisnis dan Manajemen",
                "majors": [
                    {"name": "Manajemen"},
                    {"name": "Kewirausahaan"}
                ]
            }
        ]
    },
    {
        "name": "Universitas Gadjah Mada",
        "faculties": [
            {
                "name": "Fakultas Teknik",
                "majors": [
                    {"name": "Teknik Sipil"},
                    {"name": "Teknik Mesin"},
                    {"name": "Teknik Elektro"},
                    {"name": "Teknik Kimia"},
                    {"name": "Teknik Industri"}
                ]
            },
            {
                "name": "Fakultas Ekonomika dan Bisnis",
                "majors": [
                    {"name": "Ilmu Ekonomi"},
                    {"name": "Manajemen"},
                    {"name": "Akuntansi"}
                ]
            },
            {
                "name": "Fakultas Matematika dan Ilmu Pengetahuan Alam",
                "majors": [
                    {"name": "Matematika"},
                    {"name": "Fisika"},
                    {"name": "Kimia"},
                    {"name": "Ilmu Komputer"},
                    {"name": "Elektronika dan Instrumentasi"}
                ]
            }
        ]
    },
    {
        "name": "Institut Teknologi Sepuluh Nopember",
        "faculties": [
            {
                "name": "Fakultas Teknologi Informasi dan Komunikasi",
                "majors": [
                    {"name": "Informatika"},
                    {"name": "Sistem Informasi"},
                    {"name": "Teknologi Informasi"}
                ]
            },
            {
                "name": "Fakultas Teknologi Elektro",
                "majors": [
                    {"name": "Teknik Elektro"},
                    {"name": "Teknik Komputer"},
                    {"name": "Teknik Biomedik"}
                ]
            },
            {
                "name": "Fakultas Bisnis dan Manajemen Teknologi",
                "majors": [
                    {"name": "Manajemen Bisnis"},
                    {"name": "Studi Pembangunan"}
                ]
            }
        ]
    },
    {
        "name": "Universitas Bina Nusantara",
        "faculties": [
            {
                "name": "Fakultas Ilmu Komputer",
                "majors": [
                    {"name": "Teknik Informatika"},
                    {"name": "Sistem Informasi"},
                    {"name": "Ilmu Komputer"},
                    {"name": "Sistem Komputer"}
                ]
            },
            {
                "name": "Fakultas Ekonomi dan Komunikasi",
                "majors": [
                    {"name": "Akuntansi"},
                    {"name": "Keuangan"},
                    {"name": "Manajemen"},
                    {"name": "Marketing"}
                ]
            },
            {
                "name": "Fakultas Teknik",
                "majors": [
                    {"name": "Teknik Industri"},
                    {"name": "Teknik Sipil"},
                    {"name": "Arsitektur"}
                ]
            }
        ]
    }
]


class UniversitySeeder:
    """Seeder untuk universitas."""
    
    def __init__(self):
        self.collection_name = "universities"
        self.created_count = 0
        self.existing_count = 0
        self.total_faculties = 0
        self.total_majors = 0
    
    def _create_majors_with_ids(self, majors_data):
        """Buat majors dengan ObjectId sebagai string."""
        majors_with_ids = []
        for major_data in majors_data:
            major_id = ObjectId()
            majors_with_ids.append({
                "_id": str(major_id),
                "id": str(major_id),
                "name": major_data["name"]
            })
            self.total_majors += 1
        return majors_with_ids
    
    def _create_faculties_with_ids(self, faculties_data):
        """Buat faculties dengan ObjectId sebagai string dan majors."""
        faculties_with_ids = []
        for faculty_data in faculties_data:
            faculty_id = ObjectId()
            majors_with_ids = self._create_majors_with_ids(faculty_data["majors"])
            
            faculties_with_ids.append({
                "_id": str(faculty_id),
                "id": str(faculty_id),
                "name": faculty_data["name"],
                "majors": majors_with_ids
            })
            self.total_faculties += 1
        return faculties_with_ids
    
    async def seed_universities(self):
        """Seed universitas dengan fakultas dan jurusan."""
        try:
            db = await get_database()
            collection = db[self.collection_name]
            
            logger.info("🌱 Mulai seeding universitas...")
            
            for university_data in UNIVERSITIES_DATA:
                # Cek apakah universitas sudah ada
                existing = await collection.find_one({
                    "name": {"$regex": f"^{university_data['name']}$", "$options": "i"}
                })
                
                if existing:
                    logger.info(f"✅ Universitas '{university_data['name']}' sudah ada, dilewati")
                    self.existing_count += 1
                else:
                    # Buat fakultas dengan ID
                    faculties_with_ids = self._create_faculties_with_ids(university_data["faculties"])
                    
                    # Buat universitas baru
                    university_doc = UniversityInDB(
                        name=university_data["name"],
                        is_active=True,
                        faculties=faculties_with_ids,
                        created_at=datetime.utcnow(),
                        updated_at=datetime.utcnow()
                    )
                    
                    result = await collection.insert_one(
                        university_doc.model_dump(by_alias=True, exclude={"id"})
                    )
                    
                    faculty_count = len(faculties_with_ids)
                    major_count = sum(len(f["majors"]) for f in faculties_with_ids)
                    
                    logger.info(f"✨ Universitas '{university_data['name']}' berhasil dibuat")
                    logger.info(f"   📚 {faculty_count} fakultas, {major_count} jurusan")
                    logger.info(f"   🆔 ID: {result.inserted_id}")
                    
                    self.created_count += 1
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error saat seeding universitas: {e}")
            return False
    
    async def print_summary(self):
        """Cetak ringkasan hasil seeding."""
        logger.info("\n" + "="*60)
        logger.info("📊 RINGKASAN SEEDING UNIVERSITAS")
        logger.info("="*60)
        logger.info(f"🏛️  Universitas baru dibuat: {self.created_count}")
        logger.info(f"✅ Universitas sudah ada: {self.existing_count}")
        logger.info(f"📚 Total fakultas dibuat: {self.total_faculties}")
        logger.info(f"🎓 Total jurusan dibuat: {self.total_majors}")
        logger.info(f"📝 Total universitas diproses: {self.created_count + self.existing_count}")
        logger.info("="*60)
    
    async def list_all_universities(self):
        """Tampilkan semua universitas yang ada."""
        try:
            db = await get_database()
            collection = db[self.collection_name]
            
            # Ambil semua universitas
            cursor = collection.find({}).sort("name", 1)
            universities = await cursor.to_list(length=None)
            
            logger.info("\n📋 DAFTAR UNIVERSITAS:")
            logger.info("-" * 80)
            
            for i, university in enumerate(universities, 1):
                faculty_count = len(university.get("faculties", []))
                major_count = sum(len(f.get("majors", [])) for f in university.get("faculties", []))
                status = "🟢 Aktif" if university.get("is_active", True) else "🔴 Tidak Aktif"
                
                logger.info(f"{i:2d}. {university['name']:<35} | {faculty_count:2d} fakultas | {major_count:2d} jurusan | {status}")
            
            logger.info(f"\n📊 Total: {len(universities)} universitas")
            
        except Exception as e:
            logger.error(f"❌ Error saat menampilkan universitas: {e}")
    
    async def show_university_details(self, university_name: str = None):
        """Tampilkan detail universitas tertentu atau yang pertama."""
        try:
            db = await get_database()
            collection = db[self.collection_name]
            
            if university_name:
                university = await collection.find_one({
                    "name": {"$regex": university_name, "$options": "i"}
                })
            else:
                university = await collection.find_one({})
            
            if not university:
                logger.info("❌ Universitas tidak ditemukan")
                return
            
            logger.info(f"\n🏛️  DETAIL UNIVERSITAS: {university['name']}")
            logger.info("=" * 60)
            
            for i, faculty in enumerate(university.get("faculties", []), 1):
                logger.info(f"\n{i}. 📚 {faculty['name']}")
                logger.info("   Jurusan:")
                
                for j, major in enumerate(faculty.get("majors", []), 1):
                    logger.info(f"      {j}. 🎓 {major['name']}")
            
        except Exception as e:
            logger.error(f"❌ Error saat menampilkan detail universitas: {e}")


async def main():
    """Fungsi utama untuk menjalankan seeding."""
    seeder = UniversitySeeder()
    
    try:
        # Koneksi ke database
        await connect_to_mongo()
        logger.info("🔗 Berhasil terhubung ke MongoDB")
        
        # Jalankan seeding
        success = await seeder.seed_universities()
        
        if success:
            # Tampilkan ringkasan
            await seeder.print_summary()
            
            # Tampilkan daftar universitas
            await seeder.list_all_universities()
            
            # Tampilkan detail universitas pertama
            await seeder.show_university_details("Universitas Indonesia")
            
            logger.info("\n🎉 Seeding universitas berhasil!")
        else:
            logger.error("❌ Seeding universitas gagal!")
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