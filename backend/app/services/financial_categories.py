# app/services/financial_categories.py - UPDATED untuk metode 50/30/20
from typing import Dict, List, Any

class IndonesianStudentCategories:
    """
    Kategori keuangan yang disesuaikan untuk mahasiswa Indonesia dengan metode 50/30/20
    
    Metode 50/30/20 Elizabeth Warren:
    - 50% NEEDS (Kebutuhan): Hal-hal yang HARUS dibayar untuk bertahan hidup
    - 30% WANTS (Keinginan): Hal-hal yang ingin dibeli tapi tidak wajib
    - 20% SAVINGS (Tabungan): Tabungan dan investasi untuk masa depan
    """
    
    # ===== 50% NEEDS - KEBUTUHAN POKOK MAHASISWA =====
    NEEDS_CATEGORIES = {
        "makanan_pokok": {
            "name": "Makanan Pokok",
            "keywords": ["makan", "nasi", "lauk", "sayur", "buah", "groceries", "beras", "minyak", "garam", "gula", "telur", "daging", "ikan", "tahu", "tempe", "masak", "dapur"],
            "description": "Makanan sehari-hari dan bahan pokok untuk kebutuhan gizi",
            "budget_type": "needs",
            "essential": True
        },
        "tempat_tinggal": {
            "name": "Kos/Tempat Tinggal", 
            "keywords": ["kos", "kost", "sewa", "kontrakan", "boarding house", "asrama", "indekos", "listrik", "air", "wifi kos", "kamar"],
            "description": "Biaya tempat tinggal dan utilitasnya",
            "budget_type": "needs", 
            "essential": True
        },
        "transportasi_wajib": {
            "name": "Transportasi Wajib",
            "keywords": ["transport", "angkot", "bus", "kereta", "ojol kuliah", "grab kampus", "gojek kuliah", "bensin motor", "parkir kampus"],
            "description": "Transportasi untuk ke kampus dan kebutuhan wajib",
            "budget_type": "needs",
            "essential": True
        },
        "pendidikan": {
            "name": "Pendidikan",
            "keywords": ["buku", "alat tulis", "fotocopy", "print", "tugas", "ukt", "spp", "praktikum", "lab", "seminar", "wisuda", "skripsi", "thesis"],
            "description": "Keperluan pendidikan dan kuliah yang wajib",
            "budget_type": "needs",
            "essential": True
        },
        "komunikasi_wajib": {
            "name": "Internet & Komunikasi",
            "keywords": ["internet", "wifi", "pulsa", "paket data", "kuota", "zoom", "google meet", "kuliah online"],
            "description": "Internet dan komunikasi untuk kuliah",
            "budget_type": "needs",
            "essential": True
        },
        "kesehatan_dasar": {
            "name": "Kesehatan & Kebersihan",
            "keywords": ["obat", "dokter", "puskesmas", "klinik", "vitamin wajib", "shampo", "sabun", "pasta gigi", "sikat gigi", "detergen"],
            "description": "Kesehatan dan kebersihan dasar yang wajib",
            "budget_type": "needs",
            "essential": True
        }
    }
    
    # ===== 30% WANTS - KEINGINAN DAN LIFESTYLE =====
    WANTS_CATEGORIES = {
        "hiburan": {
            "name": "Hiburan & Sosial",
            "keywords": ["nonton", "bioskop", "cinema", "game", "netflix", "spotify", "hangout", "nongkrong", "cafe", "mall", "jalan-jalan", "konser"],
            "description": "Hiburan dan kegiatan sosial yang menyenangkan",
            "budget_type": "wants",
            "essential": False
        },
        "jajan": {
            "name": "Jajan & Snack",
            "keywords": ["jajan", "snack", "es", "kopi", "bubble tea", "martabak", "bakso", "soto", "gado-gado", "foodcourt", "delivery", "gofood", "grabfood"],
            "description": "Jajan dan makanan di luar kebutuhan pokok",
            "budget_type": "wants", 
            "essential": False
        },
        "pakaian_gaya": {
            "name": "Pakaian & Aksesoris",
            "keywords": ["baju", "celana", "sepatu", "sandal", "kaos", "kemeja", "jaket", "tas", "dompet", "jam", "aksesoris", "fashion"],
            "description": "Pakaian dan aksesoris di luar kebutuhan dasar",
            "budget_type": "wants",
            "essential": False
        },
        "organisasi_sosial": {
            "name": "Organisasi & Event",
            "keywords": ["ormawa", "organisasi", "himpunan", "ukm", "bem", "kegiatan kampus", "event", "seminar", "workshop", "gathering"],
            "description": "Kegiatan organisasi dan event sosial kampus",
            "budget_type": "wants",
            "essential": False
        },
        "target_barang": {
            "name": "Target Tabungan Barang",
            "keywords": ["nabung", "tabung", "target", "ingin beli", "mau beli", "pengen beli", "laptop", "hp", "handphone", "gadget", "motor", "sepeda"],
            "description": "Menabung dari budget wants untuk barang yang diinginkan",
            "budget_type": "wants",
            "essential": False,
            "is_savings_goal": True
        },
        "lainnya_wants": {
            "name": "Lainnya (Wants)",
            "keywords": [],
            "description": "Keinginan lainnya yang tidak masuk kategori di atas",
            "budget_type": "wants",
            "essential": False
        }
    }
    
    # ===== 20% SAVINGS - TABUNGAN MASA DEPAN =====
    SAVINGS_CATEGORIES = {
        "tabungan_umum": {
            "name": "Tabungan Umum",
            "keywords": ["tabungan", "saving", "simpan", "deposito", "rekening", "menabung umum"],
            "description": "Tabungan tanpa tujuan spesifik untuk masa depan",
            "budget_type": "savings",
            "essential": True
        },
        "dana_darurat": {
            "name": "Dana Darurat",
            "keywords": ["dana darurat", "emergency", "darurat", "cadangan", "emergency fund"],
            "description": "Dana untuk situasi mendesak dan tak terduga",
            "budget_type": "savings",
            "essential": True
        },
        "investasi": {
            "name": "Investasi Masa Depan",
            "keywords": ["investasi", "reksadana", "saham", "obligasi", "sbn", "crypto", "bitcoin", "ethereum", "trading"],
            "description": "Investasi untuk pertumbuhan kekayaan jangka panjang",
            "budget_type": "savings",
            "essential": False
        },
        "tabungan_jangka_panjang": {
            "name": "Tabungan Jangka Panjang",
            "keywords": ["modal usaha", "setelah lulus", "karir", "menikah", "rumah", "masa depan", "pensiun"],
            "description": "Tabungan untuk tujuan besar setelah lulus",
            "budget_type": "savings",
            "essential": False
        }
    }
    
    # ===== INCOME CATEGORIES (tidak berubah) =====
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
    
    @classmethod
    def get_expense_category_with_budget_type(cls, text: str) -> tuple:
        """
        Deteksi kategori pengeluaran dan budget type (needs/wants/savings)
        Returns: (category_name, budget_type)
        """
        text_lower = text.lower()
        
        # Check NEEDS categories first (priority)
        for category_id, category_data in cls.NEEDS_CATEGORIES.items():
            if any(keyword in text_lower for keyword in category_data["keywords"]):
                return category_data["name"], "needs"
        
        # Check WANTS categories
        for category_id, category_data in cls.WANTS_CATEGORIES.items():
            if any(keyword in text_lower for keyword in category_data["keywords"]):
                return category_data["name"], "wants"
        
        # Check SAVINGS categories
        for category_id, category_data in cls.SAVINGS_CATEGORIES.items():
            if any(keyword in text_lower for keyword in category_data["keywords"]):
                return category_data["name"], "savings"
        
        # Default ke wants jika tidak dapat dikategorikan
        return "Lainnya (Wants)", "wants"
    
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
        """Deteksi kategori pengeluaran (backward compatibility)"""
        category_name, _ = cls.get_expense_category_with_budget_type(text)
        return category_name
    
    @classmethod
    def get_budget_type(cls, category_name: str) -> str:
        """Tentukan budget type dari nama kategori"""
        # Search in NEEDS
        for category_data in cls.NEEDS_CATEGORIES.values():
            if category_data["name"] == category_name:
                return "needs"
        
        # Search in WANTS  
        for category_data in cls.WANTS_CATEGORIES.values():
            if category_data["name"] == category_name:
                return "wants"
        
        # Search in SAVINGS
        for category_data in cls.SAVINGS_CATEGORIES.values():
            if category_data["name"] == category_name:
                return "savings"
        
        # Default
        return "wants"
    
    @classmethod
    def get_all_needs_categories(cls) -> List[str]:
        """Dapatkan semua kategori NEEDS (50%)"""
        return [cat["name"] for cat in cls.NEEDS_CATEGORIES.values()]
    
    @classmethod
    def get_all_wants_categories(cls) -> List[str]:
        """Dapatkan semua kategori WANTS (30%)"""
        return [cat["name"] for cat in cls.WANTS_CATEGORIES.values()]
    
    @classmethod
    def get_all_savings_categories(cls) -> List[str]:
        """Dapatkan semua kategori SAVINGS (20%)"""
        return [cat["name"] for cat in cls.SAVINGS_CATEGORIES.values()]
    
    @classmethod
    def get_all_income_categories(cls) -> List[str]:
        """Dapatkan semua nama kategori pemasukan"""
        return [cat["name"] for cat in cls.INCOME_CATEGORIES.values()]
    
    @classmethod
    def get_all_expense_categories(cls) -> List[str]:
        """Dapatkan semua nama kategori pengeluaran (needs + wants + savings)"""
        categories = []
        categories.extend(cls.get_all_needs_categories())
        categories.extend(cls.get_all_wants_categories()) 
        categories.extend(cls.get_all_savings_categories())
        return categories
    
    @classmethod
    def get_categories_by_budget_type(cls) -> Dict[str, List[str]]:
        """Dapatkan kategori yang digroup berdasarkan budget type 50/30/20"""
        return {
            "needs": cls.get_all_needs_categories(),
            "wants": cls.get_all_wants_categories(),
            "savings": cls.get_all_savings_categories(),
            "income": cls.get_all_income_categories()
        }
    
    @classmethod
    def get_category_suggestions(cls, category_type: str) -> Dict[str, str]:
        """Dapatkan saran kategori dengan deskripsi berdasarkan budget type"""
        if category_type == "needs":
            return {cat["name"]: cat["description"] for cat in cls.NEEDS_CATEGORIES.values()}
        elif category_type == "wants":
            return {cat["name"]: cat["description"] for cat in cls.WANTS_CATEGORIES.values()}
        elif category_type == "savings":
            return {cat["name"]: cat["description"] for cat in cls.SAVINGS_CATEGORIES.values()}
        elif category_type == "income":
            return {cat["name"]: cat["description"] for cat in cls.INCOME_CATEGORIES.values()}
        else:
            return {}
    
    @classmethod
    def get_budget_allocation_guide(cls) -> Dict[str, Any]:
        """Panduan alokasi budget 50/30/20 untuk mahasiswa Indonesia"""
        return {
            "method": "50/30/20 Elizabeth Warren",
            "description": "Metode budgeting yang membagi pemasukan menjadi 3 kategori utama",
            "allocation": {
                "needs": {
                    "percentage": 50,
                    "description": "Kebutuhan pokok yang HARUS dibayar untuk bertahan hidup",
                    "categories": cls.get_all_needs_categories(),
                    "examples": [
                        "Sewa kos Rp 800.000",
                        "Makan sehari-hari Rp 500.000", 
                        "Transport ke kampus Rp 300.000",
                        "Buku dan alat kuliah Rp 200.000"
                    ],
                    "tips": [
                        "Prioritaskan kategori ini sebelum yang lain",
                        "Jika lebih dari 50%, cari cara untuk menghemat",
                        "Focus pada efisiensi, bukan elimination"
                    ]
                },
                "wants": {
                    "percentage": 30,
                    "description": "Keinginan dan lifestyle yang membuat hidup lebih menyenangkan",
                    "categories": cls.get_all_wants_categories(),
                    "examples": [
                        "Nongkrong di cafe Rp 200.000",
                        "Beli baju baru Rp 300.000",
                        "Nonton bioskop Rp 100.000", 
                        "Nabung buat laptop Rp 400.000"
                    ],
                    "tips": [
                        "Dari 30% ini bisa untuk target tabungan barang",
                        "Boleh fleksibel, tapi jangan sampai lebih dari 30%",
                        "Gunakan untuk menjaga mental health dan socializing"
                    ]
                },
                "savings": {
                    "percentage": 20,
                    "description": "Tabungan dan investasi untuk masa depan",
                    "categories": cls.get_all_savings_categories(),
                    "examples": [
                        "Tabungan umum Rp 300.000",
                        "Dana darurat Rp 200.000",
                        "Investasi reksadana Rp 100.000",
                        "Modal usaha masa depan Rp 400.000"
                    ],
                    "tips": [
                        "Minimal 20% untuk membangun wealth jangka panjang",
                        "Prioritaskan dana darurat dulu sebelum investasi",
                        "Konsisten lebih penting daripada jumlah besar"
                    ]
                }
            },
            "reset_schedule": "Setiap tanggal 1 untuk budget bulanan baru",
            "flexibility": "Budget bisa disesuaikan kebutuhan, tapi tetap maintain proporsi 50/30/20"
        }
    
    @classmethod
    def suggest_similar_categories(cls, user_input: str, budget_type: str = None) -> List[str]:
        """Berikan saran kategori yang mirip dengan input user berdasarkan budget type"""
        user_input_lower = user_input.lower()
        suggestions = []
        
        # Tentukan categories yang akan dicari
        if budget_type == "needs":
            categories = cls.NEEDS_CATEGORIES
        elif budget_type == "wants":
            categories = cls.WANTS_CATEGORIES
        elif budget_type == "savings":
            categories = cls.SAVINGS_CATEGORIES
        else:
            # Search all expense categories
            categories = {**cls.NEEDS_CATEGORIES, **cls.WANTS_CATEGORIES, **cls.SAVINGS_CATEGORIES}
        
        for category_data in categories.values():
            # Check if any keyword partially matches
            for keyword in category_data["keywords"]:
                if keyword in user_input_lower or user_input_lower in keyword:
                    if category_data["name"] not in suggestions:
                        suggestions.append(category_data["name"])
                    break
        
        return suggestions[:3]  # Return top 3 suggestions