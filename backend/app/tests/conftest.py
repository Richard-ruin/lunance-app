# app/tests/conftest.py
import pytest
import asyncio
import sys
import os
from httpx import AsyncClient
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
from datetime import datetime

# Add parent directory to path untuk import
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from app.main import app
from app.database import get_database
from app.config import settings
from app.auth.password_utils import get_password_hash

# Test database name
TEST_DATABASE_NAME = "lunance_test"

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
async def test_db():
    """Create test database connection"""
    client = AsyncIOMotorClient(settings.mongodb_url)
    db = client[TEST_DATABASE_NAME]
    
    # Override the get_database dependency
    app.dependency_overrides[get_database] = lambda: db
    
    yield db
    
    # Cleanup: Drop test database after each test
    await client.drop_database(TEST_DATABASE_NAME)
    client.close()
    
    # Remove override
    app.dependency_overrides.clear()

@pytest.fixture
async def client():
    """Create test client"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

@pytest.fixture
async def sample_university(test_db):
    """Create sample university for testing"""
    university_data = {
        "_id": ObjectId(),
        "nama_universitas": "Universitas Indonesia",
        "fakultas": ["Fakultas Teknik", "Fakultas Ekonomi"],
        "program_studi": ["Teknik Informatika", "Manajemen"],
        "status": "approved",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    result = await test_db.universities.insert_one(university_data)
    university_data["_id"] = result.inserted_id
    
    return university_data

@pytest.fixture
async def sample_user(test_db, sample_university):
    """Create sample user for testing"""
    user_data = {
        "_id": ObjectId(),
        "email": "test@ui.ac.id",
        "password_hash": get_password_hash("password123"),
        "nama_lengkap": "Test User",
        "nomor_telepon": "081234567890",
        "universitas_id": sample_university["_id"],
        "fakultas": "Fakultas Teknik",
        "prodi": "Teknik Informatika",
        "role": "mahasiswa",
        "is_verified": True,
        "is_active": True,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    result = await test_db.users.insert_one(user_data)
    user_data["_id"] = result.inserted_id
    
    return user_data

@pytest.fixture
async def sample_admin(test_db, sample_university):
    """Create sample admin for testing"""
    admin_data = {
        "_id": ObjectId(),
        "email": "admin@ui.ac.id",
        "password_hash": get_password_hash("admin123"),
        "nama_lengkap": "Test Admin",
        "nomor_telepon": "081234567891",
        "universitas_id": sample_university["_id"],
        "fakultas": "Fakultas Teknik",
        "prodi": "Teknik Informatika",
        "role": "admin",
        "is_verified": True,
        "is_active": True,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    result = await test_db.users.insert_one(admin_data)
    admin_data["_id"] = result.inserted_id
    
    return admin_data

@pytest.fixture
async def user_token(client, sample_user):
    """Get access token for sample user"""
    response = await client.post("/auth/login", json={
        "email": "test@ui.ac.id",
        "password": "password123"
    })
    
    if response.status_code != 200:
        pytest.fail(f"Failed to login user: {response.text}")
    
    data = response.json()
    return data["access_token"]

@pytest.fixture
async def admin_token(client, sample_admin):
    """Get access token for sample admin"""
    response = await client.post("/auth/login", json={
        "email": "admin@ui.ac.id", 
        "password": "admin123"
    })
    
    if response.status_code != 200:
        pytest.fail(f"Failed to login admin: {response.text}")
    
    data = response.json()
    return data["access_token"]