"""
Transaction Schemas
Schemas untuk transaksi keuangan (income & expense)
"""

from datetime import datetime, date
from typing import Optional
from pydantic import Field, field_validator
from enum import Enum

from .base import BaseSchema, BaseResponse, BaseCreate, BaseUpdate, BaseFilter
from ..models.transaction import TransactionStatus
from ..models.category import CategoryType


# Enums for schemas
class TransactionTypeSchema(str, Enum):
    INCOME = "income"
    EXPENSE = "expense"


class TransactionStatusSchema(str, Enum):
    COMPLETED = "completed"
    PENDING = "pending"
    CANCELLED = "cancelled"


# Base Transaction Schema
class TransactionBase(BaseSchema):
    """Base transaction schema"""
    amount: float = Field(..., gt=0, description="Jumlah nominal")
    description: str = Field(..., min_length=1, max_length=500, description="Deskripsi transaksi")
    date: date = Field(..., description="Tanggal transaksi")
    time: Optional[str] = Field(default=None, description="Waktu transaksi (HH:MM)")
    location: Optional[str] = Field(default=None, max_length=200, description="Lokasi transaksi")
    notes: Optional[str] = Field(default=None, max_length=1000, description="Catatan tambahan")
    tags: Optional[list[str]] = Field(default=[], description="Tags transaksi")
    
    @field_validator("amount")
    @classmethod
    def validate_amount(cls, v):
        """Validasi nominal transaksi"""
        if v <= 0:
            raise ValueError("Nominal transaksi harus lebih dari 0")
        
        if v > 1_000_000_000:  # 1 Milyar
            raise ValueError("Nominal transaksi terlalu besar")
        
        return round(v, 2)
    
    @field_validator("date")
    @classmethod
    def validate_date(cls, v):
        """Validasi tanggal transaksi"""
        if v > date.today():
            raise ValueError("Tanggal transaksi tidak boleh di masa depan")
        
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
            time_parts = v.split(":")
            if len(time_parts) != 2:
                raise ValueError("Format waktu harus HH:MM")
            
            hour, minute = int(time_parts[0]), int(time_parts[1])
            
            if not (0 <= hour <= 23):
                raise ValueError("Jam harus antara 00-23")
            
            if not (0 <= minute <= 59):
                raise ValueError("Menit harus antara 00-59")
            
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
        
        cleaned_tags = []
        for tag in v:
            if isinstance(tag, str) and tag.strip():
                cleaned_tag = tag.strip().lower()
                if cleaned_tag not in cleaned_tags:
                    cleaned_tags.append(cleaned_tag)
        
        if len(cleaned_tags) > 10:
            raise ValueError("Maksimal 10 tags per transaksi")
        
        return cleaned_tags


class TransactionCreate(TransactionBase):
    """Schema untuk create transaction"""
    category_id: str = Field(..., description="ID Kategori")
    type: TransactionTypeSchema = Field(..., description="Tipe transaksi")
    status: TransactionStatusSchema = Field(default=TransactionStatusSchema.COMPLETED, description="Status transaksi")


class TransactionUpdate(BaseSchema):
    """Schema untuk update transaction"""
    amount: Optional[float] = Field(default=None, gt=0, description="Jumlah nominal")
    description: Optional[str] = Field(default=None, min_length=1, max_length=500, description="Deskripsi")
    category_id: Optional[str] = Field(default=None, description="ID Kategori")
    date: Optional[date] = Field(default=None, description="Tanggal transaksi")
    time: Optional[str] = Field(default=None, description="Waktu transaksi")
    location: Optional[str] = Field(default=None, max_length=200, description="Lokasi")
    notes: Optional[str] = Field(default=None, max_length=1000, description="Catatan")
    tags: Optional[list[str]] = Field(default=None, description="Tags")
    status: Optional[TransactionStatusSchema] = Field(default=None, description="Status")
    
    @field_validator("amount")
    @classmethod
    def validate_amount(cls, v):
        if v is not None:
            if v <= 0:
                raise ValueError("Nominal harus lebih dari 0")
            if v > 1_000_000_000:
                raise ValueError("Nominal terlalu besar")
            return round(v, 2)
        return v
    
    @field_validator("date")
    @classmethod
    def validate_date(cls, v):
        if v is not None:
            if v > date.today():
                raise ValueError("Tanggal tidak boleh di masa depan")
        return v


