# app/utils/timezone_utils.py
from datetime import datetime, timezone, timedelta
from typing import Optional
import pytz

# Indonesia timezone
INDONESIA_TZ = pytz.timezone('Asia/Jakarta')  # WIB (GMT+7)

def get_indonesia_now() -> datetime:
    """Get current datetime in Indonesia timezone (WIB/GMT+7)"""
    return datetime.now(INDONESIA_TZ)

def get_utc_now() -> datetime:
    """Get current datetime in UTC"""
    return datetime.now(timezone.utc)

def convert_utc_to_indonesia(utc_dt: datetime) -> datetime:
    """Convert UTC datetime to Indonesia timezone"""
    if utc_dt.tzinfo is None:
        # If naive datetime, assume it's UTC
        utc_dt = utc_dt.replace(tzinfo=timezone.utc)
    
    return utc_dt.astimezone(INDONESIA_TZ)

def convert_indonesia_to_utc(indonesia_dt: datetime) -> datetime:
    """Convert Indonesia datetime to UTC"""
    if indonesia_dt.tzinfo is None:
        # If naive datetime, assume it's Indonesia timezone
        indonesia_dt = INDONESIA_TZ.localize(indonesia_dt)
    
    return indonesia_dt.astimezone(timezone.utc)

def format_indonesia_datetime(dt: datetime, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """Format datetime in Indonesia timezone"""
    if dt.tzinfo is None:
        # Assume UTC if no timezone info
        dt = dt.replace(tzinfo=timezone.utc)
    
    indonesia_dt = dt.astimezone(INDONESIA_TZ)
    return indonesia_dt.strftime(format_str)

def get_indonesia_datetime_for_storage() -> datetime:
    """Get Indonesia datetime that's properly formatted for MongoDB storage"""
    # Store in UTC for consistency, but generate from Indonesia time
    indonesia_now = get_indonesia_now()
    return indonesia_now.astimezone(timezone.utc).replace(tzinfo=None)

def parse_indonesia_datetime(date_str: str, format_str: str = "%Y-%m-%d %H:%M:%S") -> datetime:
    """Parse datetime string as Indonesia timezone"""
    naive_dt = datetime.strptime(date_str, format_str)
    return INDONESIA_TZ.localize(naive_dt)

class IndonesiaDatetime:
    """Helper class for Indonesia datetime operations"""
    
    @staticmethod
    def now() -> datetime:
        """Current time in Indonesia timezone"""
        return get_indonesia_now()
    
    @staticmethod
    def now_for_db() -> datetime:
        """Current time formatted for database storage (UTC naive)"""
        return get_indonesia_datetime_for_storage()
    
    @staticmethod
    def from_utc(utc_dt: datetime) -> datetime:
        """Convert UTC to Indonesia timezone"""
        return convert_utc_to_indonesia(utc_dt)
    
    @staticmethod
    def to_utc(indonesia_dt: datetime) -> datetime:
        """Convert Indonesia time to UTC"""
        return convert_indonesia_to_utc(indonesia_dt)
    
    @staticmethod
    def format(dt: datetime, format_str: str = "%d/%m/%Y %H:%M") -> str:
        """Format datetime for display in Indonesia"""
        return format_indonesia_datetime(dt, format_str)
    
    @staticmethod
    def format_time_only(dt: datetime) -> str:
        """Format only time part (HH:MM)"""
        return format_indonesia_datetime(dt, "%H:%M")
    
    @staticmethod
    def format_date_only(dt: datetime) -> str:
        """Format only date part (DD/MM/YYYY)"""
        return format_indonesia_datetime(dt, "%d/%m/%Y")
    
    @staticmethod
    def format_relative(dt: datetime) -> str:
        """Format relative time (e.g., '2 jam lalu')"""
        now = get_indonesia_now()
        
        # Convert dt to Indonesia timezone if needed
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        dt_indonesia = dt.astimezone(INDONESIA_TZ)
        
        difference = now - dt_indonesia
        
        if difference.days > 0:
            if difference.days == 1:
                return '1 hari lalu'
            elif difference.days < 7:
                return f'{difference.days} hari lalu'
            elif difference.days < 30:
                weeks = difference.days // 7
                return f'{weeks} minggu lalu'
            else:
                months = difference.days // 30
                return f'{months} bulan lalu'
        
        hours = difference.seconds // 3600
        if hours > 0:
            return f'{hours} jam lalu'
        
        minutes = difference.seconds // 60
        if minutes > 0:
            return f'{minutes} menit lalu'
        
        return 'Baru saja'

# Convenience functions
def now_indonesia() -> datetime:
    """Shorthand for Indonesia current time"""
    return IndonesiaDatetime.now()

def now_for_db() -> datetime:
    """Shorthand for database-ready timestamp"""
    return IndonesiaDatetime.now_for_db()