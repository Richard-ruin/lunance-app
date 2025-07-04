"""
Utility Validators
Helper functions untuk validasi data dengan standar Indonesia
"""

import re
import dns.resolver
from typing import List, Optional
from email_validator import validate_email, EmailNotValidError

from ..config.settings import settings


def validate_indonesian_phone(phone: str) -> str:
    """
    Validasi dan normalisasi nomor telepon Indonesia
    
    Args:
        phone: Nomor telepon input
        
    Returns:
        Nomor telepon yang sudah dinormalisasi
        
    Raises:
        ValueError: Jika format nomor telepon tidak valid
    """
    if not phone:
        raise ValueError("Nomor telepon tidak boleh kosong")
    
    # Remove spaces, dashes, parentheses
    cleaned = re.sub(r'[\s\-\(\)]+', '', phone)
    
    # Remove leading zeros and normalize
    if cleaned.startswith('0'):
        cleaned = '+62' + cleaned[1:]
    elif cleaned.startswith('62'):
        cleaned = '+' + cleaned
    elif not cleaned.startswith('+62'):
        cleaned = '+62' + cleaned
    
    # Validate format: +62 followed by 9-13 digits
    if not re.match(r'^\+62[0-9]{9,13}$', cleaned):
        raise ValueError("Format nomor telepon tidak valid. Gunakan format: +62XXXXXXXXX")
    
    # Validate mobile operator prefixes (common Indonesian prefixes)
    valid_prefixes = [
        '811', '812', '813', '821', '822', '823', '851', '852', '853',  # Telkomsel
        '814', '815', '816', '855', '856', '857', '858',                 # Indosat
        '817', '818', '819', '859', '877', '878',                       # XL
        '838', '831', '832', '833',                                     # Axis
        '895', '896', '897', '898', '899',                              # Three
        '881', '882', '883', '884', '885', '886', '887', '888', '889'   # Smartfren
    ]
    
    # Extract prefix (3 digits after +62)
    prefix = cleaned[3:6]
    
    if prefix not in valid_prefixes:
        # Still allow it but log warning for unusual prefixes
        pass
    
    return cleaned


def validate_university_email(email: str) -> str:
    """
    Validasi email universitas Indonesia (.ac.id)
    
    Args:
        email: Email address
        
    Returns:
        Email yang sudah dinormalisasi
        
    Raises:
        ValueError: Jika email tidak valid atau bukan domain universitas
    """
    if not email:
        raise ValueError("Email tidak boleh kosong")
    
    # Basic email validation
    try:
        valid = validate_email(email)
        email = valid.email.lower()
    except EmailNotValidError as e:
        raise ValueError(f"Format email tidak valid: {str(e)}")
    
    # Check if it's a university domain
    if not any(email.endswith(f".{domain}") for domain in settings.valid_university_domains):
        raise ValueError(f"Email harus menggunakan domain universitas: {settings.valid_university_domains}")
    
    return email


def validate_university_domain(domain: str) -> str:
    """
    Validasi domain universitas
    
    Args:
        domain: Domain universitas
        
    Returns:
        Domain yang sudah dinormalisasi
        
    Raises:
        ValueError: Jika domain tidak valid
    """
    if not domain:
        raise ValueError("Domain tidak boleh kosong")
    
    domain = domain.lower().strip()
    
    # Must end with .ac.id
    if not domain.endswith('.ac.id'):
        raise ValueError("Domain universitas harus berakhiran .ac.id")
    
    # Basic domain format validation
    if not re.match(r'^[a-z0-9.-]+\.ac\.id$', domain):
        raise ValueError("Format domain tidak valid")
    
    # Check for invalid characters
    if '..' in domain or domain.startswith('.') or domain.startswith('-'):
        raise ValueError("Format domain tidak valid")
    
    # Minimum format: xxx.ac.id
    parts = domain.split('.')
    if len(parts) < 3:
        raise ValueError("Format domain tidak valid")
    
    return domain


def validate_currency_amount(amount: float, min_amount: float = 0, max_amount: float = 1_000_000_000) -> float:
    """
    Validasi nominal mata uang (Rupiah)
    
    Args:
        amount: Nominal yang akan divalidasi
        min_amount: Nominal minimum (default: 0)
        max_amount: Nominal maximum (default: 1 Miliar)
        
    Returns:
        Nominal yang sudah dibulatkan ke 2 desimal
        
    Raises:
        ValueError: Jika nominal tidak valid
    """
    if amount is None:
        raise ValueError("Nominal tidak boleh kosong")
    
    if amount < min_amount:
        raise ValueError(f"Nominal tidak boleh kurang dari Rp {min_amount:,.2f}")
    
    if amount > max_amount:
        raise ValueError(f"Nominal tidak boleh lebih dari Rp {max_amount:,.2f}")
    
    # Round to 2 decimal places
    return round(amount, 2)


