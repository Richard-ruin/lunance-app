# app/utils/helpers.py
from typing import Any, Dict, Optional
from datetime import datetime
import re

def create_response(data: Any = None, message: str = 'Success') -> Dict[str, Any]:
    """Create standardized API response"""
    return {
        'success': True,
        'message': message,
        'data': data,
        'timestamp': datetime.utcnow().isoformat()
    }

def create_error_response(message: str, errors: Optional[Dict] = None) -> Dict[str, Any]:
    """Create standardized API error response"""
    return {
        'success': False,
        'message': message,
        'errors': errors,
        'timestamp': datetime.utcnow().isoformat()
    }

def snake_to_camel(snake_str: str) -> str:
    """Convert snake_case to camelCase"""
    components = snake_str.split('_')
    return components[0] + ''.join(x.title() for x in components[1:])

def camel_to_snake(camel_str: str) -> str:
    """Convert camelCase to snake_case"""
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', camel_str)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

def format_currency(amount: float, currency: str = 'IDR') -> str:
    """Format currency for display"""
    if currency == 'IDR':
        return f"Rp {amount:,.0f}".replace(',', '.')
    else:
        return f"{currency} {amount:,.2f}"

def generate_transaction_id() -> str:
    """Generate unique transaction ID"""
    from datetime import datetime
    import random
    import string
    
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    
    return f"TXN{timestamp}{random_str}"

def clean_string(text: str) -> str:
    """Clean and normalize string"""
    if not text:
        return ''
    
    # Remove extra whitespace
    text = ' '.join(text.split())
    
    # Remove special characters (keep only alphanumeric and basic punctuation)
    text = re.sub(r'[^\w\s\.\,\-\(\)]', '', text)
    
    return text.strip()