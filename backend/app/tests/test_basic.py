# app/tests/test_basic.py
import pytest
import sys
import os

# Add parent directories to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

@pytest.mark.asyncio
class TestBasic:
    
    async def test_health_endpoint(self, client):
        """Test health endpoint"""
        response = await client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] == "healthy"
        print("✅ Health endpoint test passed")

    async def test_root_endpoint(self, client):
        """Test root endpoint"""
        response = await client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        print("✅ Root endpoint test passed")

    async def test_database_connection(self, test_db):
        """Test database connection"""
        # Simple database operation
        result = await test_db.test_collection.insert_one({"test": "data"})
        assert result.inserted_id is not None
        
        # Cleanup
        await test_db.test_collection.delete_one({"_id": result.inserted_id})
        print("✅ Database connection test passed")

    async def test_fixtures_creation(self, sample_university, sample_user, sample_admin):
        """Test that fixtures are created properly"""
        assert sample_university is not None
        assert sample_user is not None
        assert sample_admin is not None
        
        assert sample_university["nama_universitas"] == "Universitas Indonesia"
        assert sample_user["email"] == "test@ui.ac.id"
        assert sample_admin["role"] == "admin"
        print("✅ Fixtures creation test passed")

    async def test_login_functionality(self, client, sample_user):
        """Test basic login functionality"""
        response = await client.post("/auth/login", json={
            "email": "test@ui.ac.id",
            "password": "password123"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert "user" in data
        print("✅ Login functionality test passed")