# Script untuk memperbaiki data yang sudah ada di database
# Jalankan script ini untuk menambahkan field yang missing

from pymongo import MongoClient
from datetime import datetime
import sys

def fix_database():
    """Fix existing database data with missing fields"""
    
    try:
        # Connect to MongoDB
        client = MongoClient("mongodb://localhost:27017")
        db = client["lunance_db"]
        
        print("🔧 Starting database fix...")
        
        # 1. Fix conversations collection
        print("\n1. Fixing conversations collection...")
        
        conversations_fixed = 0
        conversations = db.conversations.find({})
        
        for conv in conversations:
            update_fields = {}
            
            # Add missing created_at
            if "created_at" not in conv:
                update_fields["created_at"] = conv.get("updated_at", datetime.utcnow())
                print(f"   Adding created_at to conversation {conv['_id']}")
            
            # Add missing status
            if "status" not in conv:
                update_fields["status"] = "active"
                print(f"   Adding status to conversation {conv['_id']}")
            
            # Add missing updated_at
            if "updated_at" not in conv:
                update_fields["updated_at"] = datetime.utcnow()
                print(f"   Adding updated_at to conversation {conv['_id']}")
            
            # Add missing message_count
            if "message_count" not in conv:
                # Count actual messages for this conversation
                message_count = db.messages.count_documents({"conversation_id": str(conv["_id"])})
                update_fields["message_count"] = message_count
                print(f"   Adding message_count ({message_count}) to conversation {conv['_id']}")
            
            # Update conversation if needed
            if update_fields:
                db.conversations.update_one(
                    {"_id": conv["_id"]},
                    {"$set": update_fields}
                )
                conversations_fixed += 1
        
        print(f"✅ Fixed {conversations_fixed} conversations")
        
        # 2. Fix messages collection
        print("\n2. Fixing messages collection...")
        
        messages_fixed = 0
        messages = db.messages.find({})
        
        for msg in messages:
            update_fields = {}
            
            # Add missing timestamp
            if "timestamp" not in msg:
                update_fields["timestamp"] = datetime.utcnow()
                print(f"   Adding timestamp to message {msg['_id']}")
            
            # Add missing status
            if "status" not in msg:
                update_fields["status"] = "sent"
                print(f"   Adding status to message {msg['_id']}")
            
            # Update message if needed
            if update_fields:
                db.messages.update_one(
                    {"_id": msg["_id"]},
                    {"$set": update_fields}
                )
                messages_fixed += 1
        
        print(f"✅ Fixed {messages_fixed} messages")
        
        # 3. Update conversation titles and last_message
        print("\n3. Updating conversation titles and last_message...")
        
        conversations = db.conversations.find({})
        title_updates = 0
        
        for conv in conversations:
            update_fields = {}
            
            # Generate title if missing
            if not conv.get("title"):
                # Get first user message for this conversation
                first_message = db.messages.find_one({
                    "conversation_id": str(conv["_id"]),
                    "sender_type": "user"
                }, sort=[("timestamp", 1)])
                
                if first_message:
                    content = first_message["content"]
                    title = content[:50] + "..." if len(content) > 50 else content
                    update_fields["title"] = title
                    print(f"   Generated title for conversation {conv['_id']}: {title}")
            
            # Update last_message if missing
            if not conv.get("last_message"):
                # Get last user message for this conversation
                last_message = db.messages.find_one({
                    "conversation_id": str(conv["_id"]),
                    "sender_type": "user"
                }, sort=[("timestamp", -1)])
                
                if last_message:
                    update_fields["last_message"] = last_message["content"]
                    update_fields["last_message_at"] = last_message.get("timestamp", datetime.utcnow())
                    print(f"   Updated last_message for conversation {conv['_id']}")
            
            # Update conversation if needed
            if update_fields:
                db.conversations.update_one(
                    {"_id": conv["_id"]},
                    {"$set": update_fields}
                )
                title_updates += 1
        
        print(f"✅ Updated {title_updates} conversation titles/last_message")
        
        # 4. Show final statistics
        print("\n📊 Final database statistics:")
        total_conversations = db.conversations.count_documents({})
        total_messages = db.messages.count_documents({})
        active_conversations = db.conversations.count_documents({"status": "active"})
        
        print(f"   Total conversations: {total_conversations}")
        print(f"   Active conversations: {active_conversations}")
        print(f"   Total messages: {total_messages}")
        
        # 5. Show sample data
        print("\n📋 Sample conversation after fix:")
        sample_conv = db.conversations.find_one({})
        if sample_conv:
            print(f"   ID: {sample_conv['_id']}")
            print(f"   Title: {sample_conv.get('title', 'No title')}")
            print(f"   Status: {sample_conv.get('status', 'No status')}")
            print(f"   Message Count: {sample_conv.get('message_count', 0)}")
            print(f"   Created At: {sample_conv.get('created_at', 'No created_at')}")
            print(f"   Updated At: {sample_conv.get('updated_at', 'No updated_at')}")
            print(f"   Last Message: {sample_conv.get('last_message', 'No last_message')}")
        
        print("\n✅ Database fix completed successfully!")
        
        client.close()
        return True
        
    except Exception as e:
        print(f"❌ Error fixing database: {e}")
        return False

def verify_fix():
    """Verify that the fix was successful"""
    
    try:
        client = MongoClient("mongodb://localhost:27017")
        db = client["lunance_db"]
        
        print("\n🔍 Verifying database fix...")
        
        # Check conversations
        conversations_missing_fields = 0
        required_conv_fields = ["created_at", "status", "updated_at", "message_count"]
        
        for conv in db.conversations.find({}):
            for field in required_conv_fields:
                if field not in conv:
                    print(f"⚠️ Conversation {conv['_id']} missing field: {field}")
                    conversations_missing_fields += 1
                    break
        
        # Check messages
        messages_missing_fields = 0
        required_msg_fields = ["timestamp", "status"]
        
        for msg in db.messages.find({}):
            for field in required_msg_fields:
                if field not in msg:
                    print(f"⚠️ Message {msg['_id']} missing field: {field}")
                    messages_missing_fields += 1
                    break
        
        if conversations_missing_fields == 0 and messages_missing_fields == 0:
            print("✅ All required fields are present!")
        else:
            print(f"❌ Found {conversations_missing_fields} conversations and {messages_missing_fields} messages with missing fields")
        
        client.close()
        
    except Exception as e:
        print(f"❌ Error verifying fix: {e}")

if __name__ == "__main__":
    print("=== Database Fix Script ===")
    print("This script will add missing fields to existing data")
    
    # Confirm before running
    if len(sys.argv) > 1 and sys.argv[1] == "--force":
        proceed = True
    else:
        response = input("Do you want to proceed? (yes/no): ")
        proceed = response.lower() in ['yes', 'y']
    
    if proceed:
        success = fix_database()
        if success:
            verify_fix()
    else:
        print("Operation cancelled.")
        
    print("\n=== Fix Script Complete ===")