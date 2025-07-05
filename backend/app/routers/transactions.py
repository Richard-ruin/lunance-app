# app/routers/transactions.py
from fastapi import APIRouter, HTTPException, Depends, Query, UploadFile, File, BackgroundTasks
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from bson import ObjectId
import csv
import io
import logging

from ..models.transaction import (
    TransactionCreate, TransactionResponse, TransactionUpdate, 
    TransactionListResponse, TransactionSummary
)
from ..middleware.auth_middleware import get_current_verified_user
from ..database import get_database
from ..utils.exceptions import NotFoundException, CustomHTTPException
from ..utils.transaction_helpers import (
    auto_categorize_transaction, detect_duplicate_transaction,
    calculate_user_balance, export_transactions_csv, import_transactions_csv
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/transactions", tags=["Transactions"])

@router.get("/", response_model=TransactionListResponse)
async def list_transactions(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    type: Optional[str] = Query(None, pattern="^(pemasukan|pengeluaran)$"),
    category_id: Optional[str] = Query(None),
    payment_method: Optional[str] = Query(None, pattern="^(cash|transfer|e-wallet|card)$"),
    date_from: Optional[datetime] = Query(None),
    date_to: Optional[datetime] = Query(None),
    amount_min: Optional[float] = Query(None, ge=0),
    amount_max: Optional[float] = Query(None, ge=0),
    search: Optional[str] = Query(None, min_length=1),
    sort_by: str = Query("date", pattern="^(date|amount|description|created_at)$"),
    sort_order: str = Query("desc", pattern="^(asc|desc)$"),
    current_user: Dict[str, Any] = Depends(get_current_verified_user),
    db = Depends(get_database)
):
    """List transactions dengan advanced filtering & pagination"""
    
    # Build filter query
    filter_query = {"user_id": ObjectId(current_user["id"])}
    
    if type:
        filter_query["type"] = type
    if category_id:
        filter_query["category_id"] = ObjectId(category_id)
    if payment_method:
        filter_query["payment_method"] = payment_method
    
    # Date range filter
    if date_from or date_to:
        date_filter = {}
        if date_from:
            date_filter["$gte"] = date_from
        if date_to:
            date_filter["$lte"] = date_to
        filter_query["date"] = date_filter
    
    # Amount range filter
    if amount_min is not None or amount_max is not None:
        amount_filter = {}
        if amount_min is not None:
            amount_filter["$gte"] = amount_min
        if amount_max is not None:
            amount_filter["$lte"] = amount_max
        filter_query["amount"] = amount_filter
    
    # Text search
    if search:
        filter_query["$or"] = [
            {"description": {"$regex": search, "$options": "i"}},
            {"notes": {"$regex": search, "$options": "i"}},
            {"tags": {"$regex": search, "$options": "i"}}
        ]
    
    # Calculate total count
    total_count = await db.transactions.count_documents(filter_query)
    total_pages = (total_count + per_page - 1) // per_page
    
    # Sort configuration
    sort_direction = 1 if sort_order == "asc" else -1
    sort_config = [(sort_by, sort_direction)]
    
    # Get transactions with pagination
    skip = (page - 1) * per_page
    cursor = db.transactions.find(filter_query).sort(sort_config).skip(skip).limit(per_page)
    transactions = await cursor.to_list(length=per_page)
    
    # Get category info for each transaction
    transaction_responses = []
    for trans in transactions:
        # Get category info
        category = await db.categories.find_one({"_id": trans["category_id"]})
        category_info = {
            "id": str(category["_id"]),
            "nama": category["nama_kategori"],
            "icon": category["icon"],
            "color": category["color"]
        } if category else None
        
        transaction_responses.append(TransactionResponse(
            _id=str(trans["_id"]),
            type=trans["type"],
            amount=trans["amount"],
            description=trans["description"],
            category=category_info,
            date=trans["date"],
            payment_method=trans["payment_method"],
            location=trans.get("location"),
            notes=trans.get("notes"),
            receipt_url=trans.get("receipt_url"),
            tags=trans.get("tags", []),
            is_recurring=trans.get("is_recurring", False),
            recurring_config=trans.get("recurring_config"),
            created_at=trans["created_at"]
        ))
    
    # Calculate summary
    summary = await calculate_transaction_summary(current_user["id"], filter_query, db)
    
    return TransactionListResponse(
        data=transaction_responses,
        pagination={
            "total": total_count,
            "page": page,
            "per_page": per_page,
            "total_pages": total_pages
        },
        summary=summary
    )

@router.get("/{transaction_id}", response_model=TransactionResponse)
async def get_transaction_detail(
    transaction_id: str,
    current_user: Dict[str, Any] = Depends(get_current_verified_user),
    db = Depends(get_database)
):
    """Get transaction detail"""
    
    # Get transaction
    transaction = await db.transactions.find_one({
        "_id": ObjectId(transaction_id),
        "user_id": ObjectId(current_user["id"])
    })
    
    if not transaction:
        raise NotFoundException("Transaksi tidak ditemukan")
    
    # Get category info
    category = await db.categories.find_one({"_id": transaction["category_id"]})
    category_info = {
        "id": str(category["_id"]),
        "nama": category["nama_kategori"],
        "icon": category["icon"],
        "color": category["color"]
    } if category else None
    
    return TransactionResponse(
        _id=str(transaction["_id"]),
        type=transaction["type"],
        amount=transaction["amount"],
        description=transaction["description"],
        category=category_info,
        date=transaction["date"],
        payment_method=transaction["payment_method"],
        location=transaction.get("location"),
        notes=transaction.get("notes"),
        receipt_url=transaction.get("receipt_url"),
        tags=transaction.get("tags", []),
        is_recurring=transaction.get("is_recurring", False),
        recurring_config=transaction.get("recurring_config"),
        created_at=transaction["created_at"]
    )

@router.post("/", response_model=TransactionResponse)
async def create_transaction(
    transaction_data: TransactionCreate,
    current_user: Dict[str, Any] = Depends(get_current_verified_user),
    db = Depends(get_database)
):
    """Create new transaction dengan smart features"""
    
    # Validate category exists and accessible
    category = await db.categories.find_one({
        "_id": ObjectId(transaction_data.category_id),
        "$or": [
            {"is_global": True, "is_active": True},
            {"created_by": ObjectId(current_user["id"]), "is_active": True}
        ]
    })
    
    if not category:
        raise CustomHTTPException(
            status_code=400,
            detail="Kategori tidak ditemukan atau tidak dapat diakses",
            error_code="INVALID_CATEGORY"
        )
    
    # Validate category type matches transaction type
    if category["type"] != transaction_data.type:
        raise CustomHTTPException(
            status_code=400,
            detail=f"Tipe kategori ({category['type']}) tidak sesuai dengan tipe transaksi ({transaction_data.type})",
            error_code="CATEGORY_TYPE_MISMATCH"
        )
    
    # Auto-categorization suggestion (if different from selected)
    suggested_category = await auto_categorize_transaction(transaction_data.description, current_user["id"], db)
    if suggested_category and str(suggested_category) != str(transaction_data.category_id):
        logger.info(f"Auto-categorization suggestion: {suggested_category} for '{transaction_data.description}'")
    
    # Duplicate detection
    duplicate = await detect_duplicate_transaction(transaction_data, current_user["id"], db)
    if duplicate:
        raise CustomHTTPException(
            status_code=400,
            detail="Transaksi serupa sudah ada dalam 24 jam terakhir",
            error_code="DUPLICATE_TRANSACTION"
        )
    
    # Create transaction
    from ..models.transaction import Transaction
    transaction = Transaction(
        user_id=ObjectId(current_user["id"]),
        type=transaction_data.type,
        amount=transaction_data.amount,
        description=transaction_data.description,
        category_id=ObjectId(transaction_data.category_id),
        date=transaction_data.date,
        payment_method=transaction_data.payment_method,
        location=transaction_data.location,
        notes=transaction_data.notes,
        tags=transaction_data.tags or [],
        is_recurring=transaction_data.is_recurring,
        recurring_config=transaction_data.recurring_config
    )
    
    result = await db.transactions.insert_one(transaction.model_dump(by_alias=True))
    
    # Update budget spending if applicable
    await update_budget_spending(current_user["id"], ObjectId(transaction_data.category_id), 
                                transaction_data.amount, transaction_data.type, db)
    
    # Get created transaction with category info
    created_transaction = await db.transactions.find_one({"_id": result.inserted_id})
    
    category_info = {
        "id": str(category["_id"]),
        "nama": category["nama_kategori"],
        "icon": category["icon"],
        "color": category["color"]
    }
    
    return TransactionResponse(
        _id=str(created_transaction["_id"]),
        type=created_transaction["type"],
        amount=created_transaction["amount"],
        description=created_transaction["description"],
        category=category_info,
        date=created_transaction["date"],
        payment_method=created_transaction["payment_method"],
        location=created_transaction.get("location"),
        notes=created_transaction.get("notes"),
        receipt_url=created_transaction.get("receipt_url"),
        tags=created_transaction.get("tags", []),
        is_recurring=created_transaction.get("is_recurring", False),
        recurring_config=created_transaction.get("recurring_config"),
        created_at=created_transaction["created_at"]
    )

@router.put("/{transaction_id}", response_model=TransactionResponse)
async def update_transaction(
    transaction_id: str,
    transaction_data: TransactionUpdate,
    current_user: Dict[str, Any] = Depends(get_current_verified_user),
    db = Depends(get_database)
):
    """Update transaction"""
    
    # Check if transaction exists and belongs to user
    existing_transaction = await db.transactions.find_one({
        "_id": ObjectId(transaction_id),
        "user_id": ObjectId(current_user["id"])
    })
    
    if not existing_transaction:
        raise NotFoundException("Transaksi tidak ditemukan")
    
    # Prepare update data
    update_data = {}
    
    # Validate and update category if provided
    if transaction_data.category_id:
        category = await db.categories.find_one({
            "_id": ObjectId(transaction_data.category_id),
            "$or": [
                {"is_global": True, "is_active": True},
                {"created_by": ObjectId(current_user["id"]), "is_active": True}
            ]
        })
        
        if not category:
            raise CustomHTTPException(
                status_code=400,
                detail="Kategori tidak ditemukan atau tidak dapat diakses",
                error_code="INVALID_CATEGORY"
            )
        
        # Validate category type if transaction type is also being updated
        trans_type = transaction_data.type or existing_transaction["type"]
        if category["type"] != trans_type:
            raise CustomHTTPException(
                status_code=400,
                detail=f"Tipe kategori ({category['type']}) tidak sesuai dengan tipe transaksi ({trans_type})",
                error_code="CATEGORY_TYPE_MISMATCH"
            )
        
        update_data["category_id"] = ObjectId(transaction_data.category_id)
    
    # Update other fields
    for field in ["type", "amount", "description", "date", "payment_method", "location", "notes", "tags"]:
        value = getattr(transaction_data, field, None)
        if value is not None:
            update_data[field] = value
    
    if update_data:
        update_data["updated_at"] = datetime.utcnow()
        await db.transactions.update_one(
            {"_id": ObjectId(transaction_id)},
            {"$set": update_data}
        )
        
        # Update budget spending if amount or category changed
        if "amount" in update_data or "category_id" in update_data:
            old_amount = existing_transaction["amount"]
            old_category = existing_transaction["category_id"]
            old_type = existing_transaction["type"]
            
            new_amount = update_data.get("amount", old_amount)
            new_category = update_data.get("category_id", old_category)
            new_type = update_data.get("type", old_type)
            
            # Revert old budget impact
            await update_budget_spending(current_user["id"], old_category, -old_amount, old_type, db)
            # Apply new budget impact
            await update_budget_spending(current_user["id"], new_category, new_amount, new_type, db)
    
    # Get updated transaction with category info
    updated_transaction = await db.transactions.find_one({"_id": ObjectId(transaction_id)})
    category = await db.categories.find_one({"_id": updated_transaction["category_id"]})
    
    category_info = {
        "id": str(category["_id"]),
        "nama": category["nama_kategori"],
        "icon": category["icon"],
        "color": category["color"]
    } if category else None
    
    return TransactionResponse(
        _id=str(updated_transaction["_id"]),
        type=updated_transaction["type"],
        amount=updated_transaction["amount"],
        description=updated_transaction["description"],
        category=category_info,
        date=updated_transaction["date"],
        payment_method=updated_transaction["payment_method"],
        location=updated_transaction.get("location"),
        notes=updated_transaction.get("notes"),
        receipt_url=updated_transaction.get("receipt_url"),
        tags=updated_transaction.get("tags", []),
        is_recurring=updated_transaction.get("is_recurring", False),
        recurring_config=updated_transaction.get("recurring_config"),
        created_at=updated_transaction["created_at"]
    )

@router.delete("/{transaction_id}")
async def delete_transaction(
    transaction_id: str,
    current_user: Dict[str, Any] = Depends(get_current_verified_user),
    db = Depends(get_database)
):
    """Delete transaction"""
    
    # Check if transaction exists and belongs to user
    transaction = await db.transactions.find_one({
        "_id": ObjectId(transaction_id),
        "user_id": ObjectId(current_user["id"])
    })
    
    if not transaction:
        raise NotFoundException("Transaksi tidak ditemukan")
    
    # Revert budget impact
    await update_budget_spending(
        current_user["id"], 
        transaction["category_id"], 
        -transaction["amount"], 
        transaction["type"], 
        db
    )
    
    # Delete transaction
    await db.transactions.delete_one({"_id": ObjectId(transaction_id)})
    
    return {"message": "Transaksi berhasil dihapus"}

@router.post("/bulk", response_model=List[TransactionResponse])
async def bulk_create_transactions(
    transactions_data: List[TransactionCreate],
    current_user: Dict[str, Any] = Depends(get_current_verified_user),
    db = Depends(get_database)
):
    """Bulk create transactions"""
    
    if len(transactions_data) > 100:
        raise CustomHTTPException(
            status_code=400,
            detail="Maksimal 100 transaksi per bulk operation",
            error_code="BULK_LIMIT_EXCEEDED"
        )
    
    created_transactions = []
    
    for trans_data in transactions_data:
        try:
            # Validate category
            category = await db.categories.find_one({
                "_id": ObjectId(trans_data.category_id),
                "$or": [
                    {"is_global": True, "is_active": True},
                    {"created_by": ObjectId(current_user["id"]), "is_active": True}
                ]
            })
            
            if not category or category["type"] != trans_data.type:
                continue  # Skip invalid transactions
            
            # Create transaction
            from ..models.transaction import Transaction
            transaction = Transaction(
                user_id=ObjectId(current_user["id"]),
                type=trans_data.type,
                amount=trans_data.amount,
                description=trans_data.description,
                category_id=ObjectId(trans_data.category_id),
                date=trans_data.date,
                payment_method=trans_data.payment_method,
                location=trans_data.location,
                notes=trans_data.notes,
                tags=trans_data.tags or []
            )
            
            result = await db.transactions.insert_one(transaction.model_dump(by_alias=True))
            
            # Update budget
            await update_budget_spending(current_user["id"], ObjectId(trans_data.category_id), 
                                        trans_data.amount, trans_data.type, db)
            
            # Get created transaction
            created_transaction = await db.transactions.find_one({"_id": result.inserted_id})
            
            category_info = {
                "id": str(category["_id"]),
                "nama": category["nama_kategori"],
                "icon": category["icon"],
                "color": category["color"]
            }
            
            created_transactions.append(TransactionResponse(
                _id=str(created_transaction["_id"]),
                type=created_transaction["type"],
                amount=created_transaction["amount"],
                description=created_transaction["description"],
                category=category_info,
                date=created_transaction["date"],
                payment_method=created_transaction["payment_method"],
                location=created_transaction.get("location"),
                notes=created_transaction.get("notes"),
                receipt_url=created_transaction.get("receipt_url"),
                tags=created_transaction.get("tags", []),
                is_recurring=created_transaction.get("is_recurring", False),
                recurring_config=created_transaction.get("recurring_config"),
                created_at=created_transaction["created_at"]
            ))
            
        except Exception as e:
            logger.error(f"Error creating transaction in bulk: {e}")
            continue
    
    return created_transactions

@router.get("/summary", response_model=Dict[str, Any])
async def get_transaction_summary(
    period: str = Query("monthly", pattern="^(daily|weekly|monthly)$"),
    date_from: Optional[datetime] = Query(None),
    date_to: Optional[datetime] = Query(None),
    current_user: Dict[str, Any] = Depends(get_current_verified_user),
    db = Depends(get_database)
):
    """Get transaction summary by period"""
    
    # Calculate date range based on period
    now = datetime.utcnow()
    if not date_from or not date_to:
        if period == "daily":
            date_from = now.replace(hour=0, minute=0, second=0, microsecond=0)
            date_to = date_from + timedelta(days=1)
        elif period == "weekly":
            days_since_monday = now.weekday()
            date_from = (now - timedelta(days=days_since_monday)).replace(hour=0, minute=0, second=0, microsecond=0)
            date_to = date_from + timedelta(days=7)
        else:  # monthly
            date_from = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            if now.month == 12:
                date_to = date_from.replace(year=now.year + 1, month=1)
            else:
                date_to = date_from.replace(month=now.month + 1)
    
    # Get transactions in period
    filter_query = {
        "user_id": ObjectId(current_user["id"]),
        "date": {"$gte": date_from, "$lt": date_to}
    }
    
    # Calculate summary
    pipeline = [
        {"$match": filter_query},
        {
            "$group": {
                "_id": "$type",
                "total": {"$sum": "$amount"},
                "count": {"$sum": 1}
            }
        }
    ]
    
    results = await db.transactions.aggregate(pipeline).to_list(length=None)
    
    summary = {
        "period": period,
        "date_from": date_from,
        "date_to": date_to,
        "total_pemasukan": 0,
        "total_pengeluaran": 0,
        "count_pemasukan": 0,
        "count_pengeluaran": 0,
        "balance": 0
    }
    
    for result in results:
        if result["_id"] == "pemasukan":
            summary["total_pemasukan"] = result["total"]
            summary["count_pemasukan"] = result["count"]
        else:
            summary["total_pengeluaran"] = result["total"]
            summary["count_pengeluaran"] = result["count"]
    
    summary["balance"] = summary["total_pemasukan"] - summary["total_pengeluaran"]
    
    return summary