# app/routers/universities.py (updated dengan email service yang benar)
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.security import HTTPBearer
from typing import List, Optional
from bson import ObjectId
from datetime import datetime

from ..database import get_database
from ..models.university import University, UniversityResponse, UniversityCreate
from ..models.university_request import (
    UniversityRequest, UniversityRequestCreate, 
    UniversityRequestResponse, UniversityRequestUpdate
)
from ..middleware.auth_middleware import get_current_user, get_current_admin_user
from ..utils.exceptions import CustomHTTPException
from ..utils.email_service import email_service  # Import yang benar

router = APIRouter(prefix="/universities", tags=["Universities"])
security = HTTPBearer()

@router.get("/", response_model=List[UniversityResponse])
async def list_universities(
    search: Optional[str] = Query(None),
    db = Depends(get_database)
):
    """List all approved universities"""
    try:
        # Build filter query
        filter_query = {"status": "approved"}
        
        if search:
            filter_query["nama_universitas"] = {"$regex": search, "$options": "i"}
        
        universities = await db.universities.find(filter_query).to_list(length=None)
        
        return [UniversityResponse(**uni) for uni in universities]
        
    except Exception as e:
        raise CustomHTTPException(
            status_code=500,
            detail=f"Gagal mengambil data universitas: {str(e)}"
        )

