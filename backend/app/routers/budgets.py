# app/routers/budgets.py
from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from bson import ObjectId

from ..models.budget import BudgetCreate, BudgetResponse, BudgetUpdate
from ..middleware.auth_middleware import get_current_verified_user
from ..database import get_database
from ..utils.exceptions import NotFoundException, CustomHTTPException
from ..utils.budget_helpers import calculate_budget_alerts, generate_budget_recommendations

router = APIRouter(prefix="/budgets", tags=["Budget Management"])

@router.get("/", response_model=List[BudgetResponse])
async def list_user_budgets(
    is_active: bool = Query(True),
    period: Optional[str] = Query(None, pattern="^(weekly|monthly)$"),
    current_user: Dict[str, Any] = Depends(get_current_verified_user),
    db = Depends(get_database)
):
    """List user budgets dengan real-time spending calculation"""
    
    filter_query = {
        "user_id": ObjectId(current_user["id"]),
        "is_active": is_active
    }
    
    if period:
        filter_query["period"] = period
    
    budgets = await db.budgets.find(filter_query).sort("created_at", -1).to_list(length=None)
    
    budget_responses = []
    for budget in budgets:
        # Get category info
        category = await db.categories.find_one({"_id": budget["category_id"]})
        category_info = {
            "id": str(category["_id"]),
            "nama": category["nama_kategori"],
            "icon": category["icon"],
            "color": category["color"]
        } if category else None
        
        # Calculate real-time spending
        spent = await calculate_budget_spending(
            current_user["id"], budget["category_id"], 
            budget["start_date"], budget["end_date"], db
        )
        
        remaining = max(0, budget["amount"] - spent)
        percentage_used = (spent / budget["amount"] * 100) if budget["amount"] > 0 else 0
        
        budget_responses.append(BudgetResponse(
            _id=str(budget["_id"]),
            category=category_info,
            amount=budget["amount"],
            period=budget["period"],
            start_date=budget["start_date"],
            end_date=budget["end_date"],
            spent=spent,
            remaining=remaining,
            percentage_used=round(percentage_used, 2),
            is_active=budget["is_active"],
            created_at=budget["created_at"]
        ))
    
    return budget_responses

@router.post("/", response_model=BudgetResponse)
async def create_budget(
    budget_data: BudgetCreate,
    current_user: Dict[str, Any] = Depends(get_current_verified_user),
    db = Depends(get_database)
):
    """Create new budget dengan validation"""
    
    # Validate category exists and accessible
    category = await db.categories.find_one({
        "_id": ObjectId(budget_data.category_id),
        "type": "pengeluaran",  # Only expense categories can have budgets
        "$or": [
            {"is_global": True, "is_active": True},
            {"created_by": ObjectId(current_user["id"]), "is_active": True}
        ]
    })
    
    if not category:
        raise CustomHTTPException(
            status_code=400,
            detail="Kategori tidak ditemukan atau bukan kategori pengeluaran",
            error_code="INVALID_CATEGORY"
        )
    
    # Check for overlapping budgets
    overlapping = await db.budgets.find_one({
        "user_id": ObjectId(current_user["id"]),
        "category_id": ObjectId(budget_data.category_id),
        "is_active": True,
        "$or": [
            {
                "start_date": {"$lte": budget_data.start_date},
                "end_date": {"$gte": budget_data.start_date}
            },
            {
                "start_date": {"$lte": budget_data.end_date},
                "end_date": {"$gte": budget_data.end_date}
            },
            {
                "start_date": {"$gte": budget_data.start_date},
                "end_date": {"$lte": budget_data.end_date}
            }
        ]
    })
    
    if overlapping:
        raise CustomHTTPException(
            status_code=400,
            detail="Budget untuk kategori ini sudah ada pada periode yang tumpang tindih",
            error_code="OVERLAPPING_BUDGET"
        )
    
    # Create budget
    from ..models.budget import Budget
    budget = Budget(
        user_id=ObjectId(current_user["id"]),
        category_id=ObjectId(budget_data.category_id),
        amount=budget_data.amount,
        period=budget_data.period,
        start_date=budget_data.start_date,
        end_date=budget_data.end_date,
        spent=0.0,
        is_active=True
    )
    
    result = await db.budgets.insert_one(budget.model_dump(by_alias=True))
    
    # Calculate initial spending
    spent = await calculate_budget_spending(
        current_user["id"], ObjectId(budget_data.category_id),
        budget_data.start_date, budget_data.end_date, db
    )
    
    # Update budget with actual spending
    await db.budgets.update_one(
        {"_id": result.inserted_id},
        {"$set": {"spent": spent}}
    )
    
    # Prepare response
    category_info = {
        "id": str(category["_id"]),
        "nama": category["nama_kategori"],
        "icon": category["icon"],
        "color": category["color"]
    }
    
    remaining = max(0, budget_data.amount - spent)
    percentage_used = (spent / budget_data.amount * 100) if budget_data.amount > 0 else 0
    
    return BudgetResponse(
        _id=str(result.inserted_id),
        category=category_info,
        amount=budget_data.amount,
        period=budget_data.period,
        start_date=budget_data.start_date,
        end_date=budget_data.end_date,
        spent=spent,
        remaining=remaining,
        percentage_used=round(percentage_used, 2),
        is_active=True,
        created_at=datetime.utcnow()
    )