def validate_hex_color(color: str) -> str:
    """
    Validasi kode warna hex
    
    Args:
        color: Kode warna hex
        
    Returns:
        Kode warna hex yang sudah dinormalisasi
        
    Raises:
        ValueError: Jika format warna tidak valid
    """
    if not color:
        raise ValueError("Kode warna tidak boleh kosong")
    
    color = color.strip().upper()
    
    # Add # if missing
    if not color.startswith('#'):
        color = '#' + color
    
    # Validate hex format
    if not re.match(r'^#[0-9A-F]{6}$', color):
        raise ValueError("Format warna harus hex 6 digit (contoh: #FF5733)")
    
    return color


def validate_password_strength(password: str) -> str:
    """
    Validasi kekuatan password
    
    Args:
        password: Password yang akan divalidasi
        
    Returns:
        Password (tanpa modifikasi)
        
    Raises:
        ValueError: Jika password tidak memenuhi kriteria
    """
    if not password:
        raise ValueError("Password tidak boleh kosong")
    
    if len(password) < 8:
        raise ValueError("Password minimal 8 karakter")
    
    if len(password) > 128:
        raise ValueError("Password maksimal 128 karakter")
    
    # Check for at least one lowercase letter
    if not re.search(r'[a-z]', password):
        raise ValueError("Password harus mengandung minimal 1 huruf kecil")
    
    # Check for at least one uppercase letter
    if not re.search(r'[A-Z]', password):
        raise ValueError("Password harus mengandung minimal 1 huruf besar")
    
    # Check for at least one digit
    if not re.search(r'\d', password):
        raise ValueError("Password harus mengandung minimal 1 angka")
    
    # Check for at least one special character
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        raise ValueError("Password harus mengandung minimal 1 karakter khusus")
    
    # Check for common weak passwords
    weak_passwords = [
        'password', '12345678', 'qwerty123', 'admin123', 
        'password123', '123456789', 'qwertyuiop'
    ]
    
    if password.lower() in weak_passwords:
        raise ValueError("Password terlalu umum, gunakan kombinasi yang lebih unik")
    
    return password


def validate_name(name: str, min_length: int = 2, max_length: int = 100) -> str:
    """
    Validasi nama (untuk nama orang, institusi, dll)
    
    Args:
        name: Nama yang akan divalidasi
        min_length: Panjang minimum
        max_length: Panjang maksimum
        
    Returns:
        Nama yang sudah dinormalisasi
        
    Raises:
        ValueError: Jika nama tidak valid
    """
    if not name or not name.strip():
        raise ValueError("Nama tidak boleh kosong")
    
    # Clean up name
    name = ' '.join(name.strip().split())
    
    if len(name) < min_length:
        raise ValueError(f"Nama minimal {min_length} karakter")
    
    if len(name) > max_length:
        raise ValueError(f"Nama maksimal {max_length} karakter")
    
    # Allow letters, spaces, and common name characters
    if not re.match(r"^[a-zA-Z\s.',-]+$", name):
        raise ValueError("Nama hanya boleh berisi huruf, spasi, dan karakter khusus (', ., -, ')")
    
    return name


def validate_text_content(text: str, min_length: int = 1, max_length: int = 1000, allow_empty: bool = False) -> Optional[str]:
    """
    Validasi konten teks (deskripsi, catatan, dll)
    
    Args:
        text: Teks yang akan divalidasi
        min_length: Panjang minimum
        max_length: Panjang maksimum
        allow_empty: Apakah boleh kosong
        
    Returns:
        Teks yang sudah dinormalisasi atau None jika empty dan diizinkan
        
    Raises:
        ValueError: Jika teks tidak valid
    """
    if not text or not text.strip():
        if allow_empty:
            return None
        raise ValueError("Teks tidak boleh kosong")
    
    # Clean up text
    text = ' '.join(text.strip().split())
    
    if len(text) < min_length:
        raise ValueError(f"Teks minimal {min_length} karakter")
    
    if len(text) > max_length:
        raise ValueError(f"Teks maksimal {max_length} karakter")
    
    return text


