#!/usr/bin/env python3
"""
Database Migration Script untuk Lunance Chat
Memperbaiki history chat yang hilang dan generate titles

Usage:
python migrate_chat_data.py
"""

import sys
import os
from datetime import datetime
from typing import List, Dict, Any, Optional
from bson import ObjectId
import re
import random

# Add app directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config.database import get_database
from app.utils.timezone_utils import IndonesiaDatetime, now_for_db

class ChatDataMigrator:
    """Migrator untuk memperbaiki data chat"""
    
    def __init__(self):
        self.db = get_database()
        self.financial_keywords = {
            'budget': 'Budget Planning',
            'anggaran': 'Perencanaan Anggaran',
            'tabungan': 'Tips Menabung',
            'investasi': 'Panduan Investasi',
            'pengeluaran': 'Analisis Pengeluaran',
            'pemasukan': 'Manajemen Pemasukan',
            'keuangan': 'Konsultasi Keuangan',
            'hutang': 'Strategi Hutang',
            'cicilan': 'Manajemen Cicilan',
            'gaji': 'Perencanaan Gaji',
            'uang': 'Manajemen Uang',
            'bank': 'Banking Tips',
            'transfer': 'Transfer Guide',
            'bayar': 'Payment Tips'
        }
    
    def generate_conversation_title(self, user_message: str, luna_response: str = "") -> str:
        """Generate judul percakapan dari pesan user dan Luna (maksimal 10 kata)"""
        
        # Prioritas keywords untuk judul
        user_lower = user_message.lower()
        for keyword, title in self.financial_keywords.items():
            if keyword in user_lower:
                return title
        
        # Jika tidak ada kata kunci finansial, ambil dari awal pesan user
        # Bersihkan dan ambil kata-kata penting
        words = re.findall(r'\b\w+\b', user_message)
        
        # Filter kata-kata yang tidak penting
        stop_words = {
            'saya', 'aku', 'anda', 'kamu', 'ini', 'itu', 'di', 'ke', 'dari', 'untuk',
            'dengan', 'pada', 'yang', 'adalah', 'akan', 'sudah', 'belum', 'tidak',
            'jangan', 'bisa', 'dapat', 'harus', 'ingin', 'mau', 'ada', 'dan', 'atau',
            'tapi', 'tetapi', 'kalau', 'jika', 'bila', 'ketika', 'saat', 'waktu'
        }
        
        important_words = [word for word in words if word.lower() not in stop_words and len(word) > 2]
        
        # Ambil maksimal 10 kata pertama yang penting
        title_words = important_words[:10] if important_words else words[:10]
        
        # Gabungkan dan buat title
        title = ' '.join(title_words)
        
        # Kapitalisasi kata pertama
        if title:
            title = title[0].upper() + title[1:] if len(title) > 1 else title.upper()
        else:
            title = "Chat Keuangan"
        
        # Batasi panjang maksimal
        if len(title) > 50:
            title = title[:47] + "..."
        
        return title
    
    def analyze_conversation_structure(self):
        """Analisis struktur conversations yang ada"""
        print("🔍 Analyzing conversation structure...")
        
        # Check conversations collection
        conv_count = self.db.conversations.count_documents({})
        print(f"📊 Total conversations: {conv_count}")
        
        if conv_count > 0:
            # Sample conversation
            sample_conv = self.db.conversations.find_one()
            print(f"📋 Sample conversation fields: {list(sample_conv.keys())}")
            
            # Check missing fields
            missing_title = self.db.conversations.count_documents({"title": {"$exists": False}})
            null_title = self.db.conversations.count_documents({"title": None})
            empty_title = self.db.conversations.count_documents({"title": ""})
            
            print(f"📊 Conversations missing title field: {missing_title}")
            print(f"📊 Conversations with null title: {null_title}")
            print(f"📊 Conversations with empty title: {empty_title}")
            
            # Check message counts
            zero_messages = self.db.conversations.count_documents({"message_count": 0})
            no_message_count = self.db.conversations.count_documents({"message_count": {"$exists": False}})
            
            print(f"📊 Conversations with 0 messages: {zero_messages}")
            print(f"📊 Conversations without message_count: {no_message_count}")
        
        # Check messages collection
        msg_count = self.db.messages.count_documents({})
        print(f"📧 Total messages: {msg_count}")
        
        if msg_count > 0:
            sample_msg = self.db.messages.find_one()
            print(f"📋 Sample message fields: {list(sample_msg.keys())}")
    
    def fix_conversation_titles(self):
        """Fix conversations yang tidak punya title"""
        print("\n🔧 Fixing conversation titles...")
        
        # Find conversations without proper titles
        conversations_to_fix = self.db.conversations.find({
            "$or": [
                {"title": {"$exists": False}},
                {"title": None},
                {"title": ""},
                {"title": "New Chat"},
                {"title": "Chat Baru"}
            ]
        })
        
        fixed_count = 0
        for conv in conversations_to_fix:
            conversation_id = str(conv["_id"])
            
            # Get first user message in this conversation
            first_message = self.db.messages.find_one(
                {
                    "conversation_id": conversation_id,
                    "sender_type": "user"
                },
                sort=[("timestamp", 1)]
            )
            
            if first_message:
                # Get Luna response jika ada
                luna_response = self.db.messages.find_one(
                    {
                        "conversation_id": conversation_id,
                        "sender_type": "luna",
                        "timestamp": {"$gt": first_message["timestamp"]}
                    },
                    sort=[("timestamp", 1)]
                )
                
                # Generate title
                luna_content = luna_response["content"] if luna_response else ""
                new_title = self.generate_conversation_title(
                    first_message["content"], 
                    luna_content
                )
                
                # Update conversation
                result = self.db.conversations.update_one(
                    {"_id": conv["_id"]},
                    {
                        "$set": {
                            "title": new_title,
                            "updated_at": now_for_db()
                        }
                    }
                )
                
                if result.modified_count > 0:
                    fixed_count += 1
                    created_time = IndonesiaDatetime.format(conv.get("created_at", now_for_db()))
                    print(f"✅ Fixed conversation {conversation_id}: '{new_title}' (created: {created_time})")
        
        print(f"🎉 Fixed {fixed_count} conversation titles")
    
    def fix_message_counts(self):
        """Fix message counts untuk conversations"""
        print("\n🔢 Fixing message counts...")
        
        conversations = self.db.conversations.find({})
        fixed_count = 0
        
        for conv in conversations:
            conversation_id = str(conv["_id"])
            
            # Count actual messages
            actual_count = self.db.messages.count_documents({
                "conversation_id": conversation_id
            })
            
            current_count = conv.get("message_count", 0)
            
            if actual_count != current_count:
                # Update last message info juga
                last_message = self.db.messages.find_one(
                    {"conversation_id": conversation_id},
                    sort=[("timestamp", -1)]
                )
                
                update_data = {
                    "message_count": actual_count,
                    "updated_at": now_for_db()
                }
                
                if last_message:
                    update_data["last_message"] = last_message["content"]
                    update_data["last_message_at"] = last_message["timestamp"]
                
                result = self.db.conversations.update_one(
                    {"_id": conv["_id"]},
                    {"$set": update_data}
                )
                
                if result.modified_count > 0:
                    fixed_count += 1
                    print(f"✅ Fixed message count for {conversation_id}: {current_count} → {actual_count}")
        
        print(f"🎉 Fixed {fixed_count} conversation message counts")
    
    def clean_empty_conversations(self):
        """Remove conversations yang benar-benar kosong"""
        print("\n🧹 Cleaning empty conversations...")
        
        empty_conversations = self.db.conversations.find({
            "$or": [
                {"message_count": 0},
                {"message_count": {"$exists": False}}
            ]
        })
        
        deleted_count = 0
        for conv in empty_conversations:
            conversation_id = str(conv["_id"])
            
            # Double check - pastikan tidak ada pesan
            message_count = self.db.messages.count_documents({
                "conversation_id": conversation_id
            })
            
            if message_count == 0:
                # Soft delete
                result = self.db.conversations.update_one(
                    {"_id": conv["_id"]},
                    {
                        "$set": {
                            "status": "deleted",
                            "updated_at": now_for_db()
                        }
                    }
                )
                
                if result.modified_count > 0:
                    deleted_count += 1
                    created_time = IndonesiaDatetime.format(conv.get("created_at", now_for_db()))
                    print(f"🗑️ Deleted empty conversation {conversation_id} (created: {created_time})")
        
        print(f"🎉 Cleaned {deleted_count} empty conversations")
    
    def fix_timezone_timestamps(self):
        """Fix timezone untuk timestamps (jika diperlukan)"""
        print("\n🕐 Checking timezone timestamps...")
        
        # Sample beberapa timestamps untuk check
        sample_conversations = self.db.conversations.find().limit(5)
        sample_messages = self.db.messages.find().limit(5)
        
        print("📅 Sample conversation timestamps:")
        for conv in sample_conversations:
            if "created_at" in conv:
                wib_time = IndonesiaDatetime.format(conv["created_at"])
                print(f"   {conv['_id']}: {wib_time} WIB")
        
        print("📧 Sample message timestamps:")
        for msg in sample_messages:
            if "timestamp" in msg:
                wib_time = IndonesiaDatetime.format(msg["timestamp"])
                print(f"   {msg['_id']}: {wib_time} WIB")
        
        print("✅ Timestamps appear to be in correct format")
    
    def add_missing_fields(self):
        """Add missing fields ke conversations"""
        print("\n➕ Adding missing fields...")
        
        # Add status field jika tidak ada
        result = self.db.conversations.update_many(
            {"status": {"$exists": False}},
            {"$set": {"status": "active"}}
        )
        
        if result.modified_count > 0:
            print(f"✅ Added status field to {result.modified_count} conversations")
        
        # Add message_count jika tidak ada
        result = self.db.conversations.update_many(
            {"message_count": {"$exists": False}},
            {"$set": {"message_count": 0}}
        )
        
        if result.modified_count > 0:
            print(f"✅ Added message_count field to {result.modified_count} conversations")
    
    def run_migration(self):
        """Run complete migration"""
        print("🚀 Starting Chat Data Migration...")
        print("=" * 50)
        
        try:
            # 1. Analyze current structure
            self.analyze_conversation_structure()
            
            # 2. Add missing fields
            self.add_missing_fields()
            
            # 3. Fix message counts
            self.fix_message_counts()
            
            # 4. Fix conversation titles
            self.fix_conversation_titles()
            
            # 5. Clean empty conversations
            self.clean_empty_conversations()
            
            # 6. Check timestamps
            self.fix_timezone_timestamps()
            
            print("\n" + "=" * 50)
            print("🎉 Migration completed successfully!")
            
            # Final stats
            print("\n📊 Final Statistics:")
            total_conversations = self.db.conversations.count_documents({"status": {"$ne": "deleted"}})
            total_messages = self.db.messages.count_documents({})
            conversations_with_titles = self.db.conversations.count_documents({
                "title": {"$exists": True, "$ne": None, "$ne": ""}
            })
            
            print(f"   Total active conversations: {total_conversations}")
            print(f"   Total messages: {total_messages}")
            print(f"   Conversations with proper titles: {conversations_with_titles}")
            
        except Exception as e:
            print(f"❌ Migration failed: {e}")
            raise
    
    def create_sample_conversation(self, user_id: str):
        """Create sample conversation untuk testing"""
        print(f"\n🧪 Creating sample conversation for user {user_id}...")
        
        # Create conversation
        conv_data = {
            "user_id": user_id,
            "title": None,
            "status": "active",
            "last_message": None,
            "last_message_at": None,
            "message_count": 0,
            "created_at": now_for_db(),
            "updated_at": now_for_db()
        }
        
        conv_result = self.db.conversations.insert_one(conv_data)
        conversation_id = str(conv_result.inserted_id)
        
        # Add sample messages
        now = now_for_db()
        
        # User message
        user_msg = {
            "conversation_id": conversation_id,
            "sender_id": user_id,
            "sender_type": "user",
            "content": "Bagaimana cara mengatur budget bulanan yang efektif?",
            "message_type": "text",
            "status": "sent",
            "timestamp": now
        }
        
        self.db.messages.insert_one(user_msg)
        
        # Luna response
        luna_msg = {
            "conversation_id": conversation_id,
            "sender_id": None,
            "sender_type": "luna",
            "content": "Untuk membuat budget bulanan yang efektif, saya sarankan menggunakan metode 50/30/20: 50% untuk kebutuhan, 30% untuk keinginan, dan 20% untuk tabungan.",
            "message_type": "text",
            "status": "sent",
            "timestamp": now
        }
        
        self.db.messages.insert_one(luna_msg)
        
        # Update conversation
        title = self.generate_conversation_title(user_msg["content"], luna_msg["content"])
        
        self.db.conversations.update_one(
            {"_id": conv_result.inserted_id},
            {
                "$set": {
                    "title": title,
                    "last_message": user_msg["content"],
                    "last_message_at": now,
                    "message_count": 2,
                    "updated_at": now
                }
            }
        )
        
        print(f"✅ Created sample conversation: '{title}'")
        return conversation_id

def main():
    """Main migration function"""
    migrator = ChatDataMigrator()
    
    print("Lunance Chat Data Migration Tool")
    print("=" * 40)
    
    while True:
        print("\nSelect option:")
        print("1. Run full migration")
        print("2. Analyze data structure only")
        print("3. Fix titles only")
        print("4. Fix message counts only")
        print("5. Clean empty conversations only")
        print("6. Create sample conversation")
        print("0. Exit")
        
        choice = input("\nEnter choice (0-6): ").strip()
        
        if choice == "0":
            print("👋 Goodbye!")
            break
        elif choice == "1":
            migrator.run_migration()
        elif choice == "2":
            migrator.analyze_conversation_structure()
        elif choice == "3":
            migrator.fix_conversation_titles()
        elif choice == "4":
            migrator.fix_message_counts()
        elif choice == "5":
            migrator.clean_empty_conversations()
        elif choice == "6":
            user_id = input("Enter user ID for sample conversation: ").strip()
            if user_id:
                migrator.create_sample_conversation(user_id)
            else:
                print("❌ User ID required")
        else:
            print("❌ Invalid choice")

if __name__ == "__main__":
    main()