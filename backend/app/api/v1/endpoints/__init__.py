# app/api/v1/endpoints/__init__.py
"""API v1 endpoints dengan semua router termasuk notifications."""

from fastapi import APIRouter
from . import (
    auth, users, universities, university_requests, 
    categories, transactions, savings_targets,
    notifications  # Pastikan notifications di-import
)

router = APIRouter()

# Include existing endpoint routers
router.include_router(auth.router, prefix="/auth", tags=["🔐 Authentication"])
router.include_router(users.router, prefix="/users", tags=["👥 User Management"])
router.include_router(universities.router, prefix="/universities", tags=["🏫 University Management"])
router.include_router(university_requests.router, prefix="/university-requests", tags=["📝 University Requests"])
router.include_router(categories.router, prefix="/categories", tags=["📂 Category Management"])
router.include_router(transactions.router, prefix="/transactions", tags=["💰 Transaction Management"])
router.include_router(savings_targets.router, prefix="/savings-targets", tags=["🎯 Savings Targets"])

# IMPORTANT: Include notifications router
router.include_router(notifications.router, prefix="/notifications", tags=["🔔 Notifications"])


# Health check endpoint untuk API v1
@router.get("/health")
async def api_health_check():
    """API v1 health check endpoint dengan semua services."""
    return {
        "status": "healthy",
        "message": "Lunance API v1 dengan semua fitur berjalan dengan baik",
        "version": "1.0.0",
        "endpoints": {
            "authentication": "/auth",
            "user_management": "/users", 
            "university_management": "/universities",
            "university_requests": "/university-requests",
            "category_management": "/categories",
            "transaction_management": "/transactions",
            "savings_targets": "/savings-targets",
            "notifications": "/notifications"  # Pastikan notifications ada di sini
        },
        "features": {
            "real_time_notifications": "Notifikasi real-time via WebSocket",
            "email_notifications": "Notifikasi via email",
            "push_notifications": "Push notification support",
            "notification_settings": "Pengaturan notifikasi personal",
            "broadcasting": "Sistem broadcast untuk admin"
        }
    }


# API info endpoint
@router.get("/info")
async def api_info():
    """API v1 information endpoint dengan detail semua capabilities."""
    endpoints_info = {
        "authentication": {
            "path": "/auth",
            "features": [
                "User registration dengan OTP",
                "Login/logout dengan JWT",
                "Password reset via email",
                "Email verification",
                "Token refresh mechanism"
            ]
        },
        "user_management": {
            "path": "/users", 
            "features": [
                "User profile management",
                "Admin user operations",
                "User statistics",
                "Search dan filtering",
                "Bulk operations"
            ]
        },
        "university_management": {
            "path": "/universities",
            "features": [
                "University CRUD operations",
                "Faculty management", 
                "Major management",
                "Public university listings",
                "Admin management tools"
            ]
        },
        "university_requests": {
            "path": "/university-requests",
            "features": [
                "Student request system",
                "Admin approval workflow",
                "Email notifications",
                "Request statistics",
                "Data suggestions"
            ]
        },
        "category_management": {
            "path": "/categories",
            "features": [
                "Global dan personal categories",
                "Category CRUD operations",
                "Usage statistics",
                "Search dan filtering",
                "Admin category management"
            ]
        },
        "transaction_management": {
            "path": "/transactions",
            "features": [
                "Transaction CRUD operations",
                "Advanced filtering dan search",
                "Bulk operations",
                "Analytics dan summaries",
                "Dashboard overview"
            ]
        },
        "savings_targets": {
            "path": "/savings-targets",
            "features": [
                "Savings target management",
                "Contribution tracking",
                "Progress projections",
                "Achievement tracking",
                "Analytics dan insights"
            ]
        },
        "notifications": {
            "path": "/notifications",
            "features": [
                "🔔 Real-time notifications",
                "📧 Email notifications",
                "📱 Push notifications", 
                "⚙️ Personal notification settings",
                "📊 Notification statistics",
                "📢 Admin broadcasting",
                "🎯 Targeted messaging",
                "📝 Notification templates dalam Bahasa Indonesia",
                "🔄 Multi-channel delivery",
                "⏰ Notification scheduling"
            ]
        }
    }
    
    return {
        "name": "Lunance API v1 - Complete Edition",
        "version": "1.0.0",
        "description": "Smart Personal Finance Management API untuk Mahasiswa Indonesia dengan fitur lengkap",
        "total_endpoints": len(endpoints_info),
        "endpoints": endpoints_info,
        "notification_features": {
            "supported_types": [
                "💰 Transaction notifications",
                "🎯 Savings goal alerts", 
                "💳 Budget warnings",
                "🤖 AI insights",
                "⏰ Reminders",
                "🔧 System notifications",
                "👨‍💼 Admin messages"
            ],
            "delivery_channels": [
                "WebSocket (Real-time)",
                "Email (HTML + Text)",
                "Push Notifications (Ready)",
                "Database Storage"
            ],
            "languages": ["Bahasa Indonesia (Primary)"],
            "personalization": [
                "Per-category settings",
                "Quiet hours",
                "Digest frequency",
                "Channel preferences"
            ]
        },
        "features": [
            "🔐 Complete Authentication System",
            "👥 User Management dengan Role-based Access",
            "🏫 University System dengan Hierarchy",
            "📝 University Request Workflow",
            "📂 Category Management (Global & Personal)",
            "💰 Transaction Management & Analytics", 
            "🎯 Savings Target System",
            "📊 Financial Dashboard & Insights",
            "🔔 Comprehensive Notification System",
            "📧 Email Integration",
            "💬 Real-time WebSocket Support",
            "📢 Broadcasting System",
            "🔍 Advanced Search dan Filtering",
            "📄 Pagination Support",
            "⚡ Rate Limiting",
            "🛡️ Security Headers",
            "📊 Performance Monitoring"
        ]
    }


__all__ = [
    "router",
    "auth",
    "users", 
    "universities",
    "university_requests",
    "categories",
    "transactions", 
    "savings_targets",
    "notifications"  # Pastikan notifications di-export
]