# app/tests/test_auth.py
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
class TestAuth:
    
    async def test_register_success(self, client: AsyncClient, test_db, sample_university):
        """Test successful user registration"""
        user_data = {
            "email": "newuser@ui.ac.id",
            "password": "password123",
            "nama_lengkap": "New User",
            "nomor_telepon": "081234567892",
            "universitas_id": str(sample_university["_id"]),
            "fakultas": "Fakultas Teknik",
            "prodi": "Teknik Informatika"
        }
        
        response = await client.post("/auth/register", json=user_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "email" in data
        assert data["email"] == user_data["email"]
        
        # Check if user was created in database
        user = await test_db.users.find_one({"email": user_data["email"]})
        assert user is not None
        assert user["is_verified"] == False
        assert user["otp_code"] is not None

    async def test_register_invalid_email(self, client: AsyncClient, sample_university):
        """Test registration with invalid email domain"""
        user_data = {
            "email": "invalid@gmail.com",
            "password": "password123",
            "nama_lengkap": "Invalid User",
            "nomor_telepon": "081234567893",
            "universitas_id": str(sample_university["_id"]),
            "fakultas": "Fakultas Teknik",
            "prodi": "Teknik Informatika"
        }
        
        response = await client.post("/auth/register", json=user_data)
        
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "domain kampus" in data["detail"]

    async def test_register_weak_password(self, client: AsyncClient, sample_university):
        """Test registration with weak password"""
        user_data = {
            "email": "weak@ui.ac.id",
            "password": "123",
            "nama_lengkap": "Weak Password User",
            "nomor_telepon": "081234567894",
            "universitas_id": str(sample_university["_id"]),
            "fakultas": "Fakultas Teknik",
            "prodi": "Teknik Informatika"
        }
        
        response = await client.post("/auth/register", json=user_data)
        
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "minimal 8 karakter" in data["detail"]

    async def test_login_success(self, client: AsyncClient, sample_user):
        """Test successful login"""
        login_data = {
            "email": "test@ui.ac.id",
            "password": "password123"
        }
        
        response = await client.post("/auth/login", json=login_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert "user" in data
        assert data["token_type"] == "bearer"

    async def test_login_invalid_credentials(self, client: AsyncClient, sample_user):
        """Test login with invalid credentials"""
        login_data = {
            "email": "test@ui.ac.id",
            "password": "wrongpassword"
        }
        
        response = await client.post("/auth/login", json=login_data)
        
        assert response.status_code == 401
        data = response.json()
        assert "detail" in data

    async def test_get_current_user(self, client: AsyncClient, user_token):
        """Test get current user endpoint"""
        headers = {"Authorization": f"Bearer {user_token}"}
        
        response = await client.get("/auth/me", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "email" in data
        assert "nama_lengkap" in data
        assert "role" in data
        assert data["email"] == "test@ui.ac.id"

    async def test_change_password(self, client: AsyncClient, user_token, test_db):
        """Test change password"""
        headers = {"Authorization": f"Bearer {user_token}"}
        password_data = {
            "current_password": "password123",
            "new_password": "newpassword123"
        }
        
        response = await client.post("/auth/change-password", 
                                   json=password_data, 
                                   headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "berhasil" in data["message"]

    async def test_forgot_password(self, client: AsyncClient, sample_user):
        """Test forgot password"""
        forgot_data = {
            "email": "test@ui.ac.id"
        }
        
        response = await client.post("/auth/forgot-password", json=forgot_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data

    async def test_refresh_token(self, client: AsyncClient, sample_user):
        """Test refresh token"""
        # First login to get refresh token
        login_response = await client.post("/auth/login", json={
            "email": "test@ui.ac.id",
            "password": "password123"
        })
        
        login_data = login_response.json()
        refresh_token = login_data["refresh_token"]
        
        # Use refresh token
        refresh_data = {
            "refresh_token": refresh_token
        }
        
        response = await client.post("/auth/refresh-token", json=refresh_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "token_type" in data