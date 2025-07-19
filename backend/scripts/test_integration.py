#!/usr/bin/env python3
# scripts/test_integration.py - Test IndoBERT parser integration
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_parser():
    """Test IndoBERT parser integration"""
    print("Testing IndoBERT Financial Parser Integration...")
    
    try:
        from app.services.indoroberta_financial_parser import IndoRoBERTaFinancialParser
        
        # Initialize parser
        parser = IndoRoBERTaFinancialParser()
        print("Parser initialized successfully")
        
        # Test cases
        test_cases = [
            "Dapat uang saku 2 juta dari ortu",
            "Bayar kos 800 ribu",
            "Belanja groceries 150rb",
            "Jajan bubble tea 25rb",
            "Mau nabung buat beli laptop 10 juta",
            "Freelance dapat 500rb"
        ]
        
        print("Testing parsing...")
        for i, test_case in enumerate(test_cases, 1):
            print(f"\nTest {i}: '{test_case}'")
            
            try:
                # Test amount parsing
                amount = parser.parse_amount(test_case)
                print(f"   Amount: {amount}")
                
                # Test transaction type
                trans_type = parser.detect_transaction_type(test_case)
                print(f"   Type: {trans_type}")
                
                # Test full parsing
                result = parser.parse_financial_data(test_case)
                print(f"   Financial data: {result['is_financial_data']}")
                
                if result['is_financial_data']:
                    print(f"   Category: {result['parsed_data'].get('category', 'N/A')}")
                    print(f"   Budget Type: {result['parsed_data'].get('budget_type', 'N/A')}")
                
            except Exception as e:
                print(f"   Error: {e}")
        
        print("\nIntegration test completed!")
        return True
        
    except ImportError as e:
        print(f"Import error: {e}")
        print("Make sure IndoRoBERTaFinancialParser is properly installed")
        return False
    except Exception as e:
        print(f"Test error: {e}")
        return False

def test_fallback():
    """Test fallback mechanism"""
    print("\nTesting fallback mechanism...")
    
    try:
        # Test with original parser
        from app.services.enhanced_financial_parser import EnhancedFinancialParser
        
        parser = EnhancedFinancialParser()
        print("Fallback parser works")
        
        # Test parsing
        result = parser.parse_financial_data("Bayar kos 800 ribu")
        print(f"   Fallback parsing: {result['is_financial_data']}")
        
        return True
        
    except Exception as e:
        print(f"Fallback test error: {e}")
        return False

def main():
    print("IndoBERT Financial Parser Integration Test")
    print("=" * 50)
    
    # Test main parser
    main_test = test_parser()
    
    # Test fallback
    fallback_test = test_fallback()
    
    print("\n" + "=" * 50)
    if main_test and fallback_test:
        print("All tests passed!")
    else:
        print("Some tests failed!")
        if not main_test:
            print("   - Main parser test failed")
        if not fallback_test:
            print("   - Fallback test failed")

if __name__ == "__main__":
    main()
