# app/tests/test_admin_users.py
import pytest
from httpx import AsyncClient
from bson import ObjectId

@pytest.mark.asyncio
class TestAdminUsers:
    
    async def test_list_users(self, client, admin_token, sample_user):
        """Test list users (admin only)"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        response = await client.get("/admin/users/", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✅ Found {len(data)} users")

    async def test_list_users_with_pagination(self, client, admin_token, sample_user):
        """Test list users with pagination"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        response = await client.get("/admin/users/?skip=0&limit=10", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) <= 10
        print(f"✅ Pagination test passed with {len(data)} users")

    async def test_list_users_with_search(self, client, admin_token, sample_user):
        """Test list users with search"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        response = await client.get("/admin/users/?search=Test", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✅ Search test passed with {len(data)} results")

    async def test_get_user_detail(self, client, admin_token, sample_user):
        """Test get user detail"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        user_id = str(sample_user["_id"])
        
        response = await client.get(f"/admin/users/{user_id}", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == sample_user["email"]
        assert data["nama_lengkap"] == sample_user["nama_lengkap"]
        print("✅ User detail test passed")

    async def test_get_user_detail_invalid_id(self, client, admin_token):
        """Test get user detail with invalid ID"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        response = await client.get("/admin/users/invalid_id", headers=headers)
        
        assert response.status_code == 400
        data = response.json()
        assert "tidak valid" in data["detail"]
        print("✅ Invalid ID test passed")

    async def test_update_user_status(self, client, admin_token, sample_user, test_db):
        """Test update user status"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        user_id = str(sample_user["_id"])
        
        response = await client.put(f"/admin/users/{user_id}/status",
                                  params={"is_active": False},
                                  headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert data["is_active"] == False
        
        # Check database
        user = await test_db.users.find_one({"_id": sample_user["_id"]})
        assert user["is_active"] == False
        print("✅ Update user status test passed")

    async def test_soft_delete_user(self, client, admin_token, sample_user, test_db):
        """Test soft delete user"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        user_id = str(sample_user["_id"])
        
        response = await client.delete(f"/admin/users/{user_id}", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "dihapus" in data["message"]
        
        # Check database - user should be deactivated, not deleted
        user = await test_db.users.find_one({"_id": sample_user["_id"]})
        assert user is not None
        assert user["is_active"] == False
        print("✅ Soft delete test passed")

    async def test_get_user_stats(self, client, admin_token, sample_user, sample_admin):
        """Test get user statistics"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        response = await client.get("/admin/users/stats/overview", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "total_users" in data
        assert "active_users" in data
        assert "verified_users" in data
        assert "total_admins" in data
        assert data["total_users"] >= 2  # At least sample_user and sample_admin
        print("✅ User stats test passed")

    async def test_unauthorized_user_access(self, client, user_token):
        """Test unauthorized access to admin endpoints"""
        headers = {"Authorization": f"Bearer {user_token}"}
        
        response = await client.get("/admin/users/", headers=headers)
        
        assert response.status_code == 403
        data = response.json()
        assert "detail" in data
        assert "admin" in data["detail"].lower()
        print("✅ Unauthorized access test passed")