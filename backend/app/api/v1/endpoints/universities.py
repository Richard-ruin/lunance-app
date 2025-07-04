"""
University Endpoints
API endpoints untuk university management dengan approval system
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query

from ....core.middleware import standard_rate_limit, auth_rate_limit
from ....crud.university import crud_university, crud_faculty, crud_department
from ....schemas.university import (
    UniversityCreate,
    UniversityUpdate,
    UniversityResponse,
    UniversityDetailResponse,
    FacultyCreate,
    FacultyUpdate,
    FacultyResponse,
    DepartmentCreate,
    DepartmentUpdate,
    DepartmentResponse,
    UniversityApproval,
    UniversityStatsResponse
)
from ....schemas.base import (
    DataResponse,
    SuccessResponse,
    PaginatedResponse
)
from ....models.university import ApprovalStatus
from ..deps import (
    get_pagination_params,
    get_search_params,
    get_current_user,
    get_current_admin_user,
    validate_university_id,
    validate_faculty_id,
    validate_department_id,
    CurrentUser
)

router = APIRouter()


# University Endpoints
@router.get(
    "/",
    response_model=PaginatedResponse,
    summary="Get universities",
    description="Get paginated list of universities"
)
@standard_rate_limit()
async def get_universities(
    *,
    pagination: tuple = Depends(get_pagination_params),
    search_params: dict = Depends(get_search_params),
    approval_status: Optional[ApprovalStatus] = Query(None, description="Filter by approval status"),
    approved_only: bool = Query(True, description="Show only approved universities")
) -> PaginatedResponse:
    """
    Get paginated list of universities
    
    - Default: hanya tampilkan universitas yang sudah approved
    - Admin dapat melihat semua status
    """
    skip, limit = pagination
    
    # Build query
    query = {}
    
    if approved_only and not approval_status:
        query["approval_status"] = ApprovalStatus.APPROVED
    elif approval_status:
        query["approval_status"] = approval_status
    
    if search_params["search"]:
        query["$or"] = [
            {"name": {"$regex": search_params["search"], "$options": "i"}},
            {"domain": {"$regex": search_params["search"], "$options": "i"}}
        ]
    
    result = await crud_university.paginate(
        page=(skip // limit) + 1,
        per_page=limit,
        query=query,
        sort_by=search_params["sort_by"] or "name",
        sort_order=search_params["sort_order"]
    )
    
    return PaginatedResponse(**result)


@router.post(
    "/",
    response_model=DataResponse[UniversityResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create university",
    description="Create new university (will be pending approval)"
)
@auth_rate_limit()
async def create_university(
    *,
    university_in: UniversityCreate,
    current_user: CurrentUser = Depends(get_current_user)
) -> DataResponse[UniversityResponse]:
    """
    Create new university
    
    - University akan dalam status pending approval
    - Domain harus unik dan berakhiran .ac.id
    """
    try:
        university = await crud_university.create_university(
            obj_in=university_in,
            created_by=current_user.id
        )
        
        return DataResponse(
            message="Universitas berhasil didaftarkan dan menunggu persetujuan",
            data=UniversityResponse.model_validate(university.model_dump())
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get(
    "/pending-approval",
    response_model=DataResponse[List[UniversityResponse]],
    summary="Get pending universities",
    description="Get universities pending approval (admin only)"
)
@standard_rate_limit()
async def get_pending_universities(
    current_user: CurrentUser = Depends(get_current_admin_user)
) -> DataResponse[List[UniversityResponse]]:
    """
    Get universities pending approval
    
    **Admin only endpoint**
    """
    universities = await crud_university.get_pending_approval()
    
    return DataResponse(
        message="Pending universities retrieved successfully",
        data=[UniversityResponse.model_validate(u.model_dump()) for u in universities]
    )


@router.post(
    "/approve",
    response_model=SuccessResponse,
    summary="Approve/Reject universities",
    description="Approve or reject university applications (admin only)"
)
@auth_rate_limit()
async def approve_university(
    *,
    approval_data: UniversityApproval,
    current_user: CurrentUser = Depends(get_current_admin_user)
) -> SuccessResponse:
    """
    Approve, reject, or suspend university
    
    **Admin only endpoint**
    """
    try:
        if approval_data.action == "approve":
            university = await crud_university.approve_university(
                university_id=approval_data.university_id,
                approved_by=current_user.id
            )
            message = "Universitas berhasil disetujui"
            
        elif approval_data.action == "reject":
            if not approval_data.reason:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Alasan penolakan harus diisi"
                )
            university = await crud_university.reject_university(
                university_id=approval_data.university_id,
                rejected_by=current_user.id,
                reason=approval_data.reason
            )
            message = "Universitas berhasil ditolak"
            
        elif approval_data.action == "suspend":
            if not approval_data.reason:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Alasan suspend harus diisi"
                )
            university = await crud_university.suspend_university(
                university_id=approval_data.university_id,
                suspended_by=current_user.id,
                reason=approval_data.reason
            )
            message = "Universitas berhasil disuspend"
        
        if not university:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Universitas tidak ditemukan"
            )
        
        return SuccessResponse(message=message)
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get(
    "/stats",
    response_model=DataResponse[UniversityStatsResponse],
    summary="Get university statistics",
    description="Get university statistics (admin only)"
)
@standard_rate_limit()
async def get_university_stats(
    current_user: CurrentUser = Depends(get_current_admin_user)
) -> DataResponse[UniversityStatsResponse]:
    """
    Get university statistics
    
    **Admin only endpoint**
    """
    stats = await crud_university.get_university_stats()
    
    return DataResponse(
        message="University statistics retrieved successfully",
        data=UniversityStatsResponse.model_validate(stats)
    )


@router.get(
    "/{university_id}",
    response_model=DataResponse[UniversityDetailResponse],
    summary="Get university by ID",
    description="Get detailed university information"
)
@standard_rate_limit()
async def get_university_by_id(
    university_id: str = Depends(validate_university_id)
) -> DataResponse[UniversityDetailResponse]:
    """Get university by ID dengan informasi lengkap"""
    university = await crud_university.get(university_id)
    
    if not university:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Universitas tidak ditemukan"
        )
    
    # Get faculties
    faculties = await crud_faculty.get_by_university(university_id)
    
    university_data = university.model_dump()
    university_data["faculties"] = [f.model_dump() for f in faculties]
    
    return DataResponse(
        message="University retrieved successfully",
        data=UniversityDetailResponse.model_validate(university_data)
    )


# Faculty Endpoints
@router.get(
    "/{university_id}/faculties",
    response_model=DataResponse[List[FacultyResponse]],
    summary="Get faculties by university",
    description="Get all faculties in a university"
)
@standard_rate_limit()
async def get_faculties_by_university(
    university_id: str = Depends(validate_university_id)
) -> DataResponse[List[FacultyResponse]]:
    """Get all faculties in a university"""
    # Verify university exists
    university = await crud_university.get(university_id)
    if not university:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Universitas tidak ditemukan"
        )
    
    faculties = await crud_faculty.get_by_university(university_id)
    
    return DataResponse(
        message="Faculties retrieved successfully",
        data=[FacultyResponse.model_validate(f.model_dump()) for f in faculties]
    )


@router.post(
    "/{university_id}/faculties",
    response_model=DataResponse[FacultyResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create faculty",
    description="Create new faculty in university"
)
@auth_rate_limit()
async def create_faculty(
    *,
    university_id: str = Depends(validate_university_id),
    faculty_in: FacultyCreate,
    current_user: CurrentUser = Depends(get_current_user)
) -> DataResponse[FacultyResponse]:
    """Create new faculty in university"""
    try:
        # Set university_id from URL
        faculty_data = faculty_in.model_dump()
        faculty_data["university_id"] = university_id
        faculty_create = FacultyCreate.model_validate(faculty_data)
        
        faculty = await crud_faculty.create_faculty(
            obj_in=faculty_create,
            created_by=current_user.id
        )
        
        return DataResponse(
            message="Fakultas berhasil dibuat",
            data=FacultyResponse.model_validate(faculty.model_dump())
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


# Department Endpoints  
@router.get(
    "/faculties/{faculty_id}/departments",
    response_model=DataResponse[List[DepartmentResponse]],
    summary="Get departments by faculty",
    description="Get all departments in a faculty"
)
@standard_rate_limit()
async def get_departments_by_faculty(
    faculty_id: str = Depends(validate_faculty_id)
) -> DataResponse[List[DepartmentResponse]]:
    """Get all departments in a faculty"""
    # Verify faculty exists
    faculty = await crud_faculty.get(faculty_id)
    if not faculty:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Fakultas tidak ditemukan"
        )
    
    departments = await crud_department.get_by_faculty(faculty_id)
    
    return DataResponse(
        message="Departments retrieved successfully",
        data=[DepartmentResponse.model_validate(d.model_dump()) for d in departments]
    )


@router.post(
    "/faculties/{faculty_id}/departments",
    response_model=DataResponse[DepartmentResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create department",
    description="Create new department in faculty"
)
@auth_rate_limit()
async def create_department(
    *,
    faculty_id: str = Depends(validate_faculty_id),
    department_in: DepartmentCreate,
    current_user: CurrentUser = Depends(get_current_user)
) -> DataResponse[DepartmentResponse]:
    """Create new department in faculty"""
    try:
        # Set faculty_id from URL
        department_data = department_in.model_dump()
        department_data["faculty_id"] = faculty_id
        department_create = DepartmentCreate.model_validate(department_data)
        
        department = await crud_department.create_department(
            obj_in=department_create,
            created_by=current_user.id
        )
        
        return DataResponse(
            message="Jurusan berhasil dibuat",
            data=DepartmentResponse.model_validate(department.model_dump())
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )