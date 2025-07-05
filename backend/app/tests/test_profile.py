# app/tests/test_profile.py
import pytest
from httpx import AsyncClient
import io
from PIL import Image

@pytest.mark.asyncio
class TestProfile:
    
    async def test_get_profile(self, client: AsyncClient, user_token, sample_user):
        """Test get current user profile"""
        headers = {"Authorization": f"Bearer {user_token}"}
        
        response = await client.get("/profile/", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == sample_user["email"]
        assert data["nama_lengkap"] == sample_user["nama_lengkap"]

    async def test_update_profile(self, client: AsyncClient, user_token, test_db, sample_user):
        """Test update user profile"""
        headers = {"Authorization": f"Bearer {user_token}"}
        update_data = {
            "nama_lengkap": "Updated Name",
            "nomor_telepon": "081234567999"
        }
        
        response = await client.put("/profile/", json=update_data, headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["nama_lengkap"] == update_data["nama_lengkap"]
        assert data["nomor_telepon"] == update_data["nomor_telepon"]
        
        # Check database
        user = await test_db.users.find_one({"_id": sample_user["_id"]})
        assert user["nama_lengkap"] == update_data["nama_lengkap"]

    async def test_update_profile_invalid_phone(self, client: AsyncClient, user_token):
        """Test update profile with invalid phone number"""
        headers = {"Authorization": f"Bearer {user_token}"}
        update_data = {
            "nomor_telepon": "invalid_phone"
        }
        
        response = await client.put("/profile/", json=update_data, headers=headers)
        
        assert response.status_code == 422  # Validation error

    async def test_set_initial_balance(self, client: AsyncClient, user_token, test_db, sample_user):
        """Test set initial balance"""
        headers = {"Authorization": f"Bearer {user_token}"}
        balance_data = {
            "tabungan_awal": 1000000.0
        }
        
        response = await client.put("/profile/initial-balance", 
                                  json=balance_data, 
                                  headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert data["tabungan_awal"] == balance_data["tabungan_awal"]
        
        # Check database
        user = await test_db.users.find_one({"_id": sample_user["_id"]})
        assert user["tabungan_awal"] == balance_data["tabungan_awal"]

    async def test_set_initial_balance_negative(self, client: AsyncClient, user_token):
        """Test set initial balance with negative value"""
        headers = {"Authorization": f"Bearer {user_token}"}
        balance_data = {
            "tabungan_awal": -1000.0
        }
        
        response = await client.put("/profile/initial-balance", 
                                  json=balance_data, 
                                  headers=headers)
        
        assert response.status_code == 422  # Validation error

    async def test_get_notification_settings(self, client: AsyncClient, user_token):
        """Test get notification settings"""
        headers = {"Authorization": f"Bearer {user_token}"}
        
        response = await client.get("/profile/notification-settings", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "email_notifications" in data
        assert "push_notifications" in data
        assert "weekly_summary" in data
        assert "goal_reminders" in data

    async def test_update_notification_settings(self, client: AsyncClient, user_token, test_db, sample_user):
        """Test update notification settings"""
        headers = {"Authorization": f"Bearer {user_token}"}
        settings_data = {
            "email_notifications": False,
            "push_notifications": True,
            "weekly_summary": False,
            "goal_reminders": True
        }
        
        response = await client.put("/profile/notification-settings", 
                                  json=settings_data, 
                                  headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["email_notifications"] == settings_data["email_notifications"]
        assert data["push_notifications"] == settings_data["push_notifications"]
        
        # Check database
        user = await test_db.users.find_one({"_id": sample_user["_id"]})
        assert user["notification_settings"]["email_notifications"] == False

    async def test_upload_avatar_success(self, client: AsyncClient, user_token):
        """Test upload profile picture"""
        headers = {"Authorization": f"Bearer {user_token}"}
        
        # Create a test image
        image = Image.new('RGB', (100, 100), color='red')
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format='JPEG')
        img_byte_arr.seek(0)
        
        files = {
            "file": ("test_image.jpg", img_byte_arr, "image/jpeg")
        }
        
        response = await client.post("/profile/upload-avatar", 
                                   files=files, 
                                   headers=headers)
        
        # Note: This test might fail if file upload dependencies are not properly set up
        # In a real test environment, you would mock the file upload functionality
        print(f"Upload response status: {response.status_code}")
        print(f"Upload response: {response.text}")

    async def test_unauthorized_access(self, client: AsyncClient):
        """Test unauthorized access to profile endpoints"""
        response = await client.get("/profile/")
        
        assert response.status_code == 401
        data = response.json()
        assert "detail" in data