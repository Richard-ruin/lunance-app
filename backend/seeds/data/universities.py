from datetime import datetime
from typing import List, Dict, Any
from ..utils.helpers import INDONESIAN_UNIVERSITIES, PROGRAM_STUDI
import random

def generate_universities_data() -> List[Dict[str, Any]]:
    """Generate university seed data"""
    universities = []
    
    for i, univ_data in enumerate(INDONESIAN_UNIVERSITIES):
        # Get program studi for each fakultas
        all_prodi = []
        for fakultas in univ_data["fakultas"]:
            if fakultas in PROGRAM_STUDI:
                all_prodi.extend(PROGRAM_STUDI[fakultas])
        
        # Remove duplicates
        all_prodi = list(set(all_prodi))
        
        university = {
            "nama_universitas": univ_data["nama"],
            "fakultas": univ_data["fakultas"],
            "program_studi": all_prodi,
            "status": "approved",
            "requested_by": None,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "approved_at": datetime.utcnow(),
            "approved_by": None,
            # Additional data for reference
            "domain": univ_data["domain"],
            "region": univ_data["region"]
        }
        
        universities.append(university)
    
    # Add some pending universities for testing
    pending_universities = [
        {
            "nama_universitas": "Universitas Teknologi Digital Indonesia",
            "fakultas": ["Teknik", "FMIPA", "Ekonomi"],
            "program_studi": ["Informatika", "Sistem Informasi", "Teknik Elektro", "Matematika", "Manajemen"],
            "status": "pending",
            "requested_by": None,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "approved_at": None,
            "approved_by": None,
            "domain": "utdi.ac.id",
            "region": "Jakarta"
        },
        {
            "nama_universitas": "Institut Sains dan Teknologi Nusantara",
            "fakultas": ["Teknik", "FMIPA"],
            "program_studi": ["Teknik Informatika", "Teknik Mesin", "Fisika", "Kimia"],
            "status": "pending",
            "requested_by": None,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "approved_at": None,
            "approved_by": None,
            "domain": "istn.ac.id",
            "region": "Bandung"
        }
    ]
    
    universities.extend(pending_universities)
    
    print(f"Generated {len(universities)} universities")
    return universities