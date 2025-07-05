from datetime import datetime, timedelta
from typing import List
import random
from faker import Faker
from passlib.context import CryptContext

fake = Faker('id_ID')  # Indonesian locale
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    """Generate password hash"""
    return pwd_context.hash(password)

def random_date_between(start_date: datetime, end_date: datetime) -> datetime:
    """Generate random date between two dates"""
    time_between = end_date - start_date
    days_between = time_between.days
    random_days = random.randrange(days_between)
    return start_date + timedelta(days=random_days)

def generate_nim() -> str:
    """Generate student ID number"""
    year = random.choice(['20', '21', '22', '23'])
    faculty_code = random.choice(['01', '02', '03', '04', '05'])
    program_code = random.choice(['001', '002', '003', '004', '005'])
    sequence = str(random.randint(1, 999)).zfill(3)
    return f"{year}{faculty_code}{program_code}{sequence}"

def generate_phone_number() -> str:
    """Generate Indonesian phone number"""
    prefix = random.choice(['0812', '0813', '0821', '0822', '0823', '0851', '0852', '0853'])
    suffix = ''.join([str(random.randint(0, 9)) for _ in range(8)])
    return f"{prefix}{suffix}"

def generate_academic_email(name: str, university_domain: str) -> str:
    """Generate academic email"""
    name_parts = name.lower().split()
    if len(name_parts) >= 2:
        username = f"{name_parts[0]}.{name_parts[1]}"
    else:
        username = name_parts[0]
    
    # Remove spaces and special characters
    username = ''.join(char for char in username if char.isalnum() or char == '.')
    
    return f"{username}@{university_domain}"

INDONESIAN_UNIVERSITIES = [
    {
        "nama": "Universitas Indonesia",
        "domain": "ui.ac.id",
        "fakultas": ["FMIPA", "Teknik", "Ekonomi", "Hukum", "Kedokteran", "FIB", "Psikologi", "FKM", "Vokasi"],
        "region": "Jakarta"
    },
    {
        "nama": "Institut Teknologi Bandung",
        "domain": "itb.ac.id", 
        "fakultas": ["FMIPA", "FITB", "FTI", "FTTM", "FTMD", "FTSL", "FPAR", "FEB"],
        "region": "Bandung"
    },
    {
        "nama": "Universitas Gadjah Mada",
        "domain": "ugm.ac.id",
        "fakultas": ["FMIPA", "Teknik", "Ekonomika dan Bisnis", "Hukum", "Kedokteran", "FIB", "Psikologi", "Pertanian"],
        "region": "Yogyakarta"
    },
    {
        "nama": "Institut Teknologi Sepuluh Nopember",
        "domain": "its.ac.id",
        "fakultas": ["FMIPA", "FTI", "FTIRS", "FTEIC", "Vokasi", "FEB"],
        "region": "Surabaya"
    },
    {
        "nama": "Universitas Brawijaya",
        "domain": "ub.ac.id",
        "fakultas": ["FMIPA", "Teknik", "Ekonomi dan Bisnis", "Hukum", "Kedokteran", "FIB", "Pertanian", "Peternakan"],
        "region": "Malang"
    },
    {
        "nama": "Universitas Diponegoro",
        "domain": "undip.ac.id",
        "fakultas": ["FMIPA", "Teknik", "Ekonomika dan Bisnis", "Hukum", "Kedokteran", "FIB", "Psikologi", "Perikanan"],
        "region": "Semarang"
    },
    {
        "nama": "Universitas Airlangga",
        "domain": "unair.ac.id",
        "fakultas": ["FMIPA", "Teknik", "Ekonomi dan Bisnis", "Hukum", "Kedokteran", "FIB", "Psikologi", "Kesehatan Masyarakat"],
        "region": "Surabaya"
    },
    {
        "nama": "Universitas Sebelas Maret",
        "domain": "uns.ac.id",
        "fakultas": ["FMIPA", "Teknik", "Ekonomi dan Bisnis", "Hukum", "Kedokteran", "FISIP", "Pertanian", "Seni Rupa"],
        "region": "Solo"
    },
    {
        "nama": "Universitas Padjadjaran",
        "domain": "unpad.ac.id",
        "fakultas": ["FMIPA", "Teknik Geologi", "Ekonomi dan Bisnis", "Hukum", "Kedokteran", "FIB", "Psikologi", "Farmasi"],
        "region": "Bandung"
    },
    {
        "nama": "Universitas Hasanuddin",
        "domain": "unhas.ac.id",
        "fakultas": ["FMIPA", "Teknik", "Ekonomi dan Bisnis", "Hukum", "Kedokteran", "FIB", "Pertanian", "Kelautan"],
        "region": "Makassar"
    }
]

