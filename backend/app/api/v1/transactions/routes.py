# app/api/v1/transactions/routes.py
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Form
from fastapi.responses import StreamingResponse
import os
import uuid
from pathlib import Path

from app.models.transaction import (
    Transaction, TransactionCreate, TransactionUpdate, TransactionResponse,
    TransactionFilter, TransactionSort, TransactionListResponse,
    TransactionSummary, CategoryBreakdown, BulkDeleteRequest, BulkDeleteResponse,
    ReceiptUploadResponse, ExportRequest, ExportFormat
)
from app.api.deps import get_current_student, get_database
from app.api.v1.transactions.crud import TransactionCRUD
from app.utils.student_helpers import generate_filename
from motor.motor_asyncio import AsyncIOMotorDatabase

router = APIRouter(tags=["transactions"])

# Helper function to convert Transaction to TransactionResponse
def to_transaction_response(transaction: Transaction) -> TransactionResponse:
    return TransactionResponse(
        _id=transaction.id or "",
        type=transaction.type,
        amount=transaction.amount,
        currency=transaction.currency,
        category_id=transaction.category_id,
        subcategory=transaction.subcategory,
        title=transaction.title,
        notes=transaction.notes,
        transaction_date=transaction.transaction_date,
        created_at=transaction.created_at,
        payment_method=transaction.payment_method,
        account_name=transaction.account_name,
        location=transaction.location,
        receipt_photo=transaction.receipt_photo,
        metadata=transaction.metadata,
        budget_impact=transaction.budget_impact
    )

