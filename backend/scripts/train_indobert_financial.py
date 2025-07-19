# scripts/train_indoroberta_models_enhanced.py - Enhanced for Natural Indonesian Student Language
import os
import json
import random
import logging
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Tuple

# Setup logging untuk Windows - tanpa emoji
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('training.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Cek dependencies
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
            logger.info(f"[OK] {package} is available")
        except ImportError:
            missing.append(pip_name)
            logger.error(f"[ERROR] {package} is missing")
    
    if missing:
        logger.error(f"Missing packages: {missing}")
        logger.error("Install with: pip install " + " ".join(missing))
        return False
    
    return True

# Only import after check
if check_dependencies():
    import torch
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import classification_report, accuracy_score
    from transformers import (
        AutoTokenizer, AutoModelForSequenceClassification,
        TrainingArguments, Trainer, EarlyStoppingCallback
    )
    from datasets import Dataset
    
    logger.info(f"[INFO] PyTorch version: {torch.__version__}")
    logger.info(f"[INFO] Transformers available")
    logger.info(f"[INFO] Training device: {'CUDA' if torch.cuda.is_available() else 'CPU'}")
else:
    exit(1)

class FinancialDatasetGenerator:
    """Enhanced dataset generator with natural Indonesian student language"""
    
    def __init__(self):
        self.setup_templates()
        self.setup_vocabulary()
    
    def setup_templates(self):
        """Setup template yang lebih natural untuk mahasiswa Indonesia"""
        self.income_templates = [
            # Format casual/slang
            "Dapet {amount} dari {source}",
            "Masuk {amount} dari {source}",
            "Terima {amount} {source}",
            "Cair {amount} dari {source}",
            "Dapat transfer {amount} dari {source}",
            "Alhamdulillah dapet {amount} dari {source}",
            "Rejeki {amount} dari {source}",
            "Untung {amount} dari {source}",
            "Bonus {amount} dari {source}",
            "Income {amount} dari {source}",
            
            # Format yang lebih formal tapi tetap mahasiswa
            "Freelance project selesai dapat {amount}",
            "Part time kemarin bayaran {amount}",
            "Jualan online laku {amount}",
            "Les privat dapat {amount}",
            "Ngajar dapat honor {amount}",
            "Kerja sampingan {amount}",
            "Project design {amount} masuk",
            "Coding project done, bayaran {amount}",
            "Event organizer dapat {amount}",
            "Jual barang bekas {amount}",
            
            # Regional variations
            "Kiriman bokap {amount}",
            "Nyokap kasih {amount}",
            "Ortu transfer {amount}",
            "Mama kirim {amount}",
            "Papa kasih jajan {amount}",
            "Bude transfer {amount}",
            "Om kasih {amount}",
            "Eyang transfer {amount}",
            "Kakak kasih {amount}",
            "Adek bayar hutang {amount}"
        ]
        
        self.expense_templates = [
            # Format natural mahasiswa
            "Abis {amount} buat {category}",
            "Keluar {amount} untuk {category}",
            "Beli {category} {amount}",
            "Bayar {category} {amount}",
            "Habis {amount} {category}",
            "Spend {amount} di {category}",
            "Buang duit {amount} buat {category}",
            "Keluarin {amount} untuk {category}",
            "Shopping {category} {amount}",
            "Boros {amount} gara-gara {category}",
            
            # Specific contexts
            "Gofood {category} {amount}",
            "Grab {category} {amount}",
            "Shopee {category} {amount}",
            "Tokped {category} {amount}",
            "COD {category} {amount}",
            "Transfer {amount} buat {category}",
            "Bayar via dana {amount} {category}",
            "Ovo pay {amount} {category}",
            "Gopay {amount} untuk {category}",
            "Spaylater {amount} {category}",
            
            # Emotional context
            "Terpaksa bayar {category} {amount}",
            "Capek deh {amount} buat {category}",
            "Sakit hati {amount} hilang gara-gara {category}",
            "Sedih {amount} melayang buat {category}",
            "Gregetan {amount} abis di {category}"
        ]
        
        self.savings_templates = [
            # Natural savings goals
            "Pengen nabung {amount} buat beli {item}",
            "Target {amount} untuk {item}",
            "Saving {amount} demi {item}",
            "Ngumpulin {amount} buat {item}",
            "Nabung dikit-dikit {amount} untuk {item}",
            "Target tahun ini beli {item} {amount}",
            "Mimpi punya {item} {amount}",
            "Kapan ya bisa beli {item} {amount}",
            "Mau {item} tapi butuh {amount}",
            "Kepengen banget {item} {amount}",
            
            # With timeline
            "Tahun depan mau beli {item} {amount}",
            "Semester depan target {item} {amount}",
            "Liburan mau beli {item} {amount}",
            "Wisuda nanti hadiah diri sendiri {item} {amount}",
            "Setelah lulus mau {item} {amount}",
            
            # Motivational
            "Harus kuat nabung {amount} demi {item}",
            "Sabar menabung {amount} untuk {item}",
            "Perjuangan {amount} demi {item}",
            "Rela skip jajan demi {item} {amount}",
            "Nahan nafsu belanja demi {item} {amount}"
        ]
        
        self.non_financial_templates = [
            # Casual greetings
            "Halo kak", "Hai admin", "P min", "Halooo",
            "Selamat pagi", "Selamat siang", "Selamat malam",
            "Morning!", "Good morning", "Pagi-pagi",
            
            # Questions
            "Mau nanya dong", "Boleh tanya?", "Gimana cara",
            "Bisa bantu?", "Tolong dong", "Help me please",
            "Butuh bantuan", "Ada yang tau?", "Siapa yang bisa",
            
            # Expressions
            "Makasih ya", "Thanks!", "Terima kasih banyak",
            "Wah keren", "Mantap jiwa", "Gaskeun",
            "Asik nih", "Seru banget", "Kece badai",
            
            # Random chat
            "Lagi ngapain?", "Udah makan?", "Gimana kabarnya?",
            "Apa kabar?", "How are you?", "Sehat-sehat ya",
            "Semangat!", "Fighting!", "You can do it!"
        ]
    
    def setup_vocabulary(self):
        """Setup vocabulary yang lebih natural untuk mahasiswa Indonesia"""
        self.amounts = [
            # Format mahasiswa yang sangat natural
            "5rb", "10rb", "15rb", "20rb", "25rb", "30rb", "50rb", 
            "75rb", "100rb", "150rb", "200rb", "250rb", "300rb", 
            "400rb", "500rb", "750rb", "800rb", "900rb",
            
            # Format spoken
            "lima ribu", "sepuluh ribu", "lima belas ribu", "dua puluh ribu",
            "lima puluh ribu", "seratus ribu", "dua ratus ribu", "lima ratus ribu",
            
            # Format kasual
            "5 rebu", "10 rebu", "50 rebu", "100 rebu", "200 rebu",
            
            # Jutaan dengan variasi natural
            "1 juta", "1,2 juta", "1,5 juta", "satu setengah juta",
            "2 juta", "2,5 juta", "dua setengah juta", "3 juta",
            "4 juta", "5 juta", "10 juta", "15 juta", "20 juta",
            
            # Format angka
            "1.000.000", "2.000.000", "5.000.000", "10.000.000",
            "500,000", "1,000,000", "2,000,000",
            
            # Format typo/kasual yang sering muncul
            "50k", "100k", "200k", "500k", "1M", "2M", "5M",
            "50.000", "100.000", "500.000"
        ]
        
        self.income_sources = [
            # Family - lebih natural
            "ortu", "orang tua", "mama", "papa", "ayah", "ibu", "mami", "papi",
            "bokap", "nyokap", "bapak", "mamah", "papah", "umi", "abi",
            "mama papa", "ortu tercinta", "keluarga", "parents",
            
            # Extended family
            "kakak", "adek", "saudara", "om", "tante", "bude", "pakde",
            "eyang", "nenek", "kakek", "sepupu", "keponakan",
            
            # Work related - natural terms
            "freelance", "project", "part time", "kerja sampingan", 
            "side job", "ngajar", "les privat", "tutor", "mentor",
            "event organizer", "EO", "jaga warung", "kasir", "sales",
            "admin", "content creator", "youtuber", "streamer",
            
            # Academic
            "beasiswa", "scholarship", "bidikmisi", "KIP", "bantuan pendidikan",
            "beasiswa prestasi", "beasiswa tidak mampu", "research grant",
            
            # Business
            "jualan", "bisnis", "usaha", "dagang", "jual online",
            "dropship", "reseller", "affiliate", "MLM", "investasi",
            
            # Bonus/rewards
            "gaji", "kantor", "THR", "bonus", "tunjangan", "honor",
            "cashback", "refund", "hadiah", "doorprize", "lomba",
            "kompetisi", "hackathon", "olimpiade"
        ]
        
        self.expense_categories = {
            # NEEDS (50%) - more natural terms
            "needs": [
                # Housing
                "kos", "kost", "kostan", "tempat tinggal", "sewa kamar", 
                "kontrakan", "boarding house", "rumah sewa", "mess",
                "listrik", "air", "wifi", "internet", "token listrik",
                "bayar kos", "uang kos", "sewa bulanan",
                
                # Food - sangat natural untuk mahasiswa
                "makan", "makanan", "lapar", "beli nasi", "warteg", "kantin",
                "catering", "makan siang", "sarapan", "makan malam",
                "groceries", "belanja bulanan", "beras", "mie instan",
                "telur", "sayur", "lauk", "protein", "cemilan sehat",
                "vitamin", "susu", "roti", "buah",
                
                # Transportation - very natural
                "transport", "transportasi", "ojol", "ojek online",
                "grab", "gojek", "maxim", "uber", "angkot", "bus",
                "kereta", "commuter line", "MRT", "LRT", "transjakarta",
                "bensin", "pertamax", "solar", "isi bensin", "bbm",
                "parkir", "tol", "tiket kereta", "tiket bus",
                "ke kampus", "pulang kampus", "PP kampus",
                
                # Education - specific to students
                "kuliah", "kampus", "UKT", "SPP", "biaya kuliah",
                "buku", "buku kuliah", "textbook", "modul", "diktat",
                "fotocopy", "print", "jilid", "alat tulis", "pulpen",
                "kertas", "tinta printer", "laptop", "charger",
                "software", "aplikasi", "zoom premium", "canva pro",
                
                # Communication & Internet
                "pulsa", "paket data", "kuota", "wifi", "internet",
                "telkomsel", "xl", "indosat", "tri", "smartfren",
                "zoom", "netflix", "spotify", "youtube premium",
                
                # Health & hygiene
                "obat", "dokter", "rumah sakit", "puskesmas", "vitamin",
                "masker", "hand sanitizer", "sabun", "shampo", "odol",
                "pasta gigi", "sikat gigi", "skincare basic", "sunscreen"
            ],
            
            # WANTS (30%) - very natural for students
            "wants": [
                # Food & drinks - sangat detail dan natural
                "jajan", "cemilan", "snack", "keripik", "coklat", "permen",
                "es krim", "gelato", "kopi", "coffee", "starbucks", "chatime",
                "bubble tea", "boba", "thai tea", "milk tea", "green tea",
                "martabak", "terang bulan", "pancake", "waffle", "crepe",
                "pizza", "burger", "ayam geprek", "ayam bakar", "sate",
                "bakso", "mie ayam", "gado-gado", "ketoprak", "siomay",
                "batagor", "cilok", "pentol", "seblak", "makaroni",
                "gofood", "grabfood", "delivery", "pesan makan",
                
                # Entertainment - sangat relatable
                "nongkrong", "hangout", "cafe", "coffee shop", "resto",
                "cinema", "bioskop", "XXI", "CGV", "nonton film",
                "netflix", "disney+", "viu", "iqiyi", "spotify",
                "game", "gaming", "steam", "mobile legends", "pubg",
                "free fire", "valorant", "genshin", "top up game",
                "skin game", "battle pass", "gacha", "microtransaction",
                "konser", "festival", "event", "tiket konser",
                "fanmeeting", "meet and greet", "merchandise",
                
                # Fashion & beauty - natural untuk mahasiswa
                "baju", "kaos", "kemeja", "dress", "celana", "jeans",
                "rok", "jaket", "hoodie", "sweater", "cardigan",
                "sepatu", "sneakers", "sandal", "high heels", "boots",
                "tas", "backpack", "totebag", "slingbag", "clutch",
                "dompet", "wallet", "jam tangan", "smartwatch",
                "aksesoris", "kalung", "gelang", "cincin", "anting",
                "makeup", "skincare", "foundation", "lipstick", "mascara",
                "eyeshadow", "blush on", "concealer", "primer", "setting spray",
                "cleanser", "toner", "moisturizer", "serum", "face mask",
                "thrift", "thrifting", "second", "preloved",
                
                # Social & organization
                "organisasi", "ukm", "himpunan", "bem", "ormawa",
                "event organisasi", "gathering", "retreat", "outbound",
                "study tour", "fieldtrip", "wisata", "liburan", "vacation",
                "tiket wisata", "hotel", "penginapan", "airbnb",
                
                # Hobbies
                "hobi", "musik", "alat musik", "gitar", "keyboard",
                "fotografi", "kamera", "lensa", "tripod", "lighting",
                "olahraga", "gym", "fitness", "membership gym",
                "peralatan olahraga", "sepeda", "skateboard"
            ],
            
            # SAVINGS & INVESTMENT (20%)
            "savings": [
                "nabung", "tabungan", "saving", "menabung", "nyimpen duit",
                "deposito", "time deposit", "reksadana", "mutual fund",
                "saham", "stock", "crypto", "bitcoin", "ethereum",
                "forex", "trading", "investasi", "investment",
                "dana darurat", "emergency fund", "dana cadangan",
                "masa depan", "future", "pension", "retirement",
                "asuransi", "insurance", "proteksi", "jaminan"
            ]
        }
        
        self.savings_items = [
            # Technology - sangat update dan natural
            "laptop", "notebook", "macbook", "macbook air", "macbook pro",
            "PC", "computer", "gaming PC", "workstation", "iMac",
            "HP", "handphone", "smartphone", "iPhone", "iPhone 14", "iPhone 15",
            "samsung", "samsung galaxy", "xiaomi", "oppo", "vivo", "realme",
            "poco", "redmi", "oneplus", "google pixel", "huawei",
            
            # Gadgets & accessories
            "headset", "headphone", "earphone", "earbuds", "airpods",
            "speaker", "JBL", "sony", "beats", "keyboard", "mouse",
            "mousepad", "webcam", "microphone", "mic", "ring light",
            "kamera", "canon", "nikon", "sony alpha", "fujifilm",
            "drone", "DJI", "action cam", "gopro", "gimbal",
            "smartwatch", "apple watch", "galaxy watch", "amazfit",
            "tablet", "iPad", "samsung tab", "surface pro",
            
            # Transportation
            "motor", "sepeda motor", "vario", "beat", "scoopy", "nmax",
            "aerox", "mio", "jupiter", "satria", "ninja", "cbr",
            "mobil", "car", "avanza", "xenia", "brio", "agya", "ayla",
            "innova", "fortuner", "pajero", "CR-V", "HR-V",
            "sepeda", "sepeda gunung", "sepeda lipat", "roadbike",
            "fixie", "bmx", "sepeda listrik",
            
            # Home & lifestyle
            "TV", "smart TV", "LED TV", "monitor", "gaming monitor",
            "kulkas", "refrigerator", "mesin cuci", "washing machine",
            "AC", "air conditioner", "kipas angin", "dispenser",
            "rice cooker", "magic com", "blender", "microwave",
            "oven", "air fryer", "vacuum cleaner",
            
            # Fashion & accessories
            "sepatu", "sneakers", "nike", "adidas", "converse", "vans",
            "new balance", "asics", "puma", "reebok", "sketchers",
            "sandal", "crocs", "birkenstock", "havaianas",
            "tas", "backpack", "jansport", "herschel", "anello",
            "fjallraven", "coach", "michael kors", "kate spade",
            "jaket", "hoodie", "uniqlo", "h&m", "zara", "bershka",
            "pull&bear", "stradivarius", "forever21",
            
            # Entertainment
            "PS5", "PlayStation", "xbox", "nintendo switch", "steam deck",
            "gaming chair", "meja gaming", "setup gaming",
            "gitar", "keyboard musik", "ukulele", "bass", "drum"
        ]
    
    def generate_intent_dataset(self, samples_per_class: int = 800) -> List[Dict]:
        """Generate dataset untuk intent classification dengan natural language"""
        dataset = []
        
        # Income samples - more variety
        for _ in range(samples_per_class):
            template = random.choice(self.income_templates)
            amount = random.choice(self.amounts)
            source = random.choice(self.income_sources)
            
            # Add natural variations
            variations = [
                template.format(amount=amount, source=source),
                f"{template.format(amount=amount, source=source)} nih",
                f"Alhamdulillah {template.format(amount=amount, source=source)}",
                f"Finally! {template.format(amount=amount, source=source)}",
                f"Yeay {template.format(amount=amount, source=source)}",
            ]
            
            text = random.choice(variations)
            dataset.append({
                "text": text,
                "label": "income"
            })
        
        # Expense samples - more natural
        for _ in range(samples_per_class):
            template = random.choice(self.expense_templates)
            amount = random.choice(self.amounts)
            
            # Random category from all expense types
            all_expense_items = (
                self.expense_categories["needs"] + 
                self.expense_categories["wants"] + 
                self.expense_categories["savings"]
            )
            category = random.choice(all_expense_items)
            
            # Add emotional context
            emotions = [
                "", " :((", " huhu", " sedih", " sakit hati", 
                " capek deh", " gregetan", " yasudahlah", " terpaksa"
            ]
            emotion = random.choice(emotions)
            
            text = template.format(amount=amount, category=category, item=category) + emotion
            dataset.append({
                "text": text,
                "label": "expense"
            })
        
        # Savings goal samples - more aspirational
        for _ in range(samples_per_class):
            template = random.choice(self.savings_templates)
            amount = random.choice(self.amounts)
            item = random.choice(self.savings_items)
            
            # Add motivation/timeline
            motivations = [
                "", " semoga kesampaian", " aamiin", " doakan ya", 
                " fighting!", " bismillah", " insyaallah", " semoga bisa"
            ]
            motivation = random.choice(motivations)
            
            text = template.format(amount=amount, item=item) + motivation
            dataset.append({
                "text": text,
                "label": "savings_goal"
            })
        
        # Non-financial samples - more variety
        for _ in range(samples_per_class):
            template = random.choice(self.non_financial_templates)
            
            # Add natural endings
            endings = [
                "", " dong", " ya", " nih", " sih", " kak", " min",
                " please", " guys", " bestie", " bro", " sis"
            ]
            ending = random.choice(endings)
            
            text = template + ending
            dataset.append({
                "text": text,
                "label": "non_financial"
            })
        
        # Shuffle dataset
        random.shuffle(dataset)
        return dataset
    
    def generate_category_dataset(self, samples_per_category: int = 100) -> List[Dict]:
        """Generate dataset untuk category classification dengan natural language"""
        dataset = []
        
        # Enhanced category mapping
        income_categories = {
            "Uang Saku/Kiriman Ortu": self.income_sources[:13],  # Family terms
            "Part-time Job": ["freelance", "part time", "kerja sampingan", "ngajar", "tutor", "kasir", "sales"],
            "Freelance/Project": ["freelance", "project", "design", "coding", "content creator", "youtuber"],
            "Beasiswa": ["beasiswa", "scholarship", "bidikmisi", "KIP", "bantuan pendidikan"],
            "Bisnis/Jualan": ["jualan", "bisnis", "usaha", "dagang", "dropship", "reseller"],
            "Hadiah/Bonus": ["hadiah", "bonus", "THR", "cashback", "refund", "doorprize", "lomba"]
        }
        
        needs_categories = {
            "Makanan Pokok": self.expense_categories["needs"][8:25],  # Food items
            "Kos/Tempat Tinggal": self.expense_categories["needs"][:8],  # Housing
            "Transportasi Wajib": self.expense_categories["needs"][25:45],  # Transport
            "Pendidikan": self.expense_categories["needs"][45:60],  # Education
            "Internet & Komunikasi": self.expense_categories["needs"][60:70],  # Communication
            "Kesehatan & Kebersihan": self.expense_categories["needs"][70:]  # Health
        }
        
        wants_categories = {
            "Jajan & Snack": self.expense_categories["wants"][:25],  # Food/drinks
            "Hiburan & Sosial": self.expense_categories["wants"][25:50],  # Entertainment
            "Pakaian & Aksesoris": self.expense_categories["wants"][50:75],  # Fashion
            "Organisasi & Event": self.expense_categories["wants"][75:85],  # Social
            "Hobi & Olahraga": self.expense_categories["wants"][85:]  # Hobbies
        }
        
        savings_categories = {
            "Tabungan Umum": ["nabung", "tabungan", "saving", "nyimpen duit"],
            "Dana Darurat": ["dana darurat", "emergency fund", "dana cadangan"],
            "Investasi": ["investasi", "saham", "reksadana", "crypto", "trading"],
            "Target Barang": self.savings_items  # All savings items
        }
        
        # Generate for each category
        all_categories = {**income_categories, **needs_categories, **wants_categories, **savings_categories}
        
        for category, keywords in all_categories.items():
            for _ in range(samples_per_category):
                text = self._generate_natural_text_for_category(category, keywords)
                dataset.append({
                    "text": text,
                    "label": category
                })
        
        random.shuffle(dataset)
        return dataset
    
    def _generate_natural_text_for_category(self, category: str, keywords: List[str]) -> str:
        """Generate natural text sample untuk kategori tertentu"""
        amount = random.choice(self.amounts)
        keyword = random.choice(keywords)
        
        # Template berdasarkan jenis kategori
        if "Ortu" in category or "Beasiswa" in category or "Bonus" in category:
            # Income templates
            templates = [
                f"Dapet {amount} dari {keyword}",
                f"Terima {amount} {keyword}",
                f"Alhamdulillah {amount} masuk dari {keyword}",
                f"Cair {amount} {keyword}",
                f"Transfer {amount} dari {keyword}"
            ]
        elif "Tabungan" in category or "Dana" in category or "Investasi" in category:
            # Savings templates
            templates = [
                f"Nabung {amount} di {keyword}",
                f"Invest {amount} ke {keyword}",
                f"Simpen {amount} buat {keyword}",
                f"Allocate {amount} untuk {keyword}",
                f"Set aside {amount} di {keyword}"
            ]
        elif "Target" in category:
            # Savings goal templates
            templates = [
                f"Pengen beli {keyword} {amount}",
                f"Target {keyword} {amount}",
                f"Nabung {amount} demi {keyword}",
                f"Mimpi punya {keyword} {amount}",
                f"Saving untuk {keyword} {amount}"
            ]
        else:
            # Expense templates
            templates = [
                f"Beli {keyword} {amount}",
                f"Bayar {keyword} {amount}",
                f"Abis {amount} buat {keyword}",
                f"Spend {amount} di {keyword}",
                f"Keluar {amount} untuk {keyword}",
                f"Gofood {keyword} {amount}",
                f"Grab {keyword} {amount}"
            ]
        
        base_text = random.choice(templates)
        
        # Add natural variations
        prefixes = ["", "Tadi ", "Kemarin ", "Barusan ", "Siang ini "]
        suffixes = ["", " nih", " dong", " huhu", " yey", " alhamdulillah", " finally"]
        
        prefix = random.choice(prefixes)
        suffix = random.choice(suffixes)
        
        return f"{prefix}{base_text}{suffix}".strip()
    
    def save_datasets(self, output_dir: str):
        """Save all generated datasets"""
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate datasets dengan ukuran yang lebih kecil untuk testing
        logger.info("[INFO] Generating enhanced natural training datasets...")
        intent_data = self.generate_intent_dataset(1000)  # 4000 total samples
        category_data = self.generate_category_dataset(150)  # ~3000 total samples
        
        # Save to files
        with open(f"{output_dir}/intent_dataset.json", 'w', encoding='utf-8') as f:
            json.dump(intent_data, f, ensure_ascii=False, indent=2)
        
        with open(f"{output_dir}/category_dataset.json", 'w', encoding='utf-8') as f:
            json.dump(category_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"[OK] Enhanced datasets saved to {output_dir}")
        logger.info(f"Intent dataset: {len(intent_data)} samples")
        logger.info(f"Category dataset: {len(category_data)} samples")
        
        # Save vocabulary for reference
        vocab_info = {
            "amounts": self.amounts,
            "income_sources": self.income_sources,
            "expense_categories": self.expense_categories,
            "savings_items": self.savings_items,
            "templates": {
                "income": self.income_templates,
                "expense": self.expense_templates,
                "savings": self.savings_templates,
                "non_financial": self.non_financial_templates
            }
        }
        
        with open(f"{output_dir}/vocabulary.json", 'w', encoding='utf-8') as f:
            json.dump(vocab_info, f, ensure_ascii=False, indent=2)
        
        logger.info(f"[OK] Vocabulary reference saved")


class IndoRoBERTaTrainer:
    """Enhanced Trainer untuk fine-tuning IndoRoBERTa models dengan natural Indonesian language"""
    
    def __init__(self, base_model: str = "indobenchmark/indobert-base-p1"):
        self.base_model = base_model
        self.output_dir = Path("models/indoroberta-financial-enhanced")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Check device
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        logger.info(f"[INFO] Training device: {self.device}")
        
        if torch.cuda.is_available():
            logger.info(f"[INFO] GPU: {torch.cuda.get_device_name()}")
            logger.info(f"[INFO] GPU Memory: {torch.cuda.get_device_properties(0).total_memory // 1024**3} GB")
    
    def verify_model_save(self, model_path: str, model_name: str) -> bool:
        """Verify that model files are actually saved"""
        logger.info(f"[CHECK] Verifying {model_name} at {model_path}")
        
        required_files = [
            "config.json",
            "tokenizer_config.json", 
            "vocab.txt",
            "label_mapping.json"
        ]
        
        # Check for model file (either pytorch_model.bin or model.safetensors)
        model_files = ["pytorch_model.bin", "model.safetensors"]
        has_model_file = any(os.path.exists(os.path.join(model_path, f)) for f in model_files)
        
        if not has_model_file:
            logger.error(f"[ERROR] No model file found in {model_path}")
            return False
        
        # Check other required files
        missing_files = []
        for file in required_files:
            file_path = os.path.join(model_path, file)
            if os.path.exists(file_path):
                file_size = os.path.getsize(file_path)
                logger.info(f"[OK] {file}: {file_size} bytes")
            else:
                missing_files.append(file)
                logger.error(f"[ERROR] Missing: {file}")
        
        if missing_files:
            logger.error(f"[ERROR] Missing files in {model_name}: {missing_files}")
            return False
        
        logger.info(f"[OK] {model_name} verification passed")
        return True
    
    def train_intent_classifier(self, dataset_path: str):
        """Train intent classification model dengan enhanced natural data"""
        logger.info("[START] Training Enhanced Intent Classification Model...")
        
        try:
            # Load dataset
            with open(dataset_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            df = pd.DataFrame(data)
            texts = df['text'].tolist()
            labels = df['label'].tolist()
            
            # Create label mapping
            unique_labels = sorted(list(set(labels)))
            label2id = {label: i for i, label in enumerate(unique_labels)}
            id2label = {i: label for label, i in label2id.items()}
            
            logger.info(f"[INFO] Intent labels ({len(unique_labels)}): {unique_labels}")
            
            # Show sample data
            logger.info("[SAMPLE] Sample training data:")
            for i in range(min(5, len(texts))):
                logger.info(f"  {labels[i]}: {texts[i]}")
            
            # Encode labels
            encoded_labels = [label2id[label] for label in labels]
            
            # Split data
            train_texts, val_texts, train_labels, val_labels = train_test_split(
                texts, encoded_labels, test_size=0.2, random_state=42, 
                stratify=encoded_labels
            )
            
            logger.info(f"[INFO] Train samples: {len(train_texts)}, Val samples: {len(val_texts)}")
            
            # Load tokenizer and model
            logger.info(f"[LOAD] Loading base model: {self.base_model}")
            tokenizer = AutoTokenizer.from_pretrained(self.base_model)
            model = AutoModelForSequenceClassification.from_pretrained(
                self.base_model,
                num_labels=len(unique_labels),
                label2id=label2id,
                id2label=id2label
            )
            
            # Tokenize data
            def tokenize_function(examples):
                return tokenizer(
                    examples["text"], 
                    truncation=True, 
                    padding=True, 
                    max_length=128
                )
            
            train_dataset = Dataset.from_dict({
                "text": train_texts,
                "labels": train_labels
            })
            val_dataset = Dataset.from_dict({
                "text": val_texts,
                "labels": val_labels
            })
            
            logger.info("[PROCESS] Tokenizing datasets...")
            train_dataset = train_dataset.map(tokenize_function, batched=True)
            val_dataset = val_dataset.map(tokenize_function, batched=True)
            
            # Enhanced training arguments
            intent_output_dir = str(self.output_dir / "intent_classifier")
            training_args = TrainingArguments(
                output_dir=intent_output_dir,
                num_train_epochs=3,  # Increased for better performance
                per_device_train_batch_size=8,  # Optimal batch size
                per_device_eval_batch_size=8,
                warmup_steps=100,
                weight_decay=0.01,
                logging_dir=str(self.output_dir / "logs"),
                logging_steps=50,
                eval_steps=200,
                eval_strategy="steps",
                save_strategy="steps", 
                save_steps=200,
                load_best_model_at_end=True,
                metric_for_best_model="eval_accuracy",
                greater_is_better=True,
                save_total_limit=2,
                report_to="none",
                dataloader_num_workers=0,
                seed=42,
                learning_rate=2e-5,  # Optimal learning rate for BERT
                lr_scheduler_type="linear"
            )
            
            # Define enhanced compute metrics
            def compute_metrics(eval_pred):
                predictions, labels = eval_pred
                predictions = np.argmax(predictions, axis=1)
                
                accuracy = accuracy_score(labels, predictions)
                report = classification_report(labels, predictions, target_names=unique_labels, output_dict=True)
                
                return {
                    "accuracy": accuracy,
                    "f1": report['macro avg']['f1-score'],
                    "precision": report['macro avg']['precision'],
                    "recall": report['macro avg']['recall']
                }
            
            # Create trainer
            logger.info("[BUILD] Creating enhanced trainer...")
            trainer = Trainer(
                model=model,
                args=training_args,
                train_dataset=train_dataset,
                eval_dataset=val_dataset,
                tokenizer=tokenizer,
                compute_metrics=compute_metrics,
                callbacks=[EarlyStoppingCallback(early_stopping_patience=5)]
            )
            
            # Train
            logger.info("[TRAIN] Starting enhanced intent classifier training...")
            trainer.train()
            
            # Evaluate
            eval_results = trainer.evaluate()
            logger.info(f"[RESULT] Enhanced intent classifier evaluation: {eval_results}")
            
            # Save model
            logger.info(f"[SAVE] Saving enhanced intent classifier to {intent_output_dir}")
            trainer.save_model(intent_output_dir)
            tokenizer.save_pretrained(intent_output_dir)
            
            # Save label mapping
            label_info = {
                "label2id": label2id,
                "id2label": id2label,
                "labels": unique_labels,
                "model_info": {
                    "base_model": self.base_model,
                    "training_samples": len(train_texts),
                    "validation_samples": len(val_texts),
                    "evaluation_results": eval_results
                }
            }
            
            label_mapping_path = os.path.join(intent_output_dir, "label_mapping.json")
            with open(label_mapping_path, 'w', encoding='utf-8') as f:
                json.dump(label_info, f, indent=2, ensure_ascii=False)
            
            # Verify save
            if self.verify_model_save(intent_output_dir, "Enhanced Intent Classifier"):
                logger.info("[OK] Enhanced intent classifier training completed!")
            else:
                logger.error("[ERROR] Enhanced intent classifier save verification failed!")
                raise Exception("Model save verification failed")
            
            return trainer, eval_results
            
        except Exception as e:
            logger.error(f"[ERROR] Enhanced intent classifier training failed: {e}")
            import traceback
            traceback.print_exc()
            raise
    
    def train_category_classifier(self, dataset_path: str):
        """Train category classification model dengan enhanced natural data"""
        logger.info("[START] Training Enhanced Category Classification Model...")
        
        try:
            # Load dataset
            with open(dataset_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            df = pd.DataFrame(data)
            texts = df['text'].tolist()
            labels = df['label'].tolist()
            
            # Create label mapping
            unique_labels = sorted(list(set(labels)))
            label2id = {label: i for i, label in enumerate(unique_labels)}
            id2label = {i: label for label, i in label2id.items()}
            
            logger.info(f"[INFO] Category labels ({len(unique_labels)}): {unique_labels}")
            
            # Show sample data
            logger.info("[SAMPLE] Sample category training data:")
            for label in unique_labels[:3]:
                sample = next((text for text, lbl in zip(texts, labels) if lbl == label), "")
                logger.info(f"  {label}: {sample}")
            
            # Encode labels
            encoded_labels = [label2id[label] for label in labels]
            
            # Split data
            train_texts, val_texts, train_labels, val_labels = train_test_split(
                texts, encoded_labels, test_size=0.2, random_state=42,
                stratify=encoded_labels
            )
            
            logger.info(f"[INFO] Train samples: {len(train_texts)}, Val samples: {len(val_texts)}")
            
            # Load tokenizer and model
            logger.info(f"[LOAD] Loading base model: {self.base_model}")
            tokenizer = AutoTokenizer.from_pretrained(self.base_model)
            model = AutoModelForSequenceClassification.from_pretrained(
                self.base_model,
                num_labels=len(unique_labels),
                label2id=label2id,
                id2label=id2label
            )
            
            # Tokenize data
            def tokenize_function(examples):
                return tokenizer(
                    examples["text"], 
                    truncation=True, 
                    padding=True, 
                    max_length=128
                )
            
            train_dataset = Dataset.from_dict({
                "text": train_texts,
                "labels": train_labels
            })
            val_dataset = Dataset.from_dict({
                "text": val_texts,
                "labels": val_labels
            })
            
            logger.info("[PROCESS] Tokenizing datasets...")
            train_dataset = train_dataset.map(tokenize_function, batched=True)
            val_dataset = val_dataset.map(tokenize_function, batched=True)
            
            # Enhanced training arguments
            category_output_dir = str(self.output_dir / "category_classifier")
            training_args = TrainingArguments(
                output_dir=category_output_dir,
                num_train_epochs=3,
                per_device_train_batch_size=8,
                per_device_eval_batch_size=8,
                warmup_steps=100,
                weight_decay=0.01,
                logging_dir=str(self.output_dir / "logs"),
                logging_steps=50,
                eval_steps=200,
                eval_strategy="steps",
                save_strategy="steps",
                save_steps=200,
                load_best_model_at_end=True,
                metric_for_best_model="eval_accuracy",
                greater_is_better=True,
                save_total_limit=2,
                report_to="none",
                dataloader_num_workers=0,
                seed=42,
                learning_rate=2e-5,
                lr_scheduler_type="linear"
            )
            
            # Define enhanced compute metrics
            def compute_metrics(eval_pred):
                predictions, labels = eval_pred
                predictions = np.argmax(predictions, axis=1)
                
                accuracy = accuracy_score(labels, predictions)
                report = classification_report(labels, predictions, target_names=unique_labels, output_dict=True)
                
                return {
                    "accuracy": accuracy,
                    "f1": report['macro avg']['f1-score'],
                    "precision": report['macro avg']['precision'],
                    "recall": report['macro avg']['recall']
                }
            
            # Create trainer
            logger.info("[BUILD] Creating enhanced trainer...")
            trainer = Trainer(
                model=model,
                args=training_args,
                train_dataset=train_dataset,
                eval_dataset=val_dataset,
                tokenizer=tokenizer,
                compute_metrics=compute_metrics,
                callbacks=[EarlyStoppingCallback(early_stopping_patience=5)]
            )
            
            # Train
            logger.info("[TRAIN] Starting enhanced category classifier training...")
            trainer.train()
            
            # Evaluate
            eval_results = trainer.evaluate()
            logger.info(f"[RESULT] Enhanced category classifier evaluation: {eval_results}")
            
            # Save model
            logger.info(f"[SAVE] Saving enhanced category classifier to {category_output_dir}")
            trainer.save_model(category_output_dir)
            tokenizer.save_pretrained(category_output_dir)
            
            # Save label mapping
            label_info = {
                "label2id": label2id,
                "id2label": id2label,
                "labels": unique_labels,
                "model_info": {
                    "base_model": self.base_model,
                    "training_samples": len(train_texts),
                    "validation_samples": len(val_texts),
                    "evaluation_results": eval_results
                }
            }
            
            label_mapping_path = os.path.join(category_output_dir, "label_mapping.json")
            with open(label_mapping_path, 'w', encoding='utf-8') as f:
                json.dump(label_info, f, indent=2, ensure_ascii=False)
            
            # Verify save
            if self.verify_model_save(category_output_dir, "Enhanced Category Classifier"):
                logger.info("[OK] Enhanced category classifier training completed!")
            else:
                logger.error("[ERROR] Enhanced category classifier save verification failed!")
                raise Exception("Model save verification failed")
            
            return trainer, eval_results
            
        except Exception as e:
            logger.error(f"[ERROR] Enhanced category classifier training failed: {e}")
            import traceback
            traceback.print_exc()
            raise
    
    def train_all_models(self):
        """Train all enhanced models dengan natural Indonesian language"""
        logger.info("[START] Starting ENHANCED IndoRoBERTa fine-tuning with natural Indonesian language...")
        
        # Generate enhanced datasets
        generator = FinancialDatasetGenerator()
        generator.save_datasets("data/training_enhanced")
        
        results = {}
        
        try:
            # Train intent classifier
            logger.info("\n" + "="*80)
            logger.info("[PHASE 1] ENHANCED INTENT CLASSIFIER TRAINING")
            logger.info("Natural Indonesian Student Language Edition")
            logger.info("="*80)
            intent_trainer, intent_results = self.train_intent_classifier("data/training_enhanced/intent_dataset.json")
            results["intent"] = intent_results
            
            # Train category classifier
            logger.info("\n" + "="*80)
            logger.info("[PHASE 2] ENHANCED CATEGORY CLASSIFIER TRAINING") 
            logger.info("Natural Indonesian Student Language Edition")
            logger.info("="*80)
            category_trainer, category_results = self.train_category_classifier("data/training_enhanced/category_dataset.json")
            results["category"] = category_results
            
            # Save enhanced training summary
            summary = {
                "training_completed": datetime.now().isoformat(),
                "base_model": self.base_model,
                "device": str(self.device),
                "enhancement": "Natural Indonesian Student Language",
                "features": [
                    "Natural slang and colloquial expressions",
                    "Regional Indonesian variations",
                    "Student-specific vocabulary",
                    "Emotional context in expressions",
                    "Modern payment methods (GoPay, OVO, etc.)",
                    "Contemporary brands and products",
                    "Social media and gaming references"
                ],
                "results": results,
                "model_paths": {
                    "intent_classifier": str(self.output_dir / "intent_classifier"),
                    "category_classifier": str(self.output_dir / "category_classifier")
                },
                "dataset_stats": {
                    "intent_samples": 4000,
                    "category_samples": 3000,
                    "total_vocabulary_terms": len(generator.amounts) + len(generator.income_sources) + sum(len(v) for v in generator.expense_categories.values()) + len(generator.savings_items)
                }
            }
            
            summary_path = self.output_dir / "enhanced_training_summary.json"
            with open(summary_path, 'w', encoding='utf-8') as f:
                json.dump(summary, f, indent=2, ensure_ascii=False)
            
            # Final verification
            logger.info("\n" + "="*80)
            logger.info("[CHECK] FINAL ENHANCED MODEL VERIFICATION")
            logger.info("="*80)
            
            intent_path = str(self.output_dir / "intent_classifier")
            category_path = str(self.output_dir / "category_classifier")
            
            intent_ok = self.verify_model_save(intent_path, "Enhanced Intent Classifier")
            category_ok = self.verify_model_save(category_path, "Enhanced Category Classifier")
            
            if intent_ok and category_ok:
                logger.info("[SUCCESS] All ENHANCED models trained and saved successfully!")
                logger.info(f"[INFO] Enhanced models saved to: {self.output_dir}")
                logger.info(f"[INFO] Enhanced training summary: {summary_path}")
                
                logger.info("\n" + "="*80)
                logger.info("[SUCCESS] ENHANCED TRAINING PIPELINE COMPLETED!")
                logger.info("🎉 Natural Indonesian Student Language Edition Ready!")
                logger.info("="*80)
                logger.info("[IMPROVEMENTS] Your model now understands:")
                logger.info("✅ Natural slang like 'dapet', 'abis', 'pengen'")
                logger.info("✅ Regional terms like 'bokap', 'nyokap', 'bude'")
                logger.info("✅ Modern payment terms like 'gopay', 'ovo', 'spaylater'")
                logger.info("✅ Student brands like 'gofood', 'grab', 'shopee'")
                logger.info("✅ Emotional expressions like 'huhu', 'alhamdulillah'")
                logger.info("✅ Contemporary gadgets and lifestyle terms")
                logger.info("="*80)
                logger.info("[NEXT] Next steps:")
                logger.info("1. Update your .env with enhanced model path")
                logger.info("2. Restart your backend server")
                logger.info("3. Test with natural Indonesian expressions!")
                logger.info("="*80)
                
            else:
                raise Exception("Enhanced model verification failed after training")
            
            return results
            
        except Exception as e:
            logger.error(f"[ERROR] Enhanced training pipeline failed: {e}")
            import traceback
            traceback.print_exc()
            raise


def main():
    """Main enhanced training pipeline dengan natural Indonesian language"""
    print("[START] Enhanced IndoRoBERTa Financial Parser Training")
    print("🇮🇩 Natural Indonesian Student Language Edition")
    print("=" * 80)
    
    # Set random seeds
    random.seed(42)
    np.random.seed(42)
    torch.manual_seed(42)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(42)
    
    # System info
    logger.info(f"[INFO] Python version: {os.sys.version}")
    logger.info(f"[INFO] PyTorch version: {torch.__version__}")
    logger.info(f"[INFO] Enhanced training with natural Indonesian language")
    
    try:
        # Check if output directories exist
        output_base = Path("models/indoroberta-financial-enhanced")
        if output_base.exists():
            logger.info(f"[INFO] Enhanced output directory exists: {output_base}")
        else:
            logger.info(f"[INFO] Creating enhanced output directory: {output_base}")
            output_base.mkdir(parents=True, exist_ok=True)
        
        # Initialize enhanced trainer
        trainer = IndoRoBERTaTrainer()
        
        # Train all enhanced models
        results = trainer.train_all_models()
        
        print("\n" + "🎉" * 20)
        print("🎉 ENHANCED TRAINING COMPLETED SUCCESSFULLY! 🎉")
        print("🇮🇩 Natural Indonesian Student Language Ready! 🇮🇩")
        print("🎉" * 20)
        print(f"[INFO] Enhanced models saved to: {trainer.output_dir}")
        print("[INFO] Your enhanced IndoRoBERTa Financial Parser is ready!")
        print("[INFO] Now understands natural Indonesian student language!")
        print("🎉" * 20)
        
    except Exception as e:
        logger.error(f"[ERROR] Enhanced pipeline failed: {e}")
        print("\n" + "❌" * 20)
        print("❌ ENHANCED TRAINING FAILED! ❌")
        print("❌" * 20)
        print(f"Error: {str(e)}")
        print("[INFO] Check training.log for detailed error information")
        print("❌" * 20)
        raise


if __name__ == "__main__":
    main()