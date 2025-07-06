import re
from typing import Any, Dict

def validate_email_domain(email: str) -> bool:
    """Validate if email has .ac.id domain"""
    if not email:
        return False
    
    # Check if email ends with .ac.id
    return email.lower().endswith('.ac.id')

def validate_email_format(email: str) -> bool:
    """Validate email format"""
    if not email:
        return False
    
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_nim(nim: str) -> bool:
    """Validate NIM format (numbers only, 8-20 characters)"""
    if not nim:
        return False
    
    # Check if NIM contains only numbers and has valid length
    return nim.isdigit() and 8 <= len(nim) <= 20

def validate_phone(phone: str) -> bool:
    """Validate phone number format"""
    if not phone:
        return True  # Phone is optional
    
    # Remove all non-digit characters
    digits_only = re.sub(r'[^0-9]', '', phone)
    
    # Check if it has valid length (8-15 digits)
    return 8 <= len(digits_only) <= 15

def validate_password_strength(password: str) -> Dict[str, Any]:
    """Validate password strength"""
    errors = []
    
    if len(password) < 8:
        errors.append('Password minimal 8 karakter')
    
    if not re.search(r'[A-Z]', password):
        errors.append('Password harus mengandung huruf besar')
    
    if not re.search(r'[a-z]', password):
        errors.append('Password harus mengandung huruf kecil')
    
    if not re.search(r'[0-9]', password):
        errors.append('Password harus mengandung angka')
    
    # Check for special characters (optional but recommended)
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        errors.append('Password disarankan mengandung karakter khusus')
    
    return {
        'is_valid': len(errors) == 0,
        'errors': errors,
        'strength': _calculate_password_strength(password)
    }

def _calculate_password_strength(password: str) -> str:
    """Calculate password strength level"""
    score = 0
    
    # Length check
    if len(password) >= 8:
        score += 1
    if len(password) >= 12:
        score += 1
    
    # Character variety check
    if re.search(r'[a-z]', password):
        score += 1
    if re.search(r'[A-Z]', password):
        score += 1
    if re.search(r'[0-9]', password):
        score += 1
    if re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        score += 1
    
    # Return strength level
    if score <= 2:
        return 'weak'
    elif score <= 4:
        return 'medium'
    else:
        return 'strong'

def validate_university_code(code: str) -> bool:
    """Validate university code format"""
    if not code:
        return False
    
    # University code should be 2-10 characters, alphanumeric
    return re.match(r'^[A-Z0-9]{2,10}$', code.upper())

def validate_fakultas_code(code: str) -> bool:
    """Validate fakultas code format"""
    if not code:
        return False
    
    # Fakultas code should be 2-10 characters, alphanumeric
    return re.match(r'^[A-Z0-9]{2,10}$', code.upper())

def validate_prodi_code(code: str) -> bool:
    """Validate program studi code format"""
    if not code:
        return False
    
    # Program studi code should be 2-10 characters, alphanumeric
    return re.match(r'^[A-Z0-9]{2,10}$', code.upper())

def validate_angkatan(angkatan: int, current_year: int = None) -> bool:
    """Validate angkatan year"""
    if current_year is None:
        from datetime import datetime
        current_year = datetime.now().year
    
    return 2000 <= angkatan <= current_year

def validate_semester(semester: int) -> bool:
    """Validate semester number"""
    return 1 <= semester <= 14

def validate_jenjang(jenjang: str) -> bool:
    """Validate jenjang pendidikan"""
    valid_jenjang = ['D3', 'D4', 'S1', 'S2', 'S3']
    return jenjang.upper() in valid_jenjang

def validate_akreditasi(akreditasi: str) -> bool:
    """Validate akreditasi grade"""
    if not akreditasi:
        return True  # Akreditasi is optional
    
    valid_grades = ['A', 'B', 'C']
    return akreditasi.upper() in valid_grades

def sanitize_string(text: str) -> str:
    """Sanitize input string"""
    if not text:
        return ''
    
    # Remove extra whitespace and strip
    text = ' '.join(text.split())
    
    # Remove potentially harmful characters
    text = re.sub(r'[<>"\']', '', text)
    
    return text.strip()

def validate_url(url: str) -> bool:
    """Validate URL format"""
    if not url:
        return True  # URL is optional
    
    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    
    return url_pattern.match(url) is not None