from typing import List, Dict, Any, Optional
from datetime import datetime
from app.models.university import University, Fakultas, ProgramStudi, UniversityRequest
from app.config.database import get_db
from bson import ObjectId

class UniversityService:
    
    @staticmethod
    def get_universities(page: int = 1, limit: int = 10, search: str = '', 
                        status_aktif: Optional[bool] = None) -> Dict[str, Any]:
        """Get universities with pagination and filtering"""
        skip = (page - 1) * limit
        filter_dict = {}
        
        # Add search filter
        if search:
            filter_dict['$or'] = [
                {'nama': {'$regex': search, '$options': 'i'}},
                {'kode': {'$regex': search, '$options': 'i'}}
            ]
        
        # Add status filter
        if status_aktif is not None:
            filter_dict['status_aktif'] = status_aktif
        
        # Get universities
        universities = University.find_all(
            filter_dict=filter_dict,
            skip=skip,
            limit=limit,
            sort=[('created_at', -1)]
        )
        
        # Get total count
        total = University.count_documents(filter_dict)
        
        return {
            'universities': [univ.model_dump() for univ in universities],
            'pagination': {
                'page': page,
                'limit': limit,
                'total': total,
                'pages': (total + limit - 1) // limit
            }
        }
    
    @staticmethod
    def get_university_by_id(university_id: str) -> Optional[Dict[str, Any]]:
        """Get university by ID"""
        university = University.find_by_id(university_id)
        return university.model_dump() if university else None
    
    @staticmethod
    def get_fakultas_by_university(university_id: str) -> List[Dict[str, Any]]:
        """Get all fakultas by university ID"""
        fakultas_list = Fakultas.find_by_university(university_id)
        return [fakultas.model_dump() for fakultas in fakultas_list]
    
    @staticmethod
    def get_prodi_by_fakultas(fakultas_id: str) -> List[Dict[str, Any]]:
        """Get all program studi by fakultas ID"""
        prodi_list = ProgramStudi.find_by_fakultas(fakultas_id)
        return [prodi.model_dump() for prodi in prodi_list]
    
    @staticmethod
    def create_university_request(data: Dict[str, Any]) -> Dict[str, Any]:
        """Create new university request"""
        # Check if university already exists
        existing_univ = University.find_by_kode(data['kode_university'])
        if existing_univ:
            raise ValueError('Universitas dengan kode tersebut sudah terdaftar')
        
        # Check if there's pending request for same university
        db = get_db()
        existing_request = db.university_requests.find_one({
            'kode_university': data['kode_university'].upper(),
            'status': 'pending'
        })
        
        if existing_request:
            raise ValueError('Sudah ada permintaan pending untuk universitas ini')
        
        # Check if user with same email already made a request
        existing_email_request = db.university_requests.find_one({
            'email': data['email'].lower(),
            'status': 'pending'
        })
        
        if existing_email_request:
            raise ValueError('Anda sudah memiliki permintaan yang sedang diproses')
        
        # Create university request
        request_data = UniversityRequest(**data)
        request_data.save()
        
        return request_data.model_dump()
    
    @staticmethod
    def search_universities(query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search universities by name or code"""
        filter_dict = {
            'status_aktif': True,
            '$or': [
                {'nama': {'$regex': query, '$options': 'i'}},
                {'kode': {'$regex': query, '$options': 'i'}}
            ]
        }
        
        universities = University.find_all(
            filter_dict=filter_dict, 
            limit=limit,
            sort=[('nama', 1)]
        )
        return [univ.model_dump() for univ in universities]
    
    @staticmethod
    def get_university_requests(page: int = 1, limit: int = 10, 
                               status: str = '') -> Dict[str, Any]:
        """Get university requests with pagination"""
        skip = (page - 1) * limit
        filter_dict = {}
        
        if status:
            filter_dict['status'] = status
        
        requests = UniversityRequest.find_all(
            filter_dict=filter_dict,
            skip=skip,
            limit=limit,
            sort=[('created_at', -1)]
        )
        
        # Get total count
        total = UniversityRequest.count_documents(filter_dict)
        
        return {
            'requests': [req.model_dump() for req in requests],
            'pagination': {
                'page': page,
                'limit': limit,
                'total': total,
                'pages': (total + limit - 1) // limit
            }
        }
    
    @staticmethod
    def get_university_request_by_id(request_id: str) -> Optional[Dict[str, Any]]:
        """Get university request by ID"""
        request_obj = UniversityRequest.find_by_id(request_id)
        return request_obj.model_dump() if request_obj else None
    
    @staticmethod
    def approve_university_request(request_id: str, admin_id: str) -> Dict[str, Any]:
        """Approve university request and create university"""
        # Get request
        request_obj = UniversityRequest.find_by_id(request_id)
        if not request_obj:
            raise ValueError('Permintaan tidak ditemukan')
        
        if request_obj.status != 'pending':
            raise ValueError('Permintaan sudah diproses sebelumnya')
        
        # Check if university with same code already exists
        existing_univ = University.find_by_kode(request_obj.kode_university)
        if existing_univ:
            raise ValueError('Universitas dengan kode tersebut sudah terdaftar')
        
        # Create university
        university_data = {
            'nama': request_obj.nama_university,
            'kode': request_obj.kode_university,
            'alamat': request_obj.alamat_university,
            'website': request_obj.website_university,
            'status_aktif': True
        }
        
        university = University(**university_data)
        university.save()
        
        # Update request status
        request_obj.status = 'approved'
        request_obj.processed_at = datetime.utcnow()
        request_obj.processed_by = admin_id
        request_obj.save()
        
        return {
            'request': request_obj.model_dump(),
            'university': university.model_dump()
        }
    
    @staticmethod
    def reject_university_request(request_id: str, admin_id: str, 
                                 catatan: str = '') -> Dict[str, Any]:
        """Reject university request"""
        # Get request
        request_obj = UniversityRequest.find_by_id(request_id)
        if not request_obj:
            raise ValueError('Permintaan tidak ditemukan')
        
        if request_obj.status != 'pending':
            raise ValueError('Permintaan sudah diproses sebelumnya')
        
        # Update request status
        request_obj.status = 'rejected'
        request_obj.catatan_admin = catatan
        request_obj.processed_at = datetime.utcnow()
        request_obj.processed_by = admin_id
        request_obj.save()
        
        return request_obj.model_dump()
    
    @staticmethod
    def get_admin_statistics() -> Dict[str, Any]:
        """Get admin dashboard statistics"""
        try:
            db = get_db()
            
            # Count statistics
            total_universities = db.universities.count_documents({})
            active_universities = db.universities.count_documents({'status_aktif': True})
            total_requests = db.university_requests.count_documents({})
            pending_requests = db.university_requests.count_documents({'status': 'pending'})
            approved_requests = db.university_requests.count_documents({'status': 'approved'})
            rejected_requests = db.university_requests.count_documents({'status': 'rejected'})
            total_users = db.users.count_documents({})
            
            # Recent requests (last 5)
            recent_requests_cursor = db.university_requests.find({}).sort('created_at', -1).limit(5)
            recent_requests = [UniversityRequest(**doc).model_dump() for doc in recent_requests_cursor]
            
            return {
                'universities': {
                    'total': total_universities,
                    'active': active_universities,
                    'inactive': total_universities - active_universities
                },
                'requests': {
                    'total': total_requests,
                    'pending': pending_requests,
                    'approved': approved_requests,
                    'rejected': rejected_requests
                },
                'users': {
                    'total': total_users
                },
                'recent_requests': recent_requests
            }
            
        except Exception as e:
            return {
                'universities': {'total': 0, 'active': 0, 'inactive': 0},
                'requests': {'total': 0, 'pending': 0, 'approved': 0, 'rejected': 0},
                'users': {'total': 0},
                'recent_requests': []
            }