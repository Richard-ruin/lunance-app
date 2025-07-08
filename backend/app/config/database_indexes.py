# app/config/database_indexes.py
"""Database indexes configuration for optimal performance with conflict resolution."""

from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo import IndexModel, ASCENDING, DESCENDING, TEXT
from pymongo.errors import OperationFailure
import logging

logger = logging.getLogger(__name__)


async def create_all_indexes(database: AsyncIOMotorDatabase):
    """Create all database indexes for optimal performance."""
    try:
        logger.info("Creating database indexes...")
        
        # User collection indexes
        await create_user_indexes(database)
        
        # University collection indexes
        await create_university_indexes(database)
        
        # Category collection indexes
        await create_category_indexes(database)
        
        # Transaction collection indexes
        await create_transaction_indexes(database)
        
        # Savings target collection indexes
        await create_savings_target_indexes(database)
        
        # University request collection indexes
        await create_university_request_indexes(database)
        
        # OTP verification collection indexes (with conflict resolution)
        await create_otp_verification_indexes(database)
        
        logger.info("All database indexes created successfully!")
        
    except Exception as e:
        logger.error(f"Error creating indexes: {e}")
        # Don't raise here to allow app to start even if indexes fail
        logger.warning("Continuing startup despite index creation issues...")


async def create_indexes_safely(collection, indexes, collection_name):
    """
    Create indexes safely with conflict resolution.
    
    Args:
        collection: MongoDB collection
        indexes: List of IndexModel objects
        collection_name: Name of collection for logging
    """
    for index in indexes:
        try:
            await collection.create_index(
                index.document["key"],
                **{k: v for k, v in index.document.items() if k != "key"}
            )
        except OperationFailure as e:
            if e.code == 85:  # IndexOptionsConflict
                logger.warning(f"Index conflict in {collection_name}: {e}")
                # Try to drop and recreate the conflicting index
                try:
                    index_name = index.document.get("name")
                    if index_name:
                        await collection.drop_index(index_name)
                        logger.info(f"Dropped conflicting index: {index_name}")
                        # Recreate the index
                        await collection.create_index(
                            index.document["key"],
                            **{k: v for k, v in index.document.items() if k != "key"}
                        )
                        logger.info(f"Recreated index: {index_name}")
                except Exception as drop_error:
                    logger.error(f"Failed to resolve index conflict for {index_name}: {drop_error}")
            else:
                logger.error(f"Failed to create index in {collection_name}: {e}")
        except Exception as e:
            logger.error(f"Unexpected error creating index in {collection_name}: {e}")


async def create_user_indexes(database: AsyncIOMotorDatabase):
    """Create indexes for users collection."""
    collection = database.users
    
    indexes = [
        # Unique indexes
        IndexModel([("email", ASCENDING)], unique=True, name="email_unique"),
        
        # Query optimization indexes
        IndexModel([("role", ASCENDING)], name="role_index"),
        IndexModel([("is_active", ASCENDING)], name="is_active_index"),
        IndexModel([("is_verified", ASCENDING)], name="is_verified_index"),
        IndexModel([("university_id", ASCENDING)], name="university_id_index"),
        IndexModel([("faculty_id", ASCENDING)], name="faculty_id_index"),
        IndexModel([("major_id", ASCENDING)], name="major_id_index"),
        
        # Timestamp indexes
        IndexModel([("created_at", DESCENDING)], name="created_at_desc"),
        IndexModel([("updated_at", DESCENDING)], name="updated_at_desc"),
        
        # Compound indexes
        IndexModel([
            ("university_id", ASCENDING),
            ("faculty_id", ASCENDING),
            ("major_id", ASCENDING)
        ], name="university_hierarchy_index"),
        
        IndexModel([
            ("role", ASCENDING),
            ("is_active", ASCENDING)
        ], name="role_active_index"),
        
        # Text search index
        IndexModel([
            ("full_name", TEXT),
            ("email", TEXT)
        ], name="user_text_search"),
    ]
    
    await create_indexes_safely(collection, indexes, "users")
    logger.info("User indexes created successfully")


