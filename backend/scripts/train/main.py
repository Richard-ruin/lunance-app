# scripts/train/main.py - MAIN TRAINING ENTRY POINT
import os
import sys
import argparse
import logging
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from training_config import TrainingConfig
from dataset_generator import AdvancedDatasetGenerator
from model_trainer import ModelTrainer
from training_validator import TrainingValidator

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('training.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def main():
    """Main training orchestrator with balanced dataset generation"""
    
    print("🚀 LUNANCE AI TRAINING SYSTEM - ADVANCED VERSION")
    print("=" * 70)
    print("🎯 Objective: Balanced detection across all financial intents")
    print("🔧 Approach: Complex dataset with reduced bias")
    print("=" * 70)
    
    parser = argparse.ArgumentParser(description="Lunance AI Training System")
    parser.add_argument("--config", default="default", help="Training configuration preset")
    parser.add_argument("--dataset-only", action="store_true", help="Only generate datasets")
    parser.add_argument("--train-only", action="store_true", help="Only train models (skip dataset generation)")
    parser.add_argument("--validate-only", action="store_true", help="Only validate existing models")
    parser.add_argument("--output-dir", default="models/indoroberta-balanced", help="Output directory")
    parser.add_argument("--samples", type=int, default=2000, help="Samples per category")
    
    args = parser.parse_args()
    
    try:
        # Initialize configuration
        logger.info("📋 Loading training configuration...")
        config = TrainingConfig(preset=args.config)
        config.update_output_dir(args.output_dir)
        config.update_sample_counts(args.samples)
        
        # Phase 1: Dataset Generation
        if not args.train_only and not args.validate_only:
            logger.info("\n🔄 PHASE 1: ADVANCED DATASET GENERATION")
            logger.info("=" * 50)
            
            generator = AdvancedDatasetGenerator(config)
            dataset_info = generator.generate_all_datasets()
            
            logger.info("✅ Dataset generation completed!")
            logger.info(f"📊 Intent samples: {dataset_info['intent_samples']}")
            logger.info(f"📊 Category samples: {dataset_info['category_samples']}")
            logger.info(f"📊 Query samples: {dataset_info['query_samples']}")
            logger.info(f"📊 Non-financial samples: {dataset_info['non_financial_samples']}")
            
            if args.dataset_only:
                logger.info("🎯 Dataset-only mode complete!")
                return
        
        # Phase 2: Model Training
        if not args.validate_only:
            logger.info("\n🤖 PHASE 2: MODEL TRAINING")
            logger.info("=" * 50)
            
            trainer = ModelTrainer(config)
            training_results = trainer.train_all_models()
            
            logger.info("✅ Model training completed!")
            for model_type, results in training_results.items():
                accuracy = results.get('eval_accuracy', 0)
                logger.info(f"📊 {model_type} accuracy: {accuracy:.3f}")
        
        # Phase 3: Validation
        if not args.train_only:
            logger.info("\n✅ PHASE 3: MODEL VALIDATION")
            logger.info("=" * 50)
            
            validator = TrainingValidator(config)
            validation_results = validator.validate_all_models()
            
            logger.info("✅ Model validation completed!")
            logger.info(f"📊 Overall performance: {validation_results['overall_score']:.3f}")
        
        logger.info("\n🎉 TRAINING PIPELINE COMPLETED SUCCESSFULLY!")
        logger.info("=" * 70)
        logger.info(f"🎯 Models saved to: {args.output_dir}")
        logger.info("🚀 Ready for deployment!")
        
    except Exception as e:
        logger.error(f"❌ Training pipeline failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()