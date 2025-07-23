# scripts/train/train_indoroberta_models_enhanced.py - FIXED VERSION
import os
import json
import random
import logging
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Tuple
import re

# Setup enhanced logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('natural_training.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def check_dependencies():
    """Check if all required packages are installed"""
    required_packages = {
        'torch': 'torch',
        'transformers': 'transformers', 
        'datasets': 'datasets',
        'sklearn': 'scikit-learn',
        'pandas': 'pandas',
        'numpy': 'numpy'
    }
    
    missing = []
    for package, pip_name in required_packages.items():
        try:
            __import__(package)
            logger.info(f"✅ {package} available")
        except ImportError:
            missing.append(pip_name)
            logger.error(f"❌ {package} missing")
    
    if missing:
        logger.error(f"Install: pip install {' '.join(missing)}")
        return False
    return True

if check_dependencies():
    import torch
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import classification_report, accuracy_score, f1_score
    from transformers import (
        AutoTokenizer, AutoModelForSequenceClassification,
        TrainingArguments, Trainer, EarlyStoppingCallback,
        DataCollatorWithPadding
    )
    from datasets import Dataset
    logger.info(f"🚀 PyTorch {torch.__version__}, Device: {'CUDA' if torch.cuda.is_available() else 'CPU'}")
else:
    exit(1)

