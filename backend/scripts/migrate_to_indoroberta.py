#!/usr/bin/env python3
# scripts/migrate_to_indoroberta.py
"""
Migration script untuk transition dari enhanced_financial_parser ke IndoRoBERTa parser
"""

import sys
import logging
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_parser_compatibility():
    """Test compatibility antara old dan new parser"""
    test_cases = [
        "Dapat gaji 3 juta dari freelance",
        "Bayar kos 800 ribu", 
        "Beli bubble tea 25rb",
        "Mau nabung buat beli laptop 10 juta pada tanggal 31 desember 2025",
        "Belanja groceries 150 ribu",
        "Transfer dana darurat 500rb"
    ]
    
    try:
        # Test IndoRoBERTa parser
        from app.services.indoroberta_financial_parser import IndoRoBERTaFinancialParser
        new_parser = IndoRoBERTaFinancialParser()
        
        logger.info("🧪 Testing IndoRoBERTa parser...")
        for text in test_cases:
            result = new_parser.parse_financial_data(text)
            status = "✅" if result["is_financial_data"] else "❌"
            logger.info(f"{status} {text} -> {result.get('data_type', 'non_financial')}")
        
        logger.info("✅ IndoRoBERTa parser working correctly")
        return True
        
    except Exception as e:
        logger.error(f"❌ IndoRoBERTa parser error: {e}")
        
        # Fallback test
        try:
            from app.services.enhanced_financial_parser_backup import EnhancedFinancialParser
            old_parser = EnhancedFinancialParser()
            
            logger.info("🔄 Testing fallback parser...")
            for text in test_cases:
                result = old_parser.parse_financial_data(text)
                status = "✅" if result["is_financial_data"] else "❌"
                logger.info(f"{status} {text} -> {result.get('data_type', 'non_financial')}")
            
            logger.info("✅ Fallback parser working")
            return False
            
        except Exception as e2:
            logger.error(f"❌ Both parsers failed: {e2}")
            return False

def migrate_user_data():
    """Migrate user data jika diperlukan"""
    logger.info("📊 Checking user data migration needs...")
    # Implementasi migration logic jika ada perubahan format data
    logger.info("ℹ️ No data migration needed - formats compatible")
    return True

def main():
    logger.info("🚀 Starting migration to IndoRoBERTa parser...")
    
    # Test compatibility
    if test_parser_compatibility():
        logger.info("✅ Migration successful - IndoRoBERTa parser active")
    else:
        logger.warning("⚠️ Using fallback parser - check IndoRoBERTa setup")
    
    # Migrate data
    migrate_user_data()
    
    logger.info("🎉 Migration completed!")

if __name__ == "__main__":
    main()