class TransactionResponse(TransactionBase, BaseResponse):
    """Schema untuk response transaction"""
    user_id: str = Field(..., description="ID User")
    category_id: str = Field(..., description="ID Kategori")
    type: TransactionTypeSchema = Field(..., description="Tipe transaksi")
    status: TransactionStatusSchema = Field(..., description="Status transaksi")
    receipt_url: Optional[str] = Field(default=None, description="URL struk")
    receipt_filename: Optional[str] = Field(default=None, description="Nama file struk")
    balance_before: Optional[float] = Field(default=None, description="Saldo sebelum")
    balance_after: Optional[float] = Field(default=None, description="Saldo setelah")


class TransactionDetailResponse(TransactionResponse):
    """Schema untuk response transaction detail dengan category info"""
    category_name: Optional[str] = Field(default=None, description="Nama kategori")
    category_icon: Optional[str] = Field(default=None, description="Icon kategori")
    category_color: Optional[str] = Field(default=None, description="Warna kategori")
    formatted_amount: Optional[str] = Field(default=None, description="Nominal terformat")


# Filter Schemas
class TransactionFilter(BaseFilter):
    """Schema untuk filter transaction"""
    user_id: Optional[str] = Field(default=None, description="Filter user")
    category_id: Optional[str] = Field(default=None, description="Filter kategori")
    type: Optional[TransactionTypeSchema] = Field(default=None, description="Filter tipe")
    status: Optional[TransactionStatusSchema] = Field(default=None, description="Filter status")
    start_date: Optional[date] = Field(default=None, description="Tanggal mulai")
    end_date: Optional[date] = Field(default=None, description="Tanggal akhir")
    min_amount: Optional[float] = Field(default=None, ge=0, description="Nominal minimum")
    max_amount: Optional[float] = Field(default=None, ge=0, description="Nominal maksimum")
    location: Optional[str] = Field(default=None, description="Filter lokasi")
    tags: Optional[list[str]] = Field(default=None, description="Filter tags")


class TransactionUserFilter(BaseSchema):
    """Schema untuk filter transaction user"""
    category_id: Optional[str] = Field(default=None, description="Filter kategori")
    type: Optional[TransactionTypeSchema] = Field(default=None, description="Filter tipe")
    start_date: Optional[date] = Field(default=None, description="Tanggal mulai")
    end_date: Optional[date] = Field(default=None, description="Tanggal akhir")
    page: int = Field(default=1, ge=1, description="Halaman")
    per_page: int = Field(default=10, ge=1, le=100, description="Item per halaman")


# Bulk Operations
class TransactionBulkCreate(BaseSchema):
    """Schema untuk bulk create transactions"""
    transactions: list[TransactionCreate] = Field(..., min_length=1, description="List transaksi")


class TransactionBulkUpdate(BaseSchema):
    """Schema untuk bulk update transactions"""
    transaction_ids: list[str] = Field(..., min_length=1, description="List ID transaksi")
    data: TransactionUpdate = Field(..., description="Data untuk update")


class TransactionBulkStatusUpdate(BaseSchema):
    """Schema untuk bulk update status transactions"""
    transaction_ids: list[str] = Field(..., min_length=1, description="List ID transaksi")
    status: TransactionStatusSchema = Field(..., description="Status baru")


class TransactionBulkDelete(BaseSchema):
    """Schema untuk bulk delete transactions"""
    transaction_ids: list[str] = Field(..., min_length=1, description="List ID transaksi")
    permanent: bool = Field(default=False, description="Hapus permanen")


# Statistics & Analytics
class TransactionStatsResponse(BaseSchema):
    """Schema untuk statistik transaksi"""
    total_transactions: int = Field(..., description="Total transaksi")
    total_income: float = Field(..., description="Total income")
    total_expense: float = Field(..., description="Total expense")
    current_balance: float = Field(..., description="Saldo saat ini")
    transaction_count_by_type: dict = Field(..., description="Jumlah transaksi per tipe")
    average_transaction_amount: float = Field(..., description="Rata-rata nominal transaksi")


