# scripts/quick_fix_existing_user.py
"""
Quick fix untuk menambah transaksi ke user yang sudah ada
User ID: 687f322a110c53c25df89f0e
"""

import sys
import os
import asyncio
from datetime import datetime, timedelta
import random

# Add project root to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.config.database import get_database
from app.models.finance import TransactionType, TransactionStatus
from bson import ObjectId

class QuickUserFix:
    def __init__(self):
        self.db = get_database()
        self.user_id = "6881f4f8917573fd61a3e102"
        
    async def add_transactions_to_existing_user(self):
        """Add realistic transactions to existing user"""
        print(f"🔧 Adding transactions to user {self.user_id}")
        
        # Check if user exists
        user = self.db.users.find_one({"_id": ObjectId(self.user_id)})
        if not user:
            print(f"❌ User {self.user_id} not found")
            return False
            
        print(f"✅ Found user: {user.get('email', 'No email')}")
        
        # Generate 3 months of realistic transactions
        transactions = self._generate_quick_transactions()
        
        # Insert transactions
        if transactions:
            result = self.db.transactions.insert_many(transactions)
            print(f"✅ Added {len(result.inserted_ids)} transactions")
            
            # Verify count
            total_count = self.db.transactions.count_documents({"user_id": self.user_id})
            confirmed_count = self.db.transactions.count_documents({
                "user_id": self.user_id, 
                "status": TransactionStatus.CONFIRMED.value
            })
            
            print(f"📊 Total transactions: {total_count}")
            print(f"📊 Confirmed transactions: {confirmed_count}")
            
            if confirmed_count >= 10:
                print("🎉 User now has enough data for predictions!")
                return True
            else:
                print("⚠️ Still need more transactions for reliable predictions")
                return False
        
        return False
    
    def _generate_quick_transactions(self):
        """Generate realistic transactions for student"""
        transactions = []
        end_date = datetime.now()
        start_date = end_date - timedelta(days=90)  # 3 months
        
        # Generate monthly pattern
        for month in range(3):
            month_start = start_date + timedelta(days=month * 30)
            
            # INCOME - 2-3 per month
            # Monthly allowance
            uang_saku_date = month_start + timedelta(days=random.randint(1, 5))
            transactions.append({
                "user_id": self.user_id,
                "type": TransactionType.INCOME.value,
                "amount": random.uniform(2000000, 2800000),
                "category": "Uang Saku",
                "description": "Uang saku bulanan dari orang tua",
                "date": uang_saku_date,
                "status": TransactionStatus.CONFIRMED.value,
                "source": "manual",
                "created_at": uang_saku_date,
                "updated_at": uang_saku_date,
                "confirmed_at": uang_saku_date
            })
            
            # Freelance income (sometimes)
            if random.random() > 0.4:
                freelance_date = month_start + timedelta(days=random.randint(10, 25))
                transactions.append({
                    "user_id": self.user_id,
                    "type": TransactionType.INCOME.value,
                    "amount": random.uniform(400000, 900000),
                    "category": "Freelance",
                    "description": random.choice([
                        "Project web development",
                        "Design grafis",
                        "Les private"
                    ]),
                    "date": freelance_date,
                    "status": TransactionStatus.CONFIRMED.value,
                    "source": "manual",
                    "created_at": freelance_date,
                    "updated_at": freelance_date,
                    "confirmed_at": freelance_date
                })
            
            # EXPENSES - 15-20 per month
            # Daily food
            for _ in range(20):
                food_date = month_start + timedelta(days=random.randint(0, 29))
                transactions.append({
                    "user_id": self.user_id,
                    "type": TransactionType.EXPENSE.value,
                    "amount": random.uniform(15000, 45000),
                    "category": "Makan",
                    "description": random.choice([
                        "Makan siang", "Sarapan", "Makan malam", 
                        "Jajan", "Beli buah"
                    ]),
                    "date": food_date,
                    "status": TransactionStatus.CONFIRMED.value,
                    "source": "manual",
                    "created_at": food_date,
                    "updated_at": food_date,
                    "confirmed_at": food_date
                })
            
            # Transport
            for _ in range(10):
                transport_date = month_start + timedelta(days=random.randint(0, 29))
                transactions.append({
                    "user_id": self.user_id,
                    "type": TransactionType.EXPENSE.value,
                    "amount": random.uniform(8000, 35000),
                    "category": "Transport",
                    "description": random.choice([
                        "Ongkos ke kampus", "Grab", "Bensin motor", "Parkir"
                    ]),
                    "date": transport_date,
                    "status": TransactionStatus.CONFIRMED.value,
                    "source": "manual",
                    "created_at": transport_date,
                    "updated_at": transport_date,
                    "confirmed_at": transport_date
                })
            
            # Monthly rent
            rent_date = month_start + timedelta(days=random.randint(1, 3))
            transactions.append({
                "user_id": self.user_id,
                "type": TransactionType.EXPENSE.value,
                "amount": random.uniform(800000, 1200000),
                "category": "Kos/Sewa",
                "description": "Bayar kos bulanan",
                "date": rent_date,
                "status": TransactionStatus.CONFIRMED.value,
                "source": "manual",
                "created_at": rent_date,
                "updated_at": rent_date,
                "confirmed_at": rent_date
            })
            
            # Entertainment & wants
            for _ in range(8):
                wants_date = month_start + timedelta(days=random.randint(0, 29))
                transactions.append({
                    "user_id": self.user_id,
                    "type": TransactionType.EXPENSE.value,
                    "amount": random.uniform(25000, 100000),
                    "category": random.choice(["Hiburan", "Shopping", "Nongkrong"]),
                    "description": random.choice([
                        "Nongkrong di cafe", "Nonton bioskop", 
                        "Beli baju", "Main billiard"
                    ]),
                    "date": wants_date,
                    "status": TransactionStatus.CONFIRMED.value,
                    "source": "manual",
                    "created_at": wants_date,
                    "updated_at": wants_date,
                    "confirmed_at": wants_date
                })
            
            # Savings
            for _ in range(2):
                savings_date = month_start + timedelta(days=random.randint(5, 25))
                transactions.append({
                    "user_id": self.user_id,
                    "type": TransactionType.EXPENSE.value,
                    "amount": random.uniform(100000, 300000),
                    "category": "Tabungan",
                    "description": "Transfer ke tabungan",
                    "date": savings_date,
                    "status": TransactionStatus.CONFIRMED.value,
                    "source": "manual",
                    "created_at": savings_date,
                    "updated_at": savings_date,
                    "confirmed_at": savings_date
                })
        
        print(f"📝 Generated {len(transactions)} transactions")
        return transactions
    
    async def verify_predictions_ready(self):
        """Verify if predictions are now working"""
        print("🔍 Verifying prediction readiness...")
        
        # Import prediction service
        try:
            from app.services.prediction_service import FinancialPredictionService
            
            service = FinancialPredictionService()
            
            # Test income prediction
            income_result = await service.predict_income(self.user_id, 30)
            print(f"Income prediction: {'✅ SUCCESS' if income_result.get('success') else '❌ FAILED'}")
            
            # Test budget performance
            budget_result = await service.predict_budget_performance(self.user_id, 30)
            print(f"Budget prediction: {'✅ SUCCESS' if budget_result.get('success') else '❌ FAILED'}")
            
            if income_result.get('success') and budget_result.get('success'):
                print("🎉 PREDICTIONS ARE NOW WORKING!")
                return True
            else:
                print("⚠️ Predictions still not working properly")
                if not income_result.get('success'):
                    print(f"Income error: {income_result.get('message', 'Unknown error')}")
                if not budget_result.get('success'):
                    print(f"Budget error: {budget_result.get('message', 'Unknown error')}")
                return False
                
        except Exception as e:
            print(f"❌ Error testing predictions: {e}")
            return False

async def main():
    """Run the quick fix"""
    print("🚀 QUICK FIX FOR EXISTING USER")
    print("=" * 40)
    
    fixer = QuickUserFix()
    
    # Add transactions
    success = await fixer.add_transactions_to_existing_user()
    
    if success:
        # Test predictions
        await fixer.verify_predictions_ready()
    
    print("=" * 40)
    print("✅ Quick fix completed!")
    print("🔄 Try accessing prediction endpoints again")

if __name__ == "__main__":
    asyncio.run(main())