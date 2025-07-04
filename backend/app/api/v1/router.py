"""
API v1 Router
Main router untuk API version 1 dengan semua endpoints
"""

from fastapi import APIRouter

from .endpoints import (
    users,
    universities,
    categories,
    transactions,
    savings_targets
)

# Create main router untuk API v1
api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(
    users.router,
    prefix="/users",
    tags=["users"]
)

api_router.include_router(
    universities.router,
    prefix="/universities",
    tags=["universities"]
)

api_router.include_router(
    categories.router,
    prefix="/categories", 
    tags=["categories"]
)

api_router.include_router(
    transactions.router,
    prefix="/transactions",
    tags=["transactions"]
)

api_router.include_router(
    savings_targets.router,
    prefix="/savings-targets",
    tags=["savings-targets"]
)