class MonthlyTransactionSummary(BaseSchema):
    """Schema untuk summary transaksi bulanan"""
    year: int = Field(..., description="Tahun")
    month: int = Field(..., description="Bulan")
    income: float = Field(..., description="Total income")
    expense: float = Field(..., description="Total expense")
    balance: float = Field(..., description="Balance bulan ini")
    transaction_count: int = Field(..., description="Jumlah transaksi")
    top_categories: list[dict] = Field(..., description="Kategori teratas")


class CategoryTransactionSummary(BaseSchema):
    """Schema untuk summary transaksi per kategori"""
    category_id: str = Field(..., description="ID kategori")
    category_name: str = Field(..., description="Nama kategori")
    transaction_count: int = Field(..., description="Jumlah transaksi")
    total_amount: float = Field(..., description="Total nominal")
    percentage_of_total: float = Field(..., description="Persentase dari total")
    latest_transaction: Optional[TransactionResponse] = Field(default=None, description="Transaksi terakhir")


class TransactionAnalytics(BaseSchema):
    """Schema untuk analytics transaksi"""
    period: str = Field(..., description="Periode analisis")
    total_income: float = Field(..., description="Total income")
    total_expense: float = Field(..., description="Total expense")
    net_income: float = Field(..., description="Net income")
    daily_average: float = Field(..., description="Rata-rata harian")
    monthly_trend: list[dict] = Field(..., description="Trend bulanan")
    category_breakdown: list[CategoryTransactionSummary] = Field(..., description="Breakdown kategori")
    spending_patterns: dict = Field(..., description="Pola pengeluaran")


# File Upload
class TransactionReceiptUpload(BaseSchema):
    """Schema untuk upload receipt"""
    transaction_id: str = Field(..., description="ID transaksi")


class TransactionReceiptResponse(BaseSchema):
    """Schema untuk response upload receipt"""
    transaction_id: str = Field(..., description="ID transaksi")
    receipt_url: str = Field(..., description="URL receipt")
    receipt_filename: str = Field(..., description="Nama file")
    file_size: int = Field(..., description="Ukuran file")
    uploaded_at: datetime = Field(..., description="Waktu upload")


# Import/Export
class TransactionExport(BaseSchema):
    """Schema untuk export transactions"""
    start_date: Optional[date] = Field(default=None, description="Tanggal mulai")
    end_date: Optional[date] = Field(default=None, description="Tanggal akhir")
    category_ids: Optional[list[str]] = Field(default=None, description="Filter kategori")
    transaction_type: Optional[TransactionTypeSchema] = Field(default=None, description="Filter tipe")
    format: str = Field(default="csv", pattern="^(csv|xlsx|json)$", description="Format export")
    include_receipts: bool = Field(default=False, description="Include receipt URLs")


class TransactionImport(BaseSchema):
    """Schema untuk import transactions"""
    transactions: list[TransactionCreate] = Field(..., min_length=1, description="List transaksi")
    validate_categories: bool = Field(default=True, description="Validasi kategori exists")
    create_missing_categories: bool = Field(default=False, description="Buat kategori yang belum ada")


class TransactionImportResponse(BaseSchema):
    """Schema untuk response import transactions"""
    success: bool = Field(..., description="Status import")
    message: str = Field(..., description="Pesan")
    imported_count: int = Field(..., description="Berhasil diimport")
    skipped_count: int = Field(..., description="Dilewati")
    error_count: int = Field(..., description="Error")
    errors: list[dict] = Field(..., description="Detail error")
    created_categories: list[str] = Field(..., description="Kategori baru dibuat")


# Balance & Financial Health
class BalanceResponse(BaseSchema):
    """Schema untuk response balance"""
    current_balance: float = Field(..., description="Saldo saat ini")
    total_income: float = Field(..., description="Total income")
    total_expense: float = Field(..., description="Total expense")
    last_transaction: Optional[TransactionResponse] = Field(default=None, description="Transaksi terakhir")
    balance_trend: str = Field(..., description="Trend saldo (increasing/decreasing/stable)")


class FinancialHealthScore(BaseSchema):
    """Schema untuk financial health score"""
    score: float = Field(..., ge=0, le=100, description="Skor kesehatan keuangan (0-100)")
    grade: str = Field(..., description="Grade (A-F)")
    factors: dict = Field(..., description="Faktor-faktor yang mempengaruhi")
    recommendations: list[str] = Field(..., description="Rekomendasi perbaikan")
    comparison_data: dict = Field(..., description="Perbandingan dengan user lain")