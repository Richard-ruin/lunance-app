# app/routers/savings_goals.py
from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any, List
from datetime import datetime, timedelta
from bson import ObjectId

from ..database import get_database
from ..middleware.auth_middleware import get_current_verified_user
from ..models.savings_goal import (
    SavingsGoal, SavingsGoalCreate, SavingsGoalUpdate, 
    SavingsGoalResponse, GoalDeposit, GoalWithdraw
)
from ..utils.exceptions import CustomHTTPException

router = APIRouter(prefix="/savings-goals", tags=["Savings Goals"])

@router.get("/", response_model=List[SavingsGoalResponse])
async def list_savings_goals(
    current_user: Dict[str, Any] = Depends(get_current_verified_user)
):
    """List user's savings goals"""
    try:
        db = await get_database()
        user_id = ObjectId(current_user["id"])
        
        goals = await db.savings_goals.find({"user_id": user_id}).to_list(100)
        
        goal_responses = []
        for goal in goals:
            # Calculate progress metrics
            progress_percentage = (goal["current_amount"] / goal["target_amount"]) * 100 if goal["target_amount"] > 0 else 0
            days_left = (goal["target_date"] - datetime.now()).days if goal["target_date"] > datetime.now() else 0
            remaining_amount = goal["target_amount"] - goal["current_amount"]
            monthly_required = remaining_amount / max(days_left / 30, 1) if days_left > 0 else 0
            
            goal_responses.append(SavingsGoalResponse(
                _id=str(goal["_id"]),
                user_id=str(goal["user_id"]),
                nama_goal=goal["nama_goal"],
                deskripsi=goal.get("deskripsi"),
                target_amount=goal["target_amount"],
                current_amount=goal["current_amount"],
                target_date=goal["target_date"],
                category=goal["category"],
                priority=goal["priority"],
                image_url=goal.get("image_url"),
                is_achieved=goal["is_achieved"],
                achieved_date=goal.get("achieved_date"),
                progress_percentage=progress_percentage,
                days_left=days_left,
                monthly_required=monthly_required,
                created_at=goal["created_at"],
                updated_at=goal["updated_at"]
            ))
        
        return goal_responses
        
    except Exception as e:
        raise CustomHTTPException(
            status_code=500,
            detail=f"Failed to fetch savings goals: {str(e)}",
            error_code="GOALS_FETCH_ERROR"
        )

@router.post("/", response_model=SavingsGoalResponse, status_code=status.HTTP_201_CREATED)
async def create_savings_goal(
    goal_data: SavingsGoalCreate,
    current_user: Dict[str, Any] = Depends(get_current_verified_user)
):
    """Create new savings goal"""
    try:
        db = await get_database()
        user_id = ObjectId(current_user["id"])
        
        goal_dict = goal_data.model_dump()
        goal_dict.update({
            "user_id": user_id,
            "current_amount": 0.0,
            "is_achieved": False,
            "achieved_date": None,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        })
        
        result = await db.savings_goals.insert_one(goal_dict)
        
        # Fetch created goal
        created_goal = await db.savings_goals.find_one({"_id": result.inserted_id})
        
        return SavingsGoalResponse(
            _id=str(created_goal["_id"]),
            user_id=str(created_goal["user_id"]),
            nama_goal=created_goal["nama_goal"],
            deskripsi=created_goal.get("deskripsi"),
            target_amount=created_goal["target_amount"],
            current_amount=created_goal["current_amount"],
            target_date=created_goal["target_date"],
            category=created_goal["category"],
            priority=created_goal["priority"],
            image_url=created_goal.get("image_url"),
            is_achieved=created_goal["is_achieved"],
            achieved_date=created_goal.get("achieved_date"),
            progress_percentage=0.0,
            days_left=(created_goal["target_date"] - datetime.now()).days,
            monthly_required=created_goal["target_amount"] / max((created_goal["target_date"] - datetime.now()).days / 30, 1),
            created_at=created_goal["created_at"],
            updated_at=created_goal["updated_at"]
        )
        
    except Exception as e:
        raise CustomHTTPException(
            status_code=500,
            detail=f"Failed to create savings goal: {str(e)}",
            error_code="GOAL_CREATE_ERROR"
        )