@router.put("/{budget_id}", response_model=BudgetResponse)
async def update_budget(
    budget_id: str,
    budget_data: BudgetUpdate,
    current_user: Dict[str, Any] = Depends(get_current_verified_user),
    db = Depends(get_database)
):
    """Update budget"""
    
    # Check if budget exists and belongs to user
    budget = await db.budgets.find_one({
        "_id": ObjectId(budget_id),
        "user_id": ObjectId(current_user["id"])
    })
    
    if not budget:
        raise NotFoundException("Budget tidak ditemukan")
    
    # Prepare update data
    update_data = {}
    
    for field in ["amount", "period", "start_date", "end_date", "is_active"]:
        value = getattr(budget_data, field, None)
        if value is not None:
            update_data[field] = value
    
    # Validate date range if dates are being updated
    if "start_date" in update_data or "end_date" in update_data:
        start_date = update_data.get("start_date", budget["start_date"])
        end_date = update_data.get("end_date", budget["end_date"])
        
        if end_date <= start_date:
            raise CustomHTTPException(
                status_code=400,
                detail="End date harus setelah start date",
                error_code="INVALID_DATE_RANGE"
            )
        
        # Check for overlapping budgets (excluding current budget)
        overlapping = await db.budgets.find_one({
            "user_id": ObjectId(current_user["id"]),
            "category_id": budget["category_id"],
            "is_active": True,
            "_id": {"$ne": ObjectId(budget_id)},
            "$or": [
                {
                    "start_date": {"$lte": start_date},
                    "end_date": {"$gte": start_date}
                },
                {
                    "start_date": {"$lte": end_date},
                    "end_date": {"$gte": end_date}
                },
                {
                    "start_date": {"$gte": start_date},
                    "end_date": {"$lte": end_date}
                }
            ]
        })
        
        if overlapping:
            raise CustomHTTPException(
                status_code=400,
                detail="Budget periode ini akan tumpang tindih dengan budget lain",
                error_code="OVERLAPPING_BUDGET"
            )
    
    if update_data:
        update_data["updated_at"] = datetime.utcnow()
        await db.budgets.update_one(
            {"_id": ObjectId(budget_id)},
            {"$set": update_data}
        )
    
    # Get updated budget
    updated_budget = await db.budgets.find_one({"_id": ObjectId(budget_id)})
    
    # Recalculate spending if date range changed
    if "start_date" in update_data or "end_date" in update_data:
        spent = await calculate_budget_spending(
            current_user["id"], updated_budget["category_id"],
            updated_budget["start_date"], updated_budget["end_date"], db
        )
        
        await db.budgets.update_one(
            {"_id": ObjectId(budget_id)},
            {"$set": {"spent": spent}}
        )
        updated_budget["spent"] = spent
    
    # Get category info
    category = await db.categories.find_one({"_id": updated_budget["category_id"]})
    category_info = {
        "id": str(category["_id"]),
        "nama": category["nama_kategori"],
        "icon": category["icon"],
        "color": category["color"]
    } if category else None
    
    remaining = max(0, updated_budget["amount"] - updated_budget["spent"])
    percentage_used = (updated_budget["spent"] / updated_budget["amount"] * 100) if updated_budget["amount"] > 0 else 0
    
    return BudgetResponse(
        _id=str(updated_budget["_id"]),
        category=category_info,
        amount=updated_budget["amount"],
        period=updated_budget["period"],
        start_date=updated_budget["start_date"],
        end_date=updated_budget["end_date"],
        spent=updated_budget["spent"],
        remaining=remaining,
        percentage_used=round(percentage_used, 2),
        is_active=updated_budget["is_active"],
        created_at=updated_budget["created_at"]
    )

