# test_luna_ai_realistic_sessions.py - Realistic Conversation Sessions Test
import asyncio
import aiohttp
import json
import time
import random
import string
from datetime import datetime, timedelta
from typing import Dict, Any, List
import os

# Configuration
BASE_URL = "http://localhost:8000"

class LunaAIRealisticTester:
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.session = None
        self.access_token = None
        self.user_id = None
        self.test_results = []
        self.conversations_created = []
        self.test_account = None
        self.current_conversation_id = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def generate_test_account(self):
        """Generate unique test account"""
        timestamp = int(time.time())
        random_str = ''.join(random.choices(string.ascii_lowercase, k=5))
        
        self.test_account = {
            "username": f"testluna_{timestamp}_{random_str}",
            "email": f"luna_test_{timestamp}_{random_str}@test.com",
            "password": "Luna123456",
            "confirm_password": "Luna123456"
        }
        return self.test_account
    
    def log_result(self, test_name: str, success: bool, conversation_id: str = None, 
                  user_message: str = None, luna_response: str = None, 
                  error: str = None, duration: float = None, session_info: str = None,
                  financial_data_detected: bool = False, confirmation_requested: bool = False):
        """Enhanced logging for realistic conversation testing"""
        result = {
            "test_name": test_name,
            "success": success,
            "conversation_id": conversation_id,
            "user_message": user_message,
            "luna_response": luna_response[:200] + "..." if luna_response and len(luna_response) > 200 else luna_response,
            "timestamp": datetime.now().isoformat(),
            "error": error,
            "duration": duration,
            "session_info": session_info,
            "financial_data_detected": financial_data_detected,
            "confirmation_requested": confirmation_requested
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        conv_info = f" [Conv: {conversation_id[:8]}...]" if conversation_id else ""
        session_info_str = f" [{session_info}]" if session_info else ""
        msg_info = f"\n    User: '{user_message}'" if user_message else ""
        luna_info = f"\n    Luna: '{luna_response[:100]}...'" if luna_response else ""
        duration_info = f" ({duration:.2f}s)" if duration else ""
        financial_info = f"\n    💰 Financial: {financial_data_detected} | Confirmation: {confirmation_requested}" if user_message else ""
        
        print(f"{status} | {test_name}{conv_info}{session_info_str}{msg_info}{luna_info}{financial_info}{duration_info}")
        if error:
            print(f"    ❌ Error: {error}")
        print()
    
    async def make_request(self, method: str, endpoint: str, data: Dict[Any, Any] = None, 
                          headers: Dict[str, str] = None) -> Dict[Any, Any]:
        """Make HTTP request"""
        url = f"{self.base_url}{endpoint}"
        
        if self.access_token and headers is None:
            headers = {"Authorization": f"Bearer {self.access_token}"}
        elif self.access_token and headers:
            headers["Authorization"] = f"Bearer {self.access_token}"
        
        start_time = time.time()
        try:
            async with self.session.request(method, url, json=data, headers=headers) as response:
                response_data = await response.json()
                duration = time.time() - start_time
                return {
                    "status_code": response.status,
                    "data": response_data,
                    "duration": duration
                }
        except Exception as e:
            duration = time.time() - start_time
            return {
                "status_code": 500,
                "error": str(e),
                "duration": duration
            }
    
    async def create_conversation(self) -> str:
        """Create new conversation and return conversation_id"""
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
    
    async def send_message(self, message: str, conversation_id: str = None, expect_confirmation: bool = False):
        """Send message in conversation and analyze response"""
        if not conversation_id:
            conversation_id = self.current_conversation_id
            
        if not conversation_id:
            return None
            
        try:
            data = {"message": message}
            result = await self.make_request("POST", f"/api/v1/chat/conversations/{conversation_id}/messages", data)
            
            if result["status_code"] == 200 and result["data"]["success"]:
                luna_response = result["data"]["data"]["luna_response"]
                financial_data = result["data"]["data"].get("financial_data")
                
                # Analyze Luna's response for confirmation request
                content_lower = luna_response["content"].lower()
                confirmation_phrases = [
                    "apakah informasi ini sudah benar",
                    "ketik \"ya\" untuk menyimpan",
                    "ketik \"tidak\" untuk membatalkan",
                    "konfirmasi",
                    "setuju"
                ]
                is_asking_confirmation = any(phrase in content_lower for phrase in confirmation_phrases)
                
                # Check if financial data was detected
                has_financial_data = bool(financial_data)
                
                return {
                    "success": True,
                    "conversation_id": conversation_id,
                    "luna_response": luna_response["content"],
                    "message_type": luna_response["message_type"],
                    "financial_data": financial_data,
                    "has_financial_data": has_financial_data,
                    "is_asking_confirmation": is_asking_confirmation,
                    "duration": result.get("duration", 0)
                }
            else:
                return {
                    "success": False,
                    "error": f"Status: {result['status_code']}",
                    "conversation_id": conversation_id,
                    "duration": result.get("duration", 0)
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "conversation_id": conversation_id,
                "duration": 0
            }
    
    # ==================== SETUP PHASE ====================
    
    async def setup_test_account(self):
        """Complete setup: Register -> Login -> Profile -> Financial"""
        print("🔧 Setting up test account for realistic Luna AI testing...")
        print("=" * 70)
        
        # 1. Health Check
        result = await self.make_request("GET", "/health")
        success = result["status_code"] == 200 and result["data"]["success"]
        self.log_result("Setup: Health Check", success, 
                      error=None if success else f"Status: {result['status_code']}")
        
        if not success:
            return False
        
        # 2. Register
        self.generate_test_account()
        result = await self.make_request("POST", "/api/v1/auth/register", self.test_account)
        success = result["status_code"] == 201 and result["data"]["success"]
        self.log_result("Setup: Registration", success,
                      error=None if success else f"Status: {result['status_code']}")
        
        if not success:
            return False
        
        # 3. Login
        login_data = {
            "email": self.test_account["email"],
            "password": self.test_account["password"]
        }
        result = await self.make_request("POST", "/api/v1/auth/login", login_data)
        success = result["status_code"] == 200 and result["data"]["success"]
        
        if success:
            tokens = result["data"]["data"]["tokens"]
            user_data = result["data"]["data"]["user"]
            self.access_token = tokens["access_token"]
            self.user_id = user_data["id"]
        
        self.log_result("Setup: Login", success,
                      error=None if success else f"Status: {result['status_code']}")
        
        if not success:
            return False
        
        # 4. Profile Setup
        profile_data = {
            "full_name": "Luna Test Student",
            "phone_number": "+628123456789",
            "university": "Universitas Indonesia",
            "city": "Jakarta",
            "occupation": "Mahasiswa & Part-time Developer",
            "notifications_enabled": True,
            "voice_enabled": True,
            "dark_mode": False
        }
        result = await self.make_request("POST", "/api/v1/auth/setup-profile", profile_data)
        success = result["status_code"] == 200 and result["data"]["success"]
        self.log_result("Setup: Profile", success,
                      error=None if success else f"Status: {result['status_code']}")
        
        if not success:
            return False
        
        # 5. Financial Setup 50/30/20
        financial_data = {
            "current_savings": 8000000,  # 8 juta initial savings
            "monthly_income": 4000000,   # 4 juta per bulan
            "primary_bank": "BCA Mobile"
        }
        result = await self.make_request("POST", "/api/v1/auth/setup-financial-50-30-20", financial_data)
        success = result["status_code"] == 200 and result["data"]["success"]
        
        if success:
            budget_info = result["data"]["data"].get("budget_allocation", {})
            print(f"💰 Budget 50/30/20 Setup:")
            print(f"   Monthly Income: Rp {financial_data['monthly_income']:,}")
            print(f"   NEEDS (50%): Rp {budget_info.get('needs_budget', 0):,.0f}")
            print(f"   WANTS (30%): Rp {budget_info.get('wants_budget', 0):,.0f}")
            print(f"   SAVINGS (20%): Rp {budget_info.get('savings_budget', 0):,.0f}")
        
        self.log_result("Setup: Financial 50/30/20", success,
                      error=None if success else f"Status: {result['status_code']}")
        
        return success
    
    # ==================== REALISTIC CONVERSATION SESSIONS ====================
    
    async def test_financial_transaction_session(self):
        """Test: Complete financial transaction session with confirmations"""
        print(f"\n💰 Testing: Financial Transaction Session with Confirmations")
        print("=" * 70)
        
        # Create conversation for financial transactions
        conversation_id = await self.create_conversation()
        if not conversation_id:
            self.log_result("Financial Session", False, error="Failed to create conversation")
            return
        
        # Scenario: Student receives money and makes expenses with confirmations
        transaction_flow = [
            {
                "message": "Dapat uang saku 3 juta dari ortu",
                "type": "income",
                "expect_confirmation": True,
                "description": "Income transaction"
            },
            {
                "message": "ya",
                "type": "confirmation", 
                "expect_confirmation": False,
                "description": "Confirm income"
            },
            {
                "message": "Bayar kos 1.2 juta",
                "type": "expense",
                "expect_confirmation": True,
                "description": "NEEDS expense"
            },
            {
                "message": "benar",
                "type": "confirmation",
                "expect_confirmation": False,
                "description": "Confirm kos payment"
            },
            {
                "message": "Beli bubble tea 28 ribu",
                "type": "expense",
                "expect_confirmation": True,
                "description": "WANTS expense"
            },
            {
                "message": "tidak",
                "type": "rejection",
                "expect_confirmation": False,
                "description": "Reject bubble tea"
            },
            {
                "message": "Beli bubble tea 25 ribu",
                "type": "expense",
                "expect_confirmation": True,
                "description": "Corrected WANTS expense"
            },
            {
                "message": "ok",
                "type": "confirmation",
                "expect_confirmation": False,
                "description": "Confirm corrected amount"
            }
        ]
        
        for i, step in enumerate(transaction_flow, 1):
            result = await self.send_message(step["message"], conversation_id, step["expect_confirmation"])
            
            if result and result["success"]:
                confirmation_match = result["is_asking_confirmation"] == step["expect_confirmation"]
                financial_detected = result["has_financial_data"] if step["type"] in ["income", "expense"] else False
                
                self.log_result(
                    f"Financial Session Step {i}: {step['description']}",
                    result["success"] and (confirmation_match or step["type"] in ["confirmation", "rejection"]),
                    conversation_id,
                    step["message"],
                    result["luna_response"],
                    duration=result["duration"],
                    session_info="Financial Transaction",
                    financial_data_detected=financial_detected,
                    confirmation_requested=result["is_asking_confirmation"]
                )
            else:
                self.log_result(
                    f"Financial Session Step {i}: {step['description']}",
                    False,
                    conversation_id,
                    step["message"],
                    error=result.get("error") if result else "No response",
                    session_info="Financial Transaction"
                )
            
            await asyncio.sleep(1.5)  # Realistic typing delay
    
    async def test_savings_goal_session(self):
        """Test: Savings goal management session"""
        print(f"\n🎯 Testing: Savings Goal Management Session")
        print("=" * 70)
        
        conversation_id = await self.create_conversation()
        if not conversation_id:
            self.log_result("Savings Goal Session", False, error="Failed to create conversation")
            return
        
        goal_flow = [
            {
                "message": "Mau nabung buat beli laptop gaming 15 juta",
                "description": "Create savings goal",
                "expect_confirmation": True
            },
            {
                "message": "ya",
                "description": "Confirm goal creation",
                "expect_confirmation": False
            },
            {
                "message": "Daftar target saya",
                "description": "List savings goals",
                "expect_confirmation": False
            },
            {
                "message": "Progress tabungan laptop",
                "description": "Check laptop progress",
                "expect_confirmation": False
            },
            {
                "message": "Ubah target laptop jadi 12 juta",
                "description": "Update laptop price",
                "expect_confirmation": False
            },
            {
                "message": "Target beli motor 22 juta pada tanggal 31 desember 2025",
                "description": "Create motor goal with deadline",
                "expect_confirmation": True
            },
            {
                "message": "setuju",
                "description": "Confirm motor goal",
                "expect_confirmation": False
            },
            {
                "message": "Semua target saya",
                "description": "List all goals",
                "expect_confirmation": False
            }
        ]
        
        for i, step in enumerate(goal_flow, 1):
            result = await self.send_message(step["message"], conversation_id)
            
            if result and result["success"]:
                self.log_result(
                    f"Savings Goal Step {i}: {step['description']}",
                    result["success"],
                    conversation_id,
                    step["message"],
                    result["luna_response"],
                    duration=result["duration"],
                    session_info="Savings Goals",
                    financial_data_detected=result["has_financial_data"],
                    confirmation_requested=result["is_asking_confirmation"]
                )
            else:
                self.log_result(
                    f"Savings Goal Step {i}: {step['description']}",
                    False,
                    conversation_id,
                    step["message"],
                    error=result.get("error") if result else "No response",
                    session_info="Savings Goals"
                )
            
            await asyncio.sleep(1.2)
    
    async def test_financial_consultation_session(self):
        """Test: Financial consultation and advice session"""
        print(f"\n💡 Testing: Financial Consultation Session")
        print("=" * 70)
        
        conversation_id = await self.create_conversation()
        if not conversation_id:
            self.log_result("Consultation Session", False, error="Failed to create conversation")
            return
        
        consultation_flow = [
            "Halo Luna, apa kabar?",
            "Kesehatan keuangan saya gimana?",
            "Total tabungan saya berapa sekarang?",
            "Analisis pengeluaran saya dong",
            "Tips hemat untuk mahasiswa Jakarta",
            "Jelaskan metode 50/30/20 secara sederhana",
            "Bagaimana cara mengoptimalkan budget WANTS?",
            "Rekomendasi investasi untuk mahasiswa"
        ]
        
        for i, message in enumerate(consultation_flow, 1):
            result = await self.send_message(message, conversation_id)
            
            if result and result["success"]:
                self.log_result(
                    f"Consultation Step {i}: {message[:30]}...",
                    result["success"],
                    conversation_id,
                    message,
                    result["luna_response"],
                    duration=result["duration"],
                    session_info="Financial Consultation",
                    financial_data_detected=result["has_financial_data"],
                    confirmation_requested=result["is_asking_confirmation"]
                )
            else:
                self.log_result(
                    f"Consultation Step {i}: {message[:30]}...",
                    False,
                    conversation_id,
                    message,
                    error=result.get("error") if result else "No response",
                    session_info="Financial Consultation"
                )
            
            await asyncio.sleep(1.0)
    
    async def test_purchase_analysis_session(self):
        """Test: Purchase analysis and decision session"""
        print(f"\n🛒 Testing: Purchase Analysis Session")
        print("=" * 70)
        
        conversation_id = await self.create_conversation()
        if not conversation_id:
            self.log_result("Purchase Analysis Session", False, error="Failed to create conversation")
            return
        
        purchase_flow = [
            "Saya ingin membeli iPhone 14 seharga 13 juta",
            "Budget WANTS saya masih berapa?",
            "Kalau saya beli HP second 8 juta gimana?",
            "Kapan waktu yang tepat untuk beli iPhone?",
            "Mau beli headphone Sony 2.5 juta juga",
            "Total kalau beli HP dan headphone berapa?",
            "Alternatif headphone yang lebih murah dong",
            "Tips nabung untuk gadget impian"
        ]
        
        for i, message in enumerate(purchase_flow, 1):
            result = await self.send_message(message, conversation_id)
            
            if result and result["success"]:
                self.log_result(
                    f"Purchase Analysis Step {i}: {message[:40]}...",
                    result["success"],
                    conversation_id,
                    message,
                    result["luna_response"],
                    duration=result["duration"],
                    session_info="Purchase Analysis",
                    financial_data_detected=result["has_financial_data"],
                    confirmation_requested=result["is_asking_confirmation"]
                )
            else:
                self.log_result(
                    f"Purchase Analysis Step {i}: {message[:40]}...",
                    False,
                    conversation_id,
                    message,
                    error=result.get("error") if result else "No response",
                    session_info="Purchase Analysis"
                )
            
            await asyncio.sleep(1.0)
    
    async def test_mixed_conversation_session(self):
        """Test: Mixed conversation with various topics"""
        print(f"\n🔄 Testing: Mixed Conversation Session")
        print("=" * 70)
        
        conversation_id = await self.create_conversation()
        if not conversation_id:
            self.log_result("Mixed Session", False, error="Failed to create conversation")
            return
        
        mixed_flow = [
            {
                "message": "Ongkos grabcar 35 ribu",
                "expect_financial": True,
                "expect_confirmation": True
            },
            {
                "message": "ya",
                "expect_financial": False,
                "expect_confirmation": False
            },
            {
                "message": "Performa budget bulan ini gimana?",
                "expect_financial": False,
                "expect_confirmation": False
            },
            {
                "message": "Freelance web design dapat 2.5 juta",
                "expect_financial": True,
                "expect_confirmation": True
            },
            {
                "message": "benar",
                "expect_financial": False,
                "expect_confirmation": False
            },
            {
                "message": "Mau beli mechanical keyboard 800 ribu, aman ga?",
                "expect_financial": False,
                "expect_confirmation": False
            },
            {
                "message": "Tips hemat transport di Jakarta",
                "expect_financial": False,
                "expect_confirmation": False
            }
        ]
        
        for i, step in enumerate(mixed_flow, 1):
            result = await self.send_message(step["message"], conversation_id)
            
            if result and result["success"]:
                financial_correct = result["has_financial_data"] == step["expect_financial"]
                confirmation_correct = result["is_asking_confirmation"] == step["expect_confirmation"]
                step_success = financial_correct and confirmation_correct
                
                self.log_result(
                    f"Mixed Session Step {i}: {step['message'][:40]}...",
                    step_success,
                    conversation_id,
                    step["message"],
                    result["luna_response"],
                    duration=result["duration"],
                    session_info="Mixed Conversation",
                    financial_data_detected=result["has_financial_data"],
                    confirmation_requested=result["is_asking_confirmation"]
                )
            else:
                self.log_result(
                    f"Mixed Session Step {i}: {step['message'][:40]}...",
                    False,
                    conversation_id,
                    step["message"],
                    error=result.get("error") if result else "No response",
                    session_info="Mixed Conversation"
                )
            
            await asyncio.sleep(1.3)
    
    async def test_error_recovery_session(self):
        """Test: Error recovery and correction session"""
        print(f"\n🔄 Testing: Error Recovery Session")
        print("=" * 70)
        
        conversation_id = await self.create_conversation()
        if not conversation_id:
            self.log_result("Error Recovery Session", False, error="Failed to create conversation")
            return
        
        error_recovery_flow = [
            "Bayar kos",  # Incomplete data
            "Maaf, maksud saya bayar kos 900 ribu",  # Correction
            "ya",  # Confirmation
            "asdfghjkl",  # Nonsense
            "Tolong abaikan pesan sebelumnya",  # Recovery
            "Beli buku algoritma 180 ribu",  # Proper transaction
            "tidak",  # Reject
            "Beli buku algoritma 165 ribu",  # Corrected amount
            "ok"  # Confirm
        ]
        
        for i, message in enumerate(error_recovery_flow, 1):
            result = await self.send_message(message, conversation_id)
            
            if result and result["success"]:
                self.log_result(
                    f"Error Recovery Step {i}: {message}",
                    result["success"],
                    conversation_id,
                    message,
                    result["luna_response"],
                    duration=result["duration"],
                    session_info="Error Recovery",
                    financial_data_detected=result["has_financial_data"],
                    confirmation_requested=result["is_asking_confirmation"]
                )
            else:
                self.log_result(
                    f"Error Recovery Step {i}: {message}",
                    False,
                    conversation_id,
                    message,
                    error=result.get("error") if result else "No response",
                    session_info="Error Recovery"
                )
            
            await asyncio.sleep(1.0)
    
    # ==================== INDIVIDUAL COMMAND TESTS ====================
    
    async def test_individual_commands(self):
        """Test: Individual commands for comparison"""
        print(f"\n⚡ Testing: Individual Commands (Each in new conversation)")
        print("=" * 70)
        
        individual_commands = [
            ("Dapat beasiswa PPA 4 juta", "Beasiswa Income"),
            ("Pengeluaran terbesar bulan ini", "Expense Analysis"),
            ("Target beli drone 6 juta", "New Savings Goal"),
            ("Budget NEEDS tersisa berapa", "Budget Check"),
            ("Cara menghemat biaya makan", "Saving Tips"),
            ("Saya mau beli sepatu Adidas 1.2 juta", "Purchase Analysis"),
            ("Progress semua target tabungan", "Goals Progress"),
            ("Tips investasi untuk pemula", "Investment Advice")
        ]
        
        for i, (command, description) in enumerate(individual_commands, 1):
            conversation_id = await self.create_conversation()
            
            if conversation_id:
                result = await self.send_message(command, conversation_id)
                
                if result and result["success"]:
                    self.log_result(
                        f"Individual Command {i}: {description}",
                        result["success"],
                        conversation_id,
                        command,
                        result["luna_response"],
                        duration=result["duration"],
                        session_info="Individual",
                        financial_data_detected=result["has_financial_data"],
                        confirmation_requested=result["is_asking_confirmation"]
                    )
                else:
                    self.log_result(
                        f"Individual Command {i}: {description}",
                        False,
                        conversation_id,
                        command,
                        error=result.get("error") if result else "No response",
                        session_info="Individual"
                    )
            else:
                self.log_result(
                    f"Individual Command {i}: {description}",
                    False,
                    None,
                    command,
                    error="Failed to create conversation",
                    session_info="Individual"
                )
            
            await asyncio.sleep(0.8)
    
    # ==================== CLEANUP & REPORTING ====================
    
    async def cleanup_test_data(self):
        """Cleanup test conversations and logout"""
        print(f"\n🧹 Cleaning up test data...")
        print("=" * 70)
        
        cleanup_success = 0
        cleanup_failed = 0
        
        # Delete conversations
        for conversation_id in self.conversations_created:
            try:
                result = await self.make_request("DELETE", f"/api/v1/chat/conversations/{conversation_id}")
                
                if result["status_code"] == 200 and result["data"]["success"]:
                    cleanup_success += 1
                else:
                    cleanup_failed += 1
                    
            except Exception as e:
                cleanup_failed += 1
        
        # Logout
        try:
            result = await self.make_request("POST", "/api/v1/auth/logout")
            logout_success = result["status_code"] == 200 and result["data"]["success"]
        except:
            logout_success = False
        
        self.log_result("Cleanup & Logout", cleanup_failed == 0 and logout_success, 
                      error=None if cleanup_failed == 0 and logout_success else f"Cleanup failed: {cleanup_failed}, Logout: {logout_success}")
        
        print(f"✅ Cleaned {cleanup_success} conversations")
        print(f"❌ Failed to clean {cleanup_failed} conversations") 
        print(f"🚪 Logout: {'Success' if logout_success else 'Failed'}")
    
    async def generate_realistic_test_report(self):
        """Generate comprehensive test report for realistic conversation sessions"""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        # Categorize by session type
        session_categories = {
            "Setup Phase": [r for r in self.test_results if r["test_name"].startswith("Setup:")],
            "Financial Transactions": [r for r in self.test_results if r.get("session_info") == "Financial Transaction"],
            "Savings Goals Management": [r for r in self.test_results if r.get("session_info") == "Savings Goals"],
            "Financial Consultation": [r for r in self.test_results if r.get("session_info") == "Financial Consultation"],
            "Purchase Analysis": [r for r in self.test_results if r.get("session_info") == "Purchase Analysis"],
            "Mixed Conversations": [r for r in self.test_results if r.get("session_info") == "Mixed Conversation"],
            "Error Recovery": [r for r in self.test_results if r.get("session_info") == "Error Recovery"],
            "Individual Commands": [r for r in self.test_results if r.get("session_info") == "Individual"],
            "System Operations": [r for r in self.test_results if r["test_name"] in ["Cleanup & Logout"]]
        }
        
        # Analyze conversation patterns
        confirmation_tests = [r for r in self.test_results if r.get("confirmation_requested")]
        financial_detection_tests = [r for r in self.test_results if r.get("financial_data_detected")]
        session_tests = [r for r in self.test_results if r.get("session_info") and r["session_info"] not in ["Individual", "Setup"]]
        
        # Calculate average response time
        response_times = [r["duration"] for r in self.test_results if r.get("duration")]
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        
        report = {
            "test_summary": {
                "test_type": "REALISTIC_CONVERSATION_SESSIONS",
                "total_tests": total_tests,
                "passed": passed_tests,
                "failed": failed_tests,
                "success_rate": f"{success_rate:.1f}%",
                "conversations_created": len(self.conversations_created),
                "test_account": self.test_account,
                "avg_response_time": f"{avg_response_time:.2f}s"
            },
            "conversation_analysis": {
                "total_sessions": len(session_tests),
                "individual_commands": len([r for r in self.test_results if r.get("session_info") == "Individual"]),
                "confirmation_requests": len(confirmation_tests),
                "financial_detections": len(financial_detection_tests),
                "session_vs_individual_ratio": f"{len(session_tests)}:{len([r for r in self.test_results if r.get('session_info') == 'Individual'])}"
            },
            "category_breakdown": {
                category: {
                    "total": len(results),
                    "passed": sum(1 for r in results if r["success"]),
                    "failed": sum(1 for r in results if not r["success"]),
                    "success_rate": f"{(sum(1 for r in results if r['success']) / len(results) * 100):.1f}%" if results else "0%"
                }
                for category, results in session_categories.items()
            },
            "luna_ai_performance": {
                "confirmation_accuracy": f"{len([r for r in confirmation_tests if r['success']]) / len(confirmation_tests) * 100:.1f}%" if confirmation_tests else "0%",
                "financial_detection_accuracy": f"{len([r for r in financial_detection_tests if r['success']]) / len(financial_detection_tests) * 100:.1f}%" if financial_detection_tests else "0%",
                "session_continuity": f"{len([r for r in session_tests if r['success']]) / len(session_tests) * 100:.1f}%" if session_tests else "0%",
                "average_response_time": f"{avg_response_time:.2f}s"
            },
            "detailed_results": self.test_results,
            "test_insights": {
                "strongest_areas": [],
                "improvement_areas": [],
                "recommendations": []
            },
            "server_url": self.base_url,
            "generated_at": datetime.now().isoformat()
        }
        
        # Generate insights
        for category, stats in report["category_breakdown"].items():
            if float(stats["success_rate"].replace("%", "")) >= 90:
                report["test_insights"]["strongest_areas"].append(f"{category} ({stats['success_rate']})")
            elif float(stats["success_rate"].replace("%", "")) < 70:
                report["test_insights"]["improvement_areas"].append(f"{category} ({stats['success_rate']})")
        
        # Generate recommendations
        if avg_response_time > 3.0:
            report["test_insights"]["recommendations"].append("Consider optimizing response time (current: {:.2f}s)".format(avg_response_time))
        if success_rate < 90:
            report["test_insights"]["recommendations"].append("Focus on improving overall success rate")
        if len(confirmation_tests) > 0 and len([r for r in confirmation_tests if r['success']]) / len(confirmation_tests) < 0.9:
            report["test_insights"]["recommendations"].append("Improve confirmation flow accuracy")
        
        if not report["test_insights"]["recommendations"]:
            report["test_insights"]["recommendations"].append("Excellent performance! Consider adding more complex test scenarios.")
        
        # Save reports
        os.makedirs("logs", exist_ok=True)
        
        # Detailed JSON report
        with open("logs/luna_realistic_sessions_report.json", "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        # Summary text report
        with open("logs/luna_realistic_sessions_summary.txt", "w", encoding="utf-8") as f:
            f.write("=" * 80 + "\n")
            f.write("LUNA AI REALISTIC CONVERSATION SESSIONS TEST REPORT\n")
            f.write("=" * 80 + "\n")
            f.write(f"Test Account: {self.test_account['email']}\n")
            f.write(f"Server URL: {self.base_url}\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Test Type: Realistic Conversation Sessions with Luna AI\n")
            f.write("\n")
            f.write("OVERALL SUMMARY:\n")
            f.write(f"Total Tests: {total_tests}\n")
            f.write(f"Passed: {passed_tests}\n") 
            f.write(f"Failed: {failed_tests}\n")
            f.write(f"Success Rate: {success_rate:.1f}%\n")
            f.write(f"Conversations Created: {len(self.conversations_created)}\n")
            f.write(f"Average Response Time: {avg_response_time:.2f}s\n")
            f.write("\n")
            f.write("CONVERSATION ANALYSIS:\n")
            conv_analysis = report["conversation_analysis"]
            f.write(f"Total Conversation Sessions: {conv_analysis['total_sessions']}\n")
            f.write(f"Individual Commands: {conv_analysis['individual_commands']}\n")
            f.write(f"Confirmation Requests: {conv_analysis['confirmation_requests']}\n")
            f.write(f"Financial Detections: {conv_analysis['financial_detections']}\n")
            f.write(f"Session vs Individual Ratio: {conv_analysis['session_vs_individual_ratio']}\n")
            f.write("\n")
            f.write("LUNA AI PERFORMANCE:\n")
            performance = report["luna_ai_performance"]
            f.write(f"Confirmation Accuracy: {performance['confirmation_accuracy']}\n")
            f.write(f"Financial Detection Accuracy: {performance['financial_detection_accuracy']}\n")
            f.write(f"Session Continuity: {performance['session_continuity']}\n")
            f.write(f"Average Response Time: {performance['average_response_time']}\n")
            f.write("\n")
            
            f.write("CATEGORY BREAKDOWN:\n")
            f.write("-" * 50 + "\n")
            for category, stats in report["category_breakdown"].items():
                f.write(f"{category}:\n")
                f.write(f"  Total: {stats['total']}, Passed: {stats['passed']}, Failed: {stats['failed']}\n")
                f.write(f"  Success Rate: {stats['success_rate']}\n")
                f.write("\n")
            
            f.write("TEST INSIGHTS:\n")
            f.write("-" * 50 + "\n")
            insights = report["test_insights"]
            if insights["strongest_areas"]:
                f.write("✅ Strongest Areas:\n")
                for area in insights["strongest_areas"]:
                    f.write(f"  - {area}\n")
                f.write("\n")
            
            if insights["improvement_areas"]:
                f.write("⚠️ Areas for Improvement:\n")
                for area in insights["improvement_areas"]:
                    f.write(f"  - {area}\n")
                f.write("\n")
            
            f.write("💡 Recommendations:\n")
            for rec in insights["recommendations"]:
                f.write(f"  - {rec}\n")
            f.write("\n")
            
            f.write("DETAILED RESULTS:\n")
            f.write("-" * 50 + "\n")
            for result in self.test_results:
                status = "PASS" if result["success"] else "FAIL"
                conv_info = f" [Conv: {result['conversation_id'][:8]}...]" if result.get('conversation_id') else ""
                session_info = f" [{result['session_info']}]" if result.get('session_info') else ""
                f.write(f"[{status}] {result['test_name']}{conv_info}{session_info}\n")
                if result.get("user_message"):
                    f.write(f"  User: {result['user_message']}\n")
                if result.get("luna_response"):
                    f.write(f"  Luna: {result['luna_response'][:100]}...\n")
                if result.get("financial_data_detected") is not None:
                    f.write(f"  Financial: {result['financial_data_detected']} | Confirmation: {result.get('confirmation_requested', False)}\n")
                if result["error"]:
                    f.write(f"  Error: {result['error']}\n")
                if result.get("duration"):
                    f.write(f"  Duration: {result['duration']:.2f}s\n")
                f.write("\n")
        
        print("=" * 80)
        print("LUNA AI REALISTIC CONVERSATION SESSIONS TEST COMPLETED")
        print("=" * 80)
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        print(f"Conversations Created: {len(self.conversations_created)}")
        print(f"Test Account: {self.test_account['email']}")
        print(f"Average Response Time: {avg_response_time:.2f}s")
        print("\nConversation Analysis:")
        print(f"  Session Tests: {conv_analysis['total_sessions']}")
        print(f"  Individual Commands: {conv_analysis['individual_commands']}")
        print(f"  Confirmation Accuracy: {performance['confirmation_accuracy']}")
        print(f"  Financial Detection: {performance['financial_detection_accuracy']}")
        print("\nReports saved to:")
        print("  - logs/luna_realistic_sessions_report.json")
        print("  - logs/luna_realistic_sessions_summary.txt")
        print("=" * 80)
        
        return report

async def run_realistic_luna_test():
    """Run realistic Luna AI conversation sessions test"""
    print("🚀 Starting REALISTIC Luna AI Conversation Sessions Test...")
    print(f"📍 Server: {BASE_URL}")
    print("🎭 Simulating realistic user interactions with Luna AI")
    print("💬 Focus: Conversation sessions, confirmations, context awareness")
    print("=" * 80)
    
    start_time = time.time()
    
    async with LunaAIRealisticTester() as tester:
        # Phase 1: Setup complete test account
        setup_success = await tester.setup_test_account()
        
        if not setup_success:
            print("❌ Test account setup failed, stopping tests")
            return
        
        print("\n✅ Test account setup completed successfully!")
        print("🤖 Luna AI is ready for realistic conversation testing")
        
        # Phase 2: Realistic conversation sessions
        await tester.test_financial_transaction_session()
        await tester.test_savings_goal_session()
        await tester.test_financial_consultation_session()
        await tester.test_purchase_analysis_session()
        await tester.test_mixed_conversation_session()
        await tester.test_error_recovery_session()
        
        # Phase 3: Individual commands for comparison
        await tester.test_individual_commands()
        
        # Phase 4: Cleanup
        await tester.cleanup_test_data()
        
        # Generate comprehensive report
        end_time = time.time()
        total_duration = end_time - start_time
        
        print(f"\n⏱️ Total test duration: {total_duration:.2f} seconds")
        
        report = await tester.generate_realistic_test_report()
        return report

if __name__ == "__main__":
    # Run the realistic conversation sessions test
    asyncio.run(run_realistic_luna_test())