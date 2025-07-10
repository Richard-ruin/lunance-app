#!/usr/bin/env python3
"""
Script untuk menjalankan Lunance Backend Server
"""

import uvicorn
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

if __name__ == "__main__":
    # Konfigurasi server
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    debug = os.getenv("DEBUG", "True").lower() == "true"
    
    print("🚀 Memulai Lunance Backend Server...")
    print(f"🌐 Host: {host}")
    print(f"🔌 Port: {port}")
    print(f"🐛 Debug Mode: {debug}")
    print(f"📖 API Documentation: http://{host}:{port}/docs")
    print("=" * 50)
    
    # Jalankan server
    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=debug,
        access_log=debug,
        log_level="info" if debug else "warning"
    )