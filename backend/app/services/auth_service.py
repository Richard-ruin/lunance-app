from typing import Dict, Any
from datetime import datetime, timedelta
import bcrypt
import jwt
from app.models.user import User
from app.models.university import University, Fakultas, ProgramStudi
from app.config.settings import Config
from app.utils.validators import validate_email_domain, validate_password_strength

class AuthService:
    
    @staticmethod
    def register_user(data: Dict[str, Any]) -> Dict[str, Any]:
        """Register new user"""
        # Validate email domain
        if not validate_email_domain(data['email']):
            raise ValueError('Email harus menggunakan domain .ac.id')
        
        # Validate password strength
        password_validation = validate_password_strength(data['password'])
        if not password_validation['is_valid']:
            raise ValueError(f"Password tidak valid: {', '.join(password_validation['errors'])}")
        
        # Check if user already exists
        existing_user = User.find_by_email(data['email'])
        if existing_user:
            raise ValueError('Email sudah terdaftar')
        
        existing_nim = User.find_by_nim(data['nim'])
        if existing_nim:
            raise ValueError('NIM sudah terdaftar')
        
        # Validate university, fakultas, and program studi
        university = University.find_by_id(data['university_id'])
        if not university:
            raise ValueError('Universitas tidak ditemukan')
        
        if not university.status_aktif:
            raise ValueError('Universitas tidak aktif')
        
        fakultas = Fakultas.find_by_id(data['fakultas_id'])
        if not fakultas:
            raise ValueError('Fakultas tidak ditemukan')
        
        # Validate fakultas belongs to university
        if str(fakultas.university_id) != data['university_id']:
            raise ValueError('Fakultas tidak sesuai dengan universitas')
        
        prodi = ProgramStudi.find_by_id(data['program_studi_id'])
        if not prodi:
            raise ValueError('Program studi tidak ditemukan')
        
        # Validate prodi belongs to fakultas
        if str(prodi.fakultas_id) != data['fakultas_id']:
            raise ValueError('Program studi tidak sesuai dengan fakultas')
        
        # Validate angkatan
        current_year = datetime.now().year
        if data['angkatan'] < 2000 or data['angkatan'] > current_year:
            raise ValueError(f'Angkatan harus antara 2000 dan {current_year}')
        
        # Hash password
        password_hash = bcrypt.hashpw(
            data['password'].encode('utf-8'),
            bcrypt.gensalt()
        ).decode('utf-8')
        
        # Create user
        user_data = {
            'email': data['email'],
            'password_hash': password_hash,
            'nama': data['nama'],
            'nim': data['nim'],
            'university_id': data['university_id'],
            'fakultas_id': data['fakultas_id'],
            'program_studi_id': data['program_studi_id'],
            'angkatan': data['angkatan'],
            'semester': data.get('semester', 1)
        }
        
        user = User(**user_data)
        user.save()
        
        # Generate token
        token = AuthService._generate_token(user)
        
        return {
            'user': user.to_dict_safe(),
            'token': token,
            'expires_in': Config.JWT_ACCESS_TOKEN_EXPIRES
        }
    
    @staticmethod
    def login_user(email: str, password: str) -> Dict[str, Any]:
        """Login user"""
        # Find user
        user = User.find_by_email(email)
        if not user:
            raise ValueError('Email atau password salah')
        
        # Check password
        if not bcrypt.checkpw(password.encode('utf-8'), user.password_hash.encode('utf-8')):
            raise ValueError('Email atau password salah')
        
        # Check if user is active
        if not user.is_active:
            raise ValueError('Akun Anda telah dinonaktifkan')
        
        # Update last login
        user.last_login = datetime.utcnow()
        user.save()
        
        # Generate token
        token = AuthService._generate_token(user)
        
        return {
            'user': user.to_dict_safe(),
            'token': token,
            'expires_in': Config.JWT_ACCESS_TOKEN_EXPIRES
        }
    
    @staticmethod
    def verify_token(token: str) -> Dict[str, Any]:
        """Verify JWT token"""
        try:
            payload = jwt.decode(
                token, 
                Config.JWT_SECRET_KEY, 
                algorithms=[Config.JWT_ALGORITHM]
            )
            
            user_id = payload.get('user_id')
            if not user_id:
                raise ValueError('Token tidak valid')
            
            user = User.find_by_id(user_id)
            if not user:
                raise ValueError('User tidak ditemukan')
            
            if not user.is_active:
                raise ValueError('Akun tidak aktif')
            
            return {
                'user': user.to_dict_safe(),
                'user_id': user_id
            }
            
        except jwt.ExpiredSignatureError:
            raise ValueError('Token sudah kadaluarsa')
        except jwt.InvalidTokenError:
            raise ValueError('Token tidak valid')
    
    @staticmethod
    def refresh_token(token: str) -> Dict[str, Any]:
        """Refresh JWT token"""
        try:
            # Verify current token
            token_data = AuthService.verify_token(token)
            user = User.find_by_id(token_data['user_id'])
            
            if not user:
                raise ValueError('User tidak ditemukan')
            
            # Generate new token
            new_token = AuthService._generate_token(user)
            
            return {
                'token': new_token,
                'expires_in': Config.JWT_ACCESS_TOKEN_EXPIRES
            }
            
        except Exception as e:
            raise ValueError(f'Gagal refresh token: {str(e)}')
    
    @staticmethod
    def _generate_token(user: User) -> str:
        """Generate JWT token"""
        payload = {
            'user_id': str(user.id),
            'email': user.email,
            'nama': user.nama,
            'nim': user.nim,
            'iat': datetime.utcnow(),
            'exp': datetime.utcnow() + timedelta(seconds=Config.JWT_ACCESS_TOKEN_EXPIRES)
        }
        
        return jwt.encode(payload, Config.JWT_SECRET_KEY, algorithm=Config.JWT_ALGORITHM)
    
    @staticmethod
    def get_user_profile(user_id: str) -> Dict[str, Any]:
        """Get complete user profile with university info"""
        user = User.find_by_id(user_id)
        if not user:
            raise ValueError('User tidak ditemukan')
        
        # Get university, fakultas, and prodi info
        university = University.find_by_id(str(user.university_id))
        fakultas = Fakultas.find_by_id(str(user.fakultas_id))
        prodi = ProgramStudi.find_by_id(str(user.program_studi_id))
        
        user_data = user.to_dict_safe()
        user_data['university'] = university.dict() if university else None
        user_data['fakultas'] = fakultas.dict() if fakultas else None
        user_data['program_studi'] = prodi.dict() if prodi else None
        
        return user_data