@router.post("/request", response_model=UniversityRequestResponse)
async def request_new_university(
    request_data: UniversityRequestCreate,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """Request new university (mahasiswa)"""
    try:
        # Check if university already exists or requested
        existing_uni = await db.universities.find_one({
            "nama_universitas": {"$regex": f"^{request_data.nama_universitas}$", "$options": "i"}
        })
        
        if existing_uni:
            raise CustomHTTPException(
                status_code=400,
                detail="Universitas sudah ada dalam sistem"
            )
        
        # Check if user already has pending request for this university
        existing_request = await db.university_requests.find_one({
            "user_id": ObjectId(current_user["id"]),
            "nama_universitas": {"$regex": f"^{request_data.nama_universitas}$", "$options": "i"},
            "status": "pending"
        })
        
        if existing_request:
            raise CustomHTTPException(
                status_code=400,
                detail="Anda sudah memiliki permintaan yang sedang diproses untuk universitas ini"
            )
        
        # Create new university request
        new_request = UniversityRequest(
            user_id=ObjectId(current_user["id"]),
            nama_universitas=request_data.nama_universitas,
            fakultas=request_data.fakultas,
            program_studi=request_data.program_studi
        )
        
        result = await db.university_requests.insert_one(new_request.model_dump())
        
        # Get the created request
        created_request = await db.university_requests.find_one({"_id": result.inserted_id})
        
        return UniversityRequestResponse(**created_request)
        
    except CustomHTTPException:
        raise
    except Exception as e:
        raise CustomHTTPException(
            status_code=500,
            detail=f"Gagal membuat permintaan universitas: {str(e)}"
        )

# Admin endpoints
@router.get("/admin/requests", response_model=List[UniversityRequestResponse])
async def list_university_requests(
    current_admin: dict = Depends(get_current_admin_user),
    status: Optional[str] = Query(None),
    db = Depends(get_database)
):
    """List pending university requests (admin)"""
    try:
        filter_query = {}
        
        if status:
            filter_query["status"] = status
        else:
            filter_query["status"] = "pending"
        
        requests = await db.university_requests.find(filter_query).to_list(length=None)
        
        return [UniversityRequestResponse(**req) for req in requests]
        
    except Exception as e:
        raise CustomHTTPException(
            status_code=500,
            detail=f"Gagal mengambil permintaan universitas: {str(e)}"
        )

@router.put("/admin/requests/{request_id}/approve")
async def approve_university_request(
    request_id: str,
    admin_notes: str = "",
    current_admin: dict = Depends(get_current_admin_user),
    db = Depends(get_database)
):
    """Approve university request"""
    try:
        if not ObjectId.is_valid(request_id):
            raise CustomHTTPException(
                status_code=400,
                detail="ID permintaan tidak valid"
            )
        
        # Get the request
        request_doc = await db.university_requests.find_one({"_id": ObjectId(request_id)})
        if not request_doc:
            raise CustomHTTPException(
                status_code=404,
                detail="Permintaan tidak ditemukan"
            )
        
        if request_doc["status"] != "pending":
            raise CustomHTTPException(
                status_code=400,
                detail="Permintaan sudah diproses sebelumnya"
            )
        
        # Create new university
        new_university = University(
            nama_universitas=request_doc["nama_universitas"],
            fakultas=[request_doc["fakultas"]],
            program_studi=[request_doc["program_studi"]],
            status="approved",
            requested_by=request_doc["user_id"],
            approved_at=datetime.utcnow(),
            approved_by=ObjectId(current_admin["id"])
        )
        
        # Insert university
        await db.universities.insert_one(new_university.model_dump())
        
        # Update request status
        await db.university_requests.update_one(
            {"_id": ObjectId(request_id)},
            {
                "$set": {
                    "status": "approved",
                    "admin_notes": admin_notes,
                    "processed_at": datetime.utcnow(),
                    "processed_by": ObjectId(current_admin["id"]),
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        # Send notification email to user
        user = await db.users.find_one({"_id": request_doc["user_id"]})
        if user:
            subject = "Permintaan Universitas Disetujui - Student Finance"
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <title>Permintaan Universitas Disetujui</title>
                <style>
                    body {{ 
                        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                        background-color: #f4f4f4;
                        margin: 0;
                        padding: 20px;
                    }}
                    .container {{
                        max-width: 600px;
                        margin: 0 auto;
                        background-color: white;
                        border-radius: 10px;
                        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                        overflow: hidden;
                    }}
                    .header {{
                        background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
                        color: white;
                        padding: 30px;
                        text-align: center;
                    }}
                    .content {{
                        padding: 40px 30px;
                    }}
                    .university-info {{
                        background-color: #f8f9fa;
                        border-left: 4px solid #28a745;
                        padding: 20px;
                        margin: 20px 0;
                    }}
                    .footer {{
                        background-color: #f8f9fa;
                        padding: 20px;
                        text-align: center;
                        color: #6c757d;
                        font-size: 14px;
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>✅ Permintaan Disetujui</h1>
                        <p>Student Finance</p>
                    </div>
                    <div class="content">
                        <h2>Halo {user['nama_lengkap']},</h2>
                        
                        <p>Kabar baik! Permintaan Anda untuk menambahkan universitas telah <strong>disetujui</strong> oleh admin.</p>
                        
                        <div class="university-info">
                            <h3>Detail Universitas:</h3>
                            <p><strong>Nama Universitas:</strong> {request_doc['nama_universitas']}</p>
                            <p><strong>Fakultas:</strong> {request_doc['fakultas']}</p>
                            <p><strong>Program Studi:</strong> {request_doc['program_studi']}</p>
                        </div>
                        
                        {f'<p><strong>Catatan Admin:</strong> {admin_notes}</p>' if admin_notes else ''}
                        
                        <p>Anda sekarang dapat menggunakan universitas ini dalam profil Anda. Silakan login kembali untuk melihat perubahan.</p>
                        
                        <p>Terima kasih telah membantu melengkapi database universitas kami!</p>
                    </div>
                    <div class="footer">
                        <p>© 2024 Student Finance App. Semua hak dilindungi.</p>
                        <p>Email ini dikirim secara otomatis, mohon jangan balas.</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            text_content = f"""
            Student Finance - Permintaan Universitas Disetujui
            
            Halo {user['nama_lengkap']},
            
            Kabar baik! Permintaan Anda untuk menambahkan universitas telah disetujui oleh admin.
            
            Detail Universitas:
            - Nama Universitas: {request_doc['nama_universitas']}
            - Fakultas: {request_doc['fakultas']}
            - Program Studi: {request_doc['program_studi']}
            
            {f'Catatan Admin: {admin_notes}' if admin_notes else ''}
            
            Anda sekarang dapat menggunakan universitas ini dalam profil Anda.
            
            Terima kasih telah membantu melengkapi database universitas kami!
            
            © 2024 Student Finance App
            """
            
            # Send email using existing email service
            await email_service.send_email_with_retry(
                to_email=user["email"],
                subject=subject,
                html_content=html_content,
                text_content=text_content
            )
        
        return {
            "message": "Permintaan universitas berhasil disetujui",
            "request_id": request_id,
            "university_name": request_doc["nama_universitas"]
        }
        
    except CustomHTTPException:
        raise
    except Exception as e:
        raise CustomHTTPException(
            status_code=500,
            detail=f"Gagal menyetujui permintaan: {str(e)}"
        )

@router.put("/admin/requests/{request_id}/reject")
async def reject_university_request(
    request_id: str,
    admin_notes: str,
    current_admin: dict = Depends(get_current_admin_user),
    db = Depends(get_database)
):
    """Reject university request"""
    try:
        if not ObjectId.is_valid(request_id):
            raise CustomHTTPException(
                status_code=400,
                detail="ID permintaan tidak valid"
            )
        
        # Get the request
        request_doc = await db.university_requests.find_one({"_id": ObjectId(request_id)})
        if not request_doc:
            raise CustomHTTPException(
                status_code=404,
                detail="Permintaan tidak ditemukan"
            )
        
        if request_doc["status"] != "pending":
            raise CustomHTTPException(
                status_code=400,
                detail="Permintaan sudah diproses sebelumnya"
            )
        
        # Update request status
        await db.university_requests.update_one(
            {"_id": ObjectId(request_id)},
            {
                "$set": {
                    "status": "rejected",
                    "admin_notes": admin_notes,
                    "processed_at": datetime.utcnow(),
                    "processed_by": ObjectId(current_admin["id"]),
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        # Send notification email to user
        user = await db.users.find_one({"_id": request_doc["user_id"]})
        if user:
            subject = "Permintaan Universitas Ditolak - Student Finance"
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <title>Permintaan Universitas Ditolak</title>
                <style>
                    body {{ 
                        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                        background-color: #f4f4f4;
                        margin: 0;
                        padding: 20px;
                    }}
                    .container {{
                        max-width: 600px;
                        margin: 0 auto;
                        background-color: white;
                        border-radius: 10px;
                        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                        overflow: hidden;
                    }}
                    .header {{
                        background: linear-gradient(135deg, #dc3545 0%, #fd7e14 100%);
                        color: white;
                        padding: 30px;
                        text-align: center;
                    }}
                    .content {{
                        padding: 40px 30px;
                    }}
                    .university-info {{
                        background-color: #f8f9fa;
                        border-left: 4px solid #dc3545;
                        padding: 20px;
                        margin: 20px 0;
                    }}
                    .reason-box {{
                        background-color: #fff3cd;
                        border: 1px solid #ffeaa7;
                        border-radius: 5px;
                        padding: 15px;
                        margin: 20px 0;
                        color: #856404;
                    }}
                    .footer {{
                        background-color: #f8f9fa;
                        padding: 20px;
                        text-align: center;
                        color: #6c757d;
                        font-size: 14px;
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>❌ Permintaan Ditolak</h1>
                        <p>Student Finance</p>
                    </div>
                    <div class="content">
                        <h2>Halo {user['nama_lengkap']},</h2>
                        
                        <p>Kami informasikan bahwa permintaan Anda untuk menambahkan universitas telah <strong>ditolak</strong> oleh admin.</p>
                        
                        <div class="university-info">
                            <h3>Detail Permintaan:</h3>
                            <p><strong>Nama Universitas:</strong> {request_doc['nama_universitas']}</p>
                            <p><strong>Fakultas:</strong> {request_doc['fakultas']}</p>
                            <p><strong>Program Studi:</strong> {request_doc['program_studi']}</p>
                        </div>
                        
                        <div class="reason-box">
                            <strong>💬 Alasan Penolakan:</strong><br>
                            {admin_notes if admin_notes else 'Tidak ada catatan tambahan dari admin.'}
                        </div>
                        
                        <p>Anda dapat mengajukan permintaan baru dengan informasi yang lebih lengkap dan akurat. Pastikan data universitas yang Anda masukkan sudah benar dan sesuai dengan standar yang berlaku.</p>
                        
                        <p>Jika Anda memiliki pertanyaan, silakan hubungi tim support kami.</p>
                    </div>
                    <div class="footer">
                        <p>© 2024 Student Finance App. Semua hak dilindungi.</p>
                        <p>Email ini dikirim secara otomatis, mohon jangan balas.</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            text_content = f"""
            Student Finance - Permintaan Universitas Ditolak
            
            Halo {user['nama_lengkap']},
            
            Kami informasikan bahwa permintaan Anda untuk menambahkan universitas telah ditolak oleh admin.
            
            Detail Permintaan:
            - Nama Universitas: {request_doc['nama_universitas']}
            - Fakultas: {request_doc['fakultas']}
            - Program Studi: {request_doc['program_studi']}
            
            Alasan Penolakan: {admin_notes if admin_notes else 'Tidak ada catatan tambahan dari admin.'}
            
            Anda dapat mengajukan permintaan baru dengan informasi yang lebih lengkap dan akurat.
            
            © 2024 Student Finance App
            """
            
            # Send email using existing email service
            await email_service.send_email_with_retry(
                to_email=user["email"],
                subject=subject,
                html_content=html_content,
                text_content=text_content
            )
        
        return {
            "message": "Permintaan universitas berhasil ditolak",
            "request_id": request_id,
            "university_name": request_doc["nama_universitas"]
        }
        
    except CustomHTTPException:
        raise
    except Exception as e:
        raise CustomHTTPException(
            status_code=500,
            detail=f"Gagal menolak permintaan: {str(e)}"
        )

@router.post("/admin", response_model=UniversityResponse)
async def create_university_directly(
    university_data: UniversityCreate,
    current_admin: dict = Depends(get_current_admin_user),
    db = Depends(get_database)
):
    """Create university directly (admin)"""
    try:
        # Check if university already exists
        existing_uni = await db.universities.find_one({
            "nama_universitas": {"$regex": f"^{university_data.nama_universitas}$", "$options": "i"}
        })
        
        if existing_uni:
            raise CustomHTTPException(
                status_code=400,
                detail="Universitas sudah ada dalam sistem"
            )
        
        # Create new university
        new_university = University(
            nama_universitas=university_data.nama_universitas,
            fakultas=university_data.fakultas,
            program_studi=university_data.program_studi,
            status="approved",
            approved_at=datetime.utcnow(),
            approved_by=ObjectId(current_admin["id"])
        )
        
        result = await db.universities.insert_one(new_university.model_dump())
        
        # Get the created university
        created_university = await db.universities.find_one({"_id": result.inserted_id})
        
        return UniversityResponse(**created_university)
        
    except CustomHTTPException:
        raise
    except Exception as e:
        raise CustomHTTPException(
            status_code=500,
            detail=f"Gagal membuat universitas: {str(e)}"
        )

@router.put("/admin/{university_id}", response_model=UniversityResponse)
async def update_university(
    university_id: str,
    university_data: UniversityCreate,
    current_admin: dict = Depends(get_current_admin_user),
    db = Depends(get_database)
):
    """Update university (admin)"""
    try:
        if not ObjectId.is_valid(university_id):
            raise CustomHTTPException(
                status_code=400,
                detail="ID universitas tidak valid"
            )
        
        # Check if university exists
        existing_uni = await db.universities.find_one({"_id": ObjectId(university_id)})
        if not existing_uni:
            raise CustomHTTPException(
                status_code=404,
                detail="Universitas tidak ditemukan"
            )
        
        # Update university
        result = await db.universities.update_one(
            {"_id": ObjectId(university_id)},
            {
                "$set": {
                    "nama_universitas": university_data.nama_universitas,
                    "fakultas": university_data.fakultas,
                    "program_studi": university_data.program_studi,
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        if result.modified_count == 0:
            raise CustomHTTPException(
                status_code=400,
                detail="Gagal memperbarui universitas"
            )
        
        # Get updated university
        updated_university = await db.universities.find_one({"_id": ObjectId(university_id)})
        
        return UniversityResponse(**updated_university)
        
    except CustomHTTPException:
        raise
    except Exception as e:
        raise CustomHTTPException(
            status_code=500,
            detail=f"Gagal memperbarui universitas: {str(e)}"
        )

@router.delete("/admin/{university_id}")
async def delete_university(
    university_id: str,
    current_admin: dict = Depends(get_current_admin_user),
    db = Depends(get_database)
):
    """Delete university (admin)"""
    try:
        if not ObjectId.is_valid(university_id):
            raise CustomHTTPException(
                status_code=400,
                detail="ID universitas tidak valid"
            )
        
        # Check if university exists
        existing_uni = await db.universities.find_one({"_id": ObjectId(university_id)})
        if not existing_uni:
            raise CustomHTTPException(
                status_code=404,
                detail="Universitas tidak ditemukan"
            )
        
        # Check if there are users associated with this university
        users_count = await db.users.count_documents({"universitas_id": ObjectId(university_id)})
        if users_count > 0:
            raise CustomHTTPException(
                status_code=400,
                detail=f"Tidak dapat menghapus universitas yang masih memiliki {users_count} pengguna terdaftar"
            )
        
        # Delete university
        result = await db.universities.delete_one({"_id": ObjectId(university_id)})
        
        if result.deleted_count == 0:
            raise CustomHTTPException(
                status_code=400,
                detail="Gagal menghapus universitas"
            )
        
        return {
            "message": "Universitas berhasil dihapus",
            "university_id": university_id,
            "university_name": existing_uni["nama_universitas"]
        }
        
    except CustomHTTPException:
        raise
    except Exception as e:
        raise CustomHTTPException(
            status_code=500,
            detail=f"Gagal menghapus universitas: {str(e)}"
        )