def validate_tags(tags: List[str], max_tags: int = 10, max_tag_length: int = 50) -> List[str]:
    """
    Validasi list tags
    
    Args:
        tags: List tags
        max_tags: Maksimum jumlah tags
        max_tag_length: Maksimum panjang per tag
        
    Returns:
        List tags yang sudah dinormalisasi dan dededuplikasi
        
    Raises:
        ValueError: Jika tags tidak valid
    """
    if not tags:
        return []
    
    if len(tags) > max_tags:
        raise ValueError(f"Maksimal {max_tags} tags")
    
    cleaned_tags = []
    for tag in tags:
        if not isinstance(tag, str):
            continue
        
        tag = tag.strip().lower()
        if not tag:
            continue
        
        if len(tag) > max_tag_length:
            raise ValueError(f"Tag '{tag}' terlalu panjang (maksimal {max_tag_length} karakter)")
        
        # Basic validation for tag format
        if not re.match(r'^[a-z0-9_-]+$', tag):
            raise ValueError(f"Tag '{tag}' mengandung karakter tidak valid (gunakan huruf, angka, _, -)")
        
        if tag not in cleaned_tags:  # Remove duplicates
            cleaned_tags.append(tag)
    
    return cleaned_tags


def validate_url(url: str, require_https: bool = False) -> str:
    """
    Validasi URL
    
    Args:
        url: URL yang akan divalidasi
        require_https: Apakah harus HTTPS
        
    Returns:
        URL yang sudah dinormalisasi
        
    Raises:
        ValueError: Jika URL tidak valid
    """
    if not url:
        raise ValueError("URL tidak boleh kosong")
    
    url = url.strip()
    
    # Add protocol if missing
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    # Basic URL validation
    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    
    if not url_pattern.match(url):
        raise ValueError("Format URL tidak valid")
    
    if require_https and not url.startswith('https://'):
        raise ValueError("URL harus menggunakan HTTPS")
    
    return url


def validate_file_extension(filename: str, allowed_extensions: List[str]) -> str:
    """
    Validasi ekstensi file
    
    Args:
        filename: Nama file
        allowed_extensions: List ekstensi yang diizinkan (tanpa titik)
        
    Returns:
        Filename (tanpa modifikasi)
        
    Raises:
        ValueError: Jika ekstensi tidak valid
    """
    if not filename:
        raise ValueError("Nama file tidak boleh kosong")
    
    file_extension = filename.lower().split('.')[-1] if '.' in filename else ''
    
    if not file_extension:
        raise ValueError("File harus memiliki ekstensi")
    
    if file_extension not in [ext.lower() for ext in allowed_extensions]:
        raise ValueError(f"Ekstensi file tidak didukung. Gunakan: {', '.join(allowed_extensions)}")
    
    return filename


def validate_coordinate(latitude: float, longitude: float) -> tuple[float, float]:
    """
    Validasi koordinat geografis
    
    Args:
        latitude: Latitude
        longitude: Longitude
        
    Returns:
        Tuple (latitude, longitude) yang sudah divalidasi
        
    Raises:
        ValueError: Jika koordinat tidak valid
    """
    if latitude < -90 or latitude > 90:
        raise ValueError("Latitude harus antara -90 dan 90")
    
    if longitude < -180 or longitude > 180:
        raise ValueError("Longitude harus antara -180 dan 180")
    
    return round(latitude, 6), round(longitude, 6)


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename untuk keamanan
    
    Args:
        filename: Nama file original
        
    Returns:
        Nama file yang sudah di-sanitize
    """
    if not filename:
        return "unnamed_file"
    
    # Remove path traversal attempts
    filename = filename.replace('..', '').replace('/', '').replace('\\', '')
    
    # Remove or replace dangerous characters
    filename = re.sub(r'[<>:"|?*]', '', filename)
    
    # Replace spaces with underscores
    filename = filename.replace(' ', '_')
    
    # Ensure it's not too long
    if len(filename) > 255:
        name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
        filename = name[:250] + ('.' + ext if ext else '')
    
    return filename


# Domain-specific validators for Indonesian context
def validate_nik(nik: str) -> str:
    """
    Validasi NIK (Nomor Induk Kependudukan) Indonesia
    
    Args:
        nik: NIK yang akan divalidasi
        
    Returns:
        NIK yang sudah dinormalisasi
        
    Raises:
        ValueError: Jika NIK tidak valid
    """
    if not nik:
        raise ValueError("NIK tidak boleh kosong")
    
    nik = nik.strip()
    
    if not nik.isdigit():
        raise ValueError("NIK hanya boleh berisi angka")
    
    if len(nik) != 16:
        raise ValueError("NIK harus 16 digit")
    
    return nik


def validate_indonesian_postal_code(postal_code: str) -> str:
    """
    Validasi kode pos Indonesia
    
    Args:
        postal_code: Kode pos
        
    Returns:
        Kode pos yang sudah dinormalisasi
        
    Raises:
        ValueError: Jika kode pos tidak valid
    """
    if not postal_code:
        raise ValueError("Kode pos tidak boleh kosong")
    
    postal_code = postal_code.strip()
    
    if not postal_code.isdigit():
        raise ValueError("Kode pos hanya boleh berisi angka")
    
    if len(postal_code) != 5:
        raise ValueError("Kode pos harus 5 digit")
    
    return postal_code