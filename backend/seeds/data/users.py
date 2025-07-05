# seeds/data/users.py (updated)
from datetime import datetime, timedelta
from typing import List, Dict, Any
from bson import ObjectId
from ..utils.helpers import (
    fake, get_password_hash, generate_phone_number, 
    generate_academic_email, random_date_between,
    INDONESIAN_UNIVERSITIES
)
import random

def generate_users_data(university_ids: List[ObjectId], num_users: int = 1000) -> List[Dict[str, Any]]:
    """Generate user seed data"""
    users = []
    
    # Create admin users first
    admin_users = generate_admin_users(university_ids)
    users.extend(admin_users)
    
    # Create regular student users
    student_users = generate_student_users(university_ids, num_users - len(admin_users))
    users.extend(student_users)
    
    print(f"Generated {len(users)} users ({len(admin_users)} admins, {len(student_users)} students)")
    return users

def generate_admin_users(university_ids: List[ObjectId]) -> List[Dict[str, Any]]:
    """Generate admin users"""
    admin_users = []
    
    # Create one admin for each university
    for i, university_id in enumerate(university_ids[:len(INDONESIAN_UNIVERSITIES)]):
        univ_data = INDONESIAN_UNIVERSITIES[i]
        
        admin_user = {
            "email": f"admin@{univ_data['domain']}",
            "password_hash": get_password_hash("AdminPassword123"),
            "nama_lengkap": f"Admin {univ_data['nama']}",
            "nomor_telepon": generate_phone_number(),
            "universitas_id": university_id,
            "fakultas": "Administrasi",
            "prodi": "Sistem Informasi",
            "role": "admin",
            "is_verified": True,
            "otp_code": None,
            "otp_expires": None,
            "is_active": True,
            # Add new fields dengan default values
            "profile_picture": None,
            "tabungan_awal": None,
            "notification_settings": {
                "email_notifications": True,
                "push_notifications": True,
                "weekly_summary": True,
                "goal_reminders": True
            },
            "preferences": {
                "language": "id",
                "currency": "IDR",
                "date_format": "DD/MM/YYYY"
            },
            "created_at": random_date_between(
                datetime.utcnow() - timedelta(days=365),
                datetime.utcnow() - timedelta(days=30)
            ),
            "updated_at": datetime.utcnow()
        }
        admin_users.append(admin_user)
    
    return admin_users

def generate_student_users(university_ids: List[ObjectId], num_students: int) -> List[Dict[str, Any]]:
    """Generate student users"""
    student_users = []
    
    for i in range(num_students):
        # Select random university
        university_index = random.randint(0, len(INDONESIAN_UNIVERSITIES) - 1)
        university_id = university_ids[university_index]
        univ_data = INDONESIAN_UNIVERSITIES[university_index]
        
        # Select random fakultas and prodi
        fakultas = random.choice(univ_data["fakultas"])
        if fakultas in ["FMIPA", "Teknik", "Ekonomi", "Ekonomika dan Bisnis", "Ekonomi dan Bisnis"]:
            # More likely to be in these faculties for student finance app
            prodi_options = ["Informatika", "Sistem Informasi", "Manajemen", "Akuntansi", "Teknik Elektro", 
                           "Matematika", "Statistika", "Ekonomi Pembangunan"]
        else:
            from ..utils.helpers import PROGRAM_STUDI
            prodi_options = PROGRAM_STUDI.get(fakultas, ["Umum"])
        
        prodi = random.choice(prodi_options)
        
        # Generate name
        nama_lengkap = fake.name()
        email = generate_academic_email(nama_lengkap, univ_data["domain"])
        
        # Ensure unique email
        email_counter = 1
        base_email = email
        while any(user["email"] == email for user in student_users):
            name_part = base_email.split("@")[0]
            domain_part = base_email.split("@")[1]
            email = f"{name_part}{email_counter}@{domain_part}"
            email_counter += 1
        
        # Random verification status (80% verified)
        is_verified = random.random() < 0.8
        
        # Random active status (95% active)
        is_active = random.random() < 0.95
        
        # Generate created date (last 2 years)
        created_at = random_date_between(
            datetime.utcnow() - timedelta(days=730),
            datetime.utcnow()
        )
        
        # Random notification settings
        notification_settings = {
            "email_notifications": random.choice([True, False]),
            "push_notifications": random.choice([True, False]),
            "weekly_summary": random.choice([True, False]),
            "goal_reminders": random.choice([True, False])
        }
        
        # Random preferences
        preferences = {
            "language": "id",
            "currency": "IDR",
            "date_format": random.choice(["DD/MM/YYYY", "MM/DD/YYYY", "YYYY-MM-DD"])
        }
        
        # Random initial balance (50% chance of having one)
        tabungan_awal = None
        if random.random() < 0.5:
            tabungan_awal = random.uniform(100000, 5000000)  # Between 100k and 5M IDR
        
        student_user = {
            "email": email,
            "password_hash": get_password_hash("StudentPassword123"),
            "nama_lengkap": nama_lengkap,
            "nomor_telepon": generate_phone_number(),
            "universitas_id": university_id,
            "fakultas": fakultas,
            "prodi": prodi,
            "role": "mahasiswa",
            "is_verified": is_verified,
            "otp_code": None if is_verified else str(fake.random_int(min=100000, max=999999)),
            "otp_expires": None if is_verified else datetime.utcnow() + timedelta(minutes=5),
            "is_active": is_active,
            # Add new fields
            "profile_picture": None,
            "tabungan_awal": tabungan_awal,
            "notification_settings": notification_settings,
            "preferences": preferences,
            "created_at": created_at,
            "updated_at": random_date_between(created_at, datetime.utcnow())
        }
        
        student_users.append(student_user)
    
    return student_users