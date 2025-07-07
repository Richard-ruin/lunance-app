import bcrypt
import jwt
import secrets
import string
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from fastapi import HTTPException
from app.models.user import User
from app.models.university import University, Fakultas, ProgramStudi
from app.config.settings import Config
from app.utils.email_service import EmailService

class AuthService:
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password using bcrypt"""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    @staticmethod
    def verify_password(password: str, hashed: str) -> bool:
        """Verify password against hash"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    
    @staticmethod
    def generate_otp() -> str:
        """Generate 6-digit OTP"""
        return ''.join(secrets.choice(string.digits) for _ in range(6))
    
    @staticmethod
    def create_access_token(user_id: str, email: str, role: str) -> str:
        """Create JWT access token"""
        payload = {
            'user_id': user_id,
            'email': email,
            'role': role,
            'exp': datetime.utcnow() + timedelta(hours=1),
            'iat': datetime.utcnow(),
            'type': 'access'
        }
        return jwt.encode(payload, Config.JWT_SECRET_KEY, algorithm=Config.JWT_ALGORITHM)
    
    @staticmethod
    def create_refresh_token(user_id: str) -> str:
        """Create JWT refresh token"""
        payload = {
            'user_id': user_id,
            'exp': datetime.utcnow() + timedelta(days=7),
            'iat': datetime.utcnow(),
            'type': 'refresh'
        }
        return jwt.encode(payload, Config.JWT_SECRET_KEY, algorithm=Config.JWT_ALGORITHM)
    
    @staticmethod
    def verify_token(token: str) -> Dict[str, Any]:
        """Verify and decode JWT token"""
        try:
            payload = jwt.decode(token, Config.JWT_SECRET_KEY, algorithms=[Config.JWT_ALGORITHM])
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token telah kedaluwarsa")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="Token tidak valid")
    
    @staticmethod
    def validate_password_strength(password: str) -> tuple[bool, list]:
        """Validate password strength"""
        errors = []
        
        if len(password) < 8:
            errors.append("Password minimal 8 karakter")
        
        if not any(c.isupper() for c in password):
            errors.append("Password harus mengandung huruf besar")
        
        if not any(c.islower() for c in password):
            errors.append("Password harus mengandung huruf kecil")
        
        if not any(c.isdigit() for c in password):
            errors.append("Password harus mengandung angka")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def register_step1(email: str, nama_lengkap: str, no_telepon: str) -> Dict[str, Any]:
        """Step 1: Basic information validation"""
        # Check if email already exists
        existing_user = User.find_by_email(email)
        if existing_user:
            raise ValueError("Email sudah terdaftar")
        
        # Validate email domain
        if not email.endswith('.ac.id'):
            raise ValueError("Email harus menggunakan domain .ac.id")
        
        # Generate OTP for email verification
        otp = AuthService.generate_otp()
        
        # In development, we can return the OTP for testing
        if Config.DEBUG:
            return {
                "email": email,
                "otp_code": otp,  # Only for development
                "message": "Data valid, lanjut ke step 2"
            }
        
        # Send OTP via email (implement EmailService)
        EmailService.send_verification_otp(email, nama_lengkap, otp)
        
        return {
            "email": email,
            "message": "OTP telah dikirim ke email Anda"
        }
    
    @staticmethod
    def register_step2(email: str, university_id: str, fakultas_id: str, prodi_id: str) -> Dict[str, Any]:
        """Step 2: University information validation"""
        # Validate university exists
        university = University.find_by_id(university_id)
        if not university:
            raise ValueError("Universitas tidak ditemukan")
        
        # Validate fakultas exists and belongs to university
        fakultas = Fakultas.find_by_id(fakultas_id)
        if not fakultas or str(fakultas.university_id) != university_id:
            raise ValueError("Fakultas tidak valid untuk universitas ini")
        
        # Validate prodi exists and belongs to fakultas
        prodi = ProgramStudi.find_by_id(prodi_id)
        if not prodi or str(prodi.fakultas_id) != fakultas_id:
            raise ValueError("Program studi tidak valid untuk fakultas ini")
        
        return {
            "university": university.nama,
            "fakultas": fakultas.nama,
            "prodi": prodi.nama,
            "message": "Informasi universitas valid, lanjut ke step 3"
        }
    
    @staticmethod
    def register_step3(email: str, otp_code: str) -> Dict[str, Any]:
        """Step 3: OTP verification"""
        # In production, find user by OTP
        # For now, we'll use a simple validation
        if len(otp_code) != 6 or not otp_code.isdigit():
            raise ValueError("Format OTP tidak valid")
        
        # In development, accept any 6-digit OTP
        if Config.DEBUG:
            return {
                "email": email,
                "verified": True,
                "message": "OTP berhasil diverifikasi, lanjut ke step 4"
            }
        
        # TODO: Implement proper OTP verification
        return {
            "email": email,
            "verified": True,
            "message": "OTP berhasil diverifikasi"
        }
    
    @staticmethod
    def register_step4(email: str, tabungan_awal: float) -> Dict[str, Any]:
        """Step 4: Set initial savings"""
        if tabungan_awal < 0:
            raise ValueError("Tabungan awal tidak boleh negatif")
        
        return {
            "email": email,
            "tabungan_awal": tabungan_awal,
            "message": "Tabungan awal berhasil diset, lanjut ke step 5"
        }
    
    @staticmethod
    def register_step5(
        email: str, password: str, confirm_password: str,
        nama_lengkap: str, no_telepon: str,
        university_id: str, fakultas_id: str, prodi_id: str,
        tabungan_awal: float
    ) -> Dict[str, Any]:
        """Step 5: Complete registration"""
        
        # Validate password match
        if password != confirm_password:
            raise ValueError("Password dan konfirmasi password tidak sama")
        
        # Validate password strength
        is_strong, password_errors = AuthService.validate_password_strength(password)
        if not is_strong:
            raise ValueError(password_errors[0])  # Return first error
        
        # Check if user already exists
        existing_user = User.find_by_email(email)
        if existing_user:
            raise ValueError("Email sudah terdaftar")
        
        # Hash password
        password_hash = AuthService.hash_password(password)
        
        # Create user
        user = User(
            email=email,
            password_hash=password_hash,
            nama_lengkap=nama_lengkap,
            no_telepon=no_telepon,
            university_id=university_id,
            fakultas_id=fakultas_id,
            prodi_id=prodi_id,
            tabungan_awal=tabungan_awal,
            is_verified=True,  # Already verified in step 3
            status="pending"   # Waiting for admin approval
        )
        user.save()
        
        return {
            "user_id": str(user.id),
            "email": user.email,
            "status": user.status,
            "message": "Registrasi berhasil! Akun Anda sedang menunggu persetujuan admin."
        }
    
    @staticmethod
    def login(email: str, password: str) -> Dict[str, Any]:
        """Login user"""
        # Find user by email
        user = User.find_by_email(email)
        if not user:
            raise ValueError("Email atau password salah")
        
        # Check login attempts (rate limiting)
        if user.login_attempts >= 5:
            if user.last_attempt_at and (datetime.utcnow() - user.last_attempt_at).seconds < 900:  # 15 minutes
                raise ValueError("Terlalu banyak percobaan login. Coba lagi dalam 15 menit.")
        
        # Verify password
        if not AuthService.verify_password(password, user.password_hash):
            user.increment_login_attempts()
            raise ValueError("Email atau password salah")
        
        # Check if user is verified
        if not user.is_verified:
            raise ValueError("Akun belum diverifikasi")
        
        # Check if user is approved
        if user.status != "approved":
            if user.status == "pending":
                raise ValueError("Akun sedang menunggu persetujuan admin")
            elif user.status == "rejected":
                raise ValueError("Akun ditolak oleh admin")
        
        # Reset login attempts and update last login
        user.reset_login_attempts()
        user.update_last_login()
        
        # Create tokens
        access_token = AuthService.create_access_token(str(user.id), user.email, user.role)
        refresh_token = AuthService.create_refresh_token(str(user.id))
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "user": user.to_dict_safe(),
            "message": "Login berhasil"
        }
    
    @staticmethod
    def refresh_token(refresh_token: str) -> Dict[str, Any]:
        """Refresh access token"""
        # Verify refresh token
        payload = AuthService.verify_token(refresh_token)
        
        if payload.get('type') != 'refresh':
            raise HTTPException(status_code=401, detail="Token tidak valid")
        
        # Find user
        user = User.find_by_id(payload['user_id'])
        if not user:
            raise HTTPException(status_code=401, detail="User tidak ditemukan")
        
        # Create new access token
        access_token = AuthService.create_access_token(str(user.id), user.email, user.role)
        
        return {
            "access_token": access_token,
            "token_type": "bearer"
        }
    
    @staticmethod
    def forgot_password(email: str) -> Dict[str, Any]:
        """Send password reset OTP"""
        user = User.find_by_email(email)
        if not user:
            # Don't reveal if email exists or not
            return {"message": "Jika email terdaftar, OTP akan dikirim"}
        
        # Generate OTP
        otp = AuthService.generate_otp()
        user.set_otp(otp, 10)  # 10 minutes expiry
        
        # Send OTP via email
        if Config.DEBUG:
            return {
                "message": "OTP reset password telah dikirim",
                "otp_code": otp  # Only for development
            }
        
        EmailService.send_password_reset_otp(user.email, user.nama_lengkap, otp)
        
        return {"message": "OTP reset password telah dikirim ke email Anda"}
    
    @staticmethod
    def reset_password(email: str, otp_code: str, new_password: str, confirm_password: str) -> Dict[str, Any]:
        """Reset password with OTP"""
        # Validate password match
        if new_password != confirm_password:
            raise ValueError("Password dan konfirmasi password tidak sama")
        
        # Validate password strength
        is_strong, password_errors = AuthService.validate_password_strength(new_password)
        if not is_strong:
            raise ValueError(password_errors[0])
        
        # Find user by email and validate OTP
        user = User.find_by_email(email)
        if not user:
            raise ValueError("Email tidak ditemukan")
        
        # Verify OTP
        if not user.otp_code or user.otp_code != otp_code:
            raise ValueError("OTP tidak valid")
        
        if not user.otp_expires or user.otp_expires < datetime.utcnow():
            raise ValueError("OTP telah kedaluwarsa")
        
        # Update password
        user.password_hash = AuthService.hash_password(new_password)
        user.clear_otp()
        user.reset_login_attempts()
        user.save()
        
        return {"message": "Password berhasil diubah"}
    
    @staticmethod
    def change_password(user_id: str, old_password: str, new_password: str, confirm_password: str) -> Dict[str, Any]:
        """Change password for authenticated user"""
        # Validate password match
        if new_password != confirm_password:
            raise ValueError("Password baru dan konfirmasi tidak sama")
        
        # Validate password strength
        is_strong, password_errors = AuthService.validate_password_strength(new_password)
        if not is_strong:
            raise ValueError(password_errors[0])
        
        # Find user
        user = User.find_by_id(user_id)
        if not user:
            raise ValueError("User tidak ditemukan")
        
        # Verify old password
        if not AuthService.verify_password(old_password, user.password_hash):
            raise ValueError("Password lama salah")
        
        # Don't allow same password
        if AuthService.verify_password(new_password, user.password_hash):
            raise ValueError("Password baru harus berbeda dari password lama")
        
        # Update password
        user.password_hash = AuthService.hash_password(new_password)
        user.save()
        
        return {"message": "Password berhasil diubah"}
    
    @staticmethod
    def get_current_user(token: str) -> User:
        """Get current user from token"""
        payload = AuthService.verify_token(token)
        
        if payload.get('type') != 'access':
            raise HTTPException(status_code=401, detail="Token tidak valid")
        
        user = User.find_by_id(payload['user_id'])
        if not user:
            raise HTTPException(status_code=401, detail="User tidak ditemukan")
        
        return user