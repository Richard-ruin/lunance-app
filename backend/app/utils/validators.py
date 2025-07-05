# app/utils/validators.py (updated)
import re
from typing import Optional, List, Dict
from email_validator import validate_email, EmailNotValidError

def validate_academic_email(email: str) -> bool:
    """Validate academic email (.ac.id)"""
    if not email.endswith('.ac.id'):
        return False
    
    try:
        validate_email(email)
        return True
    except EmailNotValidError:
        return False

def validate_phone_number(phone: str) -> bool:
    """Validate Indonesian phone number"""
    pattern = r'^(\+62|0)[0-9]{9,12}$'
    return bool(re.match(pattern, phone))

def validate_password_strength(password: str) -> tuple[bool, Optional[str]]:
    """Validate password strength"""
    if len(password) < 8:
        return False, "Password minimal 8 karakter"
    
    if not re.search(r'[A-Za-z]', password):
        return False, "Password harus mengandung huruf"
    
    if not re.search(r'[0-9]', password):
        return False, "Password harus mengandung angka"
    
    return True, None

# Extended validation utilities
class ValidationUtils:
    @staticmethod
    def validate_indonesian_phone(phone: str) -> bool:
        """Validate Indonesian phone number format"""
        # Remove all non-digit characters
        phone_digits = re.sub(r'\D', '', phone)
        
        # Check if starts with +62 or 0
        if phone.startswith('+62'):
            return len(phone_digits) >= 11 and len(phone_digits) <= 15
        elif phone.startswith('0'):
            return len(phone_digits) >= 10 and len(phone_digits) <= 14
        
        return False
    
    @staticmethod
    def validate_university_name(name: str) -> bool:
        """Validate university name"""
        if not name or len(name.strip()) < 3:
            return False
        
        # Check if contains only letters, numbers, spaces, and common punctuation
        if not re.match(r'^[a-zA-Z0-9\s\-\.\,\(\)]+$', name):
            return False
        
        return True
    
    @staticmethod
    def validate_password_detailed(password: str) -> Dict[str, any]:
        """Validate password strength and return detailed feedback"""
        result = {
            "is_valid": True,
            "errors": [],
            "score": 0
        }
        
        # Length check
        if len(password) < 8:
            result["is_valid"] = False
            result["errors"].append("Password minimal 8 karakter")
        else:
            result["score"] += 1
        
        # Uppercase letter check
        if not re.search(r'[A-Z]', password):
            result["errors"].append("Password harus mengandung huruf besar")
        else:
            result["score"] += 1
        
        # Lowercase letter check
        if not re.search(r'[a-z]', password):
            result["errors"].append("Password harus mengandung huruf kecil")
        else:
            result["score"] += 1
        
        # Number check
        if not re.search(r'[0-9]', password):
            result["is_valid"] = False
            result["errors"].append("Password harus mengandung angka")
        else:
            result["score"] += 1
        
        # Special character check
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            result["errors"].append("Password lebih kuat dengan karakter spesial")
        else:
            result["score"] += 1
        
        # Common password check
        common_passwords = [
            "password", "123456", "qwerty", "abc123", 
            "password123", "admin", "root", "user"
        ]
        
        if password.lower() in common_passwords:
            result["is_valid"] = False
            result["errors"].append("Password terlalu umum")
        
        return result
    
    @staticmethod
    def validate_file_size(file_size: int, max_size: int = 2 * 1024 * 1024) -> bool:
        """Validate file size (default: 2MB)"""
        return file_size <= max_size
    
    @staticmethod
    def validate_image_type(content_type: str) -> bool:
        """Validate image content type"""
        allowed_types = [
            'image/jpeg', 'image/jpg', 'image/png', 
            'image/gif', 'image/webp'
        ]
        return content_type in allowed_types
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Sanitize filename for safe storage"""
        # Remove path separators and dangerous characters
        filename = re.sub(r'[<>:"/\\|?*]', '', filename)
        
        # Replace spaces with underscores
        filename = filename.replace(' ', '_')
        
        # Limit length
        if len(filename) > 100:
            name, ext = filename.rsplit('.', 1)
            filename = name[:95] + '.' + ext
        
        return filename

# Backward compatibility
def validate_academic_email_compat(email: str) -> bool:
    """Backward compatibility function"""
    return validate_academic_email(email)