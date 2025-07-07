from datetime import datetime
from typing import Dict, Any, List, Optional
from app.models.user import User
from app.models.university import University, Fakultas, ProgramStudi, UniversityRequest
from app.utils.email_service import EmailService
from app.config.database import get_db

class AdminService:
    
    @staticmethod
    def get_pending_users(page: int = 1, limit: int = 10) -> Dict[str, Any]:
        """Get users pending approval"""
        try:
            return User.find_pending_users(page, limit)
        except Exception as e:
            return {'users': [], 'pagination': {}}
    
    @staticmethod
    def approve_user(user_id: str, admin_id: str, catatan: str = "") -> Dict[str, Any]:
        """Approve user registration"""
        # Find user
        user = User.find_by_id(user_id)
        if not user:
            raise ValueError("User tidak ditemukan")
        
        if user.status != "pending":
            raise ValueError("User tidak dalam status pending")
        
        # Approve user
        user.approve_user()
        
        # Send approval email
        EmailService.send_account_approved(user.email, user.nama_lengkap)
        
        # Log admin activity
        AdminService._log_activity(
            admin_id=admin_id,
            action="approve_user",
            target_id=user_id,
            description=f"Menyetujui user {user.nama_lengkap} ({user.email})",
            notes=catatan
        )
        
        return {
            "user_id": str(user.id),
            "status": user.status,
            "processed_at": datetime.utcnow().isoformat(),
            "processed_by": admin_id
        }
    
    @staticmethod
    def reject_user(user_id: str, admin_id: str, catatan: str) -> Dict[str, Any]:
        """Reject user registration"""
        # Find user
        user = User.find_by_id(user_id)
        if not user:
            raise ValueError("User tidak ditemukan")
        
        if user.status != "pending":
            raise ValueError("User tidak dalam status pending")
        
        # Reject user
        user.reject_user()
        
        # Send rejection email
        EmailService.send_account_rejected(user.email, user.nama_lengkap, catatan)
        
        # Log admin activity
        AdminService._log_activity(
            admin_id=admin_id,
            action="reject_user",
            target_id=user_id,
            description=f"Menolak user {user.nama_lengkap} ({user.email})",
            notes=catatan
        )
        
        return {
            "user_id": str(user.id),
            "status": user.status,
            "processed_at": datetime.utcnow().isoformat(),
            "processed_by": admin_id,
            "catatan": catatan
        }
    
    @staticmethod
    def get_all_users(page: int = 1, limit: int = 10, status: str = "", search: str = "") -> Dict[str, Any]:
        """Get all users with filtering"""
        try:
            skip = (page - 1) * limit
            filter_dict = {}
            
            # Add status filter
            if status:
                filter_dict['status'] = status
            
            # Add search filter
            if search:
                search_regex = {'$regex': search, '$options': 'i'}
                filter_dict['$or'] = [
                    {'nama_lengkap': search_regex},
                    {'email': search_regex}
                ]
            
            users = User.find_all('users', filter_dict, limit, skip, [('created_at', -1)])
            total = User.count_documents('users', filter_dict)
            
            return {
                'users': [user.to_dict_safe() for user in users],
                'pagination': {
                    'page': page,
                    'limit': limit,
                    'total': total,
                    'pages': (total + limit - 1) // limit,
                    'has_next': page * limit < total,
                    'has_prev': page > 1
                }
            }
        except Exception:
            return {'users': [], 'pagination': {}}
    
    @staticmethod
    def get_user_detail(user_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed user information"""
        user = User.find_by_id(user_id)
        if not user:
            return None
        
        # Get university info
        university = University.find_by_id(str(user.university_id))
        fakultas = Fakultas.find_by_id(str(user.fakultas_id))
        prodi = ProgramStudi.find_by_id(str(user.prodi_id))
        
        user_data = user.to_dict_safe()
        user_data['university_info'] = {
            'university': university.model_dump() if university else None,
            'fakultas': fakultas.model_dump() if fakultas else None,
            'prodi': prodi.model_dump() if prodi else None
        }
        
        return user_data
    
    @staticmethod
    def get_dashboard_statistics() -> Dict[str, Any]:
        """Get admin dashboard statistics"""
        try:
            # User statistics
            total_users = User.count_documents('users')
            pending_users = User.count_documents('users', {'status': 'pending'})
            approved_users = User.count_documents('users', {'status': 'approved'})
            rejected_users = User.count_documents('users', {'status': 'rejected'})
            
            # University statistics
            total_universities = University.count_documents('universities')
            total_fakultas = Fakultas.count_documents('fakultas')
            total_prodi = ProgramStudi.count_documents('program_studi')
            
            # University requests
            pending_requests = UniversityRequest.count_documents('university_requests', {'status': 'pending'})
            approved_requests = UniversityRequest.count_documents('university_requests', {'status': 'approved'})
            rejected_requests = UniversityRequest.count_documents('university_requests', {'status': 'rejected'})
            
            # Recent registrations (last 7 days)
            from datetime import timedelta
            week_ago = datetime.utcnow() - timedelta(days=7)
            recent_registrations = User.count_documents('users', {
                'created_at': {'$gte': week_ago}
            })
            
            return {
                'users': {
                    'total': total_users,
                    'pending': pending_users,
                    'approved': approved_users,
                    'rejected': rejected_users,
                    'recent_registrations': recent_registrations
                },
                'universities': {
                    'total': total_universities,
                    'fakultas': total_fakultas,
                    'program_studi': total_prodi
                },
                'university_requests': {
                    'pending': pending_requests,
                    'approved': approved_requests,
                    'rejected': rejected_requests,
                    'total': pending_requests + approved_requests + rejected_requests
                },
                'system': {
                    'maintenance_mode': False,  # TODO: Implement maintenance mode
                    'last_updated': datetime.utcnow().isoformat()
                }
            }
        except Exception as e:
            return {}
    
    @staticmethod
    def get_recent_activities(limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent admin activities"""
        try:
            db = get_db()
            activities = list(db.admin_activities.find(
                {},
                sort=[('created_at', -1)],
                limit=limit
            ))
            
            # Convert ObjectId to string
            for activity in activities:
                activity['_id'] = str(activity['_id'])
            
            return activities
        except Exception:
            return []
    
    @staticmethod
    def toggle_maintenance_mode(enabled: bool, admin_id: str) -> Dict[str, Any]:
        """Toggle system maintenance mode"""
        try:
            db = get_db()
            
            # Update system settings
            db.system_settings.update_one(
                {'key': 'maintenance_mode'},
                {
                    '$set': {
                        'value': enabled,
                        'updated_at': datetime.utcnow(),
                        'updated_by': admin_id
                    }
                },
                upsert=True
            )
            
            # Log activity
            AdminService._log_activity(
                admin_id=admin_id,
                action="toggle_maintenance",
                description=f"{'Mengaktifkan' if enabled else 'Menonaktifkan'} mode maintenance",
                notes=f"Maintenance mode: {enabled}"
            )
            
            return {
                'maintenance_mode': enabled,
                'updated_at': datetime.utcnow().isoformat(),
                'updated_by': admin_id
            }
        except Exception as e:
            raise Exception(f"Gagal mengubah mode maintenance: {str(e)}")
    
    @staticmethod
    def _log_activity(admin_id: str, action: str, description: str, target_id: str = None, notes: str = "") -> bool:
        """Log admin activity"""
        try:
            db = get_db()
            
            activity = {
                'admin_id': admin_id,
                'action': action,
                'description': description,
                'target_id': target_id,
                'notes': notes,
                'created_at': datetime.utcnow()
            }
            
            db.admin_activities.insert_one(activity)
            return True
        except Exception:
            return False
    
    @staticmethod
    def get_system_logs(page: int = 1, limit: int = 50, level: str = "") -> Dict[str, Any]:
        """Get system logs"""
        try:
            db = get_db()
            skip = (page - 1) * limit
            filter_dict = {}
            
            if level:
                filter_dict['level'] = level
            
            logs = list(db.system_logs.find(
                filter_dict,
                sort=[('created_at', -1)],
                skip=skip,
                limit=limit
            ))
            
            total = db.system_logs.count_documents(filter_dict)
            
            # Convert ObjectId to string
            for log in logs:
                log['_id'] = str(log['_id'])
            
            return {
                'logs': logs,
                'pagination': {
                    'page': page,
                    'limit': limit,
                    'total': total,
                    'pages': (total + limit - 1) // limit,
                    'has_next': page * limit < total,
                    'has_prev': page > 1
                }
            }
        except Exception:
            return {'logs': [], 'pagination': {}}