@router.post("/{goal_id}/deposit", response_model=SavingsGoalResponse)
async def add_money_to_goal(
    goal_id: str,
    deposit: GoalDeposit,
    current_user: Dict[str, Any] = Depends(get_current_verified_user)
):
    """Add money to savings goal"""
    try:
        db = await get_database()
        user_id = ObjectId(current_user["id"])
        
        # Validate goal exists and belongs to user
        goal = await db.savings_goals.find_one({
            "_id": ObjectId(goal_id),
            "user_id": user_id
        })
        
        if not goal:
            raise CustomHTTPException(
                status_code=404,
                detail="Savings goal not found",
                error_code="GOAL_NOT_FOUND"
            )
        
        if goal["is_achieved"]:
            raise CustomHTTPException(
                status_code=400,
                detail="Cannot add money to achieved goal",
                error_code="GOAL_ALREADY_ACHIEVED"
            )
        
        new_amount = goal["current_amount"] + deposit.amount
        is_achieved = new_amount >= goal["target_amount"]
        
        update_data = {
            "$set": {
                "current_amount": new_amount,
                "is_achieved": is_achieved,
                "updated_at": datetime.utcnow()
            }
        }
        
        if is_achieved and not goal["is_achieved"]:
            update_data["$set"]["achieved_date"] = datetime.utcnow()
        
        # Update goal
        await db.savings_goals.update_one(
            {"_id": ObjectId(goal_id)},
            update_data
        )
        
        # Create transaction record for goal deposit
        transaction_data = {
            "user_id": user_id,
            "amount": deposit.amount,
            "jenis": "pengeluaran",  # Money taken from balance for goal
            "description": f"Deposit ke goal: {goal['nama_goal']}",
            "notes": deposit.notes or f"Deposit untuk {goal['nama_goal']}",
            "date": datetime.utcnow(),
            "category_id": None,  # Could link to savings category
            "merchant": "Savings Goal",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        await db.transactions.insert_one(transaction_data)
        
        # Fetch updated goal
        updated_goal = await db.savings_goals.find_one({"_id": ObjectId(goal_id)})
        
        progress_percentage = (updated_goal["current_amount"] / updated_goal["target_amount"]) * 100
        days_left = (updated_goal["target_date"] - datetime.now()).days if updated_goal["target_date"] > datetime.now() else 0
        remaining_amount = updated_goal["target_amount"] - updated_goal["current_amount"]
        monthly_required = remaining_amount / max(days_left / 30, 1) if days_left > 0 and remaining_amount > 0 else 0
        
        return SavingsGoalResponse(
            _id=str(updated_goal["_id"]),
            user_id=str(updated_goal["user_id"]),
            nama_goal=updated_goal["nama_goal"],
            deskripsi=updated_goal.get("deskripsi"),
            target_amount=updated_goal["target_amount"],
            current_amount=updated_goal["current_amount"],
            target_date=updated_goal["target_date"],
            category=updated_goal["category"],
            priority=updated_goal["priority"],
            image_url=updated_goal.get("image_url"),
            is_achieved=updated_goal["is_achieved"],
            achieved_date=updated_goal.get("achieved_date"),
            progress_percentage=progress_percentage,
            days_left=days_left,
            monthly_required=monthly_required,
            created_at=updated_goal["created_at"],
            updated_at=updated_goal["updated_at"]
        )
        
    except CustomHTTPException:
        raise
    except Exception as e:
        raise CustomHTTPException(
            status_code=500,
            detail=f"Failed to add money to goal: {str(e)}",
            error_code="GOAL_DEPOSIT_ERROR"
        )

@router.get("/progress")
async def get_goals_progress_summary(
    current_user: Dict[str, Any] = Depends(get_current_verified_user)
):
    """Get goals progress summary"""
    try:
        db = await get_database()
        user_id = ObjectId(current_user["id"])
        
        # Use aggregation pipeline for efficient calculation
        pipeline = [
            {"$match": {"user_id": user_id}},
            {"$group": {
                "_id": None,
                "total_goals": {"$sum": 1},
                "achieved_goals": {"$sum": {"$cond": ["$is_achieved", 1, 0]}},
                "total_target": {"$sum": "$target_amount"},
                "total_saved": {"$sum": "$current_amount"},
                "active_goals": {"$sum": {"$cond": [{"$eq": ["$is_achieved", False]}, 1, 0]}}
            }}
        ]
        
        result = await db.savings_goals.aggregate(pipeline).to_list(1)
        
        if result:
            data = result[0]
            progress_percentage = (data["total_saved"] / data["total_target"]) * 100 if data["total_target"] > 0 else 0
            
            return {
                "total_goals": data["total_goals"],
                "active_goals": data["active_goals"],
                "achieved_goals": data["achieved_goals"],
                "total_target": data["total_target"],
                "total_saved": data["total_saved"],
                "overall_progress": progress_percentage
            }
        else:
            return {
                "total_goals": 0,
                "active_goals": 0,
                "achieved_goals": 0,
                "total_target": 0,
                "total_saved": 0,
                "overall_progress": 0
            }
        
    except Exception as e:
        raise CustomHTTPException(
            status_code=500,
            detail=f"Failed to fetch goals progress: {str(e)}",
            error_code="GOALS_PROGRESS_ERROR"
        )