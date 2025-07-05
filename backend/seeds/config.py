from typing import Dict, Any
import os
from dotenv import load_dotenv

load_dotenv()

SEED_CONFIG: Dict[str, Any] = {
    "mongodb_url": os.getenv("MONGODB_URL", "mongodb://localhost:27017/lunance"),
    "database_name": "lunance",
    "collections": {
        "universities": "universities",
        "users": "users"
    },
    "batch_size": 1000,
    "clear_existing": True
}