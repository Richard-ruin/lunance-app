from fastapi import APIRouter, HTTPException, Query, Depends
from pydantic import BaseModel
from typing import Optional
from app.services.university_service import UniversityService
from app.services.admin_service import AdminService
from app.utils.helpers import create_response
from app.middleware.auth_middleware import get_current_admin_user
from app.models.user import User

router = APIRouter()

# Request Models
class ApproveUserRequest(BaseModel):
    catatan: Optional[str] = ""

class RejectUserRequest(BaseModel):
    catatan: str = ""

class ApproveUniversityRequest(BaseModel):
    catatan: Optional[str] = ""

class RejectUniversityRequest(BaseModel):
    catatan: str = ""

# User Management Routes
@router.get("/pending-users")
async def get_pending_users(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    current_admin: User = Depends(get_current_admin_user)
):
    """Get all users pending approval"""
    try:
        result = AdminService.get_pending_users(page=page, limit=limit)
        
        return create_response(
            data=result,
            message='Berhasil mengambil data user pending'
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Terjadi kesalahan: {str(e)}')

@router.put("/approve-user/{user_id}")
async def approve_user(
    user_id: str, 
    request: ApproveUserRequest,
    current_admin: User = Depends(get_current_admin_user)
):
    """Approve user registration"""
    try:
        result = AdminService.approve_user(
            user_id=user_id,
            admin_id=str(current_admin.id),
            catatan=request.catatan
        )
        
        return create_response(
            data=result,
            message='User berhasil disetujui'
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Terjadi kesalahan: {str(e)}')

@router.put("/reject-user/{user_id}")
async def reject_user(
    user_id: str, 
    request: RejectUserRequest,
    current_admin: User = Depends(get_current_admin_user)
):
    """Reject user registration"""
    try:
        result = AdminService.reject_user(
            user_id=user_id,
            admin_id=str(current_admin.id),
            catatan=request.catatan
        )
        
        return create_response(
            data=result,
            message='User berhasil ditolak'
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Terjadi kesalahan: {str(e)}')

@router.get("/users")
async def get_all_users(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    status: str = Query("", regex=r'^(|pending|approved|rejected)$'),
    search: str = Query(""),
    current_admin: User = Depends(get_current_admin_user)
):
    """Get all users with filtering"""
    try:
        result = AdminService.get_all_users(
            page=page,
            limit=limit,
            status=status,
            search=search
        )
        
        return create_response(
            data=result,
            message='Berhasil mengambil data users'
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Terjadi kesalahan: {str(e)}')

@router.get("/users/{user_id}")
async def get_user_detail(
    user_id: str,
    current_admin: User = Depends(get_current_admin_user)
):
    """Get user detail by ID"""
    try:
        result = AdminService.get_user_detail(user_id)
        if not result:
            raise HTTPException(status_code=404, detail='User tidak ditemukan')
        
        return create_response(
            data=result,
            message='Berhasil mengambil detail user'
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Terjadi kesalahan: {str(e)}')

# University Request Management Routes
@router.get("/university-requests")
async def get_university_requests(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    status: str = Query("", regex=r'^(|pending|approved|rejected)$'),
    current_admin: User = Depends(get_current_admin_user)
):
    """Get all university requests"""
    try:
        result = UniversityService.get_university_requests(
            page=page,
            limit=limit,
            status=status
        )
        
        return create_response(
            data=result,
            message='Berhasil mengambil data permintaan universitas'
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Terjadi kesalahan: {str(e)}')

@router.post("/university-requests/{request_id}/approve")
async def approve_university_request(
    request_id: str, 
    request: ApproveUniversityRequest,
    current_admin: User = Depends(get_current_admin_user)
):
    """Approve university request"""
    try:
        result = UniversityService.approve_university_request(
            request_id=request_id, 
            admin_id=str(current_admin.id),
            catatan=request.catatan
        )
        
        return create_response(
            data=result,
            message='Permintaan universitas berhasil disetujui'
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Terjadi kesalahan: {str(e)}')

@router.post("/university-requests/{request_id}/reject")
async def reject_university_request(
    request_id: str, 
    request: RejectUniversityRequest,
    current_admin: User = Depends(get_current_admin_user)
):
    """Reject university request"""
    try:
        result = UniversityService.reject_university_request(
            request_id=request_id, 
            admin_id=str(current_admin.id), 
            catatan=request.catatan
        )
        
        return create_response(
            data=result,
            message='Permintaan universitas berhasil ditolak'
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Terjadi kesalahan: {str(e)}')

@router.get("/university-requests/{request_id}")
async def get_university_request(
    request_id: str,
    current_admin: User = Depends(get_current_admin_user)
):
    """Get specific university request"""
    try:
        result = UniversityService.get_university_request_by_id(request_id)
        if not result:
            raise HTTPException(status_code=404, detail='Permintaan tidak ditemukan')
        
        return create_response(
            data=result,
            message='Berhasil mengambil data permintaan'
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Terjadi kesalahan: {str(e)}')

# Dashboard Statistics
@router.get("/dashboard/statistics")
async def get_dashboard_statistics(
    current_admin: User = Depends(get_current_admin_user)
):
    """Get admin dashboard statistics"""
    try:
        result = AdminService.get_dashboard_statistics()
        
        return create_response(
            data=result,
            message='Berhasil mengambil statistik dashboard'
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Terjadi kesalahan: {str(e)}')

@router.get("/dashboard/recent-activities")
async def get_recent_activities(
    limit: int = Query(10, ge=1, le=50),
    current_admin: User = Depends(get_current_admin_user)
):
    """Get recent admin activities"""
    try:
        result = AdminService.get_recent_activities(limit=limit)
        
        return create_response(
            data=result,
            message='Berhasil mengambil aktivitas terbaru'
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Terjadi kesalahan: {str(e)}')

# System Management
@router.post("/system/maintenance")
async def toggle_maintenance_mode(
    enabled: bool,
    current_admin: User = Depends(get_current_admin_user)
):
    """Toggle system maintenance mode"""
    try:
        result = AdminService.toggle_maintenance_mode(
            enabled=enabled,
            admin_id=str(current_admin.id)
        )
        
        return create_response(
            data=result,
            message=f'Mode maintenance {"diaktifkan" if enabled else "dinonaktifkan"}'
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Terjadi kesalahan: {str(e)}')