@router.post("/transactions", response_model=TransactionResponse)
async def create_transaction(
    transaction_data: TransactionCreate,
    current_student: dict = Depends(get_current_student),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Create a new transaction"""
    crud = TransactionCRUD(db)
    
    try:
        transaction = await crud.create_transaction(
            student_id=str(current_student["_id"]), 
            transaction_data=transaction_data
        )
        return to_transaction_response(transaction)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/transactions", response_model=TransactionListResponse)
async def get_transactions(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    type: Optional[str] = Query(None, description="Filter by transaction type (income/expense)"),
    category_id: Optional[str] = Query(None, description="Filter by category ID"),
    payment_method: Optional[str] = Query(None, description="Filter by payment method"),
    start_date: Optional[datetime] = Query(None, description="Filter from date"),
    end_date: Optional[datetime] = Query(None, description="Filter to date"),
    min_amount: Optional[float] = Query(None, ge=0, description="Minimum amount"),
    max_amount: Optional[float] = Query(None, ge=0, description="Maximum amount"),
    search: Optional[str] = Query(None, description="Search in title, notes, account name"),
    sort: TransactionSort = Query(TransactionSort.DATE_DESC, description="Sort order"),
    current_student: dict = Depends(get_current_student),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Get transactions with pagination and filtering"""
    crud = TransactionCRUD(db)
    
    # Create filter object
    filters = TransactionFilter(
        type=type,
        category_id=category_id,
        payment_method=payment_method,
        start_date=start_date,
        end_date=end_date,
        min_amount=min_amount,
        max_amount=max_amount,
        search=search
    )
    
    skip = (page - 1) * limit
    result = await crud.get_transactions(
        student_id=str(current_student["_id"]),
        skip=skip,
        limit=limit,
        filters=filters,
        sort=sort
    )
    
    return TransactionListResponse(
        transactions=[to_transaction_response(t) for t in result["transactions"]],
        total=result["total"],
        page=result["page"],
        limit=result["limit"],
        total_pages=result["total_pages"]
    )

@router.get("/transactions/{transaction_id}", response_model=TransactionResponse)
async def get_transaction(
    transaction_id: str,
    current_student: dict = Depends(get_current_student),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Get a specific transaction"""
    crud = TransactionCRUD(db)
    
    transaction = await crud.get_transaction(
        transaction_id=transaction_id,
        student_id=str(current_student["_id"])
    )
    
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    return to_transaction_response(transaction)

@router.put("/transactions/{transaction_id}", response_model=TransactionResponse)
async def update_transaction(
    transaction_id: str,
    update_data: TransactionUpdate,
    current_student: dict = Depends(get_current_student),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Update a transaction"""
    crud = TransactionCRUD(db)
    
    transaction = await crud.update_transaction(
        transaction_id=transaction_id,
        student_id=str(current_student["_id"]),
        update_data=update_data
    )
    
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    return to_transaction_response(transaction)

@router.delete("/transactions/{transaction_id}")
async def delete_transaction(
    transaction_id: str,
    current_student: dict = Depends(get_current_student),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Delete a transaction"""
    crud = TransactionCRUD(db)
    
    success = await crud.delete_transaction(
        transaction_id=transaction_id,
        student_id=str(current_student["_id"])
    )
    
    if not success:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    return {"message": "Transaction deleted successfully"}

@router.post("/transactions/bulk-delete", response_model=BulkDeleteResponse)
async def bulk_delete_transactions(
    request: BulkDeleteRequest,
    current_student: dict = Depends(get_current_student),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Delete multiple transactions"""
    crud = TransactionCRUD(db)
    
    result = await crud.bulk_delete_transactions(
        transaction_ids=request.transaction_ids,
        student_id=str(current_student["_id"])
    )
    
    return BulkDeleteResponse(**result)

@router.get("/transactions/summary/current", response_model=TransactionSummary)
async def get_current_summary(
    start_date: Optional[datetime] = Query(None, description="Start date"),
    end_date: Optional[datetime] = Query(None, description="End date"),
    current_student: dict = Depends(get_current_student),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Get transaction summary for specified period (defaults to current month)"""
    crud = TransactionCRUD(db)
    
    summary = await crud.get_transaction_summary(
        student_id=str(current_student["_id"]),
        start_date=start_date,
        end_date=end_date
    )
    
    return summary

@router.get("/transactions/breakdown/categories", response_model=List[CategoryBreakdown])
async def get_category_breakdown(
    start_date: Optional[datetime] = Query(None, description="Start date"),
    end_date: Optional[datetime] = Query(None, description="End date"),
    type: Optional[str] = Query(None, description="Transaction type (income/expense)"),
    current_student: dict = Depends(get_current_student),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Get spending breakdown by categories"""
    crud = TransactionCRUD(db)
    
    breakdown = await crud.get_category_breakdown(
        student_id=str(current_student["_id"]),
        start_date=start_date,
        end_date=end_date,
        transaction_type=type
    )
    
    return breakdown

@router.get("/transactions/recent", response_model=List[TransactionResponse])
async def get_recent_transactions(
    limit: int = Query(5, ge=1, le=20, description="Number of recent transactions"),
    current_student: dict = Depends(get_current_student),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Get recent transactions for dashboard"""
    crud = TransactionCRUD(db)
    
    transactions = await crud.get_recent_transactions(
        student_id=str(current_student["_id"]),
        limit=limit
    )
    
    return [to_transaction_response(t) for t in transactions]

@router.get("/transactions/search/{search_term}", response_model=List[TransactionResponse])
async def search_transactions(
    search_term: str,
    limit: int = Query(20, ge=1, le=100, description="Maximum results"),
    current_student: dict = Depends(get_current_student),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Search transactions by title, notes, or account name"""
    crud = TransactionCRUD(db)
    
    transactions = await crud.search_transactions(
        student_id=str(current_student["_id"]),
        search_term=search_term,
        limit=limit
    )
    
    return [to_transaction_response(t) for t in transactions]

@router.post("/transactions/{transaction_id}/receipt", response_model=ReceiptUploadResponse)
async def upload_receipt(
    transaction_id: str,
    file: UploadFile = File(...),
    current_student: dict = Depends(get_current_student),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Upload receipt photo for a transaction"""
    
    # Validate file type
    allowed_types = ["image/jpeg", "image/png", "image/jpg"]
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400, 
            detail="Only JPEG and PNG images are allowed"
        )
    
    # Validate file size (max 5MB)
    if file.size and file.size > 5 * 1024 * 1024:
        raise HTTPException(
            status_code=400,
            detail="File size must be less than 5MB"
        )
    
    try:
        # Generate unique filename
        file_extension = Path(file.filename).suffix
        filename = f"{uuid.uuid4()}{file_extension}"
        
        # Create upload directory if it doesn't exist
        upload_dir = Path("static/uploads/receipts")
        upload_dir.mkdir(parents=True, exist_ok=True)
        
        # Save file
        file_path = upload_dir / filename
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Update transaction with receipt info
        crud = TransactionCRUD(db)
        receipt_data = {
            "filename": filename,
            "url": f"/static/uploads/receipts/{filename}",
            "uploaded_at": datetime.utcnow()
        }
        
        # Update the transaction
        from app.models.transaction import ReceiptPhoto
        receipt_photo = ReceiptPhoto(**receipt_data)
        
        update_data = TransactionUpdate()
        # Note: You might need to modify TransactionUpdate to include receipt_photo
        # For now, we'll update directly in the database
        result = await db.transactions.update_one(
            {"_id": transaction_id, "student_id": str(current_student["_id"])},
            {"$set": {"receipt_photo": receipt_data, "updated_at": datetime.utcnow()}}
        )
        
        if result.modified_count == 0:
            # Clean up uploaded file if transaction update failed
            os.remove(file_path)
            raise HTTPException(status_code=404, detail="Transaction not found")
        
        return ReceiptUploadResponse(**receipt_data)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload receipt: {str(e)}")

@router.delete("/transactions/{transaction_id}/receipt")
async def delete_receipt(
    transaction_id: str,
    current_student: dict = Depends(get_current_student),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Delete receipt photo from a transaction"""
    
    # Get transaction to find receipt filename
    transaction = await db.transactions.find_one({
        "_id": transaction_id,
        "student_id": str(current_student["_id"])
    })
    
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    # Remove receipt from filesystem
    if transaction.get("receipt_photo"):
        filename = transaction["receipt_photo"]["filename"]
        file_path = Path("static/uploads/receipts") / filename
        if file_path.exists():
            os.remove(file_path)
    
    # Update transaction to remove receipt
    result = await db.transactions.update_one(
        {"_id": transaction_id, "student_id": str(current_student["_id"])},
        {"$unset": {"receipt_photo": ""}, "$set": {"updated_at": datetime.utcnow()}}
    )
    
    return {"message": "Receipt deleted successfully"}

# Quick add endpoints for mobile app
@router.post("/transactions/quick/expense", response_model=TransactionResponse)
async def quick_add_expense(
    amount: float = Form(...),
    title: str = Form(...),
    category_id: str = Form(...),
    payment_method: str = Form(...),
    account_name: str = Form(...),
    notes: Optional[str] = Form(None),
    current_student: dict = Depends(get_current_student),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Quick add expense (for mobile widgets)"""
    transaction_data = TransactionCreate(
        type="expense",
        amount=amount,
        title=title,
        category_id=category_id,
        payment_method=payment_method,
        account_name=account_name,
        notes=notes
    )
    
    crud = TransactionCRUD(db)
    transaction = await crud.create_transaction(
        student_id=str(current_student["_id"]),
        transaction_data=transaction_data
    )
    
    return to_transaction_response(transaction)

@router.post("/transactions/quick/income", response_model=TransactionResponse)
async def quick_add_income(
    amount: float = Form(...),
    title: str = Form(...),
    category_id: str = Form(...),
    payment_method: str = Form(...),
    account_name: str = Form(...),
    notes: Optional[str] = Form(None),
    current_student: dict = Depends(get_current_student),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Quick add income (for mobile widgets)"""
    transaction_data = TransactionCreate(
        type="income",
        amount=amount,
        title=title,
        category_id=category_id,
        payment_method=payment_method,
        account_name=account_name,
        notes=notes
    )
    
    crud = TransactionCRUD(db)
    transaction = await crud.create_transaction(
        student_id=str(current_student["_id"]),
        transaction_data=transaction_data
    )
    
    return to_transaction_response(transaction)