PROGRAM_STUDI = {
    "FMIPA": ["Matematika", "Fisika", "Kimia", "Biologi", "Statistika", "Ilmu Komputer", "Geofisika"],
    "Teknik": ["Informatika", "Elektro", "Mesin", "Sipil", "Kimia", "Industri", "Lingkungan", "Biomedis"],
    "Ekonomi": ["Manajemen", "Akuntansi", "Ekonomi Pembangunan", "Bisnis Digital", "Keuangan"],
    "Ekonomika dan Bisnis": ["Manajemen", "Akuntansi", "Ekonomi Pembangunan", "Bisnis Digital", "Keuangan"],
    "Ekonomi dan Bisnis": ["Manajemen", "Akuntansi", "Ekonomi Pembangunan", "Bisnis Digital", "Keuangan"],
    "Hukum": ["Ilmu Hukum", "Hukum Bisnis", "Hukum Internasional"],
    "Kedokteran": ["Pendidikan Dokter", "Kedokteran Gigi", "Farmasi", "Keperawatan"],
    "FIB": ["Sastra Indonesia", "Sastra Inggris", "Sejarah", "Arkeologi", "Filosofi"],
    "FISIP": ["Ilmu Politik", "Hubungan Internasional", "Sosiologi", "Komunikasi", "Antropologi"],
    "Psikologi": ["Psikologi"],
    "FKM": ["Kesehatan Masyarakat", "Gizi", "Kesehatan Lingkungan"],
    "Kesehatan Masyarakat": ["Kesehatan Masyarakat", "Gizi", "Kesehatan Lingkungan"],
    "Pertanian": ["Agronomi", "Teknologi Pangan", "Peternakan", "Kehutanan"],
    "Peternakan": ["Peternakan", "Teknologi Hasil Ternak"],
    "Vokasi": ["D3 Komputer", "D3 Akuntansi", "D3 Administrasi"],
    "FEB": ["Manajemen Bisnis", "Akuntansi", "Studi Pembangunan"],
    "FITB": ["Teknik Geologi", "Teknik Geodesi", "Meteorologi"],
    "FTI": ["Teknik Kimia", "Teknik Fisika", "Teknik Industri"],
    "FTTM": ["Teknik Pertambangan", "Teknik Metalurgi", "Teknik Perminyakan"],
    "FTMD": ["Teknik Mesin", "Teknik Dirgantara", "Teknik Material"],
    "FTSL": ["Teknik Sipil", "Teknik Lingkungan", "Teknik Kelautan"],
    "FPAR": ["Seni Rupa", "Kriya", "Desain"],
    "FTEIC": ["Teknik Elektro", "Teknik Komputer", "Teknik Biomedis"],
    "FTIRS": ["Teknik Sipil", "Arsitektur", "Teknik Lingkungan"],
    "Perikanan": ["Budidaya Perairan", "Teknologi Hasil Perikanan", "Manajemen Sumberdaya Perairan"],
    "Kelautan": ["Ilmu Kelautan", "Teknik Kelautan", "Teknologi Kelautan"],
    "Farmasi": ["Farmasi", "Farmasi Klinis"],
    "Seni Rupa": ["Seni Murni", "Desain Grafis", "Desain Interior", "Kriya"]
}