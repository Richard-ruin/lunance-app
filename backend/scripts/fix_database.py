# quick_debug.py
# Script untuk quick check masalah Luna AI

def check_file_structure():
    """Check if all required files exist"""
    import os
    
    required_files = [
        "app/services/finance_service.py",
        "app/models/finance.py", 
        "app/schemas/finance_schemas.py",
        "app/routers/finance.py"
    ]
    
    print("📁 Checking file structure...")
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - FILE MISSING!")
    
    # Check if chat_service.py has been updated
    if os.path.exists("app/services/chat_service.py"):
        with open("app/services/chat_service.py", "r", encoding="utf-8") as f:
            content = f.read()
            
        if "FinanceService" in content and "parse_financial_message" in content:
            print("✅ app/services/chat_service.py - UPDATED")
        else:
            print("❌ app/services/chat_service.py - NOT UPDATED")
            print("   - Missing FinanceService import or parse_financial_message")

def test_simple_parsing():
    """Test parsing logic manually"""
    import re
    
    print("\n🔍 Testing simple parsing logic...")
    
    test_text = "Dapat gaji 5 juta"
    print(f"Testing: '{test_text}'")
    
    # Test amount detection
    money_patterns = [
        r'(\d+)\s*juta',
        r'(\d+)\s*ribu',
        r'(\d+)'
    ]
    
    amount = None
    for pattern in money_patterns:
        match = re.search(pattern, test_text.lower())
        if match:
            base_amount = float(match.group(1))
            if 'juta' in test_text.lower():
                amount = base_amount * 1000000
            elif 'ribu' in test_text.lower():
                amount = base_amount * 1000
            else:
                amount = base_amount
            print(f"Amount detected: {amount}")
            break
    
    if not amount:
        print("❌ No amount detected")
        return
    
    # Test keyword detection
    income_keywords = ['gaji', 'pendapatan', 'dapat', 'terima']
    expense_keywords = ['bayar', 'beli', 'belanja']
    
    text_lower = test_text.lower()
    
    income_found = any(keyword in text_lower for keyword in income_keywords)
    expense_found = any(keyword in text_lower for keyword in expense_keywords)
    
    print(f"Income keywords found: {income_found}")
    print(f"Expense keywords found: {expense_found}")
    
    if income_found:
        print("✅ Should be detected as INCOME")
    elif expense_found:
        print("✅ Should be detected as EXPENSE")
    else:
        print("❌ No transaction type detected")

def test_luna_response():
    """Test Luna AI response generation"""
    print("\n🤖 Testing Luna Response...")
    
    # Simulate what should happen
    test_cases = [
        {
            "input": "Dapat gaji 5 juta",
            "expected_type": "financial_confirmation",
            "expected_amount": 5000000
        },
        {
            "input": "Bayar listrik 200 ribu", 
            "expected_type": "financial_confirmation",
            "expected_amount": 200000
        }
    ]
    
    for case in test_cases:
        print(f"\nInput: '{case['input']}'")
        print(f"Expected: {case['expected_type']} with amount {case['expected_amount']}")
        
        # This is what Luna should detect
        # (Manual simulation of the logic)
        text = case['input'].lower()
        
        # Amount detection
        if 'juta' in text:
            amount_match = re.search(r'(\d+)\s*juta', text)
            if amount_match:
                amount = float(amount_match.group(1)) * 1000000
                print(f"✅ Amount should be: {amount}")
        elif 'ribu' in text:
            amount_match = re.search(r'(\d+)\s*ribu', text)
            if amount_match:
                amount = float(amount_match.group(1)) * 1000
                print(f"✅ Amount should be: {amount}")
        
        # Type detection
        if any(word in text for word in ['gaji', 'dapat', 'pendapatan']):
            print("✅ Type should be: income")
        elif any(word in text for word in ['bayar', 'beli', 'belanja']):
            print("✅ Type should be: expense")

def check_imports():
    """Check if imports work"""
    print("\n📦 Testing imports...")
    
    try:
        print("Testing basic imports...")
        import re
        import random
        from datetime import datetime
        print("✅ Basic imports OK")
        
        print("Testing database import...")
        from app.config.database import get_database
        print("✅ Database import OK")
        
        print("Testing finance service import...")
        from app.services.finance_service import FinanceService
        print("✅ Finance service import OK")
        
        print("Testing finance parser...")
        finance_service = FinanceService()
        result = finance_service.parse_financial_message("test")
        print("✅ Finance parser creation OK")
        
        return True
        
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

def main():
    print("🚀 Quick Luna AI Debug Check")
    print("=" * 40)
    
    check_file_structure()
    test_simple_parsing() 
    test_luna_response()
    imports_ok = check_imports()
    
    print("\n📋 Quick Fix Checklist:")
    print("=" * 25)
    
    if not imports_ok:
        print("❌ IMPORT ISSUES - Check file contents and dependencies")
    else:
        print("✅ Imports are working")
    
    print("\n🔧 Manual Test:")
    print("1. Restart your FastAPI server")
    print("2. Send message: 'Dapat gaji 5 juta'")
    print("3. Luna should respond with confirmation")
    
    print("\n🐛 If still not working, check:")
    print("- Server logs for error messages")
    print("- Database connection")
    print("- File permissions")
    print("- Python path issues")

if __name__ == "__main__":
    main()