# scripts/train/training_config.py - ADVANCED TRAINING CONFIGURATION
import os
from pathlib import Path
from dataclasses import dataclass
from typing import Dict, List, Any

@dataclass
class TrainingConfig:
    """Advanced training configuration with balanced approach"""
    
    # Model Configuration
    base_model: str = "indobenchmark/indobert-base-p1"
    output_dir: str = "models/indoroberta-balanced"
    
    # Dataset Balance Configuration - REDUCED BIAS
    intent_samples_per_class: int = 1500  # Reduced from 2000
    category_samples_per_class: int = 120  # Reduced from 150
    query_samples_per_class: int = 300    # NEW: For query detection
    non_financial_samples: int = 2000     # INCREASED: Better negative examples
    
    # Training Parameters - Optimized
    num_train_epochs: int = 3
    train_batch_size: int = 8
    eval_batch_size: int = 8
    learning_rate: float = 2e-5
    warmup_steps: int = 200
    
    # Validation Configuration
    test_size: float = 0.2
    validation_seed: int = 42
    
    # Advanced Features
    use_augmentation: bool = True
    use_class_weights: bool = True
    use_early_stopping: bool = True
    patience: int = 5
    
    def __init__(self, preset: str = "default"):
        """Initialize with preset configurations"""
        if preset == "balanced":
            self._setup_balanced_config()
        elif preset == "aggressive":
            self._setup_aggressive_config()
        elif preset == "conservative":
            self._setup_conservative_config()
        # default values already set above
    
    def _setup_balanced_config(self):
        """Balanced configuration - RECOMMENDED"""
        self.intent_samples_per_class = 1200
        self.category_samples_per_class = 100
        self.query_samples_per_class = 250
        self.non_financial_samples = 1800
        self.num_train_epochs = 4
        self.learning_rate = 1.5e-5
    
    def _setup_aggressive_config(self):
        """Aggressive training - More epochs, more data"""
        self.intent_samples_per_class = 2000
        self.category_samples_per_class = 150
        self.query_samples_per_class = 400
        self.non_financial_samples = 2500
        self.num_train_epochs = 5
        self.learning_rate = 1e-5
    
    def _setup_conservative_config(self):
        """Conservative training - Less overfitting risk"""
        self.intent_samples_per_class = 800
        self.category_samples_per_class = 80
        self.query_samples_per_class = 200
        self.non_financial_samples = 1200
        self.num_train_epochs = 2
        self.learning_rate = 3e-5
    
    def update_output_dir(self, output_dir: str):
        """Update output directory"""
        self.output_dir = output_dir
    
    def update_sample_counts(self, samples: int):
        """Update sample counts proportionally"""
        base_samples = 1500
        ratio = samples / base_samples
        
        self.intent_samples_per_class = int(samples)
        self.category_samples_per_class = int(120 * ratio)
        self.query_samples_per_class = int(300 * ratio)
        self.non_financial_samples = int(2000 * ratio)
    
    @property
    def data_dir(self) -> str:
        """Get data directory path"""
        return str(Path(self.output_dir).parent / "training_data")
    
    @property
    def intent_model_dir(self) -> str:
        """Get intent model directory"""
        return str(Path(self.output_dir) / "intent_classifier")
    
    @property
    def category_model_dir(self) -> str:
        """Get category model directory"""
        return str(Path(self.output_dir) / "category_classifier")
    
    @property
    def query_model_dir(self) -> str:
        """Get query model directory"""
        return str(Path(self.output_dir) / "query_classifier")
    
    def get_sample_distribution(self) -> Dict[str, int]:
        """Get complete sample distribution"""
        return {
            "intent_per_class": self.intent_samples_per_class,
            "category_per_class": self.category_samples_per_class,
            "query_per_class": self.query_samples_per_class,
            "non_financial": self.non_financial_samples,
            "total_estimated": (
                self.intent_samples_per_class * 4 +  # 4 intent classes
                self.category_samples_per_class * 15 +  # ~15 category classes
                self.query_samples_per_class * 6 +  # 6 query types
                self.non_financial_samples
            )
        }
    
    def get_class_labels(self) -> Dict[str, List[str]]:
        """Get class labels for each model"""
        return {
            "intent": [
                "income",
                "expense", 
                "savings_goal",
                "non_financial"
            ],
            "category": [
                # Income categories
                "Uang Saku/Kiriman Ortu",
                "Part-time Job",
                "Freelance/Project", 
                "Beasiswa",
                "Bisnis/Jualan",
                "Hadiah/Bonus",
                
                # Expense categories - NEEDS
                "Kos/Tempat Tinggal",
                "Makanan Pokok",
                "Transportasi Wajib",
                "Pendidikan",
                "Internet & Komunikasi",
                "Kesehatan & Kebersihan",
                
                # Expense categories - WANTS
                "Jajan & Snack",
                "Hiburan & Sosial", 
                "Fashion & Beauty",
                "Shopping Online",
                "Organisasi & Event",
                "Hobi & Olahraga",
                
                # Savings categories
                "Tabungan Umum",
                "Investasi",
                "Dana Darurat"
            ],
            "query": [
                "total_savings_query",
                "budget_performance_query", 
                "expense_analysis_query",
                "savings_progress_query",
                "financial_health_query",
                "purchase_advice_query",
                "non_query"
            ]
        }
    
    def validate_config(self) -> bool:
        """Validate configuration settings"""
        try:
            # Check required directories can be created
            Path(self.output_dir).mkdir(parents=True, exist_ok=True)
            Path(self.data_dir).mkdir(parents=True, exist_ok=True)
            
            # Validate sample counts
            if self.intent_samples_per_class < 100:
                raise ValueError("Intent samples too low (min 100)")
            
            if self.non_financial_samples < self.intent_samples_per_class:
                raise ValueError("Non-financial samples should be >= intent samples")
            
            # Validate training parameters
            if not 0 < self.learning_rate < 1:
                raise ValueError("Learning rate must be between 0 and 1")
            
            if self.num_train_epochs < 1:
                raise ValueError("Must have at least 1 training epoch")
            
            return True
            
        except Exception as e:
            print(f"❌ Configuration validation failed: {e}")
            return False
    
    def summary(self) -> str:
        """Get configuration summary"""
        distribution = self.get_sample_distribution()
        
        return f"""
🔧 TRAINING CONFIGURATION SUMMARY
{'='*50}
📦 Model: {self.base_model}
📁 Output: {self.output_dir}

📊 DATASET DISTRIBUTION:
• Intent per class: {distribution['intent_per_class']:,}
• Category per class: {distribution['category_per_class']:,}  
• Query per class: {distribution['query_per_class']:,}
• Non-financial: {distribution['non_financial']:,}
• Total estimated: {distribution['total_estimated']:,}

🎯 TRAINING PARAMETERS:
• Epochs: {self.num_train_epochs}
• Batch size: {self.train_batch_size}
• Learning rate: {self.learning_rate}
• Early stopping: {self.use_early_stopping}

⚖️ BALANCE FEATURES:
• Data augmentation: {self.use_augmentation}
• Class weights: {self.use_class_weights}
• Validation size: {self.test_size:.1%}
{'='*50}
"""

# Preset configurations
TRAINING_PRESETS = {
    "default": TrainingConfig(),
    "balanced": TrainingConfig("balanced"),
    "aggressive": TrainingConfig("aggressive"), 
    "conservative": TrainingConfig("conservative")
}