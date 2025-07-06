import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config.database import init_db
from app.config.settings import Config
from app.api.v1.university.routes import router as university_router
from app.api.v1.auth.routes import router as auth_router
from app.api.v1.admin.routes import router as admin_router

# Initialize FastAPI app
app = FastAPI(
    title="Lunance API",
    description="API untuk aplikasi manajemen keuangan mahasiswa",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database
@app.on_event("startup")
async def startup_event():
    init_db()

# Include routers
app.include_router(university_router, prefix="/api/v1/universities", tags=["Universities"])
app.include_router(auth_router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(admin_router, prefix="/api/v1/admin", tags=["Admin"])

# Health check endpoint
@app.get("/")
async def root():
    return {"message": "Lunance API is running", "status": "healthy"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "lunance-backend"}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=Config.DEBUG,
        log_level="info"
    )