async def create_university_indexes(database: AsyncIOMotorDatabase):
    """Create indexes for universities collection."""
    collection = database.universities
    
    indexes = [
        # Unique indexes
        IndexModel([("name", ASCENDING)], unique=True, name="university_name_unique"),
        
        # Query optimization indexes
        IndexModel([("is_active", ASCENDING)], name="univ_is_active_index"),
        IndexModel([("created_at", DESCENDING)], name="univ_created_at_desc"),
        IndexModel([("updated_at", DESCENDING)], name="univ_updated_at_desc"),
        
        # Faculty and major indexes (for nested documents)
        IndexModel([("faculties.name", ASCENDING)], name="faculty_name_index"),
        IndexModel([("faculties.majors.name", ASCENDING)], name="major_name_index"),
        
        # Text search index
        IndexModel([
            ("name", TEXT),
            ("faculties.name", TEXT),
            ("faculties.majors.name", TEXT)
        ], name="university_text_search"),
    ]
    
    await create_indexes_safely(collection, indexes, "universities")
    logger.info("University indexes created successfully")


async def create_category_indexes(database: AsyncIOMotorDatabase):
    """Create indexes for categories collection."""
    collection = database.categories
    
    indexes = [
        # Query optimization indexes
        IndexModel([("is_global", ASCENDING)], name="cat_is_global_index"),
        IndexModel([("user_id", ASCENDING)], name="cat_user_id_index"),
        IndexModel([("name", ASCENDING)], name="cat_name_index"),
        
        # Timestamp indexes
        IndexModel([("created_at", DESCENDING)], name="cat_created_at_desc"),
        IndexModel([("updated_at", DESCENDING)], name="cat_updated_at_desc"),
        
        # Compound indexes
        IndexModel([
            ("user_id", ASCENDING),
            ("is_global", ASCENDING)
        ], name="user_global_index"),
        
        IndexModel([
            ("is_global", ASCENDING),
            ("name", ASCENDING)
        ], name="global_name_index"),
        
        # Text search index
        IndexModel([("name", TEXT)], name="category_text_search"),
    ]
    
    await create_indexes_safely(collection, indexes, "categories")
    logger.info("Category indexes created successfully")


async def create_transaction_indexes(database: AsyncIOMotorDatabase):
    """Create indexes for transactions collection."""
    collection = database.transactions
    
    indexes = [
        # Primary query indexes
        IndexModel([("user_id", ASCENDING)], name="trans_user_id_index"),
        IndexModel([("category_id", ASCENDING)], name="trans_category_id_index"),
        IndexModel([("type", ASCENDING)], name="trans_type_index"),
        IndexModel([("date", DESCENDING)], name="trans_date_desc"),
        IndexModel([("amount", DESCENDING)], name="trans_amount_desc"),
        
        # Timestamp indexes
        IndexModel([("created_at", DESCENDING)], name="trans_created_at_desc"),
        IndexModel([("updated_at", DESCENDING)], name="trans_updated_at_desc"),
        
        # Compound indexes for common queries
        IndexModel([
            ("user_id", ASCENDING),
            ("date", DESCENDING)
        ], name="user_date_index"),
        
        IndexModel([
            ("user_id", ASCENDING),
            ("type", ASCENDING),
            ("date", DESCENDING)
        ], name="user_type_date_index"),
        
        IndexModel([
            ("user_id", ASCENDING),
            ("category_id", ASCENDING),
            ("date", DESCENDING)
        ], name="user_category_date_index"),
        
        IndexModel([
            ("user_id", ASCENDING),
            ("created_at", DESCENDING)
        ], name="trans_user_created_index"),
        
        # Range query optimization
        IndexModel([
            ("user_id", ASCENDING),
            ("date", ASCENDING),
            ("amount", ASCENDING)
        ], name="user_date_amount_index"),
        
        # Text search index
        IndexModel([("description", TEXT)], name="description_text_search"),
        
        # Analytics indexes
        IndexModel([
            ("date", ASCENDING),
            ("type", ASCENDING),
            ("amount", ASCENDING)
        ], name="analytics_index"),
    ]
    
    await create_indexes_safely(collection, indexes, "transactions")
    logger.info("Transaction indexes created successfully")


