#!/usr/bin/env python3
# scripts/run_training.py - Simple training runner
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def main():
    print("Starting IndoBERT Financial Training...")
    print("Required dependencies:")
    print("   - torch>=1.9.0")
    print("   - transformers>=4.20.0")
    print("   - datasets>=2.0.0")
    print("   - scikit-learn>=1.0.0")
    print("")
    
    try:
        # Import training script
        from scripts.train_indobert_financial import main as train_main
        train_main()
    except ImportError as e:
        print(f"Import error: {e}")
        print("Make sure to install required dependencies:")
        print("   pip install torch transformers datasets scikit-learn")
    except Exception as e:
        print(f"Training error: {e}")

if __name__ == "__main__":
    main()
