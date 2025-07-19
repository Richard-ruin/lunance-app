# test_indoroberta_integration.py - Script untuk memvalidasi IndoRoBERTa integration
import asyncio
import aiohttp
import json
import time
import logging
from datetime import datetime
from typing import Dict, Any, List

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_URL = "http://localhost:8000"

class IndoRoBERTaIntegrationTester:
    """Tester untuk memvalidasi IndoRoBERTa integration dalam Luna AI"""
    
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.session = None
        self.access_token = None
        self.user_id = None
        self.test_results = []
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def log_result(self, test_name: str, success: bool, parser_type: str = None, 
                  response_data: Any = None, error: str = None):
        """Log test result"""
        result = {
            "test_name": test_name,
            "success": success,
            "parser_type": parser_type,
            "timestamp": datetime.now().isoformat(),
            "response_data": response_data,
            "error": error
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        parser_info = f" [{parser_type}]" if parser_type else ""
        print(f"{status} | {test_name}{parser_info}")
        
        if error:
            print(f"    Error: {error}")
        
        if response_data and isinstance(response_data, dict):
            if "parser_type" in response_data:
                print(f"    Parser: {response_data['parser_type']}")
            if "is_financial_data" in response_data:
                print(f"    Financial Data Detected: {response_data['is_financial_data']}")
        print()
    
    async def make_request(self, method: str, endpoint: str, data: Dict[Any, Any] = None):
        """Make HTTP request"""
        url = f"{self.base_url}{endpoint}"
        headers = {}
        
        if self.access_token:
            headers["Authorization"] = f"Bearer {self.access_token}"
        
        try:
            async with self.session.request(method, url, json=data, headers=headers) as response:
                response_data = await response.json()
                return {
                    "status_code": response.status,
                    "data": response_data
                }
        except Exception as e:
            return {
                "status_code": 500,
                "error": str(e)
            }
    
    async def setup_test_user(self):
        """Setup test user untuk testing"""
        print("🔧 Setting up test user...")
        
        # Register test user
        register_data = {
            "username": f"indoroberta_test_{int(time.time())}",
            "email": f"indoroberta_test_{int(time.time())}@test.com",
            "password": "Test123456",
            "confirm_password": "Test123456"
        }
        
        result = await self.make_request("POST", "/api/v1/auth/register", register_data)
        if result["status_code"] != 201:
            self.log_result("Setup: Register", False, error=f"Status: {result['status_code']}")
            return False
        
        # Login
        login_data = {
            "email": register_data["email"],
            "password": register_data["password"]
        }
        
        result = await self.make_request("POST", "/api/v1/auth/login", login_data)
        if result["status_code"] != 200:
            self.log_result("Setup: Login", False, error=f"Status: {result['status_code']}")
            return False
        
        tokens = result["data"]["data"]["tokens"]
        user_data = result["data"]["data"]["user"]
        self.access_token = tokens["access_token"]
        self.user_id = user_data["id"]
        
        # Profile setup
        profile_data = {
            "full_name": "IndoRoBERTa Test User",
            "phone_number": "+628123456789",
            "university": "Test University",
            "city": "Jakarta"
        }
        
        result = await self.make_request("POST", "/api/v1/auth/setup-profile", profile_data)
        if result["status_code"] != 200:
            self.log_result("Setup: Profile", False, error=f"Status: {result['status_code']}")
            return False
        
        # Financial setup
        financial_data = {
            "current_savings": 5000000,
            "monthly_income": 3000000,
            "primary_bank": "BCA"
        }
        
        result = await self.make_request("POST", "/api/v1/auth/setup-financial-50-30-20", financial_data)
        if result["status_code"] != 200:
            self.log_result("Setup: Financial", False, error=f"Status: {result['status_code']}")
            return False
        
        self.log_result("Setup: Complete", True)
        return True
    
    async def test_health_check(self):
        """Test health check endpoint"""
        print("🏥 Testing health check...")
        
        result = await self.make_request("GET", "/health")
        success = result["status_code"] == 200
        
        parser_info = None
        if success and "data" in result["data"]:
            health_data = result["data"]["data"]
            parser_info = health_data.get("financial_parser", "unknown")
        
        self.log_result("Health Check", success, parser_info, 
                       response_data=result.get("data"))
    
    async def test_financial_parsing_endpoint(self):
        """Test demo financial parsing endpoint"""
        print("🧪 Testing financial parsing endpoint...")
        
        test_messages = [
            "Dapat uang saku 2 juta dari ortu",
            "Bayar kos 800 ribu",
            "Freelance web design dapat 1.5 juta",
            "Beli bubble tea 25 ribu",
            "Mau nabung buat beli laptop 10 juta"
        ]
        
        for i, message in enumerate(test_messages, 1):
            data = {"message": message}
            result = await self.make_request("POST", "/api/v1/demo/parse-financial", data)
            
            success = result["status_code"] == 200
            
            parser_type = None
            parse_result = None
            
            if success and "data" in result["data"]:
                data_section = result["data"]["data"]
                parse_result = data_section.get("parse_result", {})
                parser_type = parse_result.get("parsing_method", "unknown")
            
            self.log_result(f"Financial Parsing {i}: {message[:30]}...", 
                          success, parser_type, parse_result, 
                          error=None if success else f"Status: {result['status_code']}")
    
    async def test_chat_with_financial_data(self):
        """Test chat dengan financial data untuk melihat IndoRoBERTa integration"""
        print("💬 Testing chat with financial data...")
        
        # Create conversation
        result = await self.make_request("POST", "/api/v1/chat/conversations")
        if result["status_code"] != 201:
            self.log_result("Chat: Create Conversation", False, 
                          error=f"Status: {result['status_code']}")
            return
        
        conversation_id = result["data"]["data"]["conversation"]["id"]
        
        # Test financial messages
        financial_messages = [
            {
                "message": "Dapat beasiswa 3 juta",
                "expected_type": "income",
                "description": "Income detection test"
            },
            {
                "message": "ya",
                "expected_type": "confirmation",
                "description": "Confirmation test"
            },
            {
                "message": "Bayar listrik 200 ribu",
                "expected_type": "expense",
                "description": "Expense detection test"
            },
            {
                "message": "benar",
                "expected_type": "confirmation",
                "description": "Expense confirmation test"
            },
            {
                "message": "Mau nabung buat beli smartphone 8 juta",
                "expected_type": "savings_goal",
                "description": "Savings goal detection test"
            },
            {
                "message": "ok",
                "expected_type": "confirmation",
                "description": "Savings goal confirmation test"
            }
        ]
        
        for i, test_case in enumerate(financial_messages, 1):
            data = {"message": test_case["message"]}
            result = await self.make_request("POST", f"/api/v1/chat/conversations/{conversation_id}/messages", data)
            
            success = result["status_code"] == 200
            parser_type = None
            
            if success and "data" in result["data"]:
                response_data = result["data"]["data"]
                
                # Check for parser info in Luna response
                luna_response = response_data.get("luna_response", {})
                parser_info = response_data.get("parser_info", {})
                parser_type = parser_info.get("parser_type", "unknown")
                
                # Check if financial data was detected
                financial_data = response_data.get("financial_data")
                
                # Log additional info
                if financial_data:
                    print(f"    Financial Data: {financial_data}")
                
                # Check response metadata
                if luna_response.get("metadata"):
                    metadata = luna_response["metadata"]
                    if "parser_type" in metadata:
                        parser_type = metadata["parser_type"]
            
            self.log_result(f"Chat {i}: {test_case['description']}", 
                          success, parser_type, 
                          response_data={"message": test_case["message"]},
                          error=None if success else f"Status: {result['status_code']}")
            
            await asyncio.sleep(1)  # Realistic delay
    
    async def test_parser_status_endpoints(self):
        """Test parser status endpoints"""
        print("📊 Testing parser status endpoints...")
        
        # Test logs status
        result = await self.make_request("GET", "/logs/status")
        success = result["status_code"] == 200
        
        self.log_result("Parser Status: Logs", success,
                       error=None if success else f"Status: {result['status_code']}")
        
        # Test API info
        result = await self.make_request("GET", "/api/v1/info")
        success = result["status_code"] == 200
        
        parser_info = None
        if success and "data" in result["data"]:
            data_section = result["data"]["data"]
            luna_ai_info = data_section.get("luna_ai", {})
            parser_info = "IndoRoBERTa" if "IndoRoBERTa" in str(luna_ai_info) else "unknown"
        
        self.log_result("Parser Status: API Info", success, parser_info,
                       error=None if success else f"Status: {result['status_code']}")
    
    async def test_financial_queries(self):
        """Test financial queries yang memerlukan real data"""
        print("📈 Testing financial queries...")
        
        # First create conversation
        result = await self.make_request("POST", "/api/v1/chat/conversations")
        if result["status_code"] != 201:
            return
        
        conversation_id = result["data"]["data"]["conversation"]["id"]
        
        # Test financial queries
        queries = [
            "Total tabungan saya berapa?",
            "Budget performance bulan ini gimana?",
            "Kesehatan keuangan saya bagaimana?",
            "Daftar target tabungan saya"
        ]
        
        for i, query in enumerate(queries, 1):
            data = {"message": query}
            result = await self.make_request("POST", f"/api/v1/chat/conversations/{conversation_id}/messages", data)
            
            success = result["status_code"] == 200
            parser_type = None
            
            if success and "data" in result["data"]:
                parser_info = result["data"]["data"].get("parser_info", {})
                parser_type = parser_info.get("parser_type", "unknown")
            
            self.log_result(f"Financial Query {i}: {query[:40]}...", 
                          success, parser_type,
                          error=None if success else f"Status: {result['status_code']}")
    
    async def test_comparison_with_enhanced_parser(self):
        """Test comparison untuk melihat perbedaan dengan enhanced parser"""
        print("🔍 Testing comparison with enhanced parser...")
        
        # Create conversation
        result = await self.make_request("POST", "/api/v1/chat/conversations")
        if result["status_code"] != 201:
            return
        
        conversation_id = result["data"]["data"]["conversation"]["id"]
        
        # Test complex Indonesian financial expressions
        complex_messages = [
            "Dapet kiriman ortu 2.5 juta buat uang kuliah semester ini",
            "Bayar kos sama listrik total 950 ribu kemarin",
            "Freelance ngerjain website client dapat 1.8 juta minggu lalu",
            "Jajan di cafe bareng temen habis 75rb tadi siang",
            "Pengen nabung buat beli motor beat second sekitar 18 juta tahun depan"
        ]
        
        for i, message in enumerate(complex_messages, 1):
            data = {"message": message}
            result = await self.make_request("POST", f"/api/v1/chat/conversations/{conversation_id}/messages", data)
            
            success = result["status_code"] == 200
            parser_type = None
            financial_detected = False
            
            if success and "data" in result["data"]:
                response_data = result["data"]["data"]
                parser_info = response_data.get("parser_info", {})
                parser_type = parser_info.get("parser_type", "unknown")
                
                # Check if Luna detected financial data
                luna_response_content = response_data.get("luna_response", {}).get("content", "")
                financial_detected = any(phrase in luna_response_content.lower() for phrase in [
                    "detail transaksi", "target tabungan", "apakah informasi ini sudah benar",
                    "ketik ya untuk menyimpan", "dikategorikan sebagai"
                ])
            
            self.log_result(f"Complex Expression {i}: {message[:50]}...", 
                          success and financial_detected, parser_type,
                          response_data={"financial_detected": financial_detected},
                          error=None if success else f"Status: {result['status_code']}")
    
    async def generate_integration_report(self):
        """Generate comprehensive integration report"""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        # Analyze parser types
        parser_types = {}
        financial_detection_count = 0
        
        for result in self.test_results:
            parser_type = result.get("parser_type", "unknown")
            if parser_type not in parser_types:
                parser_types[parser_type] = 0
            parser_types[parser_type] += 1
            
            # Count financial detections
            if result.get("response_data") and isinstance(result["response_data"], dict):
                if (result["response_data"].get("is_financial_data") or 
                    result["response_data"].get("financial_detected")):
                    financial_detection_count += 1
        
        # Determine primary parser
        primary_parser = max(parser_types.items(), key=lambda x: x[1])[0] if parser_types else "unknown"
        
        report = {
            "test_summary": {
                "test_type": "IndoRoBERTa Integration Validation",
                "total_tests": total_tests,
                "passed": passed_tests,
                "failed": failed_tests,
                "success_rate": f"{success_rate:.1f}%",
                "primary_parser_detected": primary_parser,
                "financial_detections": financial_detection_count
            },
            "parser_analysis": {
                "parser_types_detected": parser_types,
                "indoroberta_usage": parser_types.get("IndoRoBERTa_ML", 0) + parser_types.get("IndoRoBERTa_Rules", 0),
                "enhanced_fallback_usage": parser_types.get("Enhanced_Fallback", 0),
                "unknown_parser_usage": parser_types.get("unknown", 0)
            },
            "integration_status": {
                "indoroberta_properly_integrated": primary_parser.startswith("IndoRoBERTa"),
                "ml_models_loaded": primary_parser == "IndoRoBERTa_ML",
                "using_fallback": primary_parser in ["Enhanced_Fallback", "Enhanced"],
                "integration_successful": success_rate >= 70 and primary_parser.startswith("IndoRoBERTa")
            },
            "detailed_results": self.test_results,
            "recommendations": [],
            "server_url": self.base_url,
            "generated_at": datetime.now().isoformat()
        }
        
        # Generate recommendations
        if not report["integration_status"]["indoroberta_properly_integrated"]:
            report["recommendations"].append("❌ IndoRoBERTa tidak terintegrasi dengan benar - check Luna AI Core initialization")
        
        if not report["integration_status"]["ml_models_loaded"]:
            report["recommendations"].append("⚠️ IndoRoBERTa ML models tidak ter-load - menggunakan rule-based fallback")
        
        if report["integration_status"]["using_fallback"]:
            report["recommendations"].append("🔄 Menggunakan fallback parser - check IndoRoBERTa model files dan dependencies")
        
        if financial_detection_count == 0:
            report["recommendations"].append("🚨 Tidak ada financial data yang terdeteksi - ada masalah dengan parser integration")
        
        if success_rate < 80:
            report["recommendations"].append(f"📈 Success rate rendah ({success_rate:.1f}%) - investigate failed tests")
        
        if not report["recommendations"]:
            report["recommendations"].append("✅ IndoRoBERTa integration berhasil!")
        
        # Save report
        with open("logs/indoroberta_integration_report.json", "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        # Print summary
        print("=" * 80)
        print("INDOROBERTA INTEGRATION TEST REPORT")
        print("=" * 80)
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        print(f"Primary Parser: {primary_parser}")
        print(f"Financial Detections: {financial_detection_count}")
        print("\nParser Types Detected:")
        for parser_type, count in parser_types.items():
            print(f"  {parser_type}: {count}")
        print("\nIntegration Status:")
        for key, value in report["integration_status"].items():
            print(f"  {key}: {value}")
        print("\nRecommendations:")
        for rec in report["recommendations"]:
            print(f"  {rec}")
        print("=" * 80)
        print(f"Report saved to: logs/indoroberta_integration_report.json")
        print("=" * 80)
        
        return report

async def run_indoroberta_integration_test():
    """Run comprehensive IndoRoBERTa integration test"""
    print("🚀 Starting IndoRoBERTa Integration Test...")
    print(f"📍 Server: {BASE_URL}")
    print("🎯 Goal: Validate IndoRoBERTa integration in Luna AI")
    print("=" * 80)
    
    async with IndoRoBERTaIntegrationTester() as tester:
        # Setup
        setup_success = await tester.setup_test_user()
        if not setup_success:
            print("❌ Setup failed, aborting tests")
            return
        
        # Run tests
        await tester.test_health_check()
        await tester.test_financial_parsing_endpoint()
        await tester.test_chat_with_financial_data()
        await tester.test_parser_status_endpoints()
        await tester.test_financial_queries()
        await tester.test_comparison_with_enhanced_parser()
        
        # Generate report
        report = await tester.generate_integration_report()
        return report

if __name__ == "__main__":
    # Create logs directory
    import os
    os.makedirs("logs", exist_ok=True)
    
    # Run the test
    asyncio.run(run_indoroberta_integration_test())