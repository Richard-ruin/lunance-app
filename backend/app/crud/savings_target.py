"""
SavingsTarget CRUD Operations
CRUD operations untuk SavingsTarget model dengan business logic
"""

from typing import Optional, List, Dict, Any
from datetime import datetime, date

from .base import CRUDBase
from ..models.savings_target import SavingsTarget, TargetStatus, TargetPriority
from ..schemas.savings_target import SavingsTargetCreate, SavingsTargetUpdate


class CRUDSavingsTarget(CRUDBase[SavingsTarget, SavingsTargetCreate, SavingsTargetUpdate]):
    """CRUD operations untuk SavingsTarget model"""
    
    async def create_savings_target(
        self,
        *,
        obj_in: SavingsTargetCreate,
        user_id: str
    ) -> SavingsTarget:
        """
        Create savings target untuk user
        
        Args:
            obj_in: SavingsTarget create schema
            user_id: User ID yang membuat target
            
        Returns:
            Created savings target
            
        Raises:
            ValueError: Jika validasi gagal
        """
        # Check if user sudah punya target dengan nama yang sama
        existing = await self.get_by_name(user_id, obj_in.target_name)
        if existing:
            raise ValueError(f"Target dengan nama '{obj_in.target_name}' sudah ada")
        
        # Create target
        target_data = obj_in.model_dump()
        target_data["user_id"] = user_id
        
        target = self.model(**target_data)
        await target.save()
        
        return target
    
    async def get_by_name(self, user_id: str, target_name: str) -> Optional[SavingsTarget]:
        """Get savings target by user dan nama"""
        query = {
            "user_id": user_id,
            "target_name": {"$pattern": f"^{target_name}$", "$options": "i"},
            "is_deleted": {"$ne": True}
        }
        return await self.model.find_one(query)
    
    async def get_user_targets(
        self,
        user_id: str,
        status: Optional[TargetStatus] = None,
        is_achieved: Optional[bool] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[SavingsTarget]:
        """Get savings targets untuk user dengan filter"""
        query = {
            "user_id": user_id,
            "is_deleted": {"$ne": True}
        }
        
        if status:
            query["status"] = status
        
        if is_achieved is not None:
            query["is_achieved"] = is_achieved
        
        return await self.get_multi(
            skip=skip,
            limit=limit,
            query=query,
            sort_by="target_date"
        )
    
    async def get_active_targets(self, user_id: str) -> List[SavingsTarget]:
        """Get active targets untuk user"""
        query = {
            "user_id": user_id,
            "status": TargetStatus.ACTIVE,
            "is_deleted": {"$ne": True}
        }
        return await self.get_multi(query=query, sort_by="target_date")
    
    async def get_achieved_targets(self, user_id: str) -> List[SavingsTarget]:
        """Get achieved targets untuk user"""
        query = {
            "user_id": user_id,
            "is_achieved": True,
            "is_deleted": {"$ne": True}
        }
        return await self.get_multi(
            query=query, 
            sort_by="achieved_date", 
            sort_order=-1
        )
    
    async def get_overdue_targets(self, user_id: Optional[str] = None) -> List[SavingsTarget]:
        """Get overdue targets"""
        query = {
            "target_date": {"$lt": date.today()},
            "is_achieved": False,
            "status": TargetStatus.ACTIVE,
            "is_deleted": {"$ne": True}
        }
        
        if user_id:
            query["user_id"] = user_id
        
        return await self.get_multi(query=query, sort_by="target_date")
    
    async def update_target(
        self,
        *,
        target_id: str,
        obj_in: SavingsTargetUpdate,
        user_id: str
    ) -> Optional[SavingsTarget]:
        """
        Update savings target dengan validasi ownership
        
        Args:
            target_id: ID target
            obj_in: Update data
            user_id: User ID yang update
            
        Returns:
            Updated target atau None
            
        Raises:
            ValueError: Jika tidak ada permission atau validasi gagal
        """
        target = await self.get(target_id)
        if not target:
            return None
        
        # Check ownership
        if target.user_id != user_id:
            raise ValueError("Anda tidak memiliki permission untuk mengedit target ini")
        
        # Validate nama unik jika diupdate
        update_data = obj_in.model_dump(exclude_unset=True)
        
        if "target_name" in update_data:
            existing = await self.get_by_name(user_id, update_data["target_name"])
            if existing and existing.id != target_id:
                raise ValueError(f"Target dengan nama '{update_data['target_name']}' sudah ada")
        
        return await self.update(
            id=target_id,
            obj_in=obj_in,
            updated_by=user_id
        )
    
    async def delete_target(
        self,
        *,
        target_id: str,
        user_id: str,
        soft: bool = True
    ) -> bool:
        """
        Delete savings target dengan validasi ownership
        
        Args:
            target_id: ID target
            user_id: User ID yang delete
            soft: Soft delete atau hard delete
            
        Returns:
            True jika berhasil dihapus
            
        Raises:
            ValueError: Jika tidak ada permission
        """
        target = await self.get(target_id)
        if not target:
            return False
        
        # Check ownership
        if target.user_id != user_id:
            raise ValueError("Anda tidak memiliki permission untuk menghapus target ini")
        
        if soft:
            return await self.soft_delete(id=target_id, deleted_by=user_id)
        else:
            return await self.delete(id=target_id)
    
    async def add_contribution(
        self,
        *,
        target_id: str,
        amount: float,
        user_id: str,
        description: Optional[str] = None
    ) -> Optional[SavingsTarget]:
        """Add contribution ke savings target"""
        target = await self.get(target_id)
        if not target or target.user_id != user_id:
            return None
        
        await target.add_contribution(amount, description)
        return target
    
    async def subtract_contribution(
        self,
        *,
        target_id: str,
        amount: float,
        user_id: str,
        description: Optional[str] = None
    ) -> Optional[SavingsTarget]:
        """Subtract contribution dari savings target"""
        target = await self.get(target_id)
        if not target or target.user_id != user_id:
            return None
        
        await target.subtract_contribution(amount, description)
        return target
    
    async def complete_target(self, target_id: str, user_id: str) -> bool:
        """Mark target sebagai achieved"""
        target = await self.get(target_id)
        if not target or target.user_id != user_id:
            return False
        
        await target.complete()
        return True
    
    async def cancel_target(self, target_id: str, user_id: str) -> bool:
        """Cancel target"""
        target = await self.get(target_id)
        if not target or target.user_id != user_id:
            return False
        
        await target.cancel()
        return True
    
    async def reactivate_target(self, target_id: str, user_id: str) -> bool:
        """Reactivate cancelled target"""
        target = await self.get(target_id)
        if not target or target.user_id != user_id:
            return False
        
        await target.reactivate()
        return True
    
    async def extend_deadline(
        self,
        *,
        target_id: str,
        new_date: date,
        user_id: str
    ) -> Optional[SavingsTarget]:
        """Extend target deadline"""
        target = await self.get(target_id)
        if not target or target.user_id != user_id:
            return None
        
        await target.extend_deadline(new_date)
        return target
    
    async def get_user_summary(self, user_id: str) -> Dict[str, Any]:
        """Get summary targets untuk user"""
        targets = await self.get_user_targets(user_id)
        
        total_targets = len(targets)
        achieved_targets = len([t for t in targets if t.is_achieved])
        active_targets = len([t for t in targets if t.status == TargetStatus.ACTIVE])
        total_target_amount = sum(t.target_amount for t in targets)
        total_saved_amount = sum(t.current_amount for t in targets)
        
        return {
            "total_targets": total_targets,
            "achieved_targets": achieved_targets,
            "active_targets": active_targets,
            "achievement_rate": (achieved_targets / total_targets * 100) if total_targets > 0 else 0,
            "total_target_amount": total_target_amount,
            "total_saved_amount": total_saved_amount,
            "savings_progress": (total_saved_amount / total_target_amount * 100) if total_target_amount > 0 else 0
        }
    
    async def get_targets_by_priority(
        self,
        user_id: str,
        priority: TargetPriority
    ) -> List[SavingsTarget]:
        """Get targets by priority"""
        query = {
            "user_id": user_id,
            "priority": priority,
            "status": TargetStatus.ACTIVE,
            "is_deleted": {"$ne": True}
        }
        return await self.get_multi(query=query, sort_by="target_date")
    
    async def get_near_deadline_targets(
        self,
        user_id: str,
        days_threshold: int = 7
    ) -> List[SavingsTarget]:
        """Get targets yang mendekati deadline"""
        deadline_threshold = date.today() + datetime.timedelta(days=days_threshold)
        
        query = {
            "user_id": user_id,
            "target_date": {"$lte": deadline_threshold, "$gte": date.today()},
            "is_achieved": False,
            "status": TargetStatus.ACTIVE,
            "is_deleted": {"$ne": True}
        }
        
        return await self.get_multi(query=query, sort_by="target_date")
    
    async def search_targets(
        self,
        *,
        user_id: str,
        search_term: str,
        skip: int = 0,
        limit: int = 50
    ) -> List[SavingsTarget]:
        """Search targets berdasarkan nama, deskripsi, atau kategori"""
        query = {
            "user_id": user_id,
            "$or": [
                {"target_name": {"$pattern": search_term, "$options": "i"}},
                {"description": {"$pattern": search_term, "$options": "i"}},
                {"category": {"$pattern": search_term, "$options": "i"}},
                {"motivation_note": {"$pattern": search_term, "$options": "i"}}
            ],
            "is_deleted": {"$ne": True}
        }
        
        return await self.get_multi(
            skip=skip,
            limit=limit,
            query=query,
            sort_by="target_date"
        )
    
    async def get_targets_by_category(
        self,
        user_id: str,
        category: str
    ) -> List[SavingsTarget]:
        """Get targets by category"""
        query = {
            "user_id": user_id,
            "category": {"$pattern": f"^{category}$", "$options": "i"},
            "is_deleted": {"$ne": True}
        }
        return await self.get_multi(query=query, sort_by="target_date")
    
    async def get_savings_analytics(
        self,
        user_id: str,
        period_months: int = 12
    ) -> Dict[str, Any]:
        """Get savings analytics untuk user"""
        end_date = date.today()
        start_date = end_date.replace(year=end_date.year - 1)  # 1 year ago
        
        # Get all targets dalam periode
        query = {
            "user_id": user_id,
            "created_at": {"$gte": start_date},
            "is_deleted": {"$ne": True}
        }
        
        targets = await self.get_multi(query=query)
        
        # Calculate analytics
        total_contributions = sum(t.current_amount for t in targets)
        total_targets_amount = sum(t.target_amount for t in targets)
        achieved_count = len([t for t in targets if t.is_achieved])
        
        # Average contribution per target
        avg_contribution = total_contributions / len(targets) if targets else 0
        
        # Savings rate (total saved vs total targeted)
        savings_rate = (total_contributions / total_targets_amount * 100) if total_targets_amount > 0 else 0
        
        # Category breakdown
        category_data = {}
        for target in targets:
            category = target.category or "Lainnya"
            if category not in category_data:
                category_data[category] = {
                    "count": 0,
                    "total_target": 0,
                    "total_saved": 0,
                    "achieved": 0
                }
            
            category_data[category]["count"] += 1
            category_data[category]["total_target"] += target.target_amount
            category_data[category]["total_saved"] += target.current_amount
            if target.is_achieved:
                category_data[category]["achieved"] += 1
        
        # Monthly trend (simplified)
        monthly_data = {}
        for target in targets:
            month_key = target.created_at.strftime("%Y-%m")
            if month_key not in monthly_data:
                monthly_data[month_key] = {"targets_created": 0, "amount_saved": 0}
            
            monthly_data[month_key]["targets_created"] += 1
            monthly_data[month_key]["amount_saved"] += target.current_amount
        
        monthly_trend = [
            {
                "month": month,
                "targets_created": data["targets_created"],
                "amount_saved": data["amount_saved"]
            }
            for month, data in sorted(monthly_data.items())
        ]
        
        return {
            "period": f"{start_date} to {end_date}",
            "total_targets": len(targets),
            "achieved_targets": achieved_count,
            "achievement_rate": (achieved_count / len(targets) * 100) if targets else 0,
            "total_contributions": total_contributions,
            "average_contribution": avg_contribution,
            "savings_rate": savings_rate,
            "category_breakdown": list(category_data.values()),
            "monthly_trend": monthly_trend
        }
    
    async def update_expired_targets(self) -> int:
        """Update status target yang sudah expired (background job)"""
        overdue_targets = await self.get_overdue_targets()
        
        for target in overdue_targets:
            target.status = TargetStatus.EXPIRED
            await target.save_with_timestamp()
        
        return len(overdue_targets)
    
    async def get_global_stats(self) -> Dict[str, Any]:
        """Get global statistics untuk admin"""
        total_targets = await self.count()
        active_targets = await self.count(query={"status": TargetStatus.ACTIVE})
        achieved_targets = await self.count(query={"is_achieved": True})
        expired_targets = await self.count(query={"status": TargetStatus.EXPIRED})
        
        # Average target amount
        all_targets = await self.get_multi(limit=10000)  # Get all for calculation
        avg_target_amount = sum(t.target_amount for t in all_targets) / len(all_targets) if all_targets else 0
        avg_saved_amount = sum(t.current_amount for t in all_targets) / len(all_targets) if all_targets else 0
        
        return {
            "total_targets": total_targets,
            "active_targets": active_targets,
            "achieved_targets": achieved_targets,
            "expired_targets": expired_targets,
            "achievement_rate": (achieved_targets / total_targets * 100) if total_targets > 0 else 0,
            "average_target_amount": avg_target_amount,
            "average_saved_amount": avg_saved_amount
        }
    
    async def bulk_update_status(
        self,
        *,
        target_ids: List[str],
        status: TargetStatus,
        user_id: str
    ) -> List[SavingsTarget]:
        """Bulk update status untuk targets milik user"""
        # Validate ownership
        targets = []
        for target_id in target_ids:
            target = await self.get(target_id)
            if target and target.user_id == user_id:
                targets.append(target)
        
        if not targets:
            return []
        
        # Update status
        update_data = {"status": status}
        valid_ids = [t.id for t in targets]
        
        await self.update_bulk(
            ids=valid_ids,
            obj_in=update_data,
            updated_by=user_id
        )
        
        # Return updated targets
        return await self.model.find({"_id": {"$in": valid_ids}}).to_list()


# Create instance
crud_savings_target = CRUDSavingsTarget(SavingsTarget)