import asyncio
from .utils.database import db
from .data.universities import generate_universities_data
from .data.users import generate_users_data
from .config import SEED_CONFIG

async def seed_universities():
    """Seed universities collection"""
    print("Seeding universities...")
    
    # Clear existing data
    await db.clear_collection("universities")
    
    # Generate and insert data
    universities_data = generate_universities_data()
    await db.insert_batch("universities", universities_data)
    
    # Get inserted universities for reference
    universities = await db.database.universities.find({}).to_list(length=None)
    print(f"Total universities in database: {len(universities)}")
    
    return universities

async def seed_users(universities, num_users=1000):
    """Seed users collection"""
    print(f"Seeding {num_users} users...")
    
    # Clear existing data
    await db.clear_collection("users")
    
    # Extract university IDs
    university_ids = [univ["_id"] for univ in universities]
    
    # Generate and insert data
    users_data = generate_users_data(university_ids, num_users)
    await db.insert_batch("users", users_data)
    
    print(f"Total users in database: {await db.get_collection_count('users')}")

async def main():
    """Main seeding function"""
    try:
        print("Starting database seeding...")
        await db.connect()
        
        # Seed universities first
        universities = await seed_universities()
        
        # Seed users with university references
        await seed_users(universities, num_users=1000)
        
        print("\n=== Seeding Summary ===")
        print(f"Universities: {await db.get_collection_count('universities')}")
        print(f"Users: {await db.get_collection_count('users')}")
        print("Seeding completed successfully!")
        
    except Exception as e:
        print(f"Error during seeding: {e}")
    finally:
        await db.disconnect()

if __name__ == "__main__":
    asyncio.run(main())