@router.delete("/{budget_id}")
async def delete_budget(
    budget_id: str,
    current_user: Dict[str, Any] = Depends(get_current_verified_user),
    db = Depends(get_database)
):
    """Delete budget"""
    
    # Check if budget exists and belongs to user
    budget = await db.budgets.find_one({
        "_id": ObjectId(budget_id),
        "user_id": ObjectId(current_user["id"])
    })
    
    if not budget:
        raise NotFoundException("Budget tidak ditemukan")
    
    # Soft delete (deactivate)
    await db.budgets.update_one(
        {"_id": ObjectId(budget_id)},
        {"$set": {"is_active": False, "updated_at": datetime.utcnow()}}
    )
    
    return {"message": "Budget berhasil dihapus"}

@router.get("/alerts", response_model=Dict[str, Any])
async def get_budget_alerts(
    current_user: Dict[str, Any] = Depends(get_current_verified_user),
    db = Depends(get_database)
):
    """Get budget alerts & warnings"""
    
    # Get active budgets
    now = datetime.utcnow()
    active_budgets = await db.budgets.find({
        "user_id": ObjectId(current_user["id"]),
        "is_active": True,
        "start_date": {"$lte": now},
        "end_date": {"$gte": now}
    }).to_list(length=None)
    
    alerts = {
        "critical": [],  # >100% spent
        "warning": [],   # 80-100% spent
        "caution": [],   # 60-80% spent
        "on_track": [],  # <60% spent
        "summary": {
            "total_budgets": len(active_budgets),
            "over_budget": 0,
            "near_limit": 0,
            "total_budget_amount": 0,
            "total_spent": 0
        }
    }
    
    for budget in active_budgets:
        # Calculate real-time spending
        spent = await calculate_budget_spending(
            current_user["id"], budget["category_id"],
            budget["start_date"], budget["end_date"], db
        )
        
        # Update budget spending
        await db.budgets.update_one(
            {"_id": budget["_id"]},
            {"$set": {"spent": spent, "updated_at": datetime.utcnow()}}
        )
        
        # Get category info
        category = await db.categories.find_one({"_id": budget["category_id"]})
        
        percentage_used = (spent / budget["amount"] * 100) if budget["amount"] > 0 else 0
        remaining = budget["amount"] - spent
        days_remaining = (budget["end_date"] - now).days
        
        budget_alert = {
            "budget_id": str(budget["_id"]),
            "category": {
                "id": str(category["_id"]),
                "nama": category["nama_kategori"],
                "icon": category["icon"],
                "color": category["color"]
            } if category else None,
            "amount": budget["amount"],
            "spent": spent,
            "remaining": remaining,
            "percentage_used": round(percentage_used, 2),
            "days_remaining": max(0, days_remaining),
            "period": budget["period"],
            "status": "on_track"
        }
        
        # Categorize alerts
        if percentage_used >= 100:
            budget_alert["status"] = "critical"
            alerts["critical"].append(budget_alert)
            alerts["summary"]["over_budget"] += 1
        elif percentage_used >= 80:
            budget_alert["status"] = "warning"
            alerts["warning"].append(budget_alert)
            alerts["summary"]["near_limit"] += 1
        elif percentage_used >= 60:
            budget_alert["status"] = "caution"
            alerts["caution"].append(budget_alert)
        else:
            alerts["on_track"].append(budget_alert)
        
        alerts["summary"]["total_budget_amount"] += budget["amount"]
        alerts["summary"]["total_spent"] += spent
    
    # Calculate summary percentages
    if alerts["summary"]["total_budget_amount"] > 0:
        alerts["summary"]["overall_percentage"] = round(
            (alerts["summary"]["total_spent"] / alerts["summary"]["total_budget_amount"]) * 100, 2
        )
    else:
        alerts["summary"]["overall_percentage"] = 0
    
    # Add recommendations
    alerts["recommendations"] = await generate_budget_recommendations(current_user["id"], active_budgets, db)
    
    return alerts

# Helper functions
async def calculate_budget_spending(user_id: str, category_id: ObjectId, start_date: datetime, end_date: datetime, db) -> float:
    """Calculate total spending for a budget period"""
    
    pipeline = [
        {
            "$match": {
                "user_id": ObjectId(user_id),
                "category_id": category_id,
                "type": "pengeluaran",
                "date": {
                    "$gte": start_date,
                    "$lte": end_date
                }
            }
        },
        {
            "$group": {
                "_id": None,
                "total_spent": {"$sum": "$amount"}
            }
        }
    ]
    
    result = await db.transactions.aggregate(pipeline).to_list(length=1)
    return result[0]["total_spent"] if result else 0.0