class NaturalIndonesianDatasetGenerator:
    """Enhanced dataset generator untuk natural Indonesian student language"""
    
    def __init__(self):
        self.setup_natural_templates()
        self.setup_enhanced_vocabulary()
        self.setup_natural_patterns()
    
    def setup_natural_templates(self):
        """Setup natural Indonesian templates yang sangat variatif"""
        
        # INCOME TEMPLATES - Super Natural
        self.income_templates = [
            # Slang variations
            "Dapet {amount} dari {source}", "Dapat {amount} dari {source}",
            "Terima {amount} dari {source}", "Nerima {amount} dari {source}",
            "Masuk {amount} dari {source}", "Cair {amount} dari {source}",
            "Transfer {amount} dari {source}", "Kiriman {amount} dari {source}",
            
            # Emotional context
            "Alhamdulillah dapet {amount} dari {source}",
            "Syukur dapat {amount} dari {source}",
            "Senang banget dapat {amount} dari {source}",
            "Finally! Dapet {amount} dari {source}",
            "Yeay! Masuk {amount} dari {source}",
            "Untung deh dapat {amount} dari {source}",
            
            # Regional variations
            "Bokap kasih {amount}", "Nyokap transfer {amount}",
            "Papa kirim {amount}", "Mama kasih {amount}",
            "Ortu transfer {amount}", "Bapak kirim {amount}",
            "Ibu kasih jajan {amount}", "Ayah transfer {amount}",
            "Papah kasih {amount}", "Mamah kirim {amount}",
            "Bude transfer {amount}", "Pakde kasih {amount}",
            "Om kirim {amount}", "Tante kasih {amount}",
            "Eyang transfer {amount}", "Kakak kasih {amount}",
            
            # Work context
            "Freelance project selesai dapat {amount}",
            "Part time kemarin bayaran {amount}",
            "Ngajar dapet honor {amount}",
            "Les privat dapat {amount}",
            "Kerja sampingan bayaran {amount}",
            "Project design {amount} masuk",
            "Coding project done, fee {amount}",
            "Jualan online laku {amount}",
            "Bisnis kecil profit {amount}",
            "Event organizer fee {amount}",
            
            # Academic context
            "Beasiswa {amount} cair",
            "Bantuan pendidikan {amount} masuk",
            "Scholarship {amount} turun",
            "Bidikmisi {amount} cair",
            "KIP kuliah {amount} masuk",
            
            # Modern context
            "Cashback {amount} dari belanja",
            "Refund {amount} dari tokped",
            "Bonus {amount} dari aplikasi",
            "Hadiah lomba {amount}",
            "Menang kompetisi {amount}",
        ]
        
        # EXPENSE TEMPLATES - Natural Indonesian
        self.expense_templates = [
            # Basic slang
            "Abis {amount} buat {category}", "Habis {amount} untuk {category}",
            "Keluar {amount} buat {category}", "Bayar {category} {amount}",
            "Beli {category} {amount}", "Spend {amount} di {category}",
            "Shopping {category} {amount}", "Boros {amount} gara-gara {category}",
            
            # Emotional variations
            "Capek deh abis {amount} buat {category}",
            "Sedih banget bayar {category} {amount}",
            "Sakit hati {amount} hilang gara-gara {category}",
            "Gregetan {amount} abis di {category}",
            "Terpaksa bayar {category} {amount}",
            "Huhu abis {amount} buat {category}",
            
            # Modern payment context
            "Gofood {category} {amount}", "Grabfood {category} {amount}",
            "Shopee {category} {amount}", "Tokped {category} {amount}",
            "COD {category} {amount}", "Bayar via gopay {amount} {category}",
            "Transfer ovo {amount} buat {category}",
            "Dana pay {amount} untuk {category}",
            "Spaylater {category} {amount}",
            "QRIS bayar {amount} {category}",
            
            # Student context
            "Bayar kos {amount}", "UKT semester ini {amount}",
            "Buku kuliah {amount}", "Print skripsi {amount}",
            "Fotocopy materi {amount}", "Biaya praktikum {amount}",
            "Transport kuliah {amount}", "Parkir kampus {amount}",
            "Makan kantin {amount}", "Jajan di kampus {amount}",
            
            # Time context
            "Tadi abis {amount} buat {category}",
            "Kemarin bayar {category} {amount}",
            "Barusan beli {category} {amount}",
            "Pagi ini spend {amount} di {category}",
            "Siang tadi keluar {amount} untuk {category}",
        ]
        
        # SAVINGS GOAL TEMPLATES - Aspirational Natural
        self.savings_templates = [
            # Basic aspirational
            "Pengen nabung {amount} buat beli {item}",
            "Mau nabung {amount} untuk {item}",
            "Target {amount} buat {item}",
            "Saving {amount} demi {item}",
            "Ngumpulin {amount} buat {item}",
            
            # Emotional aspirational
            "Pengen banget {item} {amount}",
            "Impian punya {item} {amount}",
            "Cita-cita beli {item} {amount}",
            "Kapan ya bisa beli {item} {amount}",
            "Someday mau punya {item} {amount}",
            "Dream item: {item} {amount}",
            
            # Timeline context
            "Tahun depan mau beli {item} {amount}",
            "Semester depan target {item} {amount}",
            "Setelah lulus mau {item} {amount}",
            "Wisuda nanti hadiah diri {item} {amount}",
            "Birthday wish: {item} {amount}",
            
            # Motivational
            "Harus kuat nabung {amount} demi {item}",
            "Perjuangan {amount} untuk {item}",
            "Rela skip jajan demi {item} {amount}",
            "Sabar menabung {amount} untuk {item}",
            "Bismillah target {item} {amount}",
            "Insyaallah bisa beli {item} {amount}",
        ]
    
    def setup_enhanced_vocabulary(self):
        """Setup vocabulary yang comprehensive dan natural"""
        
        # AMOUNTS - Super variatif dan natural
        self.amounts = [
            # Slang format
            "5rb", "10rb", "15rb", "20rb", "25rb", "30rb", "35rb", "40rb", "45rb", "50rb",
            "60rb", "70rb", "75rb", "80rb", "85rb", "90rb", "95rb", "100rb",
            "150rb", "200rb", "250rb", "300rb", "350rb", "400rb", "450rb", "500rb",
            "600rb", "700rb", "750rb", "800rb", "850rb", "900rb", "950rb",
            
            # Rebu variations
            "5 rebu", "10 rebu", "15 rebu", "20 rebu", "25 rebu", "30 rebu",
            "50 rebu", "75 rebu", "100 rebu", "150 rebu", "200 rebu",
            
            # Ribu format
            "5 ribu", "10 ribu", "15 ribu", "20 ribu", "25 ribu", "30 ribu",
            "50 ribu", "75 ribu", "100 ribu", "150 ribu", "200 ribu", "500 ribu",
            
            # Written format
            "lima ribu", "sepuluh ribu", "lima belas ribu", "dua puluh ribu",
            "lima puluh ribu", "seratus ribu", "dua ratus ribu", "lima ratus ribu",
            
            # Juta variations
            "1 juta", "1.2 juta", "1.5 juta", "satu setengah juta",
            "2 juta", "2.5 juta", "dua setengah juta", "3 juta", "4 juta", "5 juta",
            "6 juta", "7 juta", "8 juta", "9 juta", "10 juta", "15 juta", "20 juta",
            
            # Shorthand
            "50k", "100k", "200k", "500k", "1M", "2M", "5M", "10M",
            
            # Decimal variations
            "1,5 juta", "2,5 juta", "3,5 juta", "4,5 juta",
            "10,5 juta", "15,5 juta", "20,5 juta",
            
            # Formal format
            "1.000.000", "2.000.000", "5.000.000", "10.000.000",
            "500.000", "750.000", "1.500.000", "2.500.000",
        ]
        
        # INCOME SOURCES - Natural Indonesian
        self.income_sources = [
            # Family - regional variations
            "ortu", "orang tua", "bokap", "nyokap", "papa", "mama",
            "ayah", "ibu", "bapak", "mami", "papi", "papah", "mamah",
            "umi", "abi", "parents", "keluarga",
            
            # Extended family
            "kakak", "adek", "saudara", "om", "tante", "bude", "pakde",
            "eyang", "nenek", "kakek", "sepupu", "keponakan",
            
            # Work - student context
            "freelance", "project", "part time", "kerja sampingan", "side job",
            "ngajar", "les privat", "tutor", "mentor", "guru les",
            "jaga warung", "kasir", "sales", "admin", "SPG", "event organizer",
            
            # Digital work
            "content creator", "youtuber", "streamer", "influencer",
            "design graphic", "coding", "programming", "web development",
            "social media management", "copywriting", "translation",
            
            # Academic
            "beasiswa", "scholarship", "bidikmisi", "KIP kuliah", "bantuan pendidikan",
            "beasiswa prestasi", "beasiswa tidak mampu", "research grant",
            "teaching assistant", "lab assistant",
            
            # Business
            "jualan", "bisnis", "usaha", "dagang", "jual online",
            "dropship", "reseller", "affiliate marketing", "MLM",
            "olshop", "marketplace", "toko online",
            
            # Bonus/rewards
            "gaji", "kantor", "THR", "bonus", "tunjangan", "honor",
            "cashback", "refund", "hadiah", "doorprize", "lomba",
            "kompetisi", "hackathon", "olimpiade", "quiz online",
        ]
        
        # EXPENSE CATEGORIES - Comprehensive student life
        self.expense_categories = {
            # NEEDS - Essential student expenses
            "needs": [
                # Housing
                "kos", "kost", "kostan", "sewa kamar", "kontrakan", "boarding house",
                "uang kos", "bayar kos", "sewa bulanan", "deposit kos",
                "listrik", "air", "wifi kos", "token listrik", "rekening listrik",
                
                # Food - basic needs
                "makan", "makanan pokok", "beras", "minyak goreng", "garam", "gula",
                "telur", "daging", "ikan", "ayam", "sayur", "buah", "protein",
                "groceries", "belanja bulanan", "pasar", "supermarket",
                "masak", "dapur", "gas", "kompor",
                
                # Transportation - essential
                "transport", "transportasi", "angkot", "bus", "kereta",
                "commuter line", "MRT", "LRT", "transjakarta", "damri",
                "bensin", "pertamax", "solar", "isi bensin", "BBM",
                "parkir kampus", "parkir", "tol", "ke kampus", "PP kampus",
                
                # Education - mandatory
                "UKT", "SPP", "biaya kuliah", "uang kuliah", "semester",
                "buku kuliah", "textbook", "modul", "diktat", "referensi",
                "fotocopy", "print", "jilid", "binding", "kertas",
                "alat tulis", "pulpen", "pensil", "penggaris", "spidol",
                "praktikum", "lab", "biaya lab", "fieldwork", "KKN",
                
                # Health & hygiene - essential
                "obat", "dokter", "rumah sakit", "puskesmas", "klinik",
                "vitamin", "paracetamol", "betadine", "plaster",
                "sabun", "shampo", "pasta gigi", "sikat gigi", "deodorant",
                "detergen", "sabun cuci", "pembalut", "tissue",
                
                # Communication - essential
                "pulsa", "paket data", "kuota", "internet", "wifi",
                "telkomsel", "xl", "indosat", "tri", "smartfren",
                "kartu perdana", "voucher data",
            ],
            
            # WANTS - Lifestyle and entertainment
            "wants": [
                # Food & drinks - non-essential
                "jajan", "cemilan", "snack", "keripik", "coklat", "permen",
                "es krim", "gelato", "bubble tea", "boba", "thai tea",
                "milk tea", "kopi", "coffee", "cappuccino", "latte",
                "starbucks", "chatime", "koi", "xing fu tang",
                "martabak", "terang bulan", "pancake", "waffle", "crepe",
                "pizza", "burger", "KFC", "mcd", "subway", "dominos",
                "ayam geprek", "bakso", "mie ayam", "nasi gudeg",
                "soto", "gado-gado", "rujak", "kerak telor",
                
                # Digital food delivery
                "gofood", "grabfood", "shopeefood", "foodpanda",
                "delivery", "pesan makan", "order online",
                
                # Entertainment
                "nongkrong", "hangout", "cafe", "coffee shop", "resto",
                "cinema", "bioskop", "XXI", "CGV", "cinepolis",
                "nonton film", "tiket film", "popcorn", "minuman bioskop",
                "karaoke", "ktv", "timezone", "main game", "arcade",
                
                # Streaming & digital entertainment
                "netflix", "disney+", "viu", "iqiyi", "spotify", "joox",
                "youtube premium", "canva pro", "zoom pro",
                
                # Gaming
                "game", "gaming", "steam", "mobile legends", "pubg",
                "free fire", "valorant", "genshin impact", "honkai",
                "top up game", "diamond", "UC", "skin game",
                "battle pass", "gacha", "in-app purchase",
                
                # Fashion & beauty
                "baju", "kaos", "kemeja", "dress", "celana", "jeans",
                "rok", "jaket", "hoodie", "sweater", "cardigan",
                "sepatu", "sneakers", "sandal", "high heels", "boots",
                "tas", "backpack", "totebag", "slingbag", "clutch",
                "dompet", "wallet", "jam tangan", "smartwatch",
                "aksesoris", "kalung", "gelang", "cincin", "anting",
                
                # Beauty & skincare
                "makeup", "skincare", "foundation", "lipstick", "mascara",
                "eyeshadow", "blush on", "concealer", "primer",
                "cleanser", "toner", "moisturizer", "serum", "sunscreen",
                "face mask", "sheet mask", "scrub", "peeling",
                
                # Shopping platforms
                "shopee", "tokopedia", "lazada", "blibli", "zalora",
                "sociolla", "sephora", "uniqlo", "h&m", "zara",
                
                # Social & events
                "organisasi", "ukm", "himpunan", "bem", "ormawa",
                "event kampus", "gathering", "reunion", "party",
                "ultah", "birthday", "anniversary", "graduation",
                
                # Hobbies
                "hobi", "musik", "alat musik", "gitar", "keyboard",
                "fotografi", "kamera", "lensa", "editing", "software",
                "olahraga", "gym", "fitness", "yoga", "badminton",
            ],
            
            # SAVINGS - Investment and future
            "savings": [
                "nabung", "tabungan", "saving", "menabung", "deposito",
                "reksadana", "mutual fund", "saham", "stock", "obligasi",
                "crypto", "bitcoin", "ethereum", "trading", "investasi",
                "dana darurat", "emergency fund", "masa depan", "pension",
                "asuransi", "insurance", "proteksi", "jaminan",
            ]
        }
        
        # SAVINGS ITEMS - Modern student aspirations
        self.savings_items = [
            # Technology
            "laptop", "notebook", "macbook", "macbook air", "macbook pro",
            "asus", "lenovo", "acer", "hp pavilion", "dell", "gaming laptop",
            "PC", "computer", "gaming PC", "setup gaming", "monitor",
            
            # Smartphones
            "HP", "handphone", "smartphone", "iPhone", "iPhone 14", "iPhone 15",
            "samsung", "samsung galaxy", "xiaomi", "redmi", "poco",
            "oppo", "vivo", "realme", "oneplus", "google pixel",
            
            # Gadgets
            "headset", "headphone", "earphone", "earbuds", "airpods",
            "speaker", "JBL", "sony", "beats", "marshall",
            "smartwatch", "apple watch", "galaxy watch", "amazfit",
            "tablet", "iPad", "samsung tab", "surface pro",
            "kamera", "canon", "nikon", "sony alpha", "fujifilm",
            
            # Transportation
            "motor", "sepeda motor", "vario", "beat", "scoopy", "nmax",
            "aerox", "mio", "jupiter", "ninja", "cbr", "r15",
            "mobil", "car", "avanza", "xenia", "brio", "agya",
            "sepeda", "sepeda gunung", "roadbike", "sepeda lipat",
            
            # Fashion items
            "sepatu", "sneakers", "nike", "adidas", "converse", "vans",
            "tas branded", "coach", "michael kors", "longchamp",
            "jam tangan", "casio", "seiko", "fossil", "daniel wellington",
            
            # Home appliances
            "kulkas", "AC", "mesin cuci", "TV", "smart TV",
            "rice cooker", "blender", "microwave", "air fryer",
        ]
    
    def setup_natural_patterns(self):
        """Setup pola natural language Indonesia"""
        self.natural_variations = [
            # Time markers
            "{base}", "tadi {base}", "kemarin {base}", "barusan {base}",
            "pagi ini {base}", "siang tadi {base}", "malam kemarin {base}",
            
            # Emotional markers
            "alhamdulillah {base}", "syukur {base}", "senang banget {base}",
            "sedih banget {base}", "capek deh {base}", "gregetan {base}",
            "huhu {base}", "yeay {base}", "finally {base}",
            
            # Casual markers
            "{base} nih", "{base} dong", "{base} sih", "{base} ya",
            "{base} guys", "{base} bestie", "{base} bro",
            
            # Certainty markers
            "pasti {base}", "definitely {base}", "yakin {base}",
            "kayaknya {base}", "sepertinya {base}", "mungkin {base}",
        ]
        
        self.spelling_variations = {
            "dapat": ["dapet", "dpt"],
            "habis": ["abis", "abs"],
            "ingin": ["pengen", "pen"],
            "bapak": ["bokap", "bpk"],
            "ibu": ["nyokap", "emak"],
            "ribu": ["rb", "rebu", "k"],
            "juta": ["jt", "m"],
            "dengan": ["dgn", "sama"],
            "untuk": ["buat", "utk"],
            "dari": ["dr"],
        }
    
    def generate_natural_variations(self, base_text: str) -> List[str]:
        """Generate natural variations dari base text"""
        variations = []
        
        # Apply natural patterns
        for pattern in self.natural_variations[:5]:  # Limit to 5 patterns
            variation = pattern.format(base=base_text)
            variations.append(variation)
        
        # Apply spelling variations
        for formal, informal_list in self.spelling_variations.items():
            for informal in informal_list[:2]:  # Limit to 2 variations per word
                if formal in base_text:
                    varied_text = base_text.replace(formal, informal)
                    variations.append(varied_text)
        
        return variations[:8]  # Limit total variations to prevent explosion
    
    def generate_enhanced_intent_dataset(self, samples_per_class: int = 2000) -> List[Dict]:
        """Generate enhanced intent dataset dengan natural variations"""
        dataset = []
        
        logger.info(f"🔄 Generating enhanced intent dataset with {samples_per_class} samples per class...")
        
        # INCOME SAMPLES
        for i in range(samples_per_class):
            template = random.choice(self.income_templates)
            amount = random.choice(self.amounts)
            source = random.choice(self.income_sources)
            
            base_text = template.format(amount=amount, source=source)
            
            # Add some variations but not too many
            if i % 5 == 0:  # Every 5th sample gets variations
                variations = self.generate_natural_variations(base_text)
                selected_variations = random.sample(variations, min(2, len(variations)))
                
                for text in [base_text] + selected_variations:
                    dataset.append({
                        "text": text.strip(),
                        "label": "income"
                    })
            else:
                dataset.append({
                    "text": base_text.strip(),
                    "label": "income"
                })
        
        # EXPENSE SAMPLES
        for i in range(samples_per_class):
            template = random.choice(self.expense_templates)
            amount = random.choice(self.amounts)
            
            # Select category from all expense types
            all_categories = (
                self.expense_categories["needs"] + 
                self.expense_categories["wants"] + 
                self.expense_categories["savings"]
            )
            category = random.choice(all_categories)
            
            base_text = template.format(amount=amount, category=category)
            
            # Add variations occasionally
            if i % 5 == 0:
                variations = self.generate_natural_variations(base_text)
                selected_variations = random.sample(variations, min(2, len(variations)))
                
                for text in [base_text] + selected_variations:
                    dataset.append({
                        "text": text.strip(),
                        "label": "expense"
                    })
            else:
                dataset.append({
                    "text": base_text.strip(),
                    "label": "expense"
                })
        
        # SAVINGS GOAL SAMPLES
        for i in range(samples_per_class):
            template = random.choice(self.savings_templates)
            amount = random.choice(self.amounts)
            item = random.choice(self.savings_items)
            
            base_text = template.format(amount=amount, item=item)
            
            # Add variations occasionally
            if i % 5 == 0:
                variations = self.generate_natural_variations(base_text)
                selected_variations = random.sample(variations, min(2, len(variations)))
                
                for text in [base_text] + selected_variations:
                    dataset.append({
                        "text": text.strip(),
                        "label": "savings_goal"
                    })
            else:
                dataset.append({
                    "text": base_text.strip(),
                    "label": "savings_goal"
                })
        
        # NON-FINANCIAL SAMPLES
        non_financial_templates = [
            "halo", "hai", "selamat pagi", "good morning", "apa kabar",
            "gimana kabarnya", "lagi ngapain", "udah makan", "help me",
            "tolong dong", "makasih", "terima kasih", "bye", "dadah",
            "bagus", "keren", "mantap", "asik", "seru", "ok", "oke",
            "iya", "ya", "tidak", "gak", "enggak", "maybe", "mungkin",
        ]
        
        for i in range(samples_per_class):
            base_text = random.choice(non_financial_templates)
            
            # Add variations occasionally
            if i % 10 == 0:
                variations = self.generate_natural_variations(base_text)
                selected_variations = random.sample(variations, min(1, len(variations)))
                
                for text in [base_text] + selected_variations:
                    dataset.append({
                        "text": text.strip(),
                        "label": "non_financial"
                    })
            else:
                dataset.append({
                    "text": base_text.strip(),
                    "label": "non_financial"
                })
        
        # Shuffle and clean
        random.shuffle(dataset)
        
        # Remove duplicates and empty texts
        seen_texts = set()
        clean_dataset = []
        for item in dataset:
            text = item["text"].strip()
            if text and text not in seen_texts and len(text) > 2:
                seen_texts.add(text)
                clean_dataset.append(item)
        
        logger.info(f"✅ Generated {len(clean_dataset)} unique intent samples")
        return clean_dataset
    
    def generate_enhanced_category_dataset(self, samples_per_category: int = 150) -> List[Dict]:
        """Generate enhanced category dataset"""
        dataset = []
        
        logger.info(f"🔄 Generating category dataset with {samples_per_category} samples per category...")
        
        # Income categories
        income_category_mapping = {
            "Uang Saku/Kiriman Ortu": [s for s in self.income_sources if any(fam in s for fam in ["ortu", "bokap", "nyokap", "papa", "mama", "ayah", "ibu"])],
            "Part-time Job": [s for s in self.income_sources if any(work in s for work in ["part time", "kerja", "ngajar", "les", "kasir"])],
            "Freelance/Project": [s for s in self.income_sources if any(proj in s for proj in ["freelance", "project", "design", "coding"])],
            "Beasiswa": [s for s in self.income_sources if any(sch in s for sch in ["beasiswa", "scholarship", "bidikmisi"])],
            "Bisnis/Jualan": [s for s in self.income_sources if any(bus in s for bus in ["jualan", "bisnis", "usaha", "dropship"])],
            "Hadiah/Bonus": [s for s in self.income_sources if any(bonus in s for bonus in ["bonus", "hadiah", "cashback", "lomba"])],
        }
        
        # Expense categories by budget type
        expense_category_mapping = {
            "Kos/Tempat Tinggal": self.expense_categories["needs"][:15],
            "Makanan Pokok": self.expense_categories["needs"][15:30],
            "Transport Wajib": self.expense_categories["needs"][30:45],
            "Pendidikan": self.expense_categories["needs"][45:60],
            "Internet & Komunikasi": self.expense_categories["needs"][60:70],
            "Kesehatan & Kebersihan": self.expense_categories["needs"][70:],
            
            "Jajan & Snack": self.expense_categories["wants"][:30],
            "Hiburan & Sosial": self.expense_categories["wants"][30:60],
            "Fashion & Beauty": self.expense_categories["wants"][60:90],
            "Shopping Online": self.expense_categories["wants"][90:110],
            "Organisasi & Event": self.expense_categories["wants"][110:130],
            "Hobi & Olahraga": self.expense_categories["wants"][130:],
            
            "Tabungan Umum": self.expense_categories["savings"][:5],
            "Investasi": self.expense_categories["savings"][5:10],
            "Dana Darurat": self.expense_categories["savings"][10:],
        }
        
        # Generate samples for each category
        all_categories = {**income_category_mapping, **expense_category_mapping}
        
        for category_name, keywords in all_categories.items():
            if not keywords:
                continue
                
            for _ in range(samples_per_category):
                # Determine if income or expense
                if category_name in income_category_mapping:
                    template = random.choice(self.income_templates)
                    amount = random.choice(self.amounts)
                    keyword = random.choice(keywords)
                    base_text = template.format(amount=amount, source=keyword)
                else:
                    template = random.choice(self.expense_templates)
                    amount = random.choice(self.amounts)
                    keyword = random.choice(keywords)
                    base_text = template.format(amount=amount, category=keyword)
                
                dataset.append({
                    "text": base_text.strip(),
                    "label": category_name
                })
        
        # Clean dataset
        seen_texts = set()
        clean_dataset = []
        for item in dataset:
            text = item["text"].strip()
            if text and text not in seen_texts and len(text) > 2:
                seen_texts.add(text)
                clean_dataset.append(item)
        
        random.shuffle(clean_dataset)
        logger.info(f"✅ Generated {len(clean_dataset)} unique category samples")
        return clean_dataset
    
    def save_enhanced_datasets(self, output_dir: str):
        """Save enhanced datasets"""
        os.makedirs(output_dir, exist_ok=True)
        
        logger.info("🚀 Generating ENHANCED Natural Indonesian datasets...")
        
        # Generate datasets with reasonable sizes
        intent_data = self.generate_enhanced_intent_dataset(1500)  # Reduced from 2000
        category_data = self.generate_enhanced_category_dataset(100)  # Reduced from 150
        
        # Save datasets
        intent_path = f"{output_dir}/enhanced_intent_dataset.json"
        category_path = f"{output_dir}/enhanced_category_dataset.json"
        
        with open(intent_path, 'w', encoding='utf-8') as f:
            json.dump(intent_data, f, ensure_ascii=False, indent=2)
        
        with open(category_path, 'w', encoding='utf-8') as f:
            json.dump(category_data, f, ensure_ascii=False, indent=2)
        
        # Save metadata
        metadata = {
            "generation_info": {
                "generated_at": datetime.now().isoformat(),
                "enhancement_type": "Natural Indonesian Student Language",
                "intent_samples": len(intent_data),
                "category_samples": len(category_data),
                "total_samples": len(intent_data) + len(category_data)
            },
            "features": [
                "Natural Indonesian slang (dapet, abis, pengen)",
                "Regional family terms (bokap, nyokap, bude, pakde)",
                "Modern payment methods (gofood, gopay, ovo, spaylater)",
                "Student-specific vocabulary (UKT, kos, part time)",
                "Emotional context (alhamdulillah, capek deh, gregetan)",
                "Natural amount formats (50rb, 1.5 juta, 2M)",
                "Spelling variations and typos",
                "Casual punctuation and markers"
            ],
            "statistics": {
                "unique_templates": len(self.income_templates) + len(self.expense_templates) + len(self.savings_templates),
                "vocabulary_size": len(self.amounts) + len(self.income_sources) + sum(len(cat) for cat in self.expense_categories.values()) + len(self.savings_items),
                "natural_variations": len(self.natural_variations),
                "spelling_variants": len(self.spelling_variations)
            }
        }
        
        with open(f"{output_dir}/dataset_metadata.json", 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
        
        logger.info(f"✅ Enhanced datasets saved to {output_dir}")
        logger.info(f"📊 Intent samples: {len(intent_data)}")
        logger.info(f"📊 Category samples: {len(category_data)}")
        logger.info(f"📊 Total samples: {len(intent_data) + len(category_data)}")

class EnhancedIndoRoBERTaTrainer:
    """Enhanced trainer dengan optimized parameters untuk natural Indonesian"""
    
    def __init__(self, base_model: str = "indobenchmark/indobert-base-p1"):
        self.base_model = base_model
        self.output_dir = Path("models/indoroberta-financial-enhanced")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Enhanced device setup
        if torch.cuda.is_available():
            self.device = torch.device("cuda")
            torch.cuda.empty_cache()  # Clear cache
            logger.info(f"🚀 Using GPU: {torch.cuda.get_device_name()}")
            logger.info(f"💾 GPU Memory: {torch.cuda.get_device_properties(0).total_memory // 1024**3} GB")
        else:
            self.device = torch.device("cpu")
            logger.info("🖥️ Using CPU")
        
        # Set optimized random seeds
        self.set_seeds(42)
    
    def set_seeds(self, seed: int):
        """Set random seeds untuk reproducibility"""
        random.seed(seed)
        np.random.seed(seed)
        torch.manual_seed(seed)
        if torch.cuda.is_available():
            torch.cuda.manual_seed_all(seed)
        logger.info(f"🎲 Random seeds set to {seed}")
    
    def create_optimized_training_args(self, output_dir: str, model_type: str) -> TrainingArguments:
        """Create optimized training arguments - FIXED OPTIMIZER"""
        
        # FIXED: Use valid optimizer
        args = TrainingArguments(
            output_dir=output_dir,
            
            # Training parameters - optimized dan conservative
            num_train_epochs=3,  # Conservative epochs
            per_device_train_batch_size=8,  # Smaller batch size
            per_device_eval_batch_size=8,
            gradient_accumulation_steps=1,  # No accumulation untuk simplicity
            
            # Learning rate - conservative
            learning_rate=2e-5,  # Standard BERT learning rate
            weight_decay=0.01,
            warmup_steps=200,  # Conservative warmup
            lr_scheduler_type="linear",  # Stable scheduler
            
            # Evaluation and saving - more frequent
            eval_strategy="steps",
            eval_steps=200,  
            save_strategy="steps",
            save_steps=200,
            save_total_limit=2,  # Keep fewer checkpoints
            
            # Early stopping
            load_best_model_at_end=True,
            metric_for_best_model="eval_accuracy",  # Use accuracy instead of F1
            greater_is_better=True,
            
            # Performance optimizations - conservative
            dataloader_num_workers=0,  # FIXED: Use 0 workers to avoid multiprocessing issues
            group_by_length=False,  # FIXED: Disable to avoid tokenization issues
            remove_unused_columns=True,  # Keep default
            
            # Mixed precision - disable for compatibility
            fp16=False,  # FIXED: Disable FP16 to avoid potential issues
            
            # Logging
            logging_dir=f"{output_dir}/logs",
            logging_steps=50,
            report_to="none",
            
            # Optimization - FIXED: Use valid optimizer
            optim="adamw_torch",  # FIXED: Changed from adamw_hf to adamw_torch
            max_grad_norm=1.0,
            
            # Seeding
            seed=42,
            data_seed=42,
            
            # FIXED: Add additional stability parameters
            dataloader_pin_memory=False,  # Disable pin memory
            skip_memory_metrics=True,  # Skip memory metrics
        )
        
        logger.info(f"⚙️ Optimized training args created for {model_type} with optimizer: adamw_torch")
        return args
    
    def compute_enhanced_metrics(self, labels: List[str]):
        """Create enhanced metrics computation function"""
        def compute_metrics(eval_pred):
            predictions, labels = eval_pred
            predictions = np.argmax(predictions, axis=1)
            
            # Calculate basic metrics
            accuracy = accuracy_score(labels, predictions)
            
            try:
                f1_macro = f1_score(labels, predictions, average='macro')
                f1_weighted = f1_score(labels, predictions, average='weighted')
                
                # Classification report
                report = classification_report(labels, predictions, output_dict=True, zero_division=0)
                precision_macro = report['macro avg']['precision']
                recall_macro = report['macro avg']['recall']
            except:
                f1_macro = 0.0
                f1_weighted = 0.0
                precision_macro = 0.0
                recall_macro = 0.0
            
            return {
                "accuracy": accuracy,
                "f1": f1_macro,
                "f1_weighted": f1_weighted,
                "precision": precision_macro,
                "recall": recall_macro
            }
        
        return compute_metrics
    
    def train_enhanced_intent_classifier(self, dataset_path: str):
        """Train enhanced intent classifier dengan proper tokenization"""
        logger.info("🎯 Training ENHANCED Intent Classifier...")
        
        try:
            # Load and analyze dataset
            with open(dataset_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            df = pd.DataFrame(data)
            logger.info(f"📊 Dataset loaded: {len(df)} samples")
            
            # Analyze class distribution
            class_counts = df['label'].value_counts()
            logger.info("📈 Class distribution:")
            for label, count in class_counts.items():
                logger.info(f"  {label}: {count} samples ({count/len(df)*100:.1f}%)")
            
            # Create label mappings
            unique_labels = sorted(df['label'].unique())
            label2id = {label: i for i, label in enumerate(unique_labels)}
            id2label = {i: label for label, i in label2id.items()}
            
            logger.info(f"🏷️ Intent labels: {unique_labels}")
            
            # Prepare data - FIXED: Proper validation
            texts = [str(text).strip() for text in df['text'].tolist()]
            labels = [label2id[label] for label in df['label']]
            
            # Remove empty texts
            filtered_data = [(text, label) for text, label in zip(texts, labels) if len(text) > 0]
            texts, labels = zip(*filtered_data)
            texts, labels = list(texts), list(labels)
            
            logger.info(f"📊 After filtering: {len(texts)} samples")
            
            # Enhanced train-validation split dengan stratification
            train_texts, val_texts, train_labels, val_labels = train_test_split(
                texts, labels, 
                test_size=0.2,  # Standard validation split
                random_state=42,
                stratify=labels
            )
            
            logger.info(f"📊 Train: {len(train_texts)}, Validation: {len(val_texts)}")
            
            # Load model and tokenizer
            logger.info(f"🤖 Loading model: {self.base_model}")
            tokenizer = AutoTokenizer.from_pretrained(self.base_model)
            model = AutoModelForSequenceClassification.from_pretrained(
                self.base_model,
                num_labels=len(unique_labels),
                label2id=label2id,
                id2label=id2label,
                problem_type="single_label_classification"
            )
            
            # FIXED: Proper tokenization function
            def tokenize_function(examples):
                # Ensure examples["text"] is a list of strings
                texts = examples["text"]
                if isinstance(texts, str):
                    texts = [texts]
                
                return tokenizer(
                    texts,
                    truncation=True,
                    padding=True,
                    max_length=128,  # Shorter max length for stability
                )
            
            # Create datasets - FIXED: Proper dataset creation
            train_dataset = Dataset.from_dict({
                "text": train_texts,
                "labels": train_labels
            })
            val_dataset = Dataset.from_dict({
                "text": val_texts,
                "labels": val_labels
            })
            
            # Tokenize - FIXED: Proper tokenization
            logger.info("🔤 Tokenizing datasets...")
            train_dataset = train_dataset.map(
                tokenize_function, 
                batched=True, 
                remove_columns=["text"]  # Remove text column after tokenization
            )
            val_dataset = val_dataset.map(
                tokenize_function, 
                batched=True, 
                remove_columns=["text"]  # Remove text column after tokenization
            )
            
            # Data collator - FIXED: Use proper data collator
            data_collator = DataCollatorWithPadding(
                tokenizer=tokenizer,
                padding=True,
                return_tensors="pt"
            )
            
            # Training arguments
            intent_output_dir = str(self.output_dir / "intent_classifier")
            training_args = self.create_optimized_training_args(intent_output_dir, "intent")
            
            # Metrics function
            compute_metrics = self.compute_enhanced_metrics(unique_labels)
            
            # Create enhanced trainer - FIXED: Proper trainer setup
            trainer = Trainer(
                model=model,
                args=training_args,
                train_dataset=train_dataset,
                eval_dataset=val_dataset,
                tokenizer=tokenizer,
                data_collator=data_collator,
                compute_metrics=compute_metrics,
                callbacks=[EarlyStoppingCallback(early_stopping_patience=5)]
            )
            
            # Train
            logger.info("🚀 Starting enhanced training...")
            train_result = trainer.train()
            
            # Evaluate
            eval_result = trainer.evaluate()
            logger.info("📊 Final evaluation results:")
            for key, value in eval_result.items():
                logger.info(f"  {key}: {value:.4f}")
            
            # Save model
            logger.info(f"💾 Saving model to {intent_output_dir}")
            trainer.save_model()
            tokenizer.save_pretrained(intent_output_dir)
            
            # Save comprehensive metadata
            metadata = {
                "model_info": {
                    "base_model": self.base_model,
                    "model_type": "intent_classifier",
                    "enhancement": "Natural Indonesian Student Language",
                    "training_samples": len(train_texts),
                    "validation_samples": len(val_texts),
                    "num_labels": len(unique_labels),
                    "labels": unique_labels
                },
                "training_config": {
                    "epochs": training_args.num_train_epochs,
                    "batch_size": training_args.per_device_train_batch_size,
                    "learning_rate": training_args.learning_rate,
                    "warmup_steps": training_args.warmup_steps,
                    "weight_decay": training_args.weight_decay,
                    "optimizer": "adamw_torch"  # Updated
                },
                "results": {
                    "train_loss": train_result.training_loss,
                    **eval_result
                },
                "label_mapping": {
                    "label2id": label2id,
                    "id2label": id2label
                },
                "class_distribution": class_counts.to_dict(),
                "trained_at": datetime.now().isoformat()
            }
            
            with open(f"{intent_output_dir}/model_metadata.json", 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
            
            logger.info("✅ Enhanced intent classifier training completed!")
            return trainer, eval_result
            
        except Exception as e:
            logger.error(f"❌ Enhanced intent training failed: {e}")
            import traceback
            traceback.print_exc()
            raise
    
    def train_enhanced_category_classifier(self, dataset_path: str):
        """Train enhanced category classifier dengan proper handling"""
        logger.info("🏷️ Training ENHANCED Category Classifier...")
        
        try:
            # Load dataset
            with open(dataset_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            df = pd.DataFrame(data)
            logger.info(f"📊 Category dataset: {len(df)} samples")
            
            # Analyze distribution
            class_counts = df['label'].value_counts()
            logger.info("📈 Category distribution:")
            for label, count in class_counts.items():
                logger.info(f"  {label}: {count}")
            
            # Create mappings
            unique_labels = sorted(df['label'].unique())
            label2id = {label: i for i, label in enumerate(unique_labels)}
            id2label = {i: label for label, i in label2id.items()}
            
            logger.info(f"🏷️ Categories ({len(unique_labels)}): {unique_labels}")
            
            # Prepare data - FIXED: Same as intent classifier
            texts = [str(text).strip() for text in df['text'].tolist()]
            labels = [label2id[label] for label in df['label']]
            
            # Remove empty texts
            filtered_data = [(text, label) for text, label in zip(texts, labels) if len(text) > 0]
            texts, labels = zip(*filtered_data)
            texts, labels = list(texts), list(labels)
            
            # Split dengan stratification
            train_texts, val_texts, train_labels, val_labels = train_test_split(
                texts, labels,
                test_size=0.2,
                random_state=42,
                stratify=labels
            )
            
            logger.info(f"📊 Train: {len(train_texts)}, Validation: {len(val_texts)}")
            
            # Load model
            tokenizer = AutoTokenizer.from_pretrained(self.base_model)
            model = AutoModelForSequenceClassification.from_pretrained(
                self.base_model,
                num_labels=len(unique_labels),
                label2id=label2id,
                id2label=id2label
            )
            
            # Tokenization - FIXED: Same as intent classifier
            def tokenize_function(examples):
                texts = examples["text"]
                if isinstance(texts, str):
                    texts = [texts]
                
                return tokenizer(
                    texts,
                    truncation=True,
                    padding=True,
                    max_length=128,
                )
            
            # Create datasets
            train_dataset = Dataset.from_dict({
                "text": train_texts,
                "labels": train_labels
            })
            val_dataset = Dataset.from_dict({
                "text": val_texts,
                "labels": val_labels
            })
            
            # Tokenize
            train_dataset = train_dataset.map(
                tokenize_function, 
                batched=True, 
                remove_columns=["text"]
            )
            val_dataset = val_dataset.map(
                tokenize_function, 
                batched=True, 
                remove_columns=["text"]
            )
            
            # Training setup
            category_output_dir = str(self.output_dir / "category_classifier")
            training_args = self.create_optimized_training_args(category_output_dir, "category")
            
            data_collator = DataCollatorWithPadding(
                tokenizer=tokenizer,
                padding=True,
                return_tensors="pt"
            )
            compute_metrics = self.compute_enhanced_metrics(unique_labels)
            
            # Trainer
            trainer = Trainer(
                model=model,
                args=training_args,
                train_dataset=train_dataset,
                eval_dataset=val_dataset,
                tokenizer=tokenizer,
                data_collator=data_collator,
                compute_metrics=compute_metrics,
                callbacks=[EarlyStoppingCallback(early_stopping_patience=5)]
            )
            
            # Train
            logger.info("🚀 Training category classifier...")
            train_result = trainer.train()
            
            # Evaluate
            eval_result = trainer.evaluate()
            logger.info("📊 Category evaluation:")
            for key, value in eval_result.items():
                logger.info(f"  {key}: {value:.4f}")
            
            # Save
            trainer.save_model()
            tokenizer.save_pretrained(category_output_dir)
            
            # Metadata
            metadata = {
                "model_info": {
                    "base_model": self.base_model,
                    "model_type": "category_classifier",
                    "enhancement": "Natural Indonesian Categories",
                    "training_samples": len(train_texts),
                    "validation_samples": len(val_texts),
                    "num_labels": len(unique_labels)
                },
                "results": {
                    "train_loss": train_result.training_loss,
                    **eval_result
                },
                "label_mapping": {
                    "label2id": label2id,
                    "id2label": id2label
                },
                "trained_at": datetime.now().isoformat()
            }
            
            with open(f"{category_output_dir}/model_metadata.json", 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
            
            logger.info("✅ Enhanced category classifier completed!")
            return trainer, eval_result
            
        except Exception as e:
            logger.error(f"❌ Category training failed: {e}")
            import traceback
            traceback.print_exc()
            raise
    
    def train_all_enhanced_models(self):
        """Train all enhanced models"""
        logger.info("🚀 Starting ENHANCED Natural Indonesian Financial Parser Training")
        logger.info("="*80)
        
        # Generate enhanced datasets
        generator = NaturalIndonesianDatasetGenerator()
        data_dir = "data/enhanced_natural_training"
        generator.save_enhanced_datasets(data_dir)
        
        results = {}
        start_time = datetime.now()
        
        try:
            # Train intent classifier
            logger.info("\n" + "🎯" * 20)
            logger.info("PHASE 1: ENHANCED INTENT CLASSIFIER")
            logger.info("Natural Indonesian Student Language")
            logger.info("🎯" * 20)
            
            intent_trainer, intent_results = self.train_enhanced_intent_classifier(
                f"{data_dir}/enhanced_intent_dataset.json"
            )
            results["intent"] = intent_results
            
            # Train category classifier
            logger.info("\n" + "🏷️" * 20)
            logger.info("PHASE 2: ENHANCED CATEGORY CLASSIFIER")
            logger.info("Indonesian Student Categories")
            logger.info("🏷️" * 20)
            
            category_trainer, category_results = self.train_enhanced_category_classifier(
                f"{data_dir}/enhanced_category_dataset.json"
            )
            results["category"] = category_results
            
            # Training summary
            end_time = datetime.now()
            training_duration = end_time - start_time
            
            summary = {
                "training_info": {
                    "started_at": start_time.isoformat(),
                    "completed_at": end_time.isoformat(),
                    "duration_minutes": training_duration.total_seconds() / 60,
                    "enhancement_type": "Natural Indonesian Student Language",
                    "base_model": self.base_model
                },
                "results": results,
                "model_paths": {
                    "intent_classifier": str(self.output_dir / "intent_classifier"),
                    "category_classifier": str(self.output_dir / "category_classifier")
                },
                "enhancements": [
                    "Natural Indonesian slang and expressions",
                    "Regional family terminology", 
                    "Modern digital payment vocabulary",
                    "Student-specific financial terms",
                    "Emotional context in language",
                    "Optimized training parameters",
                    "Enhanced dataset generation",
                    "Improved tokenization and metrics"
                ],
                "performance_targets": {
                    "intent_accuracy": "> 0.85",
                    "category_accuracy": "> 0.80",
                    "natural_language_support": "High",
                    "confidence_threshold": "0.3 for natural language"
                }
            }
            
            summary_path = self.output_dir / "enhanced_training_summary.json"
            with open(summary_path, 'w', encoding='utf-8') as f:
                json.dump(summary, f, indent=2, ensure_ascii=False)
            
            # Success message
            logger.info("\n" + "🎉" * 30)
            logger.info("🎉 ENHANCED TRAINING COMPLETED SUCCESSFULLY! 🎉")
            logger.info("🇮🇩 Natural Indonesian Financial Parser Ready! 🇮🇩")
            logger.info("🎉" * 30)
            logger.info(f"⏱️ Training duration: {training_duration}")
            logger.info(f"📍 Models saved to: {self.output_dir}")
            logger.info(f"📊 Intent accuracy: {intent_results.get('eval_accuracy', 0):.3f}")
            logger.info(f"📊 Category accuracy: {category_results.get('eval_accuracy', 0):.3f}")
            logger.info("🎉" * 30)
            
            return results
            
        except Exception as e:
            logger.error(f"❌ Enhanced training failed: {e}")
            import traceback
            traceback.print_exc()
            raise

def main():
    """Main enhanced training function"""
    print("🚀 Enhanced Natural Indonesian Financial Parser Training")
    print("🇮🇩 Optimized for Student Language Patterns")
    print("=" * 80)
    
    # Set seeds
    random.seed(42)
    np.random.seed(42)
    torch.manual_seed(42)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(42)
    
    # System info
    logger.info(f"🖥️ System: Python {os.sys.version}")
    logger.info(f"🤖 PyTorch: {torch.__version__}")
    logger.info(f"⚡ Device: {'CUDA' if torch.cuda.is_available() else 'CPU'}")
    
    try:
        # Initialize trainer
        trainer = EnhancedIndoRoBERTaTrainer()
        
        # Train all models
        results = trainer.train_all_enhanced_models()
        
        print("\n" + "✅" * 30)
        print("✅ TRAINING BERHASIL! ENHANCED PARSER READY! ✅")
        print("🇮🇩 Mendukung Bahasa Natural Indonesia Mahasiswa 🇮🇩")
        print("✅" * 30)
        
    except Exception as e:
        logger.error(f"❌ Training failed: {e}")
        print("\n" + "❌" * 30)
        print("❌ TRAINING GAGAL! ❌")
        print("❌" * 30)
        print(f"Error: {str(e)}")
        print("Check natural_training.log for details")
        print("❌" * 30)
        raise

if __name__ == "__main__":
    main()