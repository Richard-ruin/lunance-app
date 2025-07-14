# app/services/financial_categories.py - New file for Indonesian student categories
from typing import Dict, List

class IndonesianStudentCategories:
    """Kategori keuangan yang disesuaikan untuk mahasiswa Indonesia"""
    
    # Kategori pemasukan untuk mahasiswa Indonesia
    INCOME_CATEGORIES = {
        "uang_saku": {
            "name": "Uang Saku/Kiriman Ortu",
            "keywords": ["uang saku", "kiriman", "ortu", "orang tua", "mama", "papa", "ayah", "ibu", "transfer dari"],
            "description": "Uang saku rutin dari orang tua"
        },
        "part_time": {
            "name": "Part-time Job",
            "keywords": ["part time", "kerja paruh waktu", "jaga warung", "jual", "jualan", "ojol", "grab", "gojek"],
            "description": "Penghasilan dari pekerjaan paruh waktu"
        },
        "freelance": {
            "name": "Freelance/Project",
            "keywords": ["freelance", "project", "tugas", "joki", "les private", "ngajar", "design", "coding"],
            "description": "Penghasilan dari freelance atau project"
        },
        "beasiswa": {
            "name": "Beasiswa",
            "keywords": ["beasiswa", "scholarship", "bantuan pendidikan", "bidikmisi", "pip", "kip"],
            "description": "Dana beasiswa atau bantuan pendidikan"
        },
        "hadiah": {
            "name": "Hadiah/Bonus",
            "keywords": ["hadiah", "bonus", "kado", "THR", "lomba", "menang", "juara", "reward"],
            "description": "Hadiah, bonus, atau uang dari lomba"
        },
        "lainnya": {
            "name": "Lainnya",
            "keywords": [],
            "description": "Pemasukan lainnya"
        }
    }
    
    # Kategori pengeluaran untuk mahasiswa Indonesia
    EXPENSE_CATEGORIES = {
        "makanan": {
            "name": "Makanan & Minuman",
            "keywords": ["makan", "minum", "nasi", "ayam", "soto", "gado-gado", "warteg", "indomie", "kopi", "es teh", "jajan", "snack", "kantin", "foodcourt"],
            "description": "Pengeluaran untuk makanan dan minuman sehari-hari"
        },
        "transportasi": {
            "name": "Transportasi",
            "keywords": ["transport", "angkot", "bus", "ojol", "grab", "gojek", "bensin", "parkir", "tol", "kereta", "motor", "mobil"],
            "description": "Biaya transportasi dan perjalanan"
        },
        "pendidikan": {
            "name": "Pendidikan",
            "keywords": ["buku", "alat tulis", "fotocopy", "print", "tugas", "ukt", "spp", "praktikum", "lab", "seminar", "wisuda"],
            "description": "Keperluan pendidikan dan kuliah"
        },
        "tempat_tinggal": {
            "name": "Kos/Tempat Tinggal",
            "keywords": ["kos", "kost", "sewa", "kontrakan", "boarding house", "asrama", "indekos"],
            "description": "Biaya tempat tinggal"
        },
        "komunikasi": {
            "name": "Internet & Komunikasi",
            "keywords": ["internet", "wifi", "pulsa", "paket data", "kuota", "telkomsel", "xl", "indosat", "tri", "smartfren"],
            "description": "Biaya internet, pulsa, dan komunikasi"
        },
        "hiburan": {
            "name": "Hiburan & Sosial",
            "keywords": ["nonton", "bioskop", "game", "netflix", "spotify", "hangout", "nongkrong", "cafe", "mall", "jalan-jalan"],
            "description": "Hiburan dan kegiatan sosial"
        },
        "kesehatan": {
            "name": "Kesehatan & Kebersihan",
            "keywords": ["obat", "dokter", "puskesmas", "klinik", "vitamin", "shampo", "sabun", "pasta gigi", "skincare"],
            "description": "Kesehatan dan produk kebersihan"
        },
        "pakaian": {
            "name": "Pakaian & Aksesoris",
            "keywords": ["baju", "celana", "sepatu", "sandal", "kaos", "kemeja", "jaket", "tas", "dompet", "jam"],
            "description": "Pakaian dan aksesoris"
        },
        "organisasi": {
            "name": "Organisasi & Kegiatan",
            "keywords": ["ormawa", "organisasi", "himpunan", "ukm", "bem", "kegiatan kampus", "event", "seminar"],
            "description": "Kegiatan organisasi dan kampus"
        },
        "lainnya": {
            "name": "Lainnya",
            "keywords": [],
            "description": "Pengeluaran lainnya"
        }
    }
    
    @classmethod
    def get_income_category(cls, text: str) -> str:
        """Deteksi kategori pemasukan berdasarkan teks"""
        text_lower = text.lower()
        
        for category_id, category_data in cls.INCOME_CATEGORIES.items():
            if any(keyword in text_lower for keyword in category_data["keywords"]):
                return category_data["name"]
        
        return cls.INCOME_CATEGORIES["lainnya"]["name"]
    
    @classmethod
    def get_expense_category(cls, text: str) -> str:
        """Deteksi kategori pengeluaran berdasarkan teks"""
        text_lower = text.lower()
        
        for category_id, category_data in cls.EXPENSE_CATEGORIES.items():
            if any(keyword in text_lower for keyword in category_data["keywords"]):
                return category_data["name"]
        
        return cls.EXPENSE_CATEGORIES["lainnya"]["name"]
    
    @classmethod
    def get_all_income_categories(cls) -> List[str]:
        """Dapatkan semua nama kategori pemasukan"""
        return [cat["name"] for cat in cls.INCOME_CATEGORIES.values()]
    
    @classmethod
    def get_all_expense_categories(cls) -> List[str]:
        """Dapatkan semua nama kategori pengeluaran"""
        return [cat["name"] for cat in cls.EXPENSE_CATEGORIES.values()]
    
    @classmethod
    def get_category_suggestions(cls, category_type: str) -> Dict[str, str]:
        """Dapatkan saran kategori dengan deskripsi"""
        if category_type == "income":
            return {cat["name"]: cat["description"] for cat in cls.INCOME_CATEGORIES.values()}
        elif category_type == "expense":
            return {cat["name"]: cat["description"] for cat in cls.EXPENSE_CATEGORIES.values()}
        else:
            return {}
    
    @classmethod
    def suggest_similar_categories(cls, user_input: str, category_type: str) -> List[str]:
        """Berikan saran kategori yang mirip dengan input user"""
        user_input_lower = user_input.lower()
        suggestions = []
        
        categories = cls.INCOME_CATEGORIES if category_type == "income" else cls.EXPENSE_CATEGORIES
        
        for category_data in categories.values():
            # Check if any keyword partially matches
            for keyword in category_data["keywords"]:
                if keyword in user_input_lower or user_input_lower in keyword:
                    if category_data["name"] not in suggestions:
                        suggestions.append(category_data["name"])
                    break
        
        return suggestions[:3]  # Return top 3 suggestions