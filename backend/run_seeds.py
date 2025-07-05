#!/usr/bin/env python3
"""
Script to run database seeds for Lunance API
"""
import asyncio
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from seeds.main import main

if __name__ == "__main__":
    print("Lunance Database Seeder")
    print("=" * 50)
    
    # Confirm before running
    confirm = input("This will clear existing data. Continue? (y/N): ")
    if confirm.lower() != 'y':
        print("Seeding cancelled.")
        sys.exit(0)
    
    asyncio.run(main())