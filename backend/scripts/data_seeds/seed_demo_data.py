# scripts/data_seeds/seed_demo_data_fixed.py
"""
Seeding script yang diperbaiki untuk data demo (users, transactions, savings targets).
Script ini akan membuat 100 user mahasiswa dan 1 admin.
"""

import asyncio
import sys
import os
from datetime import datetime, date, timedelta
import logging
import random
from bson import ObjectId
from faker import Faker
import uuid

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

class DemoDataSeederFixed:
    """Seeder yang diperbaiki untuk data demo."""
    
    def __init__(self):
        self.users_created = 0
        self.transactions_created = 0
        self.savings_targets_created = 0
        self.demo_users = []
        self.categories = []
        self.universities = []
        self.existing_emails = set()
    
    async def check_and_drop_problematic_indexes(self):
        """Cek dan hapus index yang bermasalah."""
        try:
            db = await get_database()
            collection = db.users
            
            # Ambil semua index yang ada
            indexes = await collection.list_indexes().to_list(length=None)
            
            logger.info("🔍 Memeriksa index yang ada...")
            
            for index in indexes:
                index_name = index.get('name', '')
                index_key = index.get('key', {})
                
                logger.info(f"   Index: {index_name} - Keys: {index_key}")
                
                # Hapus index username jika ada (karena tidak diperlukan)
                if 'username' in index_key and index_name != '_id_':
                    logger.warning(f"⚠️ Menghapus index yang bermasalah: {index_name}")
                    try:
                        await collection.drop_index(index_name)
                        logger.info(f"✅ Index {index_name} berhasil dihapus")
                    except Exception as e:
                        logger.warning(f"⚠️ Gagal menghapus index {index_name}: {e}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error checking indexes: {e}")
            return False
    
    async def load_existing_emails(self):
        """Load email yang sudah ada untuk menghindari duplikasi."""
        try:
            db = await get_database()
            collection = db.users
            
            # Ambil semua email yang sudah ada
            cursor = collection.find({}, {"email": 1})
            users = await cursor.to_list(length=None)
            
            self.existing_emails = {user.get("email") for user in users if user.get("email")}
            logger.info(f"📧 Loaded {len(self.existing_emails)} existing emails")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error loading existing emails: {e}")
            return False
    
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
    
    def _generate_unique_email(self, name, attempt=0):
        """Generate email akademik yang unik."""
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
        base_username = name.lower().replace(" ", ".")
        
        # Tambahkan suffix jika email sudah ada
        if attempt > 0:
            username = f"{base_username}.{attempt}"
        else:
            username = base_username
        
        email = f"{username}@{domain}"
        
        # Cek apakah email sudah ada
        if email in self.existing_emails:
            if attempt < 100:  # Maksimal 100 attempt
                return self._generate_unique_email(name, attempt + 1)
            else:
                # Jika masih duplikasi, gunakan UUID
                unique_id = str(uuid.uuid4())[:8]
                email = f"{base_username}.{unique_id}@{domain}"
        
        return email
    
    async def create_admin_user(self):
        """Buat user admin untuk testing."""
        try:
            db = await get_database()
            collection = db.users
            
            admin_email = "admin@lunance.ac.id"
            
            # Cek apakah admin sudah ada
            existing_admin = await collection.find_one({"email": admin_email})
            if existing_admin:
                logger.info("✅ Admin user sudah ada, dilewati")
                return True
            
            # Clean data untuk admin - pastikan tidak ada field yang None/undefined
            admin_data = {
                "email": admin_email,
                "full_name": "Admin Lunance",
                "phone_number": "6281234567890",
                "role": UserRole.ADMIN.value,
                "initial_savings": 0.0,
                "password_hash": hash_password("AdminPassword123!"),
                "is_active": True,
                "is_verified": True,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            
            # Hanya tambahkan field university jika tidak None
            if hasattr(UserInDB.model_fields, 'university_id'):
                admin_data["university_id"] = None
                admin_data["faculty_id"] = None  
                admin_data["major_id"] = None
            
            result = await collection.insert_one(admin_data)
            
            logger.info(f"✨ Admin user berhasil dibuat dengan ID: {result.inserted_id}")
            logger.info("   📧 Email: admin@lunance.ac.id")
            logger.info("   🔐 Password: AdminPassword123!")
            
            # Tambahkan email admin ke set existing emails
            self.existing_emails.add(admin_email)
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error creating admin user: {e}")
            return False
    
    async def create_demo_users(self, count=100):
        """Buat 100 users mahasiswa demo."""
        try:
            db = await get_database()
            collection = db.users
            
            logger.info(f"👥 Membuat {count} users mahasiswa demo...")
            
            # Batch processing untuk performa lebih baik
            batch_size = 10
            batch_count = 0
            
            for i in range(count):
                try:
                    name = fake.name()
                    email = self._generate_unique_email(name)
                    
                    # Skip jika email masih duplikasi
                    if email in self.existing_emails:
                        logger.warning(f"⚠️ Email {email} masih duplikasi, skip...")
                        continue
                    
                    university_id, faculty_id, major_id = self._get_random_university_data()
                    
                    # Generate phone number Indonesia yang unik
                    phone = f"628{random.randint(10000000, 99999999)}"
                    
                    # Initial savings antara 500rb - 10jt
                    initial_savings = random.uniform(500000, 10000000)
                    
                    # Clean data untuk user - pastikan tidak ada field yang None kecuali yang memang boleh None
                    user_data = {
                        "email": email,
                        "full_name": name,
                        "phone_number": phone,
                        "university_id": university_id,
                        "faculty_id": faculty_id,
                        "major_id": major_id,
                        "role": UserRole.STUDENT.value,
                        "initial_savings": round(initial_savings, 2),
                        "password_hash": hash_password("Password123!"),
                        "is_active": True,
                        "is_verified": random.choice([True, True, True, False]),  # 75% verified
                        "created_at": datetime.utcnow() - timedelta(days=random.randint(1, 365)),
                        "updated_at": datetime.utcnow()
                    }
                    
                    result = await collection.insert_one(user_data)
                    
                    # Tambahkan ke existing emails dan demo users
                    self.existing_emails.add(email)
                    self.demo_users.append({
                        "id": str(result.inserted_id),
                        "email": email,
                        "name": name,
                        "initial_savings": initial_savings
                    })
                    
                    self.users_created += 1
                    batch_count += 1
                    
                    # Log progress setiap batch
                    if batch_count >= batch_size:
                        logger.info(f"   ✨ Created {self.users_created}/{count} users")
                        batch_count = 0
                    
                except Exception as insert_error:
                    logger.warning(f"⚠️ Gagal insert user {i+1}: {insert_error}")
                    continue
            
            logger.info(f"✅ Berhasil membuat {self.users_created} users mahasiswa demo")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error creating demo users: {e}")
            return False
    
    async def create_demo_transactions(self, transactions_per_user=50):
        """Buat transactions demo untuk setiap user."""
        try:
            db = await get_database()
            collection = db.transactions
            
            logger.info(f"💰 Membuat {transactions_per_user} transaksi per user...")
            
            # Daftar deskripsi transaksi yang realistis
            income_descriptions = [
                "Gaji part-time", "Uang saku bulanan", "Freelance project", 
                "Jualan online", "Les privat", "Beasiswa", "Hadiah ulang tahun",
                "Hasil investasi", "Bonus kerja", "Jual barang bekas"
            ]
            
            expense_descriptions = [
                "Makan siang kampus", "Transportasi online", "Beli buku kuliah",
                "Bayar kos", "Beli pulsa", "Jajan di kantin", "Fotokopi tugas",
                "Beli alat tulis", "Nonton bioskop", "Belanja online",
                "Bayar internet", "Beli kopi", "Makan malam", "Bensin motor",
                "Bayar listrik", "Laundry", "Beli obat", "Potong rambut"
            ]
            
            # Batch insert untuk performa
            batch_size = 100
            transactions_batch = []
            
            for user_idx, user in enumerate(self.demo_users):
                user_id = user["id"]
                
                for _ in range(transactions_per_user):
                    # 25% income, 75% expense
                    transaction_type = TransactionType.INCOME if random.random() < 0.25 else TransactionType.EXPENSE
                    
                    # Pilih kategori yang sesuai
                    if transaction_type == TransactionType.INCOME:
                        # Kategori income
                        income_categories = [c for c in self.categories if c["name"] in ["Salary & Income", "Freelance", "Investment"]]
                        category = random.choice(income_categories) if income_categories else random.choice(self.categories)
                        description = random.choice(income_descriptions)
                        amount = random.uniform(100000, 2000000)  # 100rb - 2jt
                    else:
                        # Kategori expense
                        expense_categories = [c for c in self.categories if c["name"] not in ["Salary & Income", "Freelance", "Investment"]]
                        category = random.choice(expense_categories) if expense_categories else random.choice(self.categories)
                        description = random.choice(expense_descriptions)
                        amount = random.uniform(5000, 500000)  # 5rb - 500rb
                    
                    # Random date dalam 6 bulan terakhir
                    days_ago = random.randint(1, 180)
                    transaction_date = date.today() - timedelta(days=days_ago)
                    
                    transaction_data = {
                        "user_id": user_id,
                        "category_id": str(category["_id"]),
                        "transaction_type": transaction_type.value,
                        "amount": round(amount, 2),
                        "description": description,
                        "transaction_date": transaction_date,
                        "created_at": datetime.utcnow() - timedelta(days=days_ago),
                        "updated_at": datetime.utcnow() - timedelta(days=days_ago)
                    }
                    
                    transactions_batch.append(transaction_data)
                    
                    # Insert batch ketika mencapai batch_size
                    if len(transactions_batch) >= batch_size:
                        await collection.insert_many(transactions_batch)
                        self.transactions_created += len(transactions_batch)
                        transactions_batch = []
                
                # Log progress
                if (user_idx + 1) % 10 == 0:
                    logger.info(f"   ✨ Created transactions for {user_idx + 1}/{len(self.demo_users)} users")
            
            # Insert sisa batch
            if transactions_batch:
                await collection.insert_many(transactions_batch)
                self.transactions_created += len(transactions_batch)
            
            logger.info(f"✅ Berhasil membuat {self.transactions_created} transaksi demo")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error creating demo transactions: {e}")
            return False
    
    async def create_demo_savings_targets(self, targets_per_user=4):
        """Buat savings targets demo untuk setiap user."""
        try:
            db = await get_database()
            collection = db.savings_targets
            
            logger.info(f"🎯 Membuat {targets_per_user} target tabungan per user...")
            
            target_names = [
                "Laptop baru", "Liburan akhir tahun", "Emergency fund", 
                "Motor baru", "Kamera DSLR", "iPhone baru", "Dana skripsi",
                "Uang semester", "Modal usaha", "Gadget gaming", "Travelling Eropa",
                "Wedding fund", "Investasi emas", "Dana tugas akhir", "Tablet untuk kuliah",
                "Sepatu sneakers", "Headphone premium", "Smartwatch", "Dana magang"
            ]
            
            # Batch insert untuk performa
            batch_size = 50
            targets_batch = []
            
            for user_idx, user in enumerate(self.demo_users):
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
                    
                    # 15% chance sudah achieved
                    is_achieved = random.random() < 0.15
                    if is_achieved:
                        current_amount = target_amount
                    
                    target_data = {
                        "user_id": user_id,
                        "target_name": target_name,
                        "target_amount": round(target_amount, 2),
                        "current_amount": round(current_amount, 2),
                        "target_date": target_date,
                        "is_achieved": is_achieved,
                        "created_at": datetime.utcnow() - timedelta(days=random.randint(1, 100)),
                        "updated_at": datetime.utcnow()
                    }
                    
                    targets_batch.append(target_data)
                    
                    # Insert batch ketika mencapai batch_size
                    if len(targets_batch) >= batch_size:
                        await collection.insert_many(targets_batch)
                        self.savings_targets_created += len(targets_batch)
                        targets_batch = []
            
            # Insert sisa batch
            if targets_batch:
                await collection.insert_many(targets_batch)
                self.savings_targets_created += len(targets_batch)
            
            logger.info(f"✅ Berhasil membuat {self.savings_targets_created} target tabungan demo")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error creating demo savings targets: {e}")
            return False
    
    async def print_summary(self):
        """Cetak ringkasan hasil seeding."""
        logger.info("\n" + "="*60)
        logger.info("📊 RINGKASAN SEEDING DATA DEMO")
        logger.info("="*60)
        logger.info(f"👑 Admin user dibuat: 1")
        logger.info(f"👥 Users mahasiswa dibuat: {self.users_created}")
        logger.info(f"💰 Transaksi dibuat: {self.transactions_created}")
        logger.info(f"🎯 Target tabungan dibuat: {self.savings_targets_created}")
        logger.info("="*60)
        
        # Tampilkan beberapa contoh user
        logger.info("\n👥 CONTOH USERS MAHASISWA DEMO:")
        logger.info("-" * 60)
        for i, user in enumerate(self.demo_users[:5], 1):
            logger.info(f"{i}. {user['name']:<25} | {user['email']}")
        
        if len(self.demo_users) > 5:
            logger.info(f"   ... dan {len(self.demo_users) - 5} users lainnya")
        
        logger.info("\n🔐 KREDENSIAL LOGIN DEMO:")
        logger.info("-" * 30)
        logger.info("👑 Admin:")
        logger.info("   Email: admin@lunance.ac.id")
        logger.info("   Password: AdminPassword123!")
        logger.info(f"\n👤 Student (semua {self.users_created} demo users):")
        logger.info("   Password: Password123!")
        
        logger.info("\n💡 STATISTIK TAMBAHAN:")
        logger.info("-" * 30)
        if self.demo_users:
            avg_transactions = self.transactions_created / len(self.demo_users)
            avg_targets = self.savings_targets_created / len(self.demo_users)
            logger.info(f"📊 Rata-rata transaksi per user: {avg_transactions:.1f}")
            logger.info(f"📊 Rata-rata target per user: {avg_targets:.1f}")


async def main():
    """Fungsi utama untuk menjalankan seeding."""
    seeder = DemoDataSeederFixed()
    
    try:
        # Koneksi ke database
        await connect_to_mongo()
        logger.info("🔗 Berhasil terhubung ke MongoDB")
        
        # Cek dan hapus index yang bermasalah
        await seeder.check_and_drop_problematic_indexes()
        
        # Load existing emails untuk menghindari duplikasi
        await seeder.load_existing_emails()
        
        # Load existing data
        if not await seeder.load_existing_data():
            logger.error("❌ Gagal load data yang diperlukan!")
            sys.exit(1)
        
        # Buat admin user
        success = await seeder.create_admin_user()
        if not success:
            logger.error("❌ Gagal membuat admin user!")
            sys.exit(1)
        
        # Buat 100 demo users mahasiswa
        success = await seeder.create_demo_users(count=100)
        if not success:
            logger.error("❌ Gagal membuat demo users!")
            sys.exit(1)
        
        # Hanya buat transaksi dan target jika berhasil buat users
        if seeder.users_created > 0:
            # Buat demo transactions
            success = await seeder.create_demo_transactions(transactions_per_user=50)
            if not success:
                logger.warning("⚠️ Gagal membuat demo transactions, tapi users sudah berhasil dibuat")
            
            # Buat demo savings targets
            success = await seeder.create_demo_savings_targets(targets_per_user=4)
            if not success:
                logger.warning("⚠️ Gagal membuat demo savings targets, tapi users sudah berhasil dibuat")
        
        # Tampilkan ringkasan
        await seeder.print_summary()
        
        logger.info("\n🎉 Seeding data demo berhasil!")
        logger.info("💡 Tip: Gunakan kredensial di atas untuk login dan testing")
        
    except KeyboardInterrupt:
        logger.info("\n⚠️ Proses dihentikan oleh user")
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