async def create_savings_target_indexes(database: AsyncIOMotorDatabase):
    """Create indexes for savings_targets collection."""
    collection = database.savings_targets
    
    indexes = [
        # Primary query indexes
        IndexModel([("user_id", ASCENDING)], name="sav_user_id_index"),
        IndexModel([("is_achieved", ASCENDING)], name="sav_is_achieved_index"),
        IndexModel([("target_date", ASCENDING)], name="sav_target_date_asc"),
        IndexModel([("target_amount", DESCENDING)], name="sav_target_amount_desc"),
        IndexModel([("current_amount", DESCENDING)], name="sav_current_amount_desc"),
        
        # Timestamp indexes
        IndexModel([("created_at", DESCENDING)], name="sav_created_at_desc"),
        IndexModel([("updated_at", DESCENDING)], name="sav_updated_at_desc"),
        
        # Compound indexes
        IndexModel([
            ("user_id", ASCENDING),
            ("is_achieved", ASCENDING)
        ], name="sav_user_achieved_index"),
        
        IndexModel([
            ("user_id", ASCENDING),
            ("target_date", ASCENDING)
        ], name="sav_user_target_date_index"),
        
        IndexModel([
            ("user_id", ASCENDING),
            ("created_at", DESCENDING)
        ], name="sav_user_created_index"),
        
        # Text search index
        IndexModel([("target_name", TEXT)], name="target_name_text_search"),
    ]
    
    await create_indexes_safely(collection, indexes, "savings_targets")
    logger.info("Savings target indexes created successfully")


async def create_university_request_indexes(database: AsyncIOMotorDatabase):
    """Create indexes for university_requests collection."""
    collection = database.university_requests
    
    indexes = [
        # Primary query indexes
        IndexModel([("user_id", ASCENDING)], name="req_user_id_index"),
        IndexModel([("status", ASCENDING)], name="req_status_index"),
        
        # Timestamp indexes
        IndexModel([("created_at", DESCENDING)], name="req_created_at_desc"),
        IndexModel([("updated_at", DESCENDING)], name="req_updated_at_desc"),
        
        # Compound indexes
        IndexModel([
            ("status", ASCENDING),
            ("created_at", DESCENDING)
        ], name="req_status_created_index"),
        
        IndexModel([
            ("user_id", ASCENDING),
            ("status", ASCENDING)
        ], name="req_user_status_index"),
        
        # Text search index
        IndexModel([
            ("university_name", TEXT),
            ("faculty_name", TEXT),
            ("major_name", TEXT)
        ], name="request_text_search"),
        
        # Analytics indexes
        IndexModel([
            ("university_name", ASCENDING),
            ("faculty_name", ASCENDING),
            ("major_name", ASCENDING)
        ], name="hierarchy_analytics_index"),
    ]
    
    await create_indexes_safely(collection, indexes, "university_requests")
    logger.info("University request indexes created successfully")


