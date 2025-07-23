# scripts/train/model_trainer.py - ADVANCED MODEL TRAINER
import os
import json
import logging
import numpy as np
import pandas as pd
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score, f1_score
from sklearn.utils.class_weight import compute_class_weight

logger = logging.getLogger(__name__)

# Check and import required packages
def check_training_dependencies():
    """Check if training dependencies are available"""
    required_packages = {
        'torch': 'torch',
        'transformers': 'transformers',
        'datasets': 'datasets',
        'sklearn': 'scikit-learn'
    }
    
    missing = []
    for package, pip_name in required_packages.items():
        try:
            __import__(package)
        except ImportError:
            missing.append(pip_name)
    
    if missing:
        logger.error(f"Missing packages: {missing}")
        logger.error(f"Install with: pip install {' '.join(missing)}")
        return False
    return True

if check_training_dependencies():
    import torch
    from transformers import (
        AutoTokenizer, AutoModelForSequenceClassification,
        TrainingArguments, Trainer, EarlyStoppingCallback,
        DataCollatorWithPadding
    )
    from datasets import Dataset
    logger.info(f"🚀 Training dependencies loaded. PyTorch: {torch.__version__}")
else:
    logger.error("❌ Training dependencies not available")
    exit(1)

class ModelTrainer:
    """
    Advanced model trainer with balanced approach and multiple classifiers
    """
    
    def __init__(self, config):
        self.config = config
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        logger.info(f"🔧 Using device: {self.device}")
        
        # Setup random seeds for reproducibility
        self._set_seeds(self.config.validation_seed)
    
    def _set_seeds(self, seed: int):
        """Set random seeds for reproducibility"""
        import random
        random.seed(seed)
        np.random.seed(seed)
        torch.manual_seed(seed)
        if torch.cuda.is_available():
            torch.cuda.manual_seed_all(seed)
        logger.info(f"🎲 Random seeds set to {seed}")
    
    def train_all_models(self) -> Dict[str, Any]:
        """Train all models with advanced configuration"""
        logger.info("🚀 Starting advanced model training pipeline...")
        
        results = {}
        start_time = datetime.now()
        
        try:
            # Train Intent Classifier
            logger.info("\n" + "🎯" * 20)
            logger.info("TRAINING INTENT CLASSIFIER")
            logger.info("🎯" * 20)
            
            intent_results = self.train_intent_classifier()
            results["intent_classifier"] = intent_results
            
            # Train Category Classifier
            logger.info("\n" + "🏷️" * 20)
            logger.info("TRAINING CATEGORY CLASSIFIER")
            logger.info("🏷️" * 20)
            
            category_results = self.train_category_classifier()
            results["category_classifier"] = category_results
            
            # Train Query Classifier - NEW
            logger.info("\n" + "❓" * 20)
            logger.info("TRAINING QUERY CLASSIFIER")
            logger.info("❓" * 20)
            
            query_results = self.train_query_classifier()
            results["query_classifier"] = query_results
            
            # Generate training summary
            end_time = datetime.now()
            duration = end_time - start_time
            
            summary = self._generate_training_summary(results, start_time, end_time, duration)
            self._save_training_summary(summary)
            
            logger.info("\n🎉 TRAINING PIPELINE COMPLETED SUCCESSFULLY!")
            logger.info(f"⏱️ Total duration: {duration}")
            logger.info(f"📍 Models saved to: {self.config.output_dir}")
            
            return results
            
        except Exception as e:
            logger.error(f"❌ Training pipeline failed: {e}")
            import traceback
            traceback.print_exc()
            raise
    
    def train_intent_classifier(self) -> Dict[str, Any]:
        """Train intent classifier with balanced approach"""
        try:
            # Load dataset
            dataset_path = os.path.join(self.config.data_dir, "intent_dataset.json")
            with open(dataset_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            df = pd.DataFrame(data)
            logger.info(f"📊 Intent dataset loaded: {len(df)} samples")
            
            # Analyze class distribution
            class_counts = df['label'].value_counts()
            logger.info("📈 Intent class distribution:")
            for label, count in class_counts.items():
                logger.info(f"  {label}: {count} samples ({count/len(df)*100:.1f}%)")
            
            # Create label mappings
            unique_labels = sorted(df['label'].unique())
            label2id = {label: i for i, label in enumerate(unique_labels)}
            id2label = {i: label for label, i in label2id.items()}
            
            # Prepare data
            texts = df['text'].tolist()
            labels = [label2id[label] for label in df['label']]
            
            # Balanced train-test split
            train_texts, val_texts, train_labels, val_labels = train_test_split(
                texts, labels,
                test_size=self.config.test_size,
                random_state=self.config.validation_seed,
                stratify=labels
            )
            
            logger.info(f"📊 Train: {len(train_texts)}, Validation: {len(val_texts)}")
            
            # Calculate class weights for balanced training
            class_weights = None
            if self.config.use_class_weights:
                class_weights = compute_class_weight(
                    'balanced',
                    classes=np.unique(train_labels),
                    y=train_labels
                )
                logger.info(f"⚖️ Class weights: {dict(zip(unique_labels, class_weights))}")
            
            # Load model and tokenizer
            tokenizer = AutoTokenizer.from_pretrained(self.config.base_model)
            model = AutoModelForSequenceClassification.from_pretrained(
                self.config.base_model,
                num_labels=len(unique_labels),
                label2id=label2id,
                id2label=id2label,
                problem_type="single_label_classification"
            )
            
            # Tokenize datasets
            train_dataset = self._create_dataset(train_texts, train_labels, tokenizer)
            val_dataset = self._create_dataset(val_texts, val_labels, tokenizer)
            
            # Training arguments
            training_args = self._create_training_args(
                self.config.intent_model_dir,
                "intent_classifier"
            )
            
            # Data collator
            data_collator = DataCollatorWithPadding(
                tokenizer=tokenizer,
                padding=True,
                return_tensors="pt"
            )
            
            # Compute metrics function
            def compute_metrics(eval_pred):
                predictions, labels = eval_pred
                predictions = np.argmax(predictions, axis=1)
                
                accuracy = accuracy_score(labels, predictions)
                f1_macro = f1_score(labels, predictions, average='macro')
                f1_weighted = f1_score(labels, predictions, average='weighted')
                
                report = classification_report(labels, predictions, output_dict=True, zero_division=0)
                
                return {
                    "accuracy": accuracy,
                    "f1_macro": f1_macro,
                    "f1_weighted": f1_weighted,
                    "precision_macro": report['macro avg']['precision'],
                    "recall_macro": report['macro avg']['recall']
                }
            
            # Create trainer
            trainer = Trainer(
                model=model,
                args=training_args,
                train_dataset=train_dataset,
                eval_dataset=val_dataset,
                tokenizer=tokenizer,
                data_collator=data_collator,
                compute_metrics=compute_metrics,
                callbacks=[EarlyStoppingCallback(early_stopping_patience=self.config.patience)]
            )
            
            # Train model
            logger.info("🚀 Starting intent classifier training...")
            train_result = trainer.train()
            
            # Evaluate model
            eval_result = trainer.evaluate()
            logger.info("📊 Intent classifier evaluation:")
            for key, value in eval_result.items():
                logger.info(f"  {key}: {value:.4f}")
            
            # Save model
            logger.info(f"💾 Saving intent classifier to {self.config.intent_model_dir}")
            trainer.save_model()
            tokenizer.save_pretrained(self.config.intent_model_dir)
            
            # Save metadata
            metadata = {
                "model_info": {
                    "model_type": "intent_classifier",
                    "base_model": self.config.base_model,
                    "num_labels": len(unique_labels),
                    "labels": unique_labels,
                    "training_samples": len(train_texts),
                    "validation_samples": len(val_texts)
                },
                "training_config": {
                    "epochs": self.config.num_train_epochs,
                    "batch_size": self.config.train_batch_size,
                    "learning_rate": self.config.learning_rate,
                    "warmup_steps": self.config.warmup_steps,
                    "use_class_weights": self.config.use_class_weights,
                    "early_stopping": self.config.use_early_stopping
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
            
            metadata_path = os.path.join(self.config.intent_model_dir, "model_metadata.json")
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
            
            logger.info("✅ Intent classifier training completed!")
            return eval_result
            
        except Exception as e:
            logger.error(f"❌ Intent classifier training failed: {e}")
            raise
    
    def train_category_classifier(self) -> Dict[str, Any]:
        """Train category classifier"""
        try:
            # Load dataset
            dataset_path = os.path.join(self.config.data_dir, "category_dataset.json")
            with open(dataset_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            df = pd.DataFrame(data)
            logger.info(f"📊 Category dataset loaded: {len(df)} samples")
            
            # Analyze class distribution
            class_counts = df['label'].value_counts()
            logger.info(f"📈 Category classes: {len(class_counts)} categories")
            
            # Create label mappings
            unique_labels = sorted(df['label'].unique())
            label2id = {label: i for i, label in enumerate(unique_labels)}
            id2label = {i: label for label, i in label2id.items()}
            
            # Prepare data
            texts = df['text'].tolist()
            labels = [label2id[label] for label in df['label']]
            
            # Split data
            train_texts, val_texts, train_labels, val_labels = train_test_split(
                texts, labels,
                test_size=self.config.test_size,
                random_state=self.config.validation_seed,
                stratify=labels
            )
            
            logger.info(f"📊 Train: {len(train_texts)}, Validation: {len(val_texts)}")
            
            # Load model and tokenizer
            tokenizer = AutoTokenizer.from_pretrained(self.config.base_model)
            model = AutoModelForSequenceClassification.from_pretrained(
                self.config.base_model,
                num_labels=len(unique_labels),
                label2id=label2id,
                id2label=id2label
            )
            
            # Create datasets
            train_dataset = self._create_dataset(train_texts, train_labels, tokenizer)
            val_dataset = self._create_dataset(val_texts, val_labels, tokenizer)
            
            # Training arguments
            training_args = self._create_training_args(
                self.config.category_model_dir,
                "category_classifier"
            )
            
            # Data collator
            data_collator = DataCollatorWithPadding(
                tokenizer=tokenizer,
                padding=True,
                return_tensors="pt"
            )
            
            # Compute metrics
            def compute_metrics(eval_pred):
                predictions, labels = eval_pred
                predictions = np.argmax(predictions, axis=1)
                
                accuracy = accuracy_score(labels, predictions)
                f1_macro = f1_score(labels, predictions, average='macro')
                f1_weighted = f1_score(labels, predictions, average='weighted')
                
                return {
                    "accuracy": accuracy,
                    "f1_macro": f1_macro,
                    "f1_weighted": f1_weighted
                }
            
            # Create trainer
            trainer = Trainer(
                model=model,
                args=training_args,
                train_dataset=train_dataset,
                eval_dataset=val_dataset,
                tokenizer=tokenizer,
                data_collator=data_collator,
                compute_metrics=compute_metrics,
                callbacks=[EarlyStoppingCallback(early_stopping_patience=self.config.patience)]
            )
            
            # Train
            logger.info("🚀 Starting category classifier training...")
            train_result = trainer.train()
            
            # Evaluate
            eval_result = trainer.evaluate()
            logger.info("📊 Category classifier evaluation:")
            for key, value in eval_result.items():
                logger.info(f"  {key}: {value:.4f}")
            
            # Save model
            logger.info(f"💾 Saving category classifier to {self.config.category_model_dir}")
            trainer.save_model()
            tokenizer.save_pretrained(self.config.category_model_dir)
            
            # Save metadata
            metadata = {
                "model_info": {
                    "model_type": "category_classifier",
                    "base_model": self.config.base_model,
                    "num_labels": len(unique_labels),
                    "training_samples": len(train_texts),
                    "validation_samples": len(val_texts)
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
            
            metadata_path = os.path.join(self.config.category_model_dir, "model_metadata.json")
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
            
            logger.info("✅ Category classifier training completed!")
            return eval_result
            
        except Exception as e:
            logger.error(f"❌ Category classifier training failed: {e}")
            raise
    
    def train_query_classifier(self) -> Dict[str, Any]:
        """Train query classifier - NEW FEATURE"""
        try:
            # Load dataset
            dataset_path = os.path.join(self.config.data_dir, "query_dataset.json")
            with open(dataset_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            df = pd.DataFrame(data)
            logger.info(f"📊 Query dataset loaded: {len(df)} samples")
            
            # Analyze class distribution
            class_counts = df['label'].value_counts()
            logger.info("📈 Query class distribution:")
            for label, count in class_counts.items():
                logger.info(f"  {label}: {count} samples")
            
            # Create label mappings
            unique_labels = sorted(df['label'].unique())
            label2id = {label: i for i, label in enumerate(unique_labels)}
            id2label = {i: label for label, i in label2id.items()}
            
            # Prepare data
            texts = df['text'].tolist()
            labels = [label2id[label] for label in df['label']]
            
            # Split data
            train_texts, val_texts, train_labels, val_labels = train_test_split(
                texts, labels,
                test_size=self.config.test_size,
                random_state=self.config.validation_seed,
                stratify=labels
            )
            
            logger.info(f"📊 Train: {len(train_texts)}, Validation: {len(val_texts)}")
            
            # Load model and tokenizer
            tokenizer = AutoTokenizer.from_pretrained(self.config.base_model)
            model = AutoModelForSequenceClassification.from_pretrained(
                self.config.base_model,
                num_labels=len(unique_labels),
                label2id=label2id,
                id2label=id2label
            )
            
            # Create datasets
            train_dataset = self._create_dataset(train_texts, train_labels, tokenizer)
            val_dataset = self._create_dataset(val_texts, val_labels, tokenizer)
            
            # Training arguments
            training_args = self._create_training_args(
                self.config.query_model_dir,
                "query_classifier"
            )
            
            # Data collator
            data_collator = DataCollatorWithPadding(
                tokenizer=tokenizer,
                padding=True,
                return_tensors="pt"
            )
            
            # Compute metrics
            def compute_metrics(eval_pred):
                predictions, labels = eval_pred
                predictions = np.argmax(predictions, axis=1)
                
                accuracy = accuracy_score(labels, predictions)
                f1_macro = f1_score(labels, predictions, average='macro')
                
                return {
                    "accuracy": accuracy,
                    "f1_macro": f1_macro
                }
            
            # Create trainer
            trainer = Trainer(
                model=model,
                args=training_args,
                train_dataset=train_dataset,
                eval_dataset=val_dataset,
                tokenizer=tokenizer,
                data_collator=data_collator,
                compute_metrics=compute_metrics,
                callbacks=[EarlyStoppingCallback(early_stopping_patience=self.config.patience)]
            )
            
            # Train
            logger.info("🚀 Starting query classifier training...")
            train_result = trainer.train()
            
            # Evaluate
            eval_result = trainer.evaluate()
            logger.info("📊 Query classifier evaluation:")
            for key, value in eval_result.items():
                logger.info(f"  {key}: {value:.4f}")
            
            # Save model
            logger.info(f"💾 Saving query classifier to {self.config.query_model_dir}")
            trainer.save_model()
            tokenizer.save_pretrained(self.config.query_model_dir)
            
            # Save metadata
            metadata = {
                "model_info": {
                    "model_type": "query_classifier",
                    "base_model": self.config.base_model,
                    "num_labels": len(unique_labels),
                    "training_samples": len(train_texts),
                    "validation_samples": len(val_texts)
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
            
            metadata_path = os.path.join(self.config.query_model_dir, "model_metadata.json")
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
            
            logger.info("✅ Query classifier training completed!")
            return eval_result
            
        except Exception as e:
            logger.error(f"❌ Query classifier training failed: {e}")
            raise
    
    def _create_dataset(self, texts: List[str], labels: List[int], tokenizer) -> Dataset:
        """Create tokenized dataset"""
        def tokenize_function(examples):
            return tokenizer(
                examples["text"],
                truncation=True,
                padding=True,
                max_length=128,
                return_tensors="pt"
            )
        
        # Create dataset
        dataset = Dataset.from_dict({
            "text": texts,
            "labels": labels
        })
        
        # Tokenize
        dataset = dataset.map(
            tokenize_function,
            batched=True,
            remove_columns=["text"]
        )
        
        return dataset
    
    def _create_training_args(self, output_dir: str, model_type: str) -> TrainingArguments:
        """Create training arguments"""
        return TrainingArguments(
            output_dir=output_dir,
            
            # Training parameters
            num_train_epochs=self.config.num_train_epochs,
            per_device_train_batch_size=self.config.train_batch_size,
            per_device_eval_batch_size=self.config.eval_batch_size,
            gradient_accumulation_steps=1,
            
            # Learning rate
            learning_rate=self.config.learning_rate,
            weight_decay=0.01,
            warmup_steps=self.config.warmup_steps,
            lr_scheduler_type="linear",
            
            # Evaluation and saving
            eval_strategy="steps",
            eval_steps=200,
            save_strategy="steps",
            save_steps=200,
            save_total_limit=2,
            
            # Early stopping
            load_best_model_at_end=True,
            metric_for_best_model="eval_accuracy",
            greater_is_better=True,
            
            # Performance
            dataloader_num_workers=0,
            remove_unused_columns=True,
            fp16=False,  # Disable for stability
            
            # Logging
            logging_dir=f"{output_dir}/logs",
            logging_steps=50,
            report_to="none",
            
            # Optimization
            optim="adamw_torch",
            max_grad_norm=1.0,
            
            # Seeding
            seed=self.config.validation_seed,
            data_seed=self.config.validation_seed,
            
            # Additional stability
            dataloader_pin_memory=False,
            skip_memory_metrics=True,
        )
    
    def _generate_training_summary(self, results: Dict[str, Any], start_time: datetime, 
                                 end_time: datetime, duration) -> Dict[str, Any]:
        """Generate comprehensive training summary"""
        return {
            "training_info": {
                "started_at": start_time.isoformat(),
                "completed_at": end_time.isoformat(),
                "total_duration": str(duration),
                "duration_minutes": duration.total_seconds() / 60,
                "config_preset": "balanced",
                "base_model": self.config.base_model
            },
            "model_results": results,
            "model_paths": {
                "intent_classifier": self.config.intent_model_dir,
                "category_classifier": self.config.category_model_dir,
                "query_classifier": self.config.query_model_dir
            },
            "training_features": [
                "Balanced dataset generation",
                "Reduced financial detection bias",
                "Enhanced non-financial examples",
                "Query detection capability",
                "Class weight balancing",
                "Early stopping mechanism",
                "Stratified train-test split",
                "Advanced model configuration"
            ],
            "improvements_over_previous": [
                "Better balance between financial and non-financial",
                "Separate query detection model",
                "Reduced overfitting to financial patterns",
                "Enhanced conversation understanding",
                "More robust negative examples",
                "Improved category distribution"
            ],
            "performance_summary": {
                "intent_accuracy": results.get("intent_classifier", {}).get("eval_accuracy", 0),
                "category_accuracy": results.get("category_classifier", {}).get("eval_accuracy", 0),
                "query_accuracy": results.get("query_classifier", {}).get("eval_accuracy", 0),
                "average_accuracy": sum([
                    results.get("intent_classifier", {}).get("eval_accuracy", 0),
                    results.get("category_classifier", {}).get("eval_accuracy", 0),
                    results.get("query_classifier", {}).get("eval_accuracy", 0)
                ]) / 3
            },
            "next_steps": [
                "Test models with validation dataset",
                "Deploy to production environment", 
                "Monitor performance on real conversations",
                "Collect feedback for future improvements"
            ]
        }
    
    def _save_training_summary(self, summary: Dict[str, Any]):
        """Save training summary"""
        os.makedirs(self.config.output_dir, exist_ok=True)
        summary_path = os.path.join(self.config.output_dir, "training_summary.json")
        
        with open(summary_path, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        logger.info(f"💾 Training summary saved to {summary_path}")