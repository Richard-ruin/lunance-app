# scripts/seed_categories.py
import asyncio
import json
import os
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
from app.config.settings import settings


async def seed_default_categories():
    """Seed default student categories to MongoDB"""
    
    # Connect to MongoDB
    client = AsyncIOMotorClient(settings.DATABASE_URL)
    db = client[settings.DATABASE_NAME]
    categories_collection = db.categories
    
    # Load categories data
    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_file = os.path.join(current_dir, "..", "data", "student_categories.json")
    
    with open(data_file, 'r', encoding='utf-8') as f:
        categories_data = json.load(f)
    
    # Prepare categories for insertion
    all_categories = []
    
    # Process income categories
    for cat in categories_data["income_categories"]:
        cat["created_at"] = datetime.utcnow()
        all_categories.append(cat)
    
    # Process expense categories
    for cat in categories_data["expense_categories"]:
        cat["created_at"] = datetime.utcnow()
        all_categories.append(cat)
    
    # Check if categories already exist
    existing_count = await categories_collection.count_documents({"is_system": True})
    
    if existing_count > 0:
        print(f"Found {existing_count} existing system categories. Skipping seed.")
        return
    
    # Insert categories
    try:
        result = await categories_collection.insert_many(all_categories)
        print(f"Successfully seeded {len(result.inserted_ids)} default categories!")
        
        # Print summary
        income_count = len(categories_data["income_categories"])
        expense_count = len(categories_data["expense_categories"])
        print(f"- Income categories: {income_count}")
        print(f"- Expense categories: {expense_count}")
        
    except Exception as e:
        print(f"Error seeding categories: {e}")
    
    finally:
        client.close()


if __name__ == "__main__":
    asyncio.run(seed_default_categories())