async def create_otp_verification_indexes(database: AsyncIOMotorDatabase):
    """Create indexes for otp_verifications collection with conflict resolution."""
    collection = database.otp_verifications
    
    # First, check for existing conflicting indexes and drop them
    try:
        existing_indexes = await collection.list_indexes().to_list(length=None)
        conflicting_indexes = []
        
        for index in existing_indexes:
            index_name = index.get("name", "")
            index_key = index.get("key", {})
            
            # Check for conflicting expires_at indexes
            if "expires_at" in index_key and index_name != "otp_expiry_ttl":
                conflicting_indexes.append(index_name)
        
        # Drop conflicting indexes
        for index_name in conflicting_indexes:
            if index_name != "_id_":  # Never drop the _id index
                try:
                    await collection.drop_index(index_name)
                    logger.info(f"Dropped conflicting OTP index: {index_name}")
                except Exception as e:
                    logger.warning(f"Could not drop index {index_name}: {e}")
    
    except Exception as e:
        logger.warning(f"Error checking existing OTP indexes: {e}")
    
    # Now create the indexes
    indexes = [
        # Primary query indexes
        IndexModel([("email", ASCENDING)], name="otp_email_index"),
        IndexModel([("otp_type", ASCENDING)], name="otp_type_index"),
        IndexModel([("is_used", ASCENDING)], name="otp_is_used_index"),
        
        # Compound indexes for common queries
        IndexModel([
            ("email", ASCENDING),
            ("otp_type", ASCENDING),
            ("is_used", ASCENDING)
        ], name="email_type_used_index"),
        
        IndexModel([
            ("email", ASCENDING),
            ("otp_code", ASCENDING),
            ("otp_type", ASCENDING)
        ], name="otp_verification_index"),
        
        # Timestamp indexes
        IndexModel([("created_at", DESCENDING)], name="otp_created_at_desc"),
        
        # TTL index for automatic cleanup of expired OTPs
        # This is the critical index that was causing conflicts
        IndexModel([("expires_at", ASCENDING)], 
                  expireAfterSeconds=3600, 
                  name="otp_expiry_ttl"),
    ]
    
    await create_indexes_safely(collection, indexes, "otp_verifications")
    logger.info("OTP verification indexes created successfully")


async def create_savings_target_history_indexes(database: AsyncIOMotorDatabase):
    """Create indexes for savings_target_history collection."""
    collection = database.savings_target_history
    
    indexes = [
        # Primary query indexes
        IndexModel([("savings_target_id", ASCENDING)], name="hist_savings_target_id_index"),
        IndexModel([("action_type", ASCENDING)], name="hist_action_type_index"),
        
        # Timestamp indexes
        IndexModel([("created_at", DESCENDING)], name="hist_created_at_desc"),
        
        # Compound indexes
        IndexModel([
            ("savings_target_id", ASCENDING),
            ("created_at", DESCENDING)
        ], name="target_history_index"),
        
        IndexModel([
            ("savings_target_id", ASCENDING),
            ("action_type", ASCENDING),
            ("created_at", DESCENDING)
        ], name="target_action_history_index"),
    ]
    
    await create_indexes_safely(collection, indexes, "savings_target_history")
    logger.info("Savings target history indexes created successfully")


# Index maintenance functions
async def drop_all_indexes(database: AsyncIOMotorDatabase):
    """Drop all custom indexes (except _id)."""
    collections = [
        "users", "universities", "categories", "transactions",
        "savings_targets", "university_requests", "otp_verifications",
        "savings_target_history"
    ]
    
    for collection_name in collections:
        collection = database[collection_name]
        try:
            # Get all indexes except _id_
            indexes = await collection.list_indexes().to_list(length=None)
            for index in indexes:
                if index["name"] != "_id_":
                    await collection.drop_index(index["name"])
            logger.info(f"Dropped indexes for {collection_name}")
        except Exception as e:
            logger.warning(f"Error dropping indexes for {collection_name}: {e}")


async def rebuild_indexes(database: AsyncIOMotorDatabase):
    """Rebuild all indexes."""
    logger.info("Rebuilding all database indexes...")
    await drop_all_indexes(database)
    await create_all_indexes(database)
    logger.info("All indexes rebuilt successfully!")


async def check_index_conflicts(database: AsyncIOMotorDatabase):
    """Check for potential index conflicts."""
    logger.info("Checking for index conflicts...")
    
    collection = database.otp_verifications
    try:
        indexes = await collection.list_indexes().to_list(length=None)
        expires_at_indexes = []
        
        for index in indexes:
            if "expires_at" in index.get("key", {}):
                expires_at_indexes.append({
                    "name": index.get("name"),
                    "key": index.get("key"),
                    "expireAfterSeconds": index.get("expireAfterSeconds")
                })
        
        if len(expires_at_indexes) > 1:
            logger.warning(f"Multiple expires_at indexes found: {expires_at_indexes}")
            return True
        
        logger.info("No index conflicts detected")
        return False
        
    except Exception as e:
        logger.error(f"Error checking index conflicts: {e}")
        return False