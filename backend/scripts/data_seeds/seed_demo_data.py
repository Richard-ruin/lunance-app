# scripts/data_seeds/seed_demo_data.py
"""
Seeding script untuk data demo (users, transactions, savings targets).
Script ini akan membuat data demo untuk testing dan development.
"""

import asyncio
import sys
import os
from datetime import datetime, date, timedelta
import logging
import random
from bson import ObjectId
from faker import Faker

# Tambahkan path root project
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from app.config.database import connect_to_mongo, close_mongo_connection, get_database
from app.models.user import UserInDB, UserRole
from app.models.transaction import TransactionInDB, TransactionType
from app.models.savings_target import SavingsTargetInDB
from app.utils.password import hash_password

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Setup Faker untuk data Indonesia
fake = Faker('id_ID')


class DemoDataSeeder:
    """Seeder untuk data demo."""
    
    def __init__(self):
        self.users_created = 0
        self.transactions_created = 0
        self.savings_targets_created = 0
        self.demo_users = []
        self.categories = []
        self.universities = []
    
    async def load_existing_data(self):
        """Load data yang sudah ada (categories, universities)."""
        try:
            db = await get_database()
            
            # Load categories
            categories_cursor = db.categories.find({"is_global": True})
            self.categories = await categories_cursor.to_list(length=None)
            logger.info(f"📂 Loaded {len(self.categories)} categories")
            
            # Load universities
            universities_cursor = db.universities.find({"is_active": True})
            self.universities = await universities_cursor.to_list(length=None)
            logger.info(f"🏛️ Loaded {len(self.universities)} universities")
            
            if not self.categories:
                logger.error("❌ Tidak ada kategori global! Jalankan seed_categories.py terlebih dahulu")
                return False
            
            if not self.universities:
                logger.error("❌ Tidak ada universitas! Jalankan seed_universities.py terlebih dahulu")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error loading existing data: {e}")
            return False
    
    def _get_random_university_data(self):
        """Ambil data universitas, fakultas, dan jurusan secara random."""
        university = random.choice(self.universities)
        faculties = university.get("faculties", [])
        
        if not faculties:
            return str(university["_id"]), None, None
        
        faculty = random.choice(faculties)
        majors = faculty.get("majors", [])
        
        university_id = str(university["_id"])
        faculty_id = str(faculty.get("_id", faculty.get("id", "")))
        major_id = None
        
        if majors:
            major = random.choice(majors)
            major_id = str(major.get("_id", major.get("id", "")))
        
        return university_id, faculty_id, major_id
    
    def _generate_academic_email(self, name):
        """Generate email akademik yang valid."""
        # Ambil universitas secara random
        university = random.choice(self.universities)
        university_name = university["name"].lower()
        
        # Buat domain berdasarkan nama universitas
        if "indonesia" in university_name:
            domain = "ui.ac.id"
        elif "bandung" in university_name:
            domain = "itb.ac.id"
        elif "gadjah mada" in university_name:
            domain = "ugm.ac.id"
        elif "sepuluh nopember" in university_name:
            domain = "its.ac.id"
        elif "bina nusantara" in university_name:
            domain = "binus.ac.id"
        else:
            domain = "ac.id"
        
        # Buat username dari nama
        username = name.lower().replace(" ", ".")
        return f"{username}@{domain}"
    
    async def create_demo_users(self, count=20):
        """Buat users demo."""
        try:
            db = await get_database()
            collection = db.users
            
            logger.info(f"👥 Membuat {count} users demo...")
            
            for i in range(count):
                name = fake.name()
                email = self._generate_academic_email(name)
                
                # Cek apakah email sudah ada
                existing = await collection.find_one({"email": email})
                if existing:
                    continue
                
                university_id, faculty_id, major_id = self._get_random_university_data()
                
                # Generate phone number Indonesia
                phone = f"628{random.randint(10000000, 99999999)}"
                
                # Initial savings antara 500rb - 10jt
                initial_savings = random.uniform(500000, 10000000)
                
                user_doc = UserInDB(
                    email=email,
                    full_name=name,
                    phone_number=phone,
                    university_id=university_id,
                    faculty_id=faculty_id,
                    major_id=major_id,
                    role=UserRole.STUDENT,
                    initial_savings=round(initial_savings, 2),
                    password_hash=hash_password("Password123!"),
                    is_active=True,
                    is_verified=random.choice([True, True, True, False]),  # 75% verified
                    created_at=datetime.utcnow() - timedelta(days=random.randint(1, 365)),
                    updated_at=datetime.utcnow()
                )
                
                # Pastikan tidak ada field yang null/undefined yang bisa menyebabkan index error
                doc_data = user_doc.model_dump(by_alias=True, exclude={"id"})
                
                try:
                    result = await collection.insert_one(doc_data)
                    
                    self.demo_users.append({
                        "id": str(result.inserted_id),
                        "email": email,
                        "name": name,
                        "initial_savings": initial_savings
                    })
                    
                    self.users_created += 1
                    
                except Exception as insert_error:
                    logger.warning(f"⚠️ Gagal insert user {email}: {insert_error}")
                    # Skip user ini dan lanjut ke user berikutnya
                    continue
                
                if (i + 1) % 5 == 0:
                    logger.info(f"   ✨ Created {self.users_created}/{count} users")
            
            logger.info(f"✅ Berhasil membuat {self.users_created} users demo")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error creating demo users: {e}")
            # Jika error karena duplicate key, coba cek lebih detail
            if "E11000" in str(e) and "username" in str(e):
                logger.error("❌ Error disebabkan oleh index 'username' yang tidak diperlukan")
                logger.info("💡 Jalankan: python scripts/data_seeds/fix_database_indexes.py")
            return False
    
    async def create_demo_transactions(self, transactions_per_user=30):
        """Buat transactions demo untuk setiap user."""
        try:
            db = await get_database()
            collection = db.transactions
            
            logger.info(f"💰 Membuat {transactions_per_user} transaksi per user...")
            
            # Daftar deskripsi transaksi yang realistis
            income_descriptions = [
                "Gaji part-time", "Uang saku bulanan", "Freelance project", 
                "Jualan online", "Les privat", "Beasiswa", "Hadiah ulang tahun"
            ]
            
            expense_descriptions = [
                "Makan siang kampus", "Transportasi online", "Beli buku kuliah",
                "Bayar kos", "Beli pulsa", "Jajan di kantin", "Fotokopi tugas",
                "Beli alat tulis", "Nonton bioskop", "Belanja online",
                "Bayar internet", "Beli kopi", "Makan malam", "Bensin motor"
            ]
            
            for user in self.demo_users:
                user_id = user["id"]
                
                for _ in range(transactions_per_user):
                    # 20% income, 80% expense
                    transaction_type = TransactionType.INCOME if random.random() < 0.2 else TransactionType.EXPENSE
                    
                    # Pilih kategori yang sesuai
                    if transaction_type == TransactionType.INCOME:
                        # Kategori income: Salary, Freelance, Investment
                        income_categories = [c for c in self.categories if c["name"] in ["Salary & Income", "Freelance", "Investment"]]
                        category = random.choice(income_categories) if income_categories else random.choice(self.categories)
                        description = random.choice(income_descriptions)
                        amount = random.uniform(100000, 2000000)  # 100rb - 2jt
                    else:
                        # Kategori expense: yang lainnya
                        expense_categories = [c for c in self.categories if c["name"] not in ["Salary & Income", "Freelance", "Investment"]]
                        category = random.choice(expense_categories) if expense_categories else random.choice(self.categories)
                        description = random.choice(expense_descriptions)
                        amount = random.uniform(5000, 500000)  # 5rb - 500rb
                    
                    # Random date dalam 6 bulan terakhir
                    days_ago = random.randint(1, 180)
                    transaction_date = date.today() - timedelta(days=days_ago)
                    
                    transaction_doc = TransactionInDB(
                        user_id=user_id,
                        category_id=str(category["_id"]),
                        transaction_type=transaction_type,
                        amount=round(amount, 2),
                        description=description,
                        transaction_date=transaction_date,
                        created_at=datetime.utcnow() - timedelta(days=days_ago),
                        updated_at=datetime.utcnow() - timedelta(days=days_ago)
                    )
                    
                    await collection.insert_one(
                        transaction_doc.model_dump(by_alias=True, exclude={"id"})
                    )
                    
                    self.transactions_created += 1
                
                if len(self.demo_users) > 10 and (len([u for u in self.demo_users if u == user]) % 5 == 0):
                    logger.info(f"   ✨ Created transactions for {self.demo_users.index(user) + 1}/{len(self.demo_users)} users")
            
            logger.info(f"✅ Berhasil membuat {self.transactions_created} transaksi demo")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error creating demo transactions: {e}")
            return False
    
    async def create_demo_savings_targets(self, targets_per_user=3):
        """Buat savings targets demo untuk setiap user."""
        try:
            db = await get_database()
            collection = db.savings_targets
            
            logger.info(f"🎯 Membuat {targets_per_user} target tabungan per user...")
            
            target_names = [
                "Laptop baru", "Liburan akhir tahun", "Emergency fund", 
                "Motor baru", "Kamera DSLR", "iPhone baru", "Dana skripsi",
                "Uang semester", "Modal usaha", "Gadget gaming", "Travelling Eropa",
                "Wedding fund", "Investasi emas", "Dana tugas akhir"
            ]
            
            for user in self.demo_users:
                user_id = user["id"]
                
                for _ in range(random.randint(1, targets_per_user)):
                    target_name = random.choice(target_names)
                    target_amount = random.uniform(1000000, 25000000)  # 1jt - 25jt
                    
                    # Current amount: 0% - 80% dari target
                    progress = random.uniform(0, 0.8)
                    current_amount = target_amount * progress
                    
                    # Target date: 3 bulan - 2 tahun ke depan
                    days_ahead = random.randint(90, 730)
                    target_date = date.today() + timedelta(days=days_ahead)
                    
                    # 20% chance sudah achieved
                    is_achieved = random.random() < 0.2
                    if is_achieved:
                        current_amount = target_amount
                    
                    savings_target_doc = SavingsTargetInDB(
                        user_id=user_id,
                        target_name=target_name,
                        target_amount=round(target_amount, 2),
                        current_amount=round(current_amount, 2),
                        target_date=target_date,
                        is_achieved=is_achieved,
                        created_at=datetime.utcnow() - timedelta(days=random.randint(1, 100)),
                        updated_at=datetime.utcnow()
                    )
                    
                    await collection.insert_one(
                        savings_target_doc.model_dump(by_alias=True, exclude={"id"})
                    )
                    
                    self.savings_targets_created += 1
            
            logger.info(f"✅ Berhasil membuat {self.savings_targets_created} target tabungan demo")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error creating demo savings targets: {e}")
            return False
    
    async def create_admin_user(self):
        """Buat user admin untuk testing."""
        try:
            db = await get_database()
            collection = db.users
            
            # Cek apakah admin sudah ada
            existing_admin = await collection.find_one({"email": "admin@lunance.ac.id"})
            if existing_admin:
                logger.info("✅ Admin user sudah ada, dilewati")
                return True
            
            admin_doc = UserInDB(
                email="admin@lunance.ac.id",
                full_name="Admin Lunance",
                phone_number="6281234567890",
                university_id=None,
                faculty_id=None,
                major_id=None,
                role=UserRole.ADMIN,
                initial_savings=0.0,
                password_hash=hash_password("AdminPassword123!"),
                is_active=True,
                is_verified=True,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            # Pastikan tidak ada field yang null/undefined yang bisa menyebabkan index error
            doc_data = admin_doc.model_dump(by_alias=True, exclude={"id"})
            
            result = await collection.insert_one(doc_data)
            
            logger.info(f"✨ Admin user berhasil dibuat dengan ID: {result.inserted_id}")
            logger.info("   📧 Email: admin@lunance.ac.id")
            logger.info("   🔐 Password: AdminPassword123!")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error creating admin user: {e}")
            # Jika error karena duplicate key, coba cek lebih detail
            if "E11000" in str(e) and "username" in str(e):
                logger.error("❌ Error disebabkan oleh index 'username' yang tidak diperlukan")
                logger.info("💡 Jalankan: python scripts/data_seeds/fix_database_indexes.py")
            return False
    
    async def print_summary(self):
        """Cetak ringkasan hasil seeding."""
        logger.info("\n" + "="*60)
        logger.info("📊 RINGKASAN SEEDING DATA DEMO")
        logger.info("="*60)
        logger.info(f"👥 Users demo dibuat: {self.users_created}")
        logger.info(f"💰 Transaksi dibuat: {self.transactions_created}")
        logger.info(f"🎯 Target tabungan dibuat: {self.savings_targets_created}")
        logger.info("="*60)
        
        # Tampilkan beberapa contoh user
        logger.info("\n👥 CONTOH USERS DEMO:")
        logger.info("-" * 50)
        for i, user in enumerate(self.demo_users[:5], 1):
            logger.info(f"{i}. {user['name']:<25} | {user['email']}")
        
        if len(self.demo_users) > 5:
            logger.info(f"   ... dan {len(self.demo_users) - 5} users lainnya")
        
        logger.info("\n🔐 KREDENSIAL LOGIN DEMO:")
        logger.info("-" * 30)
        logger.info("👑 Admin:")
        logger.info("   Email: admin@lunance.ac.id")
        logger.info("   Password: AdminPassword123!")
        logger.info("\n👤 Student (semua demo users):")
        logger.info("   Password: Password123!")


async def main():
    """Fungsi utama untuk menjalankan seeding."""
    seeder = DemoDataSeeder()
    
    try:
        # Koneksi ke database
        await connect_to_mongo()
        logger.info("🔗 Berhasil terhubung ke MongoDB")
        
        # Load existing data
        if not await seeder.load_existing_data():
            logger.error("❌ Gagal load data yang diperlukan!")
            sys.exit(1)
        
        # Buat admin user
        await seeder.create_admin_user()
        
        # Buat demo users
        success = await seeder.create_demo_users(count=20)
        if not success:
            logger.error("❌ Gagal membuat demo users!")
            sys.exit(1)
        
        # Buat demo transactions
        success = await seeder.create_demo_transactions(transactions_per_user=50)
        if not success:
            logger.error("❌ Gagal membuat demo transactions!")
            sys.exit(1)
        
        # Buat demo savings targets
        success = await seeder.create_demo_savings_targets(targets_per_user=4)
        if not success:
            logger.error("❌ Gagal membuat demo savings targets!")
            sys.exit(1)
        
        # Tampilkan ringkasan
        await seeder.print_summary()
        
        logger.info("\n🎉 Seeding data demo berhasil!")
        logger.info("💡 Tip: Gunakan kredensial di atas untuk login dan testing")
        
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