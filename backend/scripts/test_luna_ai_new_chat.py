# test_luna_ai_new_chat.py - Test Luna AI dengan chat baru untuk setiap perintah
import asyncio
import aiohttp
import json
import time
from datetime import datetime
from typing import Dict, Any, List
import os

# Configuration
BASE_URL = "http://localhost:8000"
TEST_ACCOUNT = {
    "email": "richardpakpahan7383@gmail.com",
    "password": "P0o9i8u7"
}

class LunaAITesterNewChat:
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.session = None
        self.access_token = None
        self.user_id = None
        self.test_results = []
        self.conversations_created = []
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def log_result(self, test_name: str, success: bool, conversation_id: str = None, user_message: str = None, response_data: Dict[Any, Any] = None, error: str = None):
        """Log test result"""
        result = {
            "test_name": test_name,
            "success": success,
            "conversation_id": conversation_id,
            "user_message": user_message,
            "timestamp": datetime.now().isoformat(),
            "response_data": response_data,
            "error": error
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        conv_info = f" [Conv: {conversation_id}]" if conversation_id else ""
        msg_info = f"\n    Command: '{user_message}'" if user_message else ""
        print(f"{status} | {test_name}{conv_info}{msg_info}")
        if error:
            print(f"    Error: {error}")
        if response_data and success:
            print(f"    Response: {json.dumps(response_data, indent=2, ensure_ascii=False)[:200]}...")
        print()
    
    async def make_request(self, method: str, endpoint: str, data: Dict[Any, Any] = None, headers: Dict[str, str] = None) -> Dict[Any, Any]:
        """Make HTTP request"""
        url = f"{self.base_url}{endpoint}"
        
        # Add authorization header if token exists
        if self.access_token and headers is None:
            headers = {"Authorization": f"Bearer {self.access_token}"}
        elif self.access_token and headers:
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
    
    async def create_new_conversation(self) -> str:
        """Create a new conversation and return conversation_id"""
        try:
            result = await self.make_request("POST", "/api/v1/chat/conversations")
            
            if result["status_code"] == 201 and result["data"]["success"]:
                conversation_data = result["data"]["data"]["conversation"]
                conversation_id = conversation_data["id"]
                self.conversations_created.append(conversation_id)
                return conversation_id
            else:
                print(f"❌ Failed to create conversation: {result}")
                return None
                
        except Exception as e:
            print(f"❌ Error creating conversation: {e}")
            return None
    
    async def send_message_to_new_chat(self, message: str, test_name: str):
        """Send message to a new conversation"""
        # Create new conversation
        conversation_id = await self.create_new_conversation()
        
        if not conversation_id:
            self.log_result(f"{test_name} (Create Chat)", False, error="Failed to create conversation", user_message=message)
            return None
        
        # Send message to the new conversation
        try:
            data = {"message": message}
            result = await self.make_request("POST", f"/api/v1/chat/conversations/{conversation_id}/messages", data)
            
            if result["status_code"] == 200 and result["data"]["success"]:
                luna_response = result["data"]["data"]["luna_response"]
                financial_data = result["data"]["data"].get("financial_data")
                
                response_summary = {
                    "luna_content": luna_response["content"][:150] + "..." if len(luna_response["content"]) > 150 else luna_response["content"],
                    "message_type": luna_response["message_type"],
                    "has_financial_data": bool(financial_data),
                    "response_type": result["data"]["data"].get("response_type"),
                    "conversation_id": conversation_id
                }
                
                self.log_result(test_name, True, conversation_id, message, response_summary)
                return {
                    "conversation_id": conversation_id,
                    "luna_response": luna_response,
                    "financial_data": financial_data,
                    "full_result": result["data"]
                }
            else:
                self.log_result(test_name, False, conversation_id, message, error=f"Status: {result['status_code']}")
                return None
                
        except Exception as e:
            self.log_result(test_name, False, conversation_id, message, error=str(e))
            return None
    
    async def test_health_check(self):
        """Test 1: Health check"""
        try:
            result = await self.make_request("GET", "/health")
            
            if result["status_code"] == 200 and result["data"]["success"]:
                self.log_result("Health Check", True, response_data=result["data"])
            else:
                self.log_result("Health Check", False, error=f"Status: {result['status_code']}")
                
        except Exception as e:
            self.log_result("Health Check", False, error=str(e))
    
    async def test_login(self):
        """Test 2: Login with test account"""
        try:
            result = await self.make_request("POST", "/api/v1/auth/login", TEST_ACCOUNT)
            
            if result["status_code"] == 200 and result["data"]["success"]:
                # Extract token and user info
                tokens = result["data"]["data"]["tokens"]
                user_data = result["data"]["data"]["user"]
                
                self.access_token = tokens["access_token"]
                self.user_id = user_data["id"]
                
                self.log_result("Login Test Account", True, response_data={
                    "user_id": self.user_id,
                    "username": user_data["username"],
                    "has_token": bool(self.access_token),
                    "onboarding_completed": user_data["onboarding_completed"]
                })
            else:
                self.log_result("Login Test Account", False, error=f"Status: {result['status_code']}, Response: {result['data']}")
                
        except Exception as e:
            self.log_result("Login Test Account", False, error=str(e))
    
    async def test_financial_messages_new_chat(self):
        """Test 3: Test Luna AI financial parsing - setiap message di chat baru"""
        
        test_messages = [
            ("Dapat uang saku 2 juta dari ortu", "Income - Uang Saku"),
            ("Bayar kos 800 ribu", "Expense - Kos"),
            ("Jajan bubble tea 25 ribu", "Expense - Jajan"),
            ("Mau nabung buat beli laptop 10 juta", "Savings Goal - Laptop"),
            ("Belanja groceries 150 ribu", "Expense - Groceries"),
            ("Part time job dapat 500rb", "Income - Part Time"),
            ("Bayar listrik 100 ribu", "Expense - Utilities"),
            ("Target beli motor 20 juta dalam 8 bulan", "Savings Goal - Motor"),
            ("Freelance dapat 1.5 juta", "Income - Freelance"),
            ("Ongkos ojol 15rb", "Expense - Transport"),
            ("Dapat beasiswa 3 juta", "Income - Beasiswa"),
            ("Beli buku kuliah 200 ribu", "Expense - Education"),
            ("Makan warteg 25rb", "Expense - Food"),
            ("Nabung di bank 500rb", "Savings - Bank"),
            ("Bayar wifi 150rb", "Expense - Internet")
        ]
        
        print(f"\n🔄 Testing {len(test_messages)} financial messages - Each in NEW CHAT")
        print("=" * 60)
        
        for i, (message, category) in enumerate(test_messages, 1):
            print(f"📝 {i}/{len(test_messages)}: {category}")
            
            result = await self.send_message_to_new_chat(message, f"Financial Message {i}: {category}")
            
            # Wait between messages to avoid overwhelming the server
            await asyncio.sleep(1)
    
    async def test_general_questions_new_chat(self):
        """Test 4: Test Luna AI general questions - setiap question di chat baru"""
        
        general_questions = [
            ("Halo Luna, apa kabar?", "Greeting"),
            ("Jelaskan metode 50/30/20", "Budget Method Explanation"),
            ("Tips hemat untuk mahasiswa", "Money Saving Tips"),
            ("Bagaimana cara budgeting yang baik?", "Budgeting Advice"),
            ("Total tabungan saya berapa?", "Savings Check"),
            ("Kesehatan keuangan saya gimana?", "Financial Health"),
            ("Bantuan", "Help Request"),
            ("Analisis pengeluaran saya", "Expense Analysis"),
            ("Apa itu NEEDS dalam budget 50/30/20?", "NEEDS Explanation"),
            ("Contoh kategori WANTS untuk mahasiswa", "WANTS Examples"),
            ("Cara efektif menabung untuk mahasiswa", "Savings Strategy"),
            ("Luna, saya bingung ngatur keuangan", "Financial Confusion")
        ]
        
        print(f"\n🔄 Testing {len(general_questions)} general questions - Each in NEW CHAT")
        print("=" * 60)
        
        for i, (question, category) in enumerate(general_questions, 1):
            print(f"❓ {i}/{len(general_questions)}: {category}")
            
            result = await self.send_message_to_new_chat(question, f"General Question {i}: {category}")
            
            # Wait between messages
            await asyncio.sleep(0.7)
    
    async def test_financial_queries_new_chat(self):
        """Test 5: Test financial queries and analysis - setiap query di chat baru"""
        
        financial_queries = [
            ("Daftar target saya", "List Savings Goals"),
            ("Performa budget bulan ini", "Budget Performance"),
            ("Pengeluaran terbesar", "Biggest Expenses"),
            ("Saya ingin membeli iPhone seharga 15 juta", "Purchase Analysis - iPhone"),
            ("Budget NEEDS saya masih berapa?", "NEEDS Budget Check"),
            ("Progress tabungan laptop", "Laptop Savings Progress"),
            ("Ubah target laptop jadi 12 juta", "Update Savings Goal"),
            ("Hapus target motor", "Delete Savings Goal"),
            ("Saya mau beli sepeda 3 juta, aman ga?", "Purchase Analysis - Sepeda"),
            ("Budget WANTS tersisa berapa?", "WANTS Budget Check"),
            ("Pengeluaran bulan ini kategori makan", "Food Expenses"),
            ("Rekomendasi alokasi budget untuk mahasiswa", "Budget Allocation Advice")
        ]
        
        print(f"\n🔄 Testing {len(financial_queries)} financial queries - Each in NEW CHAT")
        print("=" * 60)
        
        for i, (query, category) in enumerate(financial_queries, 1):
            print(f"💰 {i}/{len(financial_queries)}: {category}")
            
            result = await self.send_message_to_new_chat(query, f"Financial Query {i}: {category}")
            
            # Wait between messages
            await asyncio.sleep(0.8)
    
    async def test_edge_cases_new_chat(self):
        """Test 6: Test edge cases dan error handling - setiap case di chat baru"""
        
        edge_cases = [
            ("", "Empty Message"),
            ("asdfghjkl", "Random Text"),
            ("Bayar kos", "Incomplete Financial Data"),
            ("Mau nabung", "Incomplete Savings Goal"),
            ("100 ribu", "Amount Only"),
            ("Saya ingin membeli", "Incomplete Purchase Query"),
            ("Ubah target", "Incomplete Update Command"),
            ("Target beli mobil 500 miliar", "Unrealistic Amount"),
            ("Bayar kos -800 ribu", "Negative Amount"),
            ("Dapat uang 0 rupiah", "Zero Amount"),
            ("Transfer ke Mars 1 juta", "Invalid Context"),
            ("Luna, kamu cantik ga?", "Personal Question")
        ]
        
        print(f"\n🔄 Testing {len(edge_cases)} edge cases - Each in NEW CHAT")
        print("=" * 60)
        
        for i, (message, category) in enumerate(edge_cases, 1):
            print(f"⚠️ {i}/{len(edge_cases)}: {category}")
            
            result = await self.send_message_to_new_chat(message, f"Edge Case {i}: {category}")
            
            # Wait between messages
            await asyncio.sleep(0.5)
    
    async def test_conversation_management(self):
        """Test 7: Test conversation management"""
        try:
            # Get conversations (should have many now)
            result = await self.make_request("GET", "/api/v1/chat/conversations")
            
            if result["status_code"] == 200 and result["data"]["success"]:
                conversations = result["data"]["data"]["conversations"]
                self.log_result("Get Conversations List", True, response_data={
                    "total_conversations": len(conversations),
                    "conversations_created_in_test": len(self.conversations_created),
                    "cleanup_stats": result["data"]["data"].get("cleanup_stats")
                })
            else:
                self.log_result("Get Conversations List", False, error=f"Status: {result['status_code']}")
                
        except Exception as e:
            self.log_result("Get Conversations List", False, error=str(e))
    
    async def cleanup_test_conversations(self):
        """Test 8: Cleanup conversations created during test"""
        print(f"\n🧹 Cleaning up {len(self.conversations_created)} test conversations...")
        
        cleanup_success = 0
        cleanup_failed = 0
        
        for conversation_id in self.conversations_created:
            try:
                result = await self.make_request("DELETE", f"/api/v1/chat/conversations/{conversation_id}")
                
                if result["status_code"] == 200 and result["data"]["success"]:
                    cleanup_success += 1
                else:
                    cleanup_failed += 1
                    
            except Exception as e:
                cleanup_failed += 1
        
        self.log_result("Cleanup Test Conversations", cleanup_failed == 0, response_data={
            "total_conversations": len(self.conversations_created),
            "cleanup_success": cleanup_success,
            "cleanup_failed": cleanup_failed
        })
    
    async def generate_report(self):
        """Generate test report"""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        report = {
            "test_summary": {
                "test_type": "NEW_CHAT_PER_COMMAND",
                "total_tests": total_tests,
                "passed": passed_tests,
                "failed": failed_tests,
                "success_rate": f"{success_rate:.1f}%",
                "conversations_created": len(self.conversations_created)
            },
            "test_results": self.test_results,
            "conversations_created": self.conversations_created,
            "account_used": TEST_ACCOUNT["email"],
            "server_url": self.base_url,
            "generated_at": datetime.now().isoformat()
        }
        
        # Save to file
        os.makedirs("logs", exist_ok=True)
        
        # Save detailed JSON report
        with open("logs/luna_test_new_chat_report.json", "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        # Save summary text report
        with open("logs/luna_test_new_chat_summary.txt", "w", encoding="utf-8") as f:
            f.write("=" * 60 + "\n")
            f.write("LUNA AI TEST REPORT - NEW CHAT PER COMMAND\n")
            f.write("=" * 60 + "\n")
            f.write(f"Test Account: {TEST_ACCOUNT['email']}\n")
            f.write(f"Server URL: {self.base_url}\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Test Type: Each command sent to NEW conversation\n")
            f.write("\n")
            f.write("SUMMARY:\n")
            f.write(f"Total Tests: {total_tests}\n")
            f.write(f"Passed: {passed_tests}\n") 
            f.write(f"Failed: {failed_tests}\n")
            f.write(f"Success Rate: {success_rate:.1f}%\n")
            f.write(f"Conversations Created: {len(self.conversations_created)}\n")
            f.write("\n")
            f.write("DETAILED RESULTS:\n")
            f.write("-" * 40 + "\n")
            
            for result in self.test_results:
                status = "PASS" if result["success"] else "FAIL"
                conv_info = f" [Conv: {result['conversation_id']}]" if result.get('conversation_id') else ""
                f.write(f"[{status}] {result['test_name']}{conv_info}\n")
                if result.get("user_message"):
                    f.write(f"  Command: {result['user_message']}\n")
                if result["error"]:
                    f.write(f"  Error: {result['error']}\n")
                f.write("\n")
        
        print("=" * 60)
        print("LUNA AI TEST COMPLETED - NEW CHAT PER COMMAND")
        print("=" * 60)
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        print(f"Conversations Created: {len(self.conversations_created)}")
        print("\nDetailed reports saved to:")
        print("  - logs/luna_test_new_chat_report.json")
        print("  - logs/luna_test_new_chat_summary.txt")
        print("=" * 60)
        
        return report

async def run_luna_tests_new_chat():
    """Run all Luna AI tests with new chat per command"""
    print("🚀 Starting Luna AI Tests - NEW CHAT PER COMMAND...")
    print(f"📍 Server: {BASE_URL}")
    print(f"👤 Account: {TEST_ACCOUNT['email']}")
    print("🔄 Strategy: Each command will be sent to a NEW conversation")
    print("=" * 60)
    
    start_time = time.time()
    
    async with LunaAITesterNewChat() as tester:
        # Run all tests in sequence
        await tester.test_health_check()
        await tester.test_login()
        
        # Only continue if login successful
        if tester.access_token:
            await tester.test_financial_messages_new_chat()
            await tester.test_general_questions_new_chat()
            await tester.test_financial_queries_new_chat()
            await tester.test_edge_cases_new_chat()
            await tester.test_conversation_management()
            await tester.cleanup_test_conversations()
        
        # Generate report
        end_time = time.time()
        duration = end_time - start_time
        
        # Update test duration in results
        for result in tester.test_results:
            if not hasattr(tester, '_duration_set'):
                result["test_duration"] = f"{duration:.2f}s"
        tester._duration_set = True
        
        report = await tester.generate_report()
        return report

if __name__ == "__main__":
    # Run the tests
    asyncio.run(run_luna_tests_new_chat())