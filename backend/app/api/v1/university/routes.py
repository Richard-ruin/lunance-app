from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from pydantic import BaseModel
from app.services.university_service import UniversityService
from app.utils.validators import validate_email_domain
from app.utils.helpers import create_response, create_error_response

router = APIRouter()

class UniversityRequestCreate(BaseModel):
    nama_university: str
    kode_university: str
    alamat_university: str
    website_university: Optional[str] = None
    nama_pemohon: str
    email: str
    nim: str

@router.get("")
async def get_universities(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    search: str = Query(""),
    status_aktif: Optional[bool] = Query(None)
):
    """Get all universities with optional filtering"""
    try:
        result = UniversityService.get_universities(
            page=page,
            limit=limit,
            search=search,
            status_aktif=status_aktif
        )
        
        return create_response(
            data=result,
            message='Berhasil mengambil data universitas'
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Terjadi kesalahan: {str(e)}')

@router.get("/{university_id}")
async def get_university(university_id: str):
    """Get university by ID"""
    try:
        university = UniversityService.get_university_by_id(university_id)
        if not university:
            raise HTTPException(status_code=404, detail='Universitas tidak ditemukan')
        
        return create_response(
            data=university,
            message='Berhasil mengambil data universitas'
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Terjadi kesalahan: {str(e)}')

@router.get("/{university_id}/fakultas")
async def get_fakultas_by_university(university_id: str):
    """Get all fakultas by university ID"""
    try:
        fakultas_list = UniversityService.get_fakultas_by_university(university_id)
        
        return create_response(
            data=fakultas_list,
            message='Berhasil mengambil data fakultas'
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Terjadi kesalahan: {str(e)}')

@router.get("/fakultas/{fakultas_id}/prodi")
async def get_prodi_by_fakultas(fakultas_id: str):
    """Get all program studi by fakultas ID"""
    try:
        prodi_list = UniversityService.get_prodi_by_fakultas(fakultas_id)
        
        return create_response(
            data=prodi_list,
            message='Berhasil mengambil data program studi'
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Terjadi kesalahan: {str(e)}')

@router.post("/request")
async def create_university_request(request_data: UniversityRequestCreate):
    """Create new university request"""
    try:
        # Validate email domain
        if not validate_email_domain(request_data.email):
            raise HTTPException(status_code=400, detail='Email harus menggunakan domain .ac.id')
        
        # Create university request
        result = UniversityService.create_university_request(request_data.dict())
        
        return create_response(
            data=result,
            message='Permintaan penambahan universitas berhasil dikirim'
        )
        
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Terjadi kesalahan: {str(e)}')

@router.get("/search")
async def search_universities(
    q: str = Query(..., min_length=2),
    limit: int = Query(10, ge=1, le=50)
):
    """Search universities by name or code"""
    try:
        results = UniversityService.search_universities(q, limit)
        
        return create_response(
            data=results,
            message='Berhasil melakukan pencarian universitas'
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Terjadi kesalahan: {str(e)}')