# test_luna_ai_single_chat.py - Test Luna AI dengan satu conversation untuk semua perintah
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

class LunaAITesterSingleChat:
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.session = None
        self.access_token = None
        self.user_id = None
        self.conversation_id = None
        self.test_results = []
        self.message_count = 0
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def log_result(self, test_name: str, success: bool, message_count: int = None, user_message: str = None, response_data: Dict[Any, Any] = None, error: str = None):
        """Log test result"""
        result = {
            "test_name": test_name,
            "success": success,
            "message_count": message_count or self.message_count,
            "conversation_id": self.conversation_id,
            "user_message": user_message,
            "timestamp": datetime.now().isoformat(),
            "response_data": response_data,
            "error": error
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        msg_info = f" [Msg #{message_count or self.message_count}]" if self.conversation_id else ""
        cmd_info = f"\n    Command: '{user_message}'" if user_message else ""
        print(f"{status} | {test_name}{msg_info}{cmd_info}")
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
    
    async def send_message_to_conversation(self, message: str, test_name: str):
        """Send message to the main conversation"""
        if not self.conversation_id:
            self.log_result(f"{test_name} (No Conversation)", False, user_message=message, error="No conversation available")
            return None
        
        self.message_count += 1
        
        try:
            data = {"message": message}
            result = await self.make_request("POST", f"/api/v1/chat/conversations/{self.conversation_id}/messages", data)
            
            if result["status_code"] == 200 and result["data"]["success"]:
                luna_response = result["data"]["data"]["luna_response"]
                financial_data = result["data"]["data"].get("financial_data")
                
                response_summary = {
                    "luna_content": luna_response["content"][:150] + "..." if len(luna_response["content"]) > 150 else luna_response["content"],
                    "message_type": luna_response["message_type"],
                    "has_financial_data": bool(financial_data),
                    "response_type": result["data"]["data"].get("response_type"),
                    "message_number": self.message_count
                }
                
                self.log_result(test_name, True, self.message_count, message, response_summary)
                return {
                    "luna_response": luna_response,
                    "financial_data": financial_data,
                    "full_result": result["data"]
                }
            else:
                self.log_result(test_name, False, self.message_count, message, error=f"Status: {result['status_code']}")
                return None
                
        except Exception as e:
            self.log_result(test_name, False, self.message_count, message, error=str(e))
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
    
    async def test_create_main_conversation(self):
        """Test 3: Create main conversation for all tests"""
        try:
            result = await self.make_request("POST", "/api/v1/chat/conversations")
            
            if result["status_code"] == 201 and result["data"]["success"]:
                conversation_data = result["data"]["data"]["conversation"]
                self.conversation_id = conversation_data["id"]
                
                self.log_result("Create Main Conversation", True, response_data={
                    "conversation_id": self.conversation_id,
                    "title": conversation_data["title"],
                    "cleanup_stats": result["data"]["data"].get("cleanup_stats")
                })
            else:
                self.log_result("Create Main Conversation", False, error=f"Status: {result['status_code']}")
                
        except Exception as e:
            self.log_result("Create Main Conversation", False, error=str(e))
    
    async def test_greeting_and_introduction(self):
        """Test 4: Start conversation with greeting"""
        greeting_messages = [
            ("Halo Luna!", "Greeting"),
            ("Saya ingin belajar mengelola keuangan", "Introduction"),
            ("Bisakah kamu bantu saya dengan budgeting?", "Request Help")
        ]
        
        print(f"\n🔄 Testing conversation start with {len(greeting_messages)} messages")
        print("=" * 60)
        
        for i, (message, category) in enumerate(greeting_messages, 1):
            print(f"👋 {i}/{len(greeting_messages)}: {category}")
            
            result = await self.send_message_to_conversation(message, f"Greeting {i}: {category}")
            
            # Wait between messages
            await asyncio.sleep(1)
    
    async def test_financial_messages_single_chat(self):
        """Test 5: Test Luna AI financial parsing - all in same conversation"""
        
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
        
        print(f"\n🔄 Testing {len(test_messages)} financial messages - All in SAME conversation")
        print("=" * 60)
        
        for i, (message, category) in enumerate(test_messages, 1):
            print(f"💰 {i}/{len(test_messages)}: {category}")
            
            result = await self.send_message_to_conversation(message, f"Financial Message {i}: {category}")
            
            # Wait between messages to avoid overwhelming the server
            await asyncio.sleep(1)
    
    async def test_financial_queries_single_chat(self):
        """Test 6: Test financial queries - all in same conversation"""
        
        financial_queries = [
            ("Total tabungan saya berapa?", "Check Total Savings"),
            ("Daftar target saya", "List Savings Goals"),
            ("Performa budget bulan ini", "Budget Performance"),
            ("Pengeluaran terbesar saya apa?", "Biggest Expenses"),
            ("Budget NEEDS saya masih berapa?", "NEEDS Budget Check"),
            ("Budget WANTS tersisa berapa?", "WANTS Budget Check"),
            ("Progress tabungan laptop gimana?", "Laptop Progress"),
            ("Kesehatan keuangan saya gimana?", "Financial Health"),
            ("Analisis pengeluaran kategori makan", "Food Analysis"),
            ("Rekomendasi untuk budget bulan depan", "Budget Recommendation")
        ]
        
        print(f"\n🔄 Testing {len(financial_queries)} financial queries - All in SAME conversation")
        print("=" * 60)
        
        for i, (query, category) in enumerate(financial_queries, 1):
            print(f"📊 {i}/{len(financial_queries)}: {category}")
            
            result = await self.send_message_to_conversation(query, f"Financial Query {i}: {category}")
            
            # Wait between messages
            await asyncio.sleep(1)
    
    async def test_purchase_analysis_single_chat(self):
        """Test 7: Test purchase analysis scenarios - all in same conversation"""
        
        purchase_scenarios = [
            ("Saya ingin membeli iPhone seharga 15 juta", "Purchase Analysis - iPhone"),
            ("Rencana beli sepeda 3 juta, aman ga?", "Purchase Analysis - Sepeda"),
            ("Mau beli jaket branded 800 ribu", "Purchase Analysis - Jaket"),
            ("Pengen beli PS5 seharga 8 juta", "Purchase Analysis - PS5"),
            ("Ingin beli laptop gaming 25 juta", "Purchase Analysis - Gaming Laptop"),
            ("Beli skincare set 500 ribu worth it ga?", "Purchase Analysis - Skincare")
        ]
        
        print(f"\n🔄 Testing {len(purchase_scenarios)} purchase analysis - All in SAME conversation")
        print("=" * 60)
        
        for i, (scenario, category) in enumerate(purchase_scenarios, 1):
            print(f"🛍️ {i}/{len(purchase_scenarios)}: {category}")
            
            result = await self.send_message_to_conversation(scenario, f"Purchase Analysis {i}: {category}")
            
            # Wait between messages
            await asyncio.sleep(1)
    
    async def test_goal_management_single_chat(self):
        """Test 8: Test savings goal management - all in same conversation"""
        
        goal_commands = [
            ("Ubah target laptop jadi 12 juta", "Update Laptop Goal"),
            ("Ganti deadline motor ke bulan december", "Update Motor Deadline"),
            ("Buat target baru: tablet 5 juta", "Create Tablet Goal"),
            ("Progress semua target saya", "Check All Progress"),
            ("Hapus target motor", "Delete Motor Goal"),
            ("Target mana yang paling urgent?", "Most Urgent Goal")
        ]
        
        print(f"\n🔄 Testing {len(goal_commands)} goal management commands - All in SAME conversation")
        print("=" * 60)
        
        for i, (command, category) in enumerate(goal_commands, 1):
            print(f"🎯 {i}/{len(goal_commands)}: {category}")
            
            result = await self.send_message_to_conversation(command, f"Goal Management {i}: {category}")
            
            # Wait between messages
            await asyncio.sleep(1)
    
    async def test_advice_and_tips_single_chat(self):
        """Test 9: Test advice and tips - all in same conversation"""
        
        advice_requests = [
            ("Tips hemat untuk mahasiswa", "Money Saving Tips"),
            ("Jelaskan metode 50/30/20 lebih detail", "Budget Method Detail"),
            ("Cara efektif menabung untuk mahasiswa", "Savings Strategy"),
            ("Bagaimana mengatasi pengeluaran impulsif?", "Impulse Control"),
            ("Investasi apa yang cocok untuk mahasiswa?", "Student Investment"),
            ("Luna, saya sering boros, gimana solusinya?", "Spending Problem"),
            ("Tips cari penghasilan tambahan mahasiswa", "Side Income Tips")
        ]
        
        print(f"\n🔄 Testing {len(advice_requests)} advice requests - All in SAME conversation")
        print("=" * 60)
        
        for i, (request, category) in enumerate(advice_requests, 1):
            print(f"💡 {i}/{len(advice_requests)}: {category}")
            
            result = await self.send_message_to_conversation(request, f"Advice Request {i}: {category}")
            
            # Wait between messages
            await asyncio.sleep(0.8)
    
    async def test_conversation_context(self):
        """Test 10: Test conversation context and memory"""
        
        context_tests = [
            ("Berapa total pengeluaran saya tadi?", "Context - Previous Expenses"),
            ("Target laptop yang tadi saya ubah jadi berapa?", "Context - Previous Goal Change"),
            ("Coba rangkum percakapan kita hari ini", "Context - Conversation Summary"),
            ("Apa saran terbaik yang sudah kamu berikan?", "Context - Previous Advice"),
            ("Dari semua transaksi tadi, mana yang paling boros?", "Context - Transaction Analysis")
        ]
        
        print(f"\n🔄 Testing {len(context_tests)} context tests - Testing conversation memory")
        print("=" * 60)
        
        for i, (test, category) in enumerate(context_tests, 1):
            print(f"🧠 {i}/{len(context_tests)}: {category}")
            
            result = await self.send_message_to_conversation(test, f"Context Test {i}: {category}")
            
            # Wait between messages
            await asyncio.sleep(1)
    
    async def test_conversation_end(self):
        """Test 11: End conversation gracefully"""
        
        end_messages = [
            ("Terima kasih Luna, sangat membantu!", "Thank You"),
            ("Sampai jumpa!", "Goodbye")
        ]
        
        print(f"\n🔄 Testing conversation end with {len(end_messages)} messages")
        print("=" * 60)
        
        for i, (message, category) in enumerate(end_messages, 1):
            print(f"👋 {i}/{len(end_messages)}: {category}")
            
            result = await self.send_message_to_conversation(message, f"End {i}: {category}")
            
            # Wait between messages
            await asyncio.sleep(0.5)
    
    async def test_conversation_history(self):
        """Test 12: Get conversation history"""
        try:
            result = await self.make_request("GET", f"/api/v1/chat/conversations/{self.conversation_id}/messages")
            
            if result["status_code"] == 200 and result["data"]["success"]:
                messages = result["data"]["data"]["messages"]
                conversation = result["data"]["data"]["conversation"]
                
                self.log_result("Get Conversation History", True, response_data={
                    "total_messages": len(messages),
                    "conversation_message_count": conversation["message_count"],
                    "messages_match": len(messages) == conversation["message_count"]
                })
            else:
                self.log_result("Get Conversation History", False, error=f"Status: {result['status_code']}")
                
        except Exception as e:
            self.log_result("Get Conversation History", False, error=str(e))
    
    async def generate_report(self):
        """Generate test report"""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        report = {
            "test_summary": {
                "test_type": "SINGLE_CONVERSATION",
                "total_tests": total_tests,
                "passed": passed_tests,
                "failed": failed_tests,
                "success_rate": f"{success_rate:.1f}%",
                "total_messages_sent": self.message_count,
                "conversation_id": self.conversation_id
            },
            "test_results": self.test_results,
            "conversation_id": self.conversation_id,
            "total_messages": self.message_count,
            "account_used": TEST_ACCOUNT["email"],
            "server_url": self.base_url,
            "generated_at": datetime.now().isoformat()
        }
        
        # Save to file
        os.makedirs("logs", exist_ok=True)
        
        # Save detailed JSON report
        with open("logs/luna_test_single_chat_report.json", "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        # Save summary text report
        with open("logs/luna_test_single_chat_summary.txt", "w", encoding="utf-8") as f:
            f.write("=" * 60 + "\n")
            f.write("LUNA AI TEST REPORT - SINGLE CONVERSATION\n")
            f.write("=" * 60 + "\n")
            f.write(f"Test Account: {TEST_ACCOUNT['email']}\n")
            f.write(f"Server URL: {self.base_url}\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Test Type: All commands sent to SINGLE conversation\n")
            f.write(f"Conversation ID: {self.conversation_id}\n")
            f.write("\n")
            f.write("SUMMARY:\n")
            f.write(f"Total Tests: {total_tests}\n")
            f.write(f"Passed: {passed_tests}\n") 
            f.write(f"Failed: {failed_tests}\n")
            f.write(f"Success Rate: {success_rate:.1f}%\n")
            f.write(f"Total Messages Sent: {self.message_count}\n")
            f.write("\n")
            f.write("DETAILED RESULTS:\n")
            f.write("-" * 40 + "\n")
            
            for result in self.test_results:
                status = "PASS" if result["success"] else "FAIL"
                msg_info = f" [Msg #{result['message_count']}]" if result.get('message_count') else ""
                f.write(f"[{status}] {result['test_name']}{msg_info}\n")
                if result.get("user_message"):
                    f.write(f"  Command: {result['user_message']}\n")
                if result["error"]:
                    f.write(f"  Error: {result['error']}\n")
                f.write("\n")
        
        print("=" * 60)
        print("LUNA AI TEST COMPLETED - SINGLE CONVERSATION")
        print("=" * 60)
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        print(f"Total Messages Sent: {self.message_count}")
        print(f"Conversation ID: {self.conversation_id}")
        print("\nDetailed reports saved to:")
        print("  - logs/luna_test_single_chat_report.json")
        print("  - logs/luna_test_single_chat_summary.txt")
        print("=" * 60)
        
        return report

async def run_luna_tests_single_chat():
    """Run all Luna AI tests in single conversation"""
    print("🚀 Starting Luna AI Tests - SINGLE CONVERSATION...")
    print(f"📍 Server: {BASE_URL}")
    print(f"👤 Account: {TEST_ACCOUNT['email']}")
    print("🔄 Strategy: All commands will be sent to ONE conversation")
    print("=" * 60)
    
    start_time = time.time()
    
    async with LunaAITesterSingleChat() as tester:
        # Run all tests in sequence
        await tester.test_health_check()
        await tester.test_login()
        
        # Only continue if login successful
        if tester.access_token:
            await tester.test_create_main_conversation()
            
            # Only continue if conversation created
            if tester.conversation_id:
                await tester.test_greeting_and_introduction()
                await tester.test_financial_messages_single_chat()
                await tester.test_financial_queries_single_chat()
                await tester.test_purchase_analysis_single_chat()
                await tester.test_goal_management_single_chat()
                await tester.test_advice_and_tips_single_chat()
                await tester.test_conversation_context()
                await tester.test_conversation_end()
                await tester.test_conversation_history()
        
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
    asyncio.run(run_luna_tests_single_chat())