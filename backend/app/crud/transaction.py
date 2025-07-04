"""
Transaction CRUD Operations
CRUD operations untuk Transaction model dengan business logic
"""

from typing import Optional, List, Dict, Any
from datetime import datetime, date
from dateutil.relativedelta import relativedelta

from .base import CRUDBase
from ..models.transaction import Transaction, TransactionStatus
from ..models.category import CategoryType
from ..schemas.transaction import TransactionCreate, TransactionUpdate


class CRUDTransaction(CRUDBase[Transaction, TransactionCreate, TransactionUpdate]):
    """CRUD operations untuk Transaction model"""
    
    async def create_transaction(
        self,
        *,
        obj_in: TransactionCreate,
        user_id: str
    ) -> Transaction:
        """
        Create transaction dengan validasi kategori dan business logic
        
        Args:
            obj_in: Transaction create schema
            user_id: User ID yang membuat transaksi
            
        Returns:
            Created transaction
            
        Raises:
            ValueError: Jika validasi gagal
        """
        # Validate category exists dan bisa digunakan user
        from .category import crud_category
        
        category = await crud_category.get(obj_in.category_id)
        if not category:
            raise ValueError("Kategori tidak ditemukan")
        
        if not category.can_be_used_by(user_id):
            raise ValueError("Anda tidak memiliki akses ke kategori ini")
        
        # Validate type consistency dengan category
        if category.type != obj_in.type:
            raise ValueError("Tipe transaksi tidak sesuai dengan kategori")
        
        # Create transaction
        transaction_data = obj_in.model_dump()
        transaction_data["user_id"] = user_id
        
        transaction = self.model(**transaction_data)
        await transaction.save()
        
        # Increment category usage
        await crud_category.increment_usage(obj_in.category_id, user_id)
        
        return transaction
    
    async def get_user_transactions(
        self,
        user_id: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        transaction_type: Optional[CategoryType] = None,
        category_id: Optional[str] = None,
        status: Optional[TransactionStatus] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Transaction]:
        """Get transactions untuk user dengan filter"""
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
        
        # Status filter
        if status:
            query["status"] = status
        
        return await self.get_multi(
            skip=skip,
            limit=limit,
            query=query,
            sort_by="date",
            sort_order=-1
        )
    
    async def update_transaction(
        self,
        *,
        transaction_id: str,
        obj_in: TransactionUpdate,
        user_id: str
    ) -> Optional[Transaction]:
        """
        Update transaction dengan validasi ownership
        
        Args:
            transaction_id: ID transaksi
            obj_in: Update data
            user_id: User ID yang update
            
        Returns:
            Updated transaction atau None
            
        Raises:
            ValueError: Jika tidak ada permission atau validasi gagal
        """
        transaction = await self.get(transaction_id)
        if not transaction:
            return None
        
        # Check ownership
        if transaction.user_id != user_id:
            raise ValueError("Anda tidak memiliki permission untuk mengedit transaksi ini")
        
        # Validate category jika diupdate
        update_data = obj_in.model_dump(exclude_unset=True)
        
        if "category_id" in update_data:
            from .category import crud_category
            
            category = await crud_category.get(update_data["category_id"])
            if not category:
                raise ValueError("Kategori tidak ditemukan")
            
            if not category.can_be_used_by(user_id):
                raise ValueError("Anda tidak memiliki akses ke kategori ini")
            
            # Check type consistency jika type juga diupdate
            transaction_type = update_data.get("type", transaction.type)
            if category.type != transaction_type:
                raise ValueError("Tipe transaksi tidak sesuai dengan kategori")
        
        return await self.update(
            id=transaction_id,
            obj_in=obj_in,
            updated_by=user_id
        )
    
    async def delete_transaction(
        self,
        *,
        transaction_id: str,
        user_id: str,
        soft: bool = True
    ) -> bool:
        """
        Delete transaction dengan validasi ownership
        
        Args:
            transaction_id: ID transaksi
            user_id: User ID yang delete
            soft: Soft delete atau hard delete
            
        Returns:
            True jika berhasil dihapus
            
        Raises:
            ValueError: Jika tidak ada permission
        """
        transaction = await self.get(transaction_id)
        if not transaction:
            return False
        
        # Check ownership
        if transaction.user_id != user_id:
            raise ValueError("Anda tidak memiliki permission untuk menghapus transaksi ini")
        
        if soft:
            return await self.soft_delete(id=transaction_id, deleted_by=user_id)
        else:
            return await self.delete(id=transaction_id)
    
    async def complete_transaction(self, transaction_id: str, user_id: str) -> bool:
        """Mark transaction sebagai completed"""
        transaction = await self.get(transaction_id)
        if not transaction or transaction.user_id != user_id:
            return False
        
        await transaction.complete()
        return True
    
    async def cancel_transaction(self, transaction_id: str, user_id: str) -> bool:
        """Cancel transaction"""
        transaction = await self.get(transaction_id)
        if not transaction or transaction.user_id != user_id:
            return False
        
        await transaction.cancel()
        return True
    
    async def get_user_balance(self, user_id: str) -> Dict[str, float]:
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
        
        result = await self.model.aggregate(pipeline).to_list()
        
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
    
    async def get_monthly_summary(
        self,
        user_id: str,
        year: int,
        month: int
    ) -> Dict[str, Any]:
        """Get summary transaksi bulanan"""
        start_date = date(year, month, 1)
        
        # Calculate last day of month
        if month == 12:
            end_date = date(year + 1, 1, 1) - relativedelta(days=1)
        else:
            end_date = date(year, month + 1, 1) - relativedelta(days=1)
        
        transactions = await self.get_user_transactions(
            user_id=user_id,
            start_date=start_date,
            end_date=end_date,
            status=TransactionStatus.COMPLETED
        )
        
        income = sum(t.amount for t in transactions if t.is_income())
        expense = sum(t.amount for t in transactions if t.is_expense())
        
        return {
            "year": year,
            "month": month,
            "income": income,
            "expense": expense,
            "balance": income - expense,
            "transaction_count": len(transactions),
            "transactions": [t.to_dict() for t in transactions]
        }
    
    async def get_category_summary(
        self,
        user_id: str,
        category_id: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """Get summary transaksi per kategori"""
        query = {
            "user_id": user_id,
            "category_id": category_id,
            "status": TransactionStatus.COMPLETED,
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
        
        transactions = await self.get_multi(
            query=query,
            sort_by="date",
            sort_order=-1
        )
        
        total_amount = sum(t.amount for t in transactions)
        
        return {
            "category_id": category_id,
            "transaction_count": len(transactions),
            "total_amount": total_amount,
            "latest_transaction": transactions[0].to_dict() if transactions else None,
            "transactions": [t.to_dict() for t in transactions]
        }
    
    async def get_spending_analytics(
        self,
        user_id: str,
        period_months: int = 6
    ) -> Dict[str, Any]:
        """Get spending analytics untuk user"""
        end_date = date.today()
        start_date = end_date - relativedelta(months=period_months)
        
        # Get transactions dalam periode
        transactions = await self.get_user_transactions(
            user_id=user_id,
            start_date=start_date,
            end_date=end_date,
            status=TransactionStatus.COMPLETED
        )
        
        # Calculate totals
        total_income = sum(t.amount for t in transactions if t.is_income())
        total_expense = sum(t.amount for t in transactions if t.is_expense())
        net_income = total_income - total_expense
        
        # Daily average
        days_in_period = (end_date - start_date).days
        daily_average = total_expense / days_in_period if days_in_period > 0 else 0
        
        # Category breakdown
        category_summary = {}
        for transaction in transactions:
            if transaction.is_expense():
                category_id = transaction.category_id
                if category_id not in category_summary:
                    category_summary[category_id] = {
                        "category_id": category_id,
                        "amount": 0,
                        "count": 0
                    }
                category_summary[category_id]["amount"] += transaction.amount
                category_summary[category_id]["count"] += 1
        
        # Sort by amount
        top_categories = sorted(
            category_summary.values(),
            key=lambda x: x["amount"],
            reverse=True
        )[:10]
        
        # Monthly trend
        monthly_data = {}
        for transaction in transactions:
            month_key = transaction.date.strftime("%Y-%m")
            if month_key not in monthly_data:
                monthly_data[month_key] = {"income": 0, "expense": 0}
            
            if transaction.is_income():
                monthly_data[month_key]["income"] += transaction.amount
            else:
                monthly_data[month_key]["expense"] += transaction.amount
        
        monthly_trend = [
            {
                "month": month,
                "income": data["income"],
                "expense": data["expense"],
                "balance": data["income"] - data["expense"]
            }
            for month, data in sorted(monthly_data.items())
        ]
        
        return {
            "period": f"{start_date} to {end_date}",
            "total_income": total_income,
            "total_expense": total_expense,
            "net_income": net_income,
            "daily_average_expense": daily_average,
            "transaction_count": len(transactions),
            "top_expense_categories": top_categories,
            "monthly_trend": monthly_trend
        }
    
    async def search_transactions(
        self,
        *,
        user_id: str,
        search_term: str,
        skip: int = 0,
        limit: int = 50
    ) -> List[Transaction]:
        """Search transactions berdasarkan description, notes, atau tags"""
        query = {
            "user_id": user_id,
            "$or": [
                {"description": {"$pattern": search_term, "$options": "i"}},
                {"notes": {"$pattern": search_term, "$options": "i"}},
                {"location": {"$pattern": search_term, "$options": "i"}},
                {"tags": {"$in": [search_term.lower()]}}
            ],
            "is_deleted": {"$ne": True}
        }
        
        return await self.get_multi(
            skip=skip,
            limit=limit,
            query=query,
            sort_by="date",
            sort_order=-1
        )
    
    async def get_recent_transactions(
        self,
        user_id: str,
        limit: int = 10
    ) -> List[Transaction]:
        """Get recent transactions untuk user"""
        query = {
            "user_id": user_id,
            "is_deleted": {"$ne": True}
        }
        
        return await self.get_multi(
            query=query,
            limit=limit,
            sort_by="created_at",
            sort_order=-1
        )
    
    async def bulk_update_category(
        self,
        *,
        old_category_id: str,
        new_category_id: str,
        user_id: str
    ) -> int:
        """Bulk update category untuk transactions"""
        # Validate categories
        from .category import crud_category
        
        new_category = await crud_category.get(new_category_id)
        if not new_category:
            raise ValueError("Kategori tujuan tidak ditemukan")
        
        if not new_category.can_be_used_by(user_id):
            raise ValueError("Anda tidak memiliki akses ke kategori tujuan")
        
        # Update transactions
        query = {
            "user_id": user_id,
            "category_id": old_category_id,
            "is_deleted": {"$ne": True}
        }
        
        update_data = {
            "category_id": new_category_id,
            "updated_at": datetime.utcnow(),
            "updated_by": user_id
        }
        
        result = await self.model.find(query).update({"$set": update_data})
        return result.modified_count if hasattr(result, 'modified_count') else 0
    
    async def add_transaction_tag(
        self,
        transaction_id: str,
        tag: str,
        user_id: str
    ) -> bool:
        """Add tag ke transaction"""
        transaction = await self.get(transaction_id)
        if not transaction or transaction.user_id != user_id:
            return False
        
        await transaction.add_tag(tag)
        return True
    
    async def remove_transaction_tag(
        self,
        transaction_id: str,
        tag: str,
        user_id: str
    ) -> bool:
        """Remove tag dari transaction"""
        transaction = await self.get(transaction_id)
        if not transaction or transaction.user_id != user_id:
            return False
        
        await transaction.remove_tag(tag)
        return True


# Create instance
crud_transaction = CRUDTransaction(Transaction)