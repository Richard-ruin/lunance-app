"""
Transaction Model
Model untuk pencatatan transaksi keuangan (income & expense)
"""

from datetime import datetime, date
from typing import Optional
from enum import Enum
from decimal import Decimal
from pydantic import Field, field_validator, model_validator
from beanie import Indexed

from .base import BaseDocument, SoftDeleteMixin, AuditMixin
from .category import CategoryType


class TransactionStatus(str, Enum):
    """Status transaksi"""
    COMPLETED = "completed"
    PENDING = "pending"
    CANCELLED = "cancelled"


class Transaction(BaseDocument, SoftDeleteMixin, AuditMixin):
    """
    Model Transaksi keuangan
    
    Fields:
    - user_id: Reference ke User
    - category_id: Reference ke Category
    - type: Tipe transaksi (income/expense)
    - amount: Jumlah nominal
    - description: Deskripsi transaksi
    - date: Tanggal transaksi
    - status: Status transaksi
    - location: Lokasi transaksi (opsional)
    - notes: Catatan tambahan
    - receipt_url: URL struk/bukti transaksi
    """
    
    # References
    user_id: Indexed(str) = Field(..., description="ID User")
    category_id: Indexed(str) = Field(..., description="ID Kategori")
    
    # Transaction Details
    type: CategoryType = Field(..., description="Tipe transaksi")
    amount: float = Field(..., gt=0, description="Jumlah nominal")
    description: str = Field(..., min_length=1, max_length=500, description="Deskripsi transaksi")
    
    # Date & Time
    date: Indexed(date) = Field(..., description="Tanggal transaksi")
    time: Optional[str] = Field(default=None, description="Waktu transaksi (HH:MM)")
    
    # Status & Metadata
    status: TransactionStatus = Field(default=TransactionStatus.COMPLETED, description="Status transaksi")
    location: Optional[str] = Field(default=None, max_length=200, description="Lokasi transaksi")
    notes: Optional[str] = Field(default=None, max_length=1000, description="Catatan tambahan")
    
    # Attachments
    receipt_url: Optional[str] = Field(default=None, description="URL struk/bukti transaksi")
    receipt_filename: Optional[str] = Field(default=None, description="Nama file struk")
    
    # Tags untuk kategorisasi lebih detail
    tags: Optional[list[str]] = Field(default=[], description="Tags transaksi")
    
    # Financial tracking
    balance_before: Optional[float] = Field(default=None, description="Saldo sebelum transaksi")
    balance_after: Optional[float] = Field(default=None, description="Saldo setelah transaksi")
    
    class Settings:
        name = "transactions"
        indexes = [
            "user_id",
            "category_id",
            "type",
            "date",
            "status",
            "amount",
            [("user_id", 1), ("date", -1)],  # User transactions by date desc
            [("user_id", 1), ("type", 1)],   # User transactions by type
            [("user_id", 1), ("category_id", 1)],  # User transactions by category
            [("date", -1), ("type", 1)],     # All transactions by date and type
        ]
    
    @field_validator("amount")
    @classmethod
    def validate_amount(cls, v):
        """Validasi nominal transaksi"""
        if v <= 0:
            raise ValueError("Nominal transaksi harus lebih dari 0")
        
        # Limit maksimum untuk mencegah input yang tidak realistis
        if v > 1_000_000_000:  # 1 Milyar
            raise ValueError("Nominal transaksi terlalu besar")
        
        # Round ke 2 decimal places
        return round(v, 2)
    
    @field_validator("description")
    @classmethod
    def validate_description(cls, v):
        """Validasi deskripsi transaksi"""
        if not v or not v.strip():
            raise ValueError("Deskripsi transaksi tidak boleh kosong")
        
        # Clean up description
        v = " ".join(v.strip().split())
        
        return v
    
    @field_validator("date")
    @classmethod
    def validate_date(cls, v):
        """Validasi tanggal transaksi"""
        if not v:
            raise ValueError("Tanggal transaksi tidak boleh kosong")
        
        # Tanggal tidak boleh di masa depan
        if v > date.today():
            raise ValueError("Tanggal transaksi tidak boleh di masa depan")
        
        # Tanggal tidak boleh terlalu lama (misalnya 10 tahun)
        min_date = date.today().replace(year=date.today().year - 10)
        if v < min_date:
            raise ValueError("Tanggal transaksi terlalu lama")
        
        return v
    
    @field_validator("time")
    @classmethod
    def validate_time(cls, v):
        """Validasi format waktu"""
        if not v:
            return v
        
        try:
            # Validate HH:MM format
            time_parts = v.split(":")
            if len(time_parts) != 2:
                raise ValueError("Format waktu harus HH:MM")
            
            hour, minute = int(time_parts[0]), int(time_parts[1])
            
            if not (0 <= hour <= 23):
                raise ValueError("Jam harus antara 00-23")
            
            if not (0 <= minute <= 59):
                raise ValueError("Menit harus antara 00-59")
            
            # Return formatted time
            return f"{hour:02d}:{minute:02d}"
            
        except (ValueError, TypeError) as e:
            if "invalid literal" in str(e):
                raise ValueError("Format waktu tidak valid (gunakan HH:MM)")
            raise e
    
    @field_validator("tags")
    @classmethod
    def validate_tags(cls, v):
        """Validasi tags"""
        if not v:
            return []
        
        # Clean up tags
        cleaned_tags = []
        for tag in v:
            if isinstance(tag, str) and tag.strip():
                cleaned_tag = tag.strip().lower()
                if cleaned_tag not in cleaned_tags:  # Remove duplicates
                    cleaned_tags.append(cleaned_tag)
        
        # Limit jumlah tags
        if len(cleaned_tags) > 10:
            raise ValueError("Maksimal 10 tags per transaksi")
        
        return cleaned_tags
    
    @field_validator("location")
    @classmethod
    def validate_location(cls, v):
        """Validasi lokasi"""
        if not v:
            return v
        
        v = v.strip()
        if not v:
            return None
        
        return v
    
    @model_validator(mode="after")
    def validate_transaction_consistency(self):
        """Validasi konsistensi data transaksi"""
        # Pastikan type dan amount konsisten
        if self.type and self.amount:
            if self.type == CategoryType.EXPENSE and self.amount < 0:
                raise ValueError("Nominal expense tidak boleh negatif")
            
            if self.type == CategoryType.INCOME and self.amount < 0:
                raise ValueError("Nominal income tidak boleh negatif")
        
        return self
    
    def is_income(self) -> bool:
        """Check apakah transaksi adalah income"""
        return self.type == CategoryType.INCOME
    
    def is_expense(self) -> bool:
        """Check apakah transaksi adalah expense"""
        return self.type == CategoryType.EXPENSE
    
    def is_completed(self) -> bool:
        """Check apakah transaksi sudah completed"""
        return self.status == TransactionStatus.COMPLETED
    
    def get_effective_amount(self) -> float:
        """Get nominal efektif untuk perhitungan saldo (income +, expense -)"""
        if self.is_income():
            return self.amount
        else:
            return -self.amount
    
    def get_formatted_amount(self) -> str:
        """Get formatted amount dengan currency"""
        return f"Rp {self.amount:,.2f}"
    
    def get_date_time(self) -> datetime:
        """Get combined datetime dari date dan time"""
        if self.time:
            try:
                hour, minute = map(int, self.time.split(":"))
                return datetime.combine(self.date, datetime.min.time().replace(hour=hour, minute=minute))
            except:
                pass
        
        return datetime.combine(self.date, datetime.min.time())
    
    async def complete(self):
        """Mark transaksi sebagai completed"""
        self.status = TransactionStatus.COMPLETED
        await self.save_with_timestamp()
    
    async def cancel(self):
        """Cancel transaksi"""
        self.status = TransactionStatus.CANCELLED
        await self.save_with_timestamp()
    
    async def add_tag(self, tag: str):
        """Tambah tag ke transaksi"""
        tag = tag.strip().lower()
        if tag and tag not in self.tags:
            if len(self.tags) >= 10:
                raise ValueError("Maksimal 10 tags per transaksi")
            self.tags.append(tag)
            await self.save_with_timestamp()
    
    async def remove_tag(self, tag: str):
        """Hapus tag dari transaksi"""
        tag = tag.strip().lower()
        if tag in self.tags:
            self.tags.remove(tag)
            await self.save_with_timestamp()
    
    @classmethod
    async def find_by_user(
        cls, 
        user_id: str, 
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        transaction_type: Optional[CategoryType] = None,
        category_id: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ):
        """Find transactions by user dengan filter"""
        query = {
            "user_id": user_id,
            "is_deleted": {"$ne": True}
        }
        
        # Date filter
        if start_date or end_date:
            date_filter = {}
            if start_date:
                date_filter["$gte"] = start_date
            if end_date:
                date_filter["$lte"] = end_date
            query["date"] = date_filter
        
        # Type filter
        if transaction_type:
            query["type"] = transaction_type
        
        # Category filter
        if category_id:
            query["category_id"] = category_id
        
        return await cls.find(query).sort([("date", -1), ("created_at", -1)]).skip(skip).limit(limit).to_list()
    
    @classmethod
    async def get_user_balance(cls, user_id: str) -> dict:
        """Calculate user balance dari semua transaksi completed"""
        pipeline = [
            {
                "$match": {
                    "user_id": user_id,
                    "status": TransactionStatus.COMPLETED,
                    "is_deleted": {"$ne": True}
                }
            },
            {
                "$group": {
                    "_id": "$type",
                    "total": {"$sum": "$amount"}
                }
            }
        ]
        
        result = await cls.aggregate(pipeline).to_list()
        
        income = 0
        expense = 0
        
        for item in result:
            if item["_id"] == CategoryType.INCOME:
                income = item["total"]
            elif item["_id"] == CategoryType.EXPENSE:
                expense = item["total"]
        
        balance = income - expense
        
        return {
            "income": income,
            "expense": expense,
            "balance": balance
        }
    
    @classmethod
    async def get_monthly_summary(cls, user_id: str, year: int, month: int) -> dict:
        """Get summary transaksi bulanan"""
        start_date = date(year, month, 1)
        
        # Calculate last day of month
        if month == 12:
            end_date = date(year + 1, 1, 1) - datetime.timedelta(days=1)
        else:
            end_date = date(year, month + 1, 1) - datetime.timedelta(days=1)
        
        transactions = await cls.find_by_user(
            user_id=user_id,
            start_date=start_date,
            end_date=end_date
        )
        
        income = sum(t.amount for t in transactions if t.is_income() and t.is_completed())
        expense = sum(t.amount for t in transactions if t.is_expense() and t.is_completed())
        
        return {
            "year": year,
            "month": month,
            "income": income,
            "expense": expense,
            "balance": income - expense,
            "transaction_count": len([t for t in transactions if t.is_completed()]),
            "transactions": [t.to_dict() for t in transactions]
        }
    
    @classmethod
    async def get_category_summary(cls, user_id: str, category_id: str) -> dict:
        """Get summary transaksi per kategori"""
        transactions = await cls.find({
            "user_id": user_id,
            "category_id": category_id,
            "status": TransactionStatus.COMPLETED,
            "is_deleted": {"$ne": True}
        }).to_list()
        
        total_amount = sum(t.amount for t in transactions)
        
        return {
            "category_id": category_id,
            "transaction_count": len(transactions),
            "total_amount": total_amount,
            "latest_transaction": transactions[0].to_dict() if transactions else None
        }