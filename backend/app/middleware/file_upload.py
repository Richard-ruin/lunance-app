# app/middleware/file_upload.py
from fastapi import HTTPException, UploadFile
from typing import List, Optional
import os
import magic
from pathlib import Path

class FileUploadMiddleware:
    def __init__(
        self,
        max_file_size: int = 2 * 1024 * 1024,  # 2MB
        allowed_extensions: List[str] = None,
        allowed_mime_types: List[str] = None,
        upload_dir: str = "uploads"
    ):
        self.max_file_size = max_file_size
        self.allowed_extensions = allowed_extensions or ['.jpg', '.jpeg', '.png', '.gif']
        self.allowed_mime_types = allowed_mime_types or [
            'image/jpeg', 'image/png', 'image/gif', 'image/jpg'
        ]
        self.upload_dir = upload_dir
        
        # Create upload directory if it doesn't exist
        Path(self.upload_dir).mkdir(parents=True, exist_ok=True)
    
    async def validate_file(self, file: UploadFile) -> bool:
        """Validate uploaded file"""
        # Check file size
        if file.size and file.size > self.max_file_size:
            raise HTTPException(
                status_code=400,
                detail=f"Ukuran file terlalu besar. Maksimal {self.max_file_size // (1024*1024)}MB"
            )
        
        # Check file extension
        file_extension = Path(file.filename).suffix.lower()
        if file_extension not in self.allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"Format file tidak didukung. Gunakan: {', '.join(self.allowed_extensions)}"
            )
        
        # Check MIME type
        if file.content_type not in self.allowed_mime_types:
            raise HTTPException(
                status_code=400,
                detail="Tipe file tidak valid"
            )
        
        return True
    
    async def validate_file_content(self, file_content: bytes) -> bool:
        """Validate file content using python-magic"""
        try:
            mime_type = magic.from_buffer(file_content, mime=True)
            if mime_type not in self.allowed_mime_types:
                raise HTTPException(
                    status_code=400,
                    detail="Konten file tidak valid"
                )
            return True
        except Exception:
            # If magic is not available, skip content validation
            return True

# Global file upload middleware instance
file_upload_middleware = FileUploadMiddleware()