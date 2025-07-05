# app/utils/transaction_helpers.py
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from bson import ObjectId
import re
import csv
import io

async def auto_categorize_transaction(description: str, user_id: str, db) -> Optional[ObjectId]:
    """Auto-categorize transaction based on description"""
    
    # Define categorization rules
    categorization_rules = {
        "makanan": ["makan", "food", "restaurant", "warung", "cafe", "coffee", "mcd", "kfc"],
        "transportasi": ["transport", "ojek", "bus", "train", "taxi", "gojek", "grab", "bensin", "parkir"],
        "belanja": ["shop", "mall", "market", "beli", "indomaret", "alfamart"],
        "pendidikan": ["buku", "kursus", "seminar", "workshop", "study", "kuliah"],
        "hiburan": ["movie", "cinema", "game", "musik", "concert", "streaming"],
        "kesehatan": ["doctor", "obat", "vitamin", "hospital", "clinic"],
        "utilitas": ["listrik", "air", "internet", "wifi", "pulsa", "token"]
    }
    
    description_lower = description.lower()
    
    # Find matching category keywords
    for category_type, keywords in categorization_rules.items():
        for keyword in keywords:
            if keyword in description_lower:
                # Find category with this name for user
                category = await db.categories.find_one({
                    "nama_kategori": {"$regex": category_type, "$options": "i"},
                    "$or": [
                        {"is_global": True, "is_active": True},
                        {"created_by": ObjectId(user_id), "is_active": True}
                    ]
                })
                if category:
                    return category["_id"]
    
    return None

async def detect_duplicate_transaction(transaction_data, user_id: str, db) -> bool:
    """Detect potential duplicate transactions"""
    
    # Check for similar transactions in last 24 hours
    time_threshold = datetime.utcnow() - timedelta(hours=24)
    
    similar_transaction = await db.transactions.find_one({
        "user_id": ObjectId(user_id),
        "amount": transaction_data.amount,
        "description": transaction_data.description,
        "category_id": ObjectId(transaction_data.category_id),
        "created_at": {"$gte": time_threshold}
    })
    
    return similar_transaction is not None

async def calculate_user_balance(user_id: str, db) -> Dict[str, float]:
    """Calculate user's current balance"""
    
    pipeline = [
        {"$match": {"user_id": ObjectId(user_id)}},
        {
            "$group": {
                "_id": "$type",
                "total": {"$sum": "$amount"}
            }
        }
    ]
    
    results = await db.transactions.aggregate(pipeline).to_list(length=None)
    
    pemasukan = 0
    pengeluaran = 0
    
    for result in results:
        if result["_id"] == "pemasukan":
            pemasukan = result["total"]
        else:
            pengeluaran = result["total"]
    
    # Add initial balance if set
    user = await db.users.find_one({"_id": ObjectId(user_id)})
    initial_balance = user.get("tabungan_awal", 0) if user else 0
    
    balance = initial_balance + pemasukan - pengeluaran
    
    return {
        "initial_balance": initial_balance,
        "total_pemasukan": pemasukan,
        "total_pengeluaran": pengeluaran,
        "current_balance": balance
    }

async def calculate_transaction_summary(user_id: str, filter_query: Dict, db):
    """Calculate transaction summary for given filter"""
    
    # Modify filter to include aggregation
    summary_pipeline = [
        {"$match": filter_query},
        {
            "$group": {
                "_id": "$type",
                "total": {"$sum": "$amount"},
                "count": {"$sum": 1}
            }
        }
    ]
    
    results = await db.transactions.aggregate(summary_pipeline).to_list(length=None)
    
    summary = {
        "total_pemasukan": 0,
        "total_pengeluaran": 0,
        "balance": 0
    }
    
    for result in results:
        if result["_id"] == "pemasukan":
            summary["total_pemasukan"] = result["total"]
        else:
            summary["total_pengeluaran"] = result["total"]
    
    summary["balance"] = summary["total_pemasukan"] - summary["total_pengeluaran"]
    
    from ..models.transaction import TransactionSummary
    return TransactionSummary(**summary)

async def update_budget_spending(user_id: str, category_id: ObjectId, amount: float, transaction_type: str, db):
    """Update budget spending when transaction is created/updated/deleted"""
    
    if transaction_type != "pengeluaran":
        return  # Only track spending for expenses
    
    # Find active budgets for this category
    now = datetime.utcnow()
    budgets = await db.budgets.find({
        "user_id": ObjectId(user_id),
        "category_id": category_id,
        "is_active": True,
        "start_date": {"$lte": now},
        "end_date": {"$gte": now}
    }).to_list(length=None)
    
    for budget in budgets:
        # Calculate current spending
        spending_pipeline = [
            {
                "$match": {
                    "user_id": ObjectId(user_id),
                    "category_id": category_id,
                    "type": "pengeluaran",
                    "date": {
                        "$gte": budget["start_date"],
                        "$lte": budget["end_date"]
                    }
                }
            },
            {
                "$group": {
                    "_id": None,
                    "total_spent": {"$sum": "$amount"}
                }
            }
        ]
        
        result = await db.transactions.aggregate(spending_pipeline).to_list(length=1)
        total_spent = result[0]["total_spent"] if result else 0
        
        # Update budget
        await db.budgets.update_one(
            {"_id": budget["_id"]},
            {"$set": {"spent": total_spent, "updated_at": datetime.utcnow()}}
        )

def export_transactions_csv(transactions: List[Dict]) -> str:
    """Export transactions to CSV format"""
    
    output = io.StringIO()
    fieldnames = ['date', 'type', 'amount', 'description', 'category', 'payment_method', 'location', 'notes']
    
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    
    for trans in transactions:
        writer.writerow({
            'date': trans['date'].strftime('%Y-%m-%d %H:%M:%S'),
            'type': trans['type'],
            'amount': trans['amount'],
            'description': trans['description'],
            'category': trans.get('category', {}).get('nama', ''),
            'payment_method': trans['payment_method'],
            'location': trans.get('location', ''),
            'notes': trans.get('notes', '')
        })
    
    return output.getvalue()

def import_transactions_csv(csv_content: str, user_id: str) -> List[Dict]:
    """Import transactions from CSV content"""
    
    transactions = []
    csv_file = io.StringIO(csv_content)
    reader = csv.DictReader(csv_file)
    
    for row in reader:
        try:
            transaction = {
                'user_id': ObjectId(user_id),
                'date': datetime.strptime(row['date'], '%Y-%m-%d %H:%M:%S'),
                'type': row['type'],
                'amount': float(row['amount']),
                'description': row['description'],
                'payment_method': row['payment_method'],
                'location': row.get('location', ''),
                'notes': row.get('notes', ''),
                'tags': [],
                'created_at': datetime.utcnow()
            }
            transactions.append(transaction)
        except (ValueError, KeyError) as e:
            continue  # Skip invalid rows
    
    return transactions