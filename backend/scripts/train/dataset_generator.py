# scripts/train/dataset_generator.py - ADVANCED BALANCED DATASET GENERATOR
import os
import json
import random
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any
from collections import defaultdict

logger = logging.getLogger(__name__)

class AdvancedDatasetGenerator:
    """
    ADVANCED dataset generator with balanced approach
    
    Key improvements:
    1. Reduced bias towards financial detection
    2. Enhanced non-financial examples  
    3. Better query detection training
    4. Improved category balance
    5. Advanced data augmentation
    """
    
    def __init__(self, config):
        self.config = config
        self.setup_advanced_templates()
        self.setup_enhanced_vocabulary()
        self.setup_query_patterns()
        self.setup_non_financial_patterns()
        
    def setup_advanced_templates(self):
        """Setup balanced templates with reduced financial bias"""
        
        # INCOME TEMPLATES - More conservative
        self.income_templates = [
            # Natural but clear income expressions
            "Dapat {amount} dari {source}",
            "Terima {amount} dari {source}",
            "Transfer masuk {amount} dari {source}",
            "{source} kasih {amount}",
            "{source} kirim {amount}",
            "Gaji {amount} dari {source}",
            "Honor {amount} dari {source}",
            "Fee {amount} dari {source}",
            "Beasiswa {amount} cair",
            "Bonus {amount} dari {source}",
            "Cashback {amount}",
            "Refund {amount}",
            "Freelance {amount} selesai",
            "Part time dapat {amount}",
            "Jualan {amount} profit",
            # Family context
            "Uang saku {amount} dari ortu",
            "Papa transfer {amount}",
            "Mama kasih {amount}",
            "Bokap kirim {amount}",
            "Nyokap kasih jajan {amount}",
        ]
        
        # EXPENSE TEMPLATES - More conservative
        self.expense_templates = [
            # Clear expense expressions
            "Bayar {category} {amount}",
            "Beli {category} {amount}",
            "Belanja {category} {amount}",
            "Habis {amount} untuk {category}",
            "Keluar {amount} buat {category}",
            "Spend {amount} di {category}",
            "Boros {amount} untuk {category}",
            "{category} {amount}",
            "Ongkos {category} {amount}",
            "Biaya {category} {amount}",
            # Modern payment
            "Gofood {category} {amount}",
            "Grabfood {category} {amount}",
            "COD {category} {amount}",
            "Bayar pakai GoPay {amount} untuk {category}",
            "Transfer {amount} buat {category}",
        ]
        
        # SAVINGS GOAL TEMPLATES - More conservative  
        self.savings_goal_templates = [
            # Clear savings intent
            "Mau nabung {amount} buat {item}",
            "Target beli {item} {amount}",
            "Pengen beli {item} {amount}",
            "Ingin beli {item} seharga {amount}",
            "Planning beli {item} budget {amount}",
            "Saving untuk {item} {amount}",
            "Target tabungan {item} {amount}",
            "Mau saving buat {item} {amount}",
            "Goal beli {item} {amount}",
            "Rencana beli {item} {amount}",
            # With deadlines
            "Target beli {item} {amount} {deadline}",
            "Mau beli {item} {amount} pada {deadline}",
            "Planning {item} {amount} deadline {deadline}",
        ]
    
    def setup_enhanced_vocabulary(self):
        """Enhanced vocabulary with better balance"""
        
        # Amount formats - More conservative
        self.amounts = [
            # Common student amounts
            "50rb", "100rb", "150rb", "200rb", "250rb", "300rb", "500rb",
            "1 juta", "1.5 juta", "2 juta", "2.5 juta", "3 juta", "5 juta",
            "50 ribu", "100 ribu", "200 ribu", "500 ribu",
            "lima puluh ribu", "seratus ribu", "dua ratus ribu",
            "50k", "100k", "200k", "500k", "1M", "2M",
            # Decimal variations
            "1,5 juta", "2,5 juta", "3,5 juta",
        ]
        
        # Income sources - Balanced
        self.income_sources = [
            # Family
            "ortu", "orang tua", "papa", "mama", "ayah", "ibu",
            "bokap", "nyokap", "bapak", "keluarga",
            # Work
            "freelance", "part time", "kerja sampingan", "ngajar", 
            "les privat", "kasir", "admin", "tutor",
            # Academic
            "beasiswa", "scholarship", "bidikmisi", "bantuan pendidikan",
            # Business
            "jualan", "bisnis", "usaha", "dropship", "olshop",
            # Bonus
            "bonus", "hadiah", "cashback", "refund", "lomba",
        ]
        
        # Expense categories - Balanced across NEEDS/WANTS/SAVINGS
        self.expense_categories = {
            "needs": [
                "kos", "sewa kamar", "listrik", "air", "wifi",
                "makan", "groceries", "beras", "lauk pauk",
                "transport", "bensin", "angkot", "bus", "kereta",
                "buku kuliah", "alat tulis", "fotocopy", "print",
                "pulsa", "paket data", "internet",
                "obat", "vitamin", "sabun", "shampo", "pasta gigi",
            ],
            "wants": [
                "jajan", "snack", "kopi", "bubble tea", "es krim",
                "nonton", "bioskop", "netflix", "spotify", "game",
                "baju", "sepatu", "tas", "aksesoris", "kosmetik",
                "nongkrong", "cafe", "hangout", "karaoke", "mall",
                "gofood", "grabfood", "delivery", "takeaway",
                "organisasi", "event", "gathering", "party",
            ],
            "savings": [
                "tabungan", "deposito", "investasi", "reksadana",
                "dana darurat", "masa depan", "pension fund",
            ]
        }
        
        # Savings items - Common student aspirations
        self.savings_items = [
            # Technology
            "laptop", "notebook", "macbook", "gaming laptop",
            "smartphone", "iPhone", "samsung", "xiaomi", "oppo",
            "headset", "earphone", "airpods", "speaker",
            "tablet", "iPad", "smartwatch", "kamera",
            # Transportation
            "motor", "sepeda motor", "vario", "beat", "scoopy",
            "mobil", "car", "sepeda", "sepeda gunung",
            # Fashion & lifestyle
            "sepatu branded", "tas branded", "jam tangan",
            # Appliances
            "kulkas", "AC", "TV", "mesin cuci",
        ]
        
        # Deadlines for savings goals
        self.deadlines = [
            "tanggal 31 desember 2025",
            "akhir tahun 2025", 
            "bulan januari 2026",
            "sebelum wisuda",
            "tahun depan",
            "semester depan",
            "dalam 6 bulan",
            "dalam 1 tahun",
        ]
    
    def setup_query_patterns(self):
        """Setup query detection patterns - NEW FEATURE"""
        
        self.query_templates = {
            "total_savings_query": [
                "Total tabungan saya berapa",
                "Berapa total tabungan saya",
                "Jumlah tabungan saya",
                "Tabungan saya ada berapa",
                "Cek total tabungan",
                "Saldo tabungan saya",
                "Total uang saya berapa",
                "Berapa duit saya sekarang",
                "Uang saya tersisa berapa",
                "Current savings saya",
            ],
            "budget_performance_query": [
                "Budget performance bulan ini",
                "Performance budget saya",
                "Bagaimana budget saya",
                "Budget 50/30/20 gimana",
                "Kondisi budget saya",
                "Status budget bulanan",
                "Performa anggaran saya",
                "Budget tracking bulan ini",
                "Seberapa baik budget saya",
                "Analisis budget saya",
            ],
            "expense_analysis_query": [
                "Pengeluaran terbesar saya",
                "Analisis pengeluaran saya",
                "Breakdown pengeluaran saya",
                "Spending analysis",
                "Kategori pengeluaran terbanyak",
                "Dimana uang saya habis",
                "Expense terbesar apa",
                "Rincian pengeluaran saya",
                "Pattern spending saya",
                "Evaluasi pengeluaran",
            ],
            "savings_progress_query": [
                "Progress tabungan saya",
                "Kemajuan target tabungan",
                "Progress saving goals",
                "Target tabungan gimana",
                "Pencapaian target saya",
                "Daftar target tabungan",
                "List target saya",
                "Status saving goals",
                "Progress menabung saya",
                "Target achievement saya",
            ],
            "financial_health_query": [
                "Kesehatan keuangan saya",
                "Financial health saya",
                "Kondisi finansial saya",
                "Sehat ga keuangan saya",
                "Status keuangan saya",
                "Health check finansial",
                "Evaluasi keuangan saya",
                "Assessment finansial",
                "Overall financial status",
                "Keuangan saya bagus ga",
            ],
            "purchase_advice_query": [
                "Saya ingin membeli {item} seharga {amount}",
                "Mau beli {item} {amount} aman ga",
                "Planning beli {item} {amount}",
                "Beli {item} {amount} recommended ga",
                "Budget untuk {item} {amount}",
                "Advice beli {item} {amount}",
                "Worth it ga beli {item} {amount}",
                "Sebaiknya beli {item} {amount}",
                "Analisis pembelian {item} {amount}",
                "Konsultasi beli {item} {amount}",
            ]
        }
    
    def setup_non_financial_patterns(self):
        """Setup enhanced non-financial patterns to reduce bias"""
        
        self.non_financial_templates = [
            # Greetings & social
            "Halo", "Hai", "Hi", "Hello", "Selamat pagi", "Selamat siang",
            "Apa kabar", "Gimana kabarnya", "How are you", "What's up",
            "Good morning", "Good afternoon", "Good evening",
            
            # Questions about app/system
            "Cara pakai aplikasi ini gimana",
            "Fitur apa aja yang ada",
            "Bagaimana cara mendaftar",
            "Lupa password",
            "Reset password",
            "Logout dari aplikasi",
            "Update profile",
            "Ganti email",
            "Hapus akun",
            "Privacy policy",
            "Terms of service",
            
            # General questions
            "Apa itu budgeting",
            "Metode 50/30/20 itu apa",
            "Tips hemat untuk mahasiswa",
            "Cara menabung yang baik",
            "Investasi untuk pemula",
            "Perbedaan tabungan dan investasi",
            "Apa itu reksadana",
            "Cara memulai investasi",
            "Financial planning untuk mahasiswa",
            "Money management tips",
            
            # Casual conversation
            "Terima kasih", "Thanks", "Thank you", "Makasih",
            "Oke", "OK", "Alright", "Baik", "Siap",
            "Maaf", "Sorry", "Excuse me", "Permisi",
            "Bye", "Goodbye", "Sampai jumpa", "See you",
            
            # Random/irrelevant
            "Cuaca hari ini", "Macet ga jalanan", "Rekomendasi tempat makan",
            "Film bagus apa", "Musik terbaru", "Berita hari ini",
            "Jadwal kuliah", "Tugas deadline", "Ujian kapan",
            "Liburan kemana", "Weekend plan", "Hobi apa",
            
            # Asking for help (non-financial)
            "Help me", "Tolong dong", "Bantuan", "Gimana caranya",
            "Explain please", "Jelaskan dong", "I don't understand",
            "Ga ngerti", "Bingung", "Confused",
            
            # Expressions without financial context
            "Capek banget hari ini", "Senang banget", "Sedih nih",
            "Bosan", "Stress kuliah", "Happy weekend",
            "Lagi gabut", "Weekend vibes", "Mood boost",
            "Energy drain", "Semangat pagi", "Good vibes",
            
            # Academic/study related (non-financial)
            "Jadwal ujian kapan", "Tugas susah banget", "Dosen killer",
            "Semester ini berat", "Skripsi progress", "Thesis defense",
            "Graduation plan", "Study abroad", "Scholarship non-financial",
            "Academic achievement", "GPA calculation", "Credit hours",
            
            # Technology/general
            "Internet lambat", "Laptop error", "HP hang",
            "Software recommendation", "App terbaik", "Game seru",
            "Social media trend", "YouTube channel", "Podcast recommendation",
            
            # Health & lifestyle (non-financial)
            "Tips sehat", "Olahraga rutin", "Diet plan",
            "Workout routine", "Mental health", "Self care",
            "Sleep schedule", "Healthy lifestyle", "Nutrition tips",
        ]
    
    def generate_all_datasets(self) -> Dict[str, Any]:
        """Generate all balanced datasets"""
        logger.info("🔄 Starting advanced dataset generation...")
        
        # Create output directory
        os.makedirs(self.config.data_dir, exist_ok=True)
        
        # Generate datasets
        intent_data = self.generate_intent_dataset()
        category_data = self.generate_category_dataset()
        query_data = self.generate_query_dataset()  # NEW
        
        # Save datasets
        self._save_dataset(intent_data, "intent_dataset.json")
        self._save_dataset(category_data, "category_dataset.json") 
        self._save_dataset(query_data, "query_dataset.json")  # NEW
        
        # Generate metadata
        metadata = self._generate_metadata(intent_data, category_data, query_data)
        self._save_metadata(metadata)
        
        logger.info("✅ Advanced dataset generation completed!")
        
        return {
            "intent_samples": len(intent_data),
            "category_samples": len(category_data),
            "query_samples": len(query_data),
            "non_financial_samples": sum(1 for item in intent_data if item["label"] == "non_financial"),
            "total_samples": len(intent_data) + len(category_data) + len(query_data)
        }
    
    def generate_intent_dataset(self) -> List[Dict[str, Any]]:
        """Generate balanced intent dataset with reduced financial bias"""
        logger.info("📊 Generating balanced intent dataset...")
        
        dataset = []
        
        # Financial intent samples (REDUCED COUNT to prevent bias)
        financial_samples_per_type = self.config.intent_samples_per_class
        
        # Income samples
        for _ in range(financial_samples_per_type):
            template = random.choice(self.income_templates)
            amount = random.choice(self.amounts)
            source = random.choice(self.income_sources)
            
            text = template.format(amount=amount, source=source)
            dataset.append({"text": text, "label": "income"})
        
        # Expense samples
        for _ in range(financial_samples_per_type):
            template = random.choice(self.expense_templates)
            amount = random.choice(self.amounts)
            
            # Select category from all expense types
            all_categories = (
                self.expense_categories["needs"] + 
                self.expense_categories["wants"] + 
                self.expense_categories["savings"]
            )
            category = random.choice(all_categories)
            
            text = template.format(amount=amount, category=category)
            dataset.append({"text": text, "label": "expense"})
        
        # Savings goal samples
        for _ in range(financial_samples_per_type):
            template = random.choice(self.savings_goal_templates)
            amount = random.choice(self.amounts)
            item = random.choice(self.savings_items)
            
            # Some with deadlines
            if "{deadline}" in template:
                deadline = random.choice(self.deadlines)
                text = template.format(amount=amount, item=item, deadline=deadline)
            else:
                text = template.format(amount=amount, item=item)
                
            dataset.append({"text": text, "label": "savings_goal"})
        
        # NON-FINANCIAL samples (INCREASED to balance dataset)
        non_financial_count = self.config.non_financial_samples
        
        for _ in range(non_financial_count):
            text = random.choice(self.non_financial_templates)
            
            # Add some variations to non-financial templates
            if random.random() < 0.3:  # 30% chance of variation
                variations = [
                    f"{text} ya", f"{text} dong", f"{text} nih",
                    f"Mau tanya {text.lower()}", f"Gimana {text.lower()}",
                    f"{text} banget", f"{text} sih"
                ]
                text = random.choice(variations)
            
            dataset.append({"text": text, "label": "non_financial"})
        
        # Shuffle and clean
        random.shuffle(dataset)
        dataset = self._clean_dataset(dataset)
        
        logger.info(f"✅ Intent dataset: {len(dataset)} samples")
        return dataset
    
    def generate_category_dataset(self) -> List[Dict[str, Any]]:
        """Generate balanced category dataset"""
        logger.info("📊 Generating category dataset...")
        
        dataset = []
        samples_per_category = self.config.category_samples_per_class
        
        # Income categories
        income_categories = self.config.get_class_labels()["category"][:6]  # First 6 are income
        for category in income_categories:
            for _ in range(samples_per_category):
                template = random.choice(self.income_templates)
                amount = random.choice(self.amounts)
                source = self._get_source_for_category(category)
                
                text = template.format(amount=amount, source=source)
                dataset.append({"text": text, "label": category})
        
        # Expense categories
        expense_categories = self.config.get_class_labels()["category"][6:]  # Rest are expense
        for category in expense_categories:
            for _ in range(samples_per_category):
                template = random.choice(self.expense_templates)
                amount = random.choice(self.amounts)
                expense_item = self._get_expense_for_category(category)
                
                text = template.format(amount=amount, category=expense_item)
                dataset.append({"text": text, "label": category})
        
        # Shuffle and clean
        random.shuffle(dataset)
        dataset = self._clean_dataset(dataset)
        
        logger.info(f"✅ Category dataset: {len(dataset)} samples")
        return dataset
    
    def generate_query_dataset(self) -> List[Dict[str, Any]]:
        """Generate query detection dataset - NEW FEATURE"""
        logger.info("📊 Generating query dataset...")
        
        dataset = []
        samples_per_query = self.config.query_samples_per_class
        
        # Query samples
        for query_type, templates in self.query_templates.items():
            for _ in range(samples_per_query):
                template = random.choice(templates)
                
                # Handle purchase advice queries with variables
                if "{item}" in template and "{amount}" in template:
                    item = random.choice(self.savings_items)
                    amount = random.choice(self.amounts)
                    text = template.format(item=item, amount=amount)
                else:
                    text = template
                
                # Add variations
                if random.random() < 0.3:
                    variations = [
                        f"{text} dong", f"{text} ya", f"Mau tanya {text.lower()}",
                        f"Bisa {text.lower()}", f"Gimana {text.lower()}"
                    ]
                    text = random.choice(variations)
                
                dataset.append({"text": text, "label": query_type})
        
        # Non-query samples (regular conversation)
        non_query_samples = samples_per_query
        for _ in range(non_query_samples):
            text = random.choice(self.non_financial_templates)
            dataset.append({"text": text, "label": "non_query"})
        
        # Shuffle and clean
        random.shuffle(dataset)
        dataset = self._clean_dataset(dataset)
        
        logger.info(f"✅ Query dataset: {len(dataset)} samples")
        return dataset
    
    def _get_source_for_category(self, category: str) -> str:
        """Get appropriate source for income category"""
        category_sources = {
            "Uang Saku/Kiriman Ortu": ["ortu", "papa", "mama", "bokap", "nyokap", "keluarga"],
            "Part-time Job": ["part time", "kerja sampingan", "kasir", "admin", "tutor"],
            "Freelance/Project": ["freelance", "project", "ngajar", "les privat", "coding"],
            "Beasiswa": ["beasiswa", "scholarship", "bidikmisi", "bantuan pendidikan"],
            "Bisnis/Jualan": ["jualan", "bisnis", "usaha", "dropship", "olshop"],
            "Hadiah/Bonus": ["bonus", "hadiah", "cashback", "refund", "lomba"]
        }
        sources = category_sources.get(category, self.income_sources)
        return random.choice(sources)
    
    def _get_expense_for_category(self, category: str) -> str:
        """Get appropriate expense item for category"""
        category_expenses = {
            "Kos/Tempat Tinggal": self.expense_categories["needs"][:5],
            "Makanan Pokok": self.expense_categories["needs"][5:9],
            "Transportasi Wajib": self.expense_categories["needs"][9:12],
            "Pendidikan": self.expense_categories["needs"][12:16],
            "Internet & Komunikasi": self.expense_categories["needs"][16:19],
            "Kesehatan & Kebersihan": self.expense_categories["needs"][19:],
            "Jajan & Snack": self.expense_categories["wants"][:5],
            "Hiburan & Sosial": self.expense_categories["wants"][5:10],
            "Fashion & Beauty": self.expense_categories["wants"][10:14],
            "Shopping Online": self.expense_categories["wants"][14:17],
            "Organisasi & Event": self.expense_categories["wants"][17:21],
            "Hobi & Olahraga": self.expense_categories["wants"][21:],
            "Tabungan Umum": self.expense_categories["savings"][:2],
            "Investasi": self.expense_categories["savings"][2:5],
            "Dana Darurat": self.expense_categories["savings"][5:]
        }
        expenses = category_expenses.get(category, self.expense_categories["wants"])
        return random.choice(expenses)
    
    def _clean_dataset(self, dataset: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Clean dataset from duplicates and invalid entries"""
        seen_texts = set()
        clean_dataset = []
        
        for item in dataset:
            text = item["text"].strip()
            if text and text not in seen_texts and len(text) > 2:
                seen_texts.add(text)
                clean_dataset.append(item)
        
        return clean_dataset
    
    def _save_dataset(self, dataset: List[Dict[str, Any]], filename: str):
        """Save dataset to file"""
        filepath = os.path.join(self.config.data_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(dataset, f, ensure_ascii=False, indent=2)
        logger.info(f"💾 Saved {filename}: {len(dataset)} samples")
    
    def _generate_metadata(self, intent_data, category_data, query_data) -> Dict[str, Any]:
        """Generate comprehensive metadata"""
        return {
            "generation_info": {
                "generated_at": datetime.now().isoformat(),
                "generator_version": "AdvancedBalanced_v1.0",
                "config": {
                    "intent_samples_per_class": self.config.intent_samples_per_class,
                    "category_samples_per_class": self.config.category_samples_per_class,
                    "query_samples_per_class": self.config.query_samples_per_class,
                    "non_financial_samples": self.config.non_financial_samples
                }
            },
            "dataset_stats": {
                "intent_dataset": {
                    "total_samples": len(intent_data),
                    "class_distribution": self._get_class_distribution(intent_data)
                },
                "category_dataset": {
                    "total_samples": len(category_data),
                    "class_distribution": self._get_class_distribution(category_data)
                },
                "query_dataset": {
                    "total_samples": len(query_data),
                    "class_distribution": self._get_class_distribution(query_data)
                }
            },
            "balance_features": [
                "Reduced financial detection bias",
                "Enhanced non-financial examples",
                "Query detection training",
                "Balanced category distribution",
                "Advanced template variations",
                "Conservative financial vocabulary"
            ],
            "improvements": [
                "Reduced intent samples to prevent overfitting",
                "Increased non-financial samples for better balance",
                "Added query detection dataset",
                "Better category-specific vocabulary",
                "Enhanced conversation patterns",
                "Improved negative examples"
            ]
        }
    
    def _get_class_distribution(self, dataset: List[Dict[str, Any]]) -> Dict[str, int]:
        """Get class distribution for dataset"""
        distribution = defaultdict(int)
        for item in dataset:
            distribution[item["label"]] += 1
        return dict(distribution)
    
    def _save_metadata(self, metadata: Dict[str, Any]):
        """Save metadata to file"""
        filepath = os.path.join(self.config.data_dir, "dataset_metadata.json")
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
        logger.info("💾 Saved dataset metadata")