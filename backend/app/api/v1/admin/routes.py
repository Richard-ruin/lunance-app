from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional
from app.services.university_service import UniversityService
from app.utils.helpers import create_response

router = APIRouter()

class ApproveRequest(BaseModel):
    admin_id: str

class RejectRequest(BaseModel):
    admin_id: str
    catatan: str = ""

@router.get("/university-requests")
async def get_university_requests(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    status: str = Query("")
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
async def approve_university_request(request_id: str, approve_data: ApproveRequest):
    """Approve university request"""
    try:
        result = UniversityService.approve_university_request(
            request_id, 
            approve_data.admin_id
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
async def reject_university_request(request_id: str, reject_data: RejectRequest):
    """Reject university request"""
    try:
        result = UniversityService.reject_university_request(
            request_id, 
            reject_data.admin_id, 
            reject_data.catatan
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
async def get_university_request(request_id: str):
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

@router.get("/statistics")
async def get_admin_statistics():
    """Get admin dashboard statistics"""
    try:
        result = UniversityService.get_admin_statistics()
        
        return create_response(
            data=result,
            message='Berhasil mengambil statistik admin'
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Terjadi kesalahan: {str(e)}')