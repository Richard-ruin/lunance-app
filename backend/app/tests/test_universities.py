# app/tests/test_universities.py
import pytest
from httpx import AsyncClient
from bson import ObjectId

@pytest.mark.asyncio
class TestUniversities:
    
    async def test_list_universities(self, client: AsyncClient, sample_university):
        """Test list universities endpoint"""
        response = await client.get("/universities/")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        assert data[0]["nama_universitas"] == "Universitas Indonesia"

    async def test_search_universities(self, client: AsyncClient, sample_university):
        """Test search universities"""
        response = await client.get("/universities/?search=Indonesia")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1

    async def test_request_new_university(self, client: AsyncClient, user_token, test_db):
        """Test request new university"""
        headers = {"Authorization": f"Bearer {user_token}"}
        request_data = {
            "nama_universitas": "Universitas Baru",
            "fakultas": "Fakultas Baru",
            "program_studi": "Program Studi Baru"
        }
        
        response = await client.post("/universities/request", 
                                   json=request_data, 
                                   headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert data["nama_universitas"] == request_data["nama_universitas"]
        assert data["status"] == "pending"

    async def test_request_existing_university(self, client: AsyncClient, user_token, sample_university):
        """Test request existing university (should fail)"""
        headers = {"Authorization": f"Bearer {user_token}"}
        request_data = {
            "nama_universitas": "Universitas Indonesia",
            "fakultas": "Fakultas Teknik",
            "program_studi": "Teknik Informatika"
        }
        
        response = await client.post("/universities/request", 
                                   json=request_data, 
                                   headers=headers)
        
        assert response.status_code == 400
        data = response.json()
        assert "sudah ada" in data["detail"]

    async def test_list_university_requests_admin(self, client: AsyncClient, admin_token, test_db, sample_user):
        """Test list university requests (admin only)"""
        # Create a sample request first
        request_data = {
            "_id": ObjectId(),
            "user_id": sample_user["_id"],
            "nama_universitas": "Test University Request",
            "fakultas": "Test Faculty",
            "program_studi": "Test Program",
            "status": "pending",
            "admin_notes": "",
            "created_at": sample_user["created_at"],
            "updated_at": sample_user["updated_at"]
        }
        await test_db.university_requests.insert_one(request_data)
        
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = await client.get("/universities/admin/requests", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1

    async def test_approve_university_request(self, client: AsyncClient, admin_token, test_db, sample_user):
        """Test approve university request"""
        # Create a sample request first
        request_data = {
            "_id": ObjectId(),
            "user_id": sample_user["_id"],
            "nama_universitas": "Test University Approve",
            "fakultas": "Test Faculty",
            "program_studi": "Test Program",
            "status": "pending",
            "admin_notes": "",
            "created_at": sample_user["created_at"],
            "updated_at": sample_user["updated_at"]
        }
        result = await test_db.university_requests.insert_one(request_data)
        request_id = str(result.inserted_id)
        
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = await client.put(f"/universities/admin/requests/{request_id}/approve",
                                  params={"admin_notes": "Approved for testing"},
                                  headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "disetujui" in data["message"]
        
        # Check if university was created
        university = await test_db.universities.find_one({
            "nama_universitas": "Test University Approve"
        })
        assert university is not None
        assert university["status"] == "approved"

    async def test_reject_university_request(self, client: AsyncClient, admin_token, test_db, sample_user):
        """Test reject university request"""
        # Create a sample request first
        request_data = {
            "_id": ObjectId(),
            "user_id": sample_user["_id"],
            "nama_universitas": "Test University Reject",
            "fakultas": "Test Faculty",
            "program_studi": "Test Program",
            "status": "pending",
            "admin_notes": "",
            "created_at": sample_user["created_at"],
            "updated_at": sample_user["updated_at"]
        }
        result = await test_db.university_requests.insert_one(request_data)
        request_id = str(result.inserted_id)
        
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = await client.put(f"/universities/admin/requests/{request_id}/reject",
                                  params={"admin_notes": "Invalid data"},
                                  headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "ditolak" in data["message"]

    async def test_create_university_directly_admin(self, client: AsyncClient, admin_token):
        """Test create university directly (admin)"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        university_data = {
            "nama_universitas": "Direct University",
            "fakultas": ["Fakultas A", "Fakultas B"],
            "program_studi": ["Program A", "Program B"]
        }
        
        response = await client.post("/universities/admin", 
                                   json=university_data, 
                                   headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["nama_universitas"] == university_data["nama_universitas"]
        assert data["status"] == "approved"

    async def test_unauthorized_admin_access(self, client: AsyncClient, user_token):
        """Test unauthorized access to admin endpoints"""
        headers = {"Authorization": f"Bearer {user_token}"}
        
        response = await client.get("/universities/admin/requests", headers=headers)
        
        assert response.status_code == 403
        data = response.json()
        assert "detail" in data