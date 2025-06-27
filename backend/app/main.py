from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import logging
import os

from app.config.database import connect_to_mongo, close_mongo_connection
from app.config.settings import settings
from app.api.v1.auth.routes import router as auth_router
from app.api.v1.students.routes import router as students_router
from app.api.v1.dashboard.routes import router as dashboard_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    # Create static directories if they don't exist
    os.makedirs("static/uploads/profile_pictures", exist_ok=True)
    os.makedirs("static/uploads", exist_ok=True)
    
    await connect_to_mongo()
    yield
    # Shutdown
    await close_mongo_connection()

# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files - untuk profile pictures
app.mount(
    "/static/profile_pictures", 
    StaticFiles(directory="static/uploads/profile_pictures"), 
    name="profile_pictures"
)

# Mount static files - untuk uploads umum (receipts, etc)
app.mount(
    "/static/uploads", 
    StaticFiles(directory="static/uploads"), 
    name="uploads"
)

# Include routers
app.include_router(auth_router, prefix="/api/v1")
app.include_router(students_router, prefix="/api/v1/students")
app.include_router(dashboard_router, prefix="/api/v1/dashboard")

@app.get("/")
async def root():
    return {
        "message": "Student Finance Tracker API",
        "version": settings.APP_VERSION,
        "status": "running"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}