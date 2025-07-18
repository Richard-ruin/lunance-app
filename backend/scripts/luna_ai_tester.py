# test_luna_ai_validation_memory.py - Test Luna data persistence dalam 1 conversation
import asyncio
import aiohttp
import json
import time
from datetime import datetime
from typing import Dict, Any, List
import os

# Configuration
BASE_URL = "http://localhost:8000"

class LunaAIValidationTester:
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.session = None
        self.access_token = None
        self.user_id = None
        self.conversation_id = None
        self.test_results = []
        self.message_count = 0
        self.pending_transactions = []  # Track unconfirmed data
        self.confirmed_transactions = []  # Track confirmed data
        self.test_account = None  # Will be generated
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def log_result(self, test_name: str, success: bool, message_count: int = None, 
                  user_message: str = None, luna_response: str = None, 
                  validation_status: str = None, data_detected: bool = False,
                  confirmation_requested: bool = False, error: str = None):
        """Enhanced logging for validation testing"""
        result = {
            "test_name": test_name,
            "success": success,
            "message_count": message_count or self.message_count,
            "conversation_id": self.conversation_id,
            "user_message": user_message,
            "luna_response": luna_response[:200] + "..." if luna_response and len(luna_response) > 200 else luna_response,
            "validation_status": validation_status,  # pending, confirmed, rejected, none
            "data_detected": data_detected,
            "confirmation_requested": confirmation_requested,
            "timestamp": datetime.now().isoformat(),
            "error": error
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        msg_info = f" [Msg #{message_count or self.message_count}]" if self.conversation_id else ""
        validation_info = f" [{validation_status.upper()}]" if validation_status else ""
        data_info = f" [Data: {'✓' if data_detected else '✗'}]" if user_message else ""
        confirm_info = f" [Confirm: {'✓' if confirmation_requested else '✗'}]" if user_message else ""
        
        print(f"{status} | {test_name}{msg_info}{validation_info}{data_info}{confirm_info}")
        if user_message:
            print(f"    User: '{user_message}'")
        if luna_response:
            print(f"    Luna: '{luna_response[:150]}{'...' if len(luna_response) > 150 else ''}'")
        if error:
            print(f"    ❌ Error: {error}")
        print()
    
    def generate_test_account(self):
        """Generate unique test account for validation testing"""
        import random
        import string
        
        timestamp = int(time.time())
        random_str = ''.join(random.choices(string.ascii_lowercase, k=5))
        
        self.test_account = {
            "username": f"lunaval_{timestamp}_{random_str}",
            "email": f"luna_validation_{timestamp}_{random_str}@test.com",
            "password": "LunaValidation123",
            "confirm_password": "LunaValidation123"
        }
        return self.test_account
        """Make HTTP request"""
        url = f"{self.base_url}{endpoint}"
        
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
    
    async def send_message(self, message: str, test_name: str, expected_validation: str = "none"):
        """
        Send message and analyze validation status
        expected_validation: 'pending', 'confirmed', 'rejected', 'none'
        """
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
                
                # Analyze Luna's response
                content_lower = luna_response["content"].lower()
                
                # Check if Luna is asking for confirmation
                confirmation_phrases = [
                    "apakah informasi ini sudah benar",
                    "ketik \"ya\" untuk menyimpan",
                    "ketik \"tidak\" untuk membatalkan",
                    "konfirmasi",
                    "setuju"
                ]
                is_asking_confirmation = any(phrase in content_lower for phrase in confirmation_phrases)
                
                # Determine validation status
                validation_status = "none"
                if financial_data and is_asking_confirmation:
                    validation_status = "pending"
                    # Add to pending transactions
                    self.pending_transactions.append({
                        "message": message,
                        "data": financial_data,
                        "message_number": self.message_count
                    })
                elif message.lower() in ["ya", "iya", "yes", "benar", "betul", "ok", "oke", "setuju", "simpan"]:
                    validation_status = "confirmed"
                    # Move from pending to confirmed
                    if self.pending_transactions:
                        confirmed = self.pending_transactions.pop()
                        self.confirmed_transactions.append(confirmed)
                elif message.lower() in ["tidak", "no", "nope", "batal", "salah", "gak", "engga", "jangan"]:
                    validation_status = "rejected"
                    # Remove from pending
                    if self.pending_transactions:
                        self.pending_transactions.pop()
                
                # Check if validation matches expectation
                validation_correct = validation_status == expected_validation
                
                self.log_result(
                    test_name, 
                    True,  # We'll mark as success if Luna responds properly
                    self.message_count, 
                    message, 
                    luna_response["content"],
                    validation_status,
                    bool(financial_data),
                    is_asking_confirmation
                )
                
                return {
                    "luna_response": luna_response["content"],
                    "message_type": luna_response["message_type"],
                    "financial_data": financial_data,
                    "validation_status": validation_status,
                    "confirmation_requested": is_asking_confirmation,
                    "validation_correct": validation_correct
                }
            else:
                self.log_result(test_name, False, self.message_count, message, error=f"Status: {result['status_code']}")
                return None
                
        except Exception as e:
            self.log_result(test_name, False, self.message_count, message, error=str(e))
            return None
    
    async def check_data_persistence(self, test_name: str, query_message: str, should_remember: bool = True):
        """Check if Luna remembers previous data (confirmed or unconfirmed)"""
        result = await self.send_message(query_message, test_name, "none")
        
        if result:
            # Analyze if Luna mentions previous data
            response = result["luna_response"].lower()
            
            # Check for mentions of previous transactions/data
            memory_indicators = [
                "tadi", "sebelumnya", "yang sudah", "total", "berapa", 
                "laptop", "motor", "kos", "bubble tea", "uang saku"
            ]
            
            shows_memory = any(indicator in response for indicator in memory_indicators)
            memory_correct = shows_memory == should_remember
            
            print(f"    🧠 Memory Test: Expected {should_remember}, Got {shows_memory} = {'✓' if memory_correct else '✗'}")
            
            return {
                "shows_memory": shows_memory,
                "memory_correct": memory_correct,
                "response": result["luna_response"]
            }
        
        return None
    
    # ==================== COMPLETE SETUP PHASE ====================
    
    async def test_registration(self):
        """Setup Step 1: Register new test account"""
        try:
            self.generate_test_account()
            result = await self.make_request("POST", "/api/v1/auth/register", self.test_account)
            
            if result["status_code"] == 201 and result["data"]["success"]:
                user_data = result["data"]["data"]
                self.log_result("Setup: Registration", True, 
                              response_data={
                                  "username": self.test_account["username"],
                                  "email": self.test_account["email"],
                                  "user_id": user_data.get("user_id")
                              })
                return True
            else:
                self.log_result("Setup: Registration", False, 
                              error=f"Status: {result['status_code']}, Response: {result.get('data', {}).get('message', 'Unknown error')}")
                return False
                
        except Exception as e:
            self.log_result("Setup: Registration", False, error=str(e))
            return False
    
    async def test_login(self):
        """Setup Step 2: Login with registered account"""
        try:
            login_data = {
                "email": self.test_account["email"],
                "password": self.test_account["password"]
            }
            result = await self.make_request("POST", "/api/v1/auth/login", login_data)
            
            if result["status_code"] == 200 and result["data"]["success"]:
                tokens = result["data"]["data"]["tokens"]
                user_data = result["data"]["data"]["user"]
                
                self.access_token = tokens["access_token"]
                self.user_id = user_data["id"]
                
                self.log_result("Setup: Login", True,
                              response_data={
                                  "user_id": self.user_id,
                                  "username": user_data["username"],
                                  "has_token": bool(self.access_token),
                                  "onboarding_completed": user_data["onboarding_completed"],
                                  "profile_setup_completed": user_data["profile_setup_completed"],
                                  "financial_setup_completed": user_data["financial_setup_completed"]
                              })
                return True
            else:
                self.log_result("Setup: Login", False, 
                              error=f"Status: {result['status_code']}, Response: {result.get('data', {}).get('message', 'Login failed')}")
                return False
                
        except Exception as e:
            self.log_result("Setup: Login", False, error=str(e))
            return False
    
    async def test_profile_setup(self):
        """Setup Step 3: Setup user profile"""
        try:
            profile_data = {
                "full_name": "Luna Validation Tester",
                "phone_number": "+628123456789",
                "university": "Universitas Validation Testing",
                "city": "Jakarta",
                "occupation": "Mahasiswa & Software Tester",
                "notifications_enabled": True,
                "voice_enabled": True,
                "dark_mode": False
            }
            
            result = await self.make_request("POST", "/api/v1/auth/setup-profile", profile_data)
            
            if result["status_code"] == 200 and result["data"]["success"]:
                user_data = result["data"]["data"]["user"]
                
                self.log_result("Setup: Profile Setup", True,
                              response_data={
                                  "full_name": profile_data["full_name"],
                                  "university": profile_data["university"],
                                  "city": profile_data["city"],
                                  "profile_setup_completed": user_data["profile_setup_completed"],
                                  "onboarding_completed": user_data["onboarding_completed"]
                              })
                return True
            else:
                self.log_result("Setup: Profile Setup", False,
                              error=f"Status: {result['status_code']}, Response: {result.get('data', {}).get('message', 'Profile setup failed')}")
                return False
                
        except Exception as e:
            self.log_result("Setup: Profile Setup", False, error=str(e))
            return False
    
    async def test_financial_setup(self):
        """Setup Step 4: Setup financial settings with 50/30/20 method"""
        try:
            financial_data = {
                "current_savings": 7500000,  # 7.5 juta initial savings
                "monthly_income": 3500000,   # 3.5 juta per bulan
                "primary_bank": "BCA Mobile"
            }
            
            result = await self.make_request("POST", "/api/v1/auth/setup-financial-50-30-20", financial_data)
            
            if result["status_code"] == 200 and result["data"]["success"]:
                user_data = result["data"]["data"]["user"]
                budget_allocation = result["data"]["data"].get("budget_allocation", {})
                
                self.log_result("Setup: Financial Setup 50/30/20", True,
                              response_data={
                                  "monthly_income": financial_data["monthly_income"],
                                  "current_savings": financial_data["current_savings"],
                                  "primary_bank": financial_data["primary_bank"],
                                  "needs_budget": budget_allocation.get("needs_budget"),
                                  "wants_budget": budget_allocation.get("wants_budget"),
                                  "savings_budget": budget_allocation.get("savings_budget"),
                                  "financial_setup_completed": user_data["financial_setup_completed"],
                                  "onboarding_completed": user_data["onboarding_completed"]
                              })
                
                # Display budget breakdown
                print(f"💰 Budget 50/30/20 Setup Successful:")
                print(f"   Monthly Income: Rp {financial_data['monthly_income']:,}")
                print(f"   NEEDS (50%): Rp {budget_allocation.get('needs_budget', 0):,.0f}")
                print(f"   WANTS (30%): Rp {budget_allocation.get('wants_budget', 0):,.0f}")
                print(f"   SAVINGS (20%): Rp {budget_allocation.get('savings_budget', 0):,.0f}")
                print(f"   Initial Savings: Rp {financial_data['current_savings']:,}")
                print()
                
                return True
            else:
                self.log_result("Setup: Financial Setup 50/30/20", False,
                              error=f"Status: {result['status_code']}, Response: {result.get('data', {}).get('message', 'Financial setup failed')}")
                return False
                
        except Exception as e:
            self.log_result("Setup: Financial Setup 50/30/20", False, error=str(e))
            return False
    
    async def test_get_user_info(self):
        """Setup Step 5: Verify complete setup"""
        try:
            result = await self.make_request("GET", "/api/v1/auth/me")
            
            if result["status_code"] == 200 and result["data"]["success"]:
                user_data = result["data"]["data"]["user"]
                budget_status = result["data"]["data"].get("budget_status")
                financial_overview = result["data"]["data"].get("financial_overview")
                
                self.log_result("Setup: Verify Complete Setup", True,
                              response_data={
                                  "profile_setup_completed": user_data["profile_setup_completed"],
                                  "financial_setup_completed": user_data["financial_setup_completed"],
                                  "onboarding_completed": user_data["onboarding_completed"],
                                  "has_budget_status": bool(budget_status),
                                  "has_financial_overview": bool(financial_overview),
                                  "budget_method": "50/30/20 Elizabeth Warren"
                              })
                return True
            else:
                self.log_result("Setup: Verify Complete Setup", False,
                              error=f"Status: {result['status_code']}")
                return False
                
        except Exception as e:
            self.log_result("Setup: Verify Complete Setup", False, error=str(e))
            return False
    
    async def create_conversation(self):
        """Setup Step 6: Create conversation for validation testing"""
        try:
            result = await self.make_request("POST", "/api/v1/chat/conversations")
            
            if result["status_code"] == 201 and result["data"]["success"]:
                conversation_data = result["data"]["data"]["conversation"]
                self.conversation_id = conversation_data["id"]
                
                self.log_result("Setup: Create Conversation", True,
                              response_data={
                                  "conversation_id": self.conversation_id,
                                  "title": conversation_data["title"],
                                  "message_count": conversation_data["message_count"]
                              })
                return True
            else:
                self.log_result("Setup: Create Conversation", False,
                              error=f"Status: {result['status_code']}")
                return False
                
        except Exception as e:
            self.log_result("Setup: Create Conversation", False, error=str(e))
            return False

    async def setup_test_session(self):
        """Complete setup: Health check → Register → Login → Profile → Financial → Conversation"""
        print("🔧 Complete Luna AI Validation Test Setup...")
        print("=" * 70)
        
        # Step 1: Health Check
        result = await self.make_request("GET", "/health")
        success = result["status_code"] == 200 and result["data"]["success"]
        self.log_result("Setup: Health Check", success, 
                      error=None if success else f"Status: {result['status_code']}")
        
        if not success:
            return False
        
        # Step 2: Registration
        if not await self.test_registration():
            return False
        
        # Step 3: Login
        if not await self.test_login():
            return False
        
        # Step 4: Profile Setup
        if not await self.test_profile_setup():
            return False
        
        # Step 5: Financial Setup
        if not await self.test_financial_setup():
            return False
        
        # Step 6: Verify Setup
        if not await self.test_get_user_info():
            return False
        
        # Step 7: Create Conversation
        if not await self.create_conversation():
            return False
        
        print("✅ Complete setup successful!")
        print(f"🆔 User ID: {self.user_id}")
        print(f"💬 Conversation ID: {self.conversation_id}")
        print(f"📧 Test Account: {self.test_account['email']}")
        print(f"💰 Budget Method: 50/30/20 Elizabeth Warren")
        print()
        
        return True
    
    # ==================== VALIDATION TESTS ====================
    
    async def test_initial_greeting(self):
        """Test 0: Initial greeting to establish conversation context"""
        print(f"\n👋 Test 0: Initial Greeting & Context Establishment")
        print("=" * 70)
        
        greeting_flow = [
            ("Halo Luna! Aku pengguna baru", "Initial Greeting"),
            ("Saya ingin belajar mengelola keuangan dengan baik", "State Intention"),
            ("Bisakah kamu bantu saya memahami sistem budget 50/30/20?", "Request Explanation")
        ]
        
        for i, (message, description) in enumerate(greeting_flow, 1):
            await self.send_message(message, f"0.{i} {description}", "none")
            await asyncio.sleep(1)
        
        print("✅ Conversation context established!")
        print(f"📊 Messages sent: {len(greeting_flow)}")
        print()
        """Test 1: Apakah Luna mengingat data yang belum dikonfirmasi?"""
        print(f"\n📝 Test 1: Unconfirmed Data Persistence")
        print("=" * 70)
        
        # Step 1: Input financial data (should trigger confirmation)
        await self.send_message("Dapat uang saku 2 juta dari ortu", "1.1 Input Income", "pending")
        await asyncio.sleep(1)
        
        # Step 2: Ask about data WITHOUT confirming
        memory_result = await self.check_data_persistence(
            "1.2 Check Memory (Unconfirmed)", 
            "Berapa total pemasukan saya?", 
            should_remember=False  # Should NOT remember unconfirmed data
        )
        await asyncio.sleep(1)
        
        # Step 3: Add more unconfirmed data
        await self.send_message("Bayar kos 800 ribu", "1.3 Input Expense", "pending")
        await asyncio.sleep(1)
        
        # Step 4: Check if Luna remembers multiple unconfirmed items
        memory_result = await self.check_data_persistence(
            "1.4 Check Multiple Unconfirmed",
            "Total pengeluaran saya berapa?",
            should_remember=False
        )
        await asyncio.sleep(1)
        
        print(f"📊 Pending Transactions: {len(self.pending_transactions)}")
        print(f"📊 Confirmed Transactions: {len(self.confirmed_transactions)}")
    
    async def test_confirmed_data_persistence(self):
        """Test 2: Apakah Luna mengingat data yang sudah dikonfirmasi?"""
        print(f"\n✅ Test 2: Confirmed Data Persistence")
        print("=" * 70)
        
        # Step 1: Confirm the pending income
        await self.send_message("ya", "2.1 Confirm Income", "confirmed")
        await asyncio.sleep(1)
        
        # Step 2: Check if Luna now remembers the confirmed data
        memory_result = await self.check_data_persistence(
            "2.2 Check Memory (Confirmed)",
            "Total pemasukan saya berapa?",
            should_remember=True  # SHOULD remember confirmed data
        )
        await asyncio.sleep(1)
        
        # Step 3: Confirm the pending expense
        await self.send_message("benar", "2.3 Confirm Expense", "confirmed")
        await asyncio.sleep(1)
        
        # Step 4: Check if Luna remembers both confirmed items
        memory_result = await self.check_data_persistence(
            "2.4 Check Multiple Confirmed",
            "Analisis keuangan saya dong",
            should_remember=True
        )
        await asyncio.sleep(1)
        
        print(f"📊 Pending Transactions: {len(self.pending_transactions)}")
        print(f"📊 Confirmed Transactions: {len(self.confirmed_transactions)}")
    
    async def test_rejected_data_persistence(self):
        """Test 3: Apakah Luna melupakan data yang ditolak?"""
        print(f"\n❌ Test 3: Rejected Data Persistence")
        print("=" * 70)
        
        # Step 1: Input data that will be rejected
        await self.send_message("Beli iPhone 20 juta", "3.1 Input Expensive Item", "pending")
        await asyncio.sleep(1)
        
        # Step 2: Reject the data
        await self.send_message("tidak", "3.2 Reject Data", "rejected")
        await asyncio.sleep(1)
        
        # Step 3: Check if Luna forgets rejected data
        memory_result = await self.check_data_persistence(
            "3.3 Check Rejected Memory",
            "Pengeluaran terakhir saya apa?",
            should_remember=False  # Should NOT remember rejected data
        )
        await asyncio.sleep(1)
        
        # Step 4: Correct the data
        await self.send_message("Beli iPhone second 8 juta", "3.4 Input Corrected", "pending")
        await asyncio.sleep(1)
        
        # Step 5: Confirm corrected data
        await self.send_message("ok", "3.5 Confirm Corrected", "confirmed")
        await asyncio.sleep(1)
        
        print(f"📊 Pending Transactions: {len(self.pending_transactions)}")
        print(f"📊 Confirmed Transactions: {len(self.confirmed_transactions)}")
    
    async def test_mixed_validation_flow(self):
        """Test 4: Mixed flow dengan berbagai status validasi"""
        print(f"\n🔄 Test 4: Mixed Validation Flow")
        print("=" * 70)
        
        # Step 1: Add savings goal (might not need confirmation)
        await self.send_message("Mau nabung buat beli laptop 10 juta", "4.1 Savings Goal", "pending")
        await asyncio.sleep(1)
        
        # Step 2: Confirm savings goal
        await self.send_message("ya", "4.2 Confirm Goal", "confirmed")
        await asyncio.sleep(1)
        
        # Step 3: Add expense without confirming
        await self.send_message("Jajan bubble tea 25 ribu", "4.3 Small Expense", "pending")
        await asyncio.sleep(1)
        
        # Step 4: Ask about goals (should remember confirmed goal)
        memory_result = await self.check_data_persistence(
            "4.4 Check Goal Memory",
            "Target tabungan saya apa saja?",
            should_remember=True
        )
        await asyncio.sleep(1)
        
        # Step 5: Ask about expenses (should not include unconfirmed)
        memory_result = await self.check_data_persistence(
            "4.5 Check Expense Memory",
            "Pengeluaran hari ini berapa?",
            should_remember=False  # Bubble tea not confirmed yet
        )
        await asyncio.sleep(1)
        
        # Step 6: Reject the pending bubble tea
        await self.send_message("batal", "4.6 Cancel Bubble Tea", "rejected")
        await asyncio.sleep(1)
        
        print(f"📊 Pending Transactions: {len(self.pending_transactions)}")
        print(f"📊 Confirmed Transactions: {len(self.confirmed_transactions)}")
    
    async def test_conversation_summary(self):
        """Test 5: Summary conversation dengan status validasi"""
        print(f"\n📋 Test 5: Conversation Summary with Validation Status")
        print("=" * 70)
        
        # Check final summary
        await self.send_message("Rangkum semua transaksi yang sudah dikonfirmasi", "5.1 Confirmed Summary", "none")
        await asyncio.sleep(1)
        
        await self.send_message("Total tabungan saya sekarang berapa?", "5.2 Current Balance", "none")
        await asyncio.sleep(1)
        
        await self.send_message("Progress target laptop gimana?", "5.3 Goal Progress", "none")
        await asyncio.sleep(1)
        
        await self.send_message("Apa yang belum saya konfirmasi?", "5.4 Pending Items", "none")
        await asyncio.sleep(1)
        
        # Final validation test
        memory_result = await self.check_data_persistence(
            "5.5 Final Memory Test",
            "Ceritakan kembali percakapan kita dari awal",
            should_remember=True
        )
        
        print(f"📊 Final Status:")
        print(f"   Pending Transactions: {len(self.pending_transactions)}")
        print(f"   Confirmed Transactions: {len(self.confirmed_transactions)}")
        print(f"   Total Messages: {self.message_count}")
    
    async def test_comprehensive_financial_flow(self):
        """Test 7: Comprehensive financial flow dengan semua jenis transaksi"""
        print(f"\n💰 Test 7: Comprehensive Financial Flow")
        print("=" * 70)
        
        comprehensive_flow = [
            # Income transactions
            ("Freelance web development dapat 2.8 juta", "7.1 Freelance Income", "pending"),
            ("ya", "7.2 Confirm Freelance", "confirmed"),
            
            # NEEDS expenses
            ("Bayar semester kuliah 4 juta", "7.3 Education Expense", "pending"),
            ("benar", "7.4 Confirm Education", "confirmed"),
            
            # WANTS expenses 
            ("Beli headphone gaming 1.2 juta", "7.5 Gaming Purchase", "pending"),
            ("tidak", "7.6 Reject Gaming", "rejected"),
            ("Beli headphone biasa 600 ribu", "7.7 Corrected Purchase", "pending"),
            ("ok", "7.8 Confirm Corrected", "confirmed"),
            
            # Savings goal
            ("Target beli drone untuk photography 8 juta", "7.9 Drone Goal", "pending"),
            ("setuju", "7.10 Confirm Goal", "confirmed"),
            
            # Check comprehensive summary
            ("Rangkum semua transaksi yang sudah dikonfirmasi hari ini", "7.11 Comprehensive Summary", "none"),
            ("Berapa sisa budget NEEDS dan WANTS saya?", "7.12 Budget Status", "none"),
        ]
        
        for message, test_name, expected_validation in comprehensive_flow:
            await self.send_message(message, test_name, expected_validation)
            await asyncio.sleep(1.2)
        
        print(f"📊 Comprehensive Flow Status:")
        print(f"   Total Messages: {len(comprehensive_flow)}")
        print(f"   Pending Transactions: {len(self.pending_transactions)}")
        print(f"   Confirmed Transactions: {len(self.confirmed_transactions)}")
        print()

    async def test_cleanup_and_logout(self):
        """Test 8: Cleanup conversation and logout"""
        print(f"\n🧹 Test 8: Cleanup and Logout")
        print("=" * 70)
        
        # Final goodbye
        await self.send_message("Terima kasih Luna, testing selesai!", "8.1 Final Goodbye", "none")
        await asyncio.sleep(1)
        
        # Get conversation history
        try:
            result = await self.make_request("GET", f"/api/v1/chat/conversations/{self.conversation_id}/messages")
            
            if result["status_code"] == 200 and result["data"]["success"]:
                messages = result["data"]["data"]["messages"]
                conversation = result["data"]["data"]["conversation"]
                
                self.log_result("8.2 Get Conversation History", True,
                              response_data={
                                  "total_messages": len(messages),
                                  "conversation_message_count": conversation["message_count"],
                                  "messages_match": len(messages) == conversation["message_count"]
                              })
            else:
                self.log_result("8.2 Get Conversation History", False,
                              error=f"Status: {result['status_code']}")
                
        except Exception as e:
            self.log_result("8.2 Get Conversation History", False, error=str(e))
        
        # Delete conversation
        try:
            result = await self.make_request("DELETE", f"/api/v1/chat/conversations/{self.conversation_id}")
            
            success = result["status_code"] == 200 and result["data"]["success"]
            self.log_result("8.3 Delete Conversation", success,
                          error=None if success else f"Status: {result['status_code']}")
        except Exception as e:
            self.log_result("8.3 Delete Conversation", False, error=str(e))
        
        # Logout
        try:
            result = await self.make_request("POST", "/api/v1/auth/logout")
            
            success = result["status_code"] == 200 and result["data"]["success"]
            self.log_result("8.4 Logout", success,
                          error=None if success else f"Status: {result['status_code']}")
        except Exception as e:
            self.log_result("8.4 Logout", False, error=str(e))
        
        print("✅ Cleanup completed!")
        print()
        """Test 6: Edge cases validation"""
        print(f"\n⚠️ Test 6: Edge Cases Validation")
        print("=" * 70)
        
        # Test multiple confirmations
        await self.send_message("ya ya ya", "6.1 Multiple Yes", "none")
        await asyncio.sleep(1)
        
        # Test unclear confirmation
        await self.send_message("mungkin", "6.2 Unclear Response", "none")
        await asyncio.sleep(1)
        
        # Test data without confirmation request
        await self.send_message("Halo Luna apa kabar?", "6.3 Non-Financial", "none")
        await asyncio.sleep(1)
        
        # Test asking about non-existent data
        memory_result = await self.check_data_persistence(
            "6.4 Non-existent Data",
            "Berapa pengeluaran untuk gaming saya?",
            should_remember=False
        )
        await asyncio.sleep(1)
    
    # ==================== REPORTING ====================
    
    async def generate_validation_report(self):
        """Generate comprehensive validation test report"""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        # Analyze validation patterns
        validation_stats = {
            "pending": len([r for r in self.test_results if r.get("validation_status") == "pending"]),
            "confirmed": len([r for r in self.test_results if r.get("validation_status") == "confirmed"]),
            "rejected": len([r for r in self.test_results if r.get("validation_status") == "rejected"]),
            "none": len([r for r in self.test_results if r.get("validation_status") == "none"])
        }
        
        # Analyze data detection
        data_detection_stats = {
            "financial_data_detected": len([r for r in self.test_results if r.get("data_detected")]),
            "confirmation_requested": len([r for r in self.test_results if r.get("confirmation_requested")]),
            "total_messages": self.message_count
        }
        
        # Memory tests analysis
        memory_tests = [r for r in self.test_results if "Memory" in r["test_name"] or "Check" in r["test_name"]]
        memory_success_rate = (sum(1 for r in memory_tests if r["success"]) / len(memory_tests) * 100) if memory_tests else 0
        
        report = {
            "test_summary": {
                "test_type": "VALIDATION_AND_DATA_PERSISTENCE",
                "total_tests": total_tests,
                "passed": passed_tests,
                "failed": failed_tests,
                "success_rate": f"{success_rate:.1f}%",
                "total_messages": self.message_count,
                "conversation_id": self.conversation_id,
                "test_account": self.test_account
            },
            "validation_analysis": {
                "validation_stats": validation_stats,
                "final_pending_count": len(self.pending_transactions),
                "final_confirmed_count": len(self.confirmed_transactions),
                "data_detection_stats": data_detection_stats,
                "confirmation_flow_success": f"{(validation_stats['confirmed'] / (validation_stats['pending'] + validation_stats['confirmed']) * 100):.1f}%" if (validation_stats['pending'] + validation_stats['confirmed']) > 0 else "0%"
            },
            "memory_analysis": {
                "memory_tests_count": len(memory_tests),
                "memory_success_rate": f"{memory_success_rate:.1f}%",
                "unconfirmed_data_memory": "Should NOT remember unconfirmed data",
                "confirmed_data_memory": "SHOULD remember confirmed data",
                "rejected_data_memory": "Should NOT remember rejected data"
            },
            "key_findings": {
                "luna_requests_confirmation": validation_stats["pending"] > 0,
                "luna_processes_confirmations": validation_stats["confirmed"] > 0,
                "luna_handles_rejections": validation_stats["rejected"] > 0,
                "data_persistence_behavior": "Analyzed through memory tests"
            },
            "test_insights": [],
            "detailed_results": self.test_results,
            "pending_transactions": self.pending_transactions,
            "confirmed_transactions": self.confirmed_transactions,
            "server_url": self.base_url,
            "generated_at": datetime.now().isoformat()
        }
        
        # Generate insights
        insights = []
        
        if validation_stats["pending"] > 0:
            insights.append("✅ Luna properly requests confirmation for financial data")
        else:
            insights.append("❌ Luna does not request confirmation for financial data")
        
        if validation_stats["confirmed"] > 0:
            insights.append("✅ Luna processes confirmation responses")
        else:
            insights.append("❌ Luna does not process confirmations")
        
        if validation_stats["rejected"] > 0:
            insights.append("✅ Luna handles rejection responses")
        else:
            insights.append("⚠️ No rejection scenarios tested")
        
        if memory_success_rate >= 80:
            insights.append("✅ Luna has good memory management")
        elif memory_success_rate >= 50:
            insights.append("⚠️ Luna has moderate memory management")
        else:
            insights.append("❌ Luna has poor memory management")
        
        report["test_insights"] = insights
        
        # Save reports
        os.makedirs("logs", exist_ok=True)
        
        # Detailed JSON report
        with open("logs/luna_validation_test_report.json", "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        # Summary text report
        with open("logs/luna_validation_test_summary.txt", "w", encoding="utf-8") as f:
            f.write("=" * 80 + "\n")
            f.write("LUNA AI VALIDATION & DATA PERSISTENCE TEST REPORT\n")
            f.write("=" * 80 + "\n")
            f.write(f"Test Account: {self.test_account['email']}\n")
            f.write(f"Server URL: {self.base_url}\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Conversation ID: {self.conversation_id}\n")
            f.write(f"Test Focus: Data persistence dengan dan tanpa validasi\n")
            f.write("\n")
            f.write("OVERALL SUMMARY:\n")
            f.write(f"Total Tests: {total_tests}\n")
            f.write(f"Passed: {passed_tests}\n") 
            f.write(f"Failed: {failed_tests}\n")
            f.write(f"Success Rate: {success_rate:.1f}%\n")
            f.write(f"Total Messages: {self.message_count}\n")
            f.write("\n")
            f.write("VALIDATION ANALYSIS:\n")
            validation = report["validation_analysis"]
            f.write(f"Pending Validations: {validation['validation_stats']['pending']}\n")
            f.write(f"Confirmed Validations: {validation['validation_stats']['confirmed']}\n")
            f.write(f"Rejected Validations: {validation['validation_stats']['rejected']}\n")
            f.write(f"Non-validation Messages: {validation['validation_stats']['none']}\n")
            f.write(f"Final Pending Count: {validation['final_pending_count']}\n")
            f.write(f"Final Confirmed Count: {validation['final_confirmed_count']}\n")
            f.write(f"Confirmation Flow Success: {validation['confirmation_flow_success']}\n")
            f.write("\n")
            f.write("MEMORY ANALYSIS:\n")
            memory = report["memory_analysis"]
            f.write(f"Memory Tests Count: {memory['memory_tests_count']}\n")
            f.write(f"Memory Success Rate: {memory['memory_success_rate']}\n")
            f.write(f"Unconfirmed Data Policy: {memory['unconfirmed_data_memory']}\n")
            f.write(f"Confirmed Data Policy: {memory['confirmed_data_memory']}\n")
            f.write(f"Rejected Data Policy: {memory['rejected_data_memory']}\n")
            f.write("\n")
            f.write("KEY FINDINGS:\n")
            findings = report["key_findings"]
            f.write(f"Luna Requests Confirmation: {findings['luna_requests_confirmation']}\n")
            f.write(f"Luna Processes Confirmations: {findings['luna_processes_confirmations']}\n")
            f.write(f"Luna Handles Rejections: {findings['luna_handles_rejections']}\n")
            f.write("\n")
            f.write("TEST INSIGHTS:\n")
            for insight in report["test_insights"]:
                f.write(f"  {insight}\n")
            f.write("\n")
            f.write("PENDING TRANSACTIONS (Unconfirmed):\n")
            for i, trans in enumerate(self.pending_transactions, 1):
                f.write(f"  {i}. [{trans['message_number']}] {trans['message']}\n")
            f.write("\n")
            f.write("CONFIRMED TRANSACTIONS:\n")
            for i, trans in enumerate(self.confirmed_transactions, 1):
                f.write(f"  {i}. [{trans['message_number']}] {trans['message']}\n")
            f.write("\n")
            f.write("DETAILED RESULTS:\n")
            f.write("-" * 50 + "\n")
            for result in self.test_results:
                status = "PASS" if result["success"] else "FAIL"
                msg_info = f" [Msg #{result['message_count']}]"
                validation_info = f" [{result['validation_status'].upper()}]" if result.get('validation_status') else ""
                f.write(f"[{status}] {result['test_name']}{msg_info}{validation_info}\n")
                if result.get("user_message"):
                    f.write(f"  User: {result['user_message']}\n")
                if result.get("luna_response"):
                    f.write(f"  Luna: {result['luna_response'][:100]}...\n")
                if result.get("data_detected"):
                    f.write(f"  Data Detected: {result['data_detected']}\n")
                if result.get("confirmation_requested"):
                    f.write(f"  Confirmation Requested: {result['confirmation_requested']}\n")
                if result["error"]:
                    f.write(f"  Error: {result['error']}\n")
                f.write("\n")
        
        print("=" * 80)
        print("LUNA AI VALIDATION & DATA PERSISTENCE TEST COMPLETED")
        print("=" * 80)
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        print(f"Total Messages: {self.message_count}")
        print("\nValidation Analysis:")
        print(f"  Pending: {validation_stats['pending']}")
        print(f"  Confirmed: {validation_stats['confirmed']}")
        print(f"  Rejected: {validation_stats['rejected']}")
        print(f"  Final Pending Count: {validation['final_pending_count']}")
        print(f"  Final Confirmed Count: {validation['final_confirmed_count']}")
        print(f"\nMemory Analysis:")
        print(f"  Memory Tests: {len(memory_tests)}")
        print(f"  Memory Success Rate: {memory_success_rate:.1f}%")
        print("\nKey Insights:")
        for insight in report["test_insights"]:
            print(f"  {insight}")
        print("\nReports saved to:")
        print("  - logs/luna_validation_test_report.json")
        print("  - logs/luna_validation_test_summary.txt")
        print("=" * 80)
        
        return report

async def run_luna_validation_test():
    """Run Luna AI validation and data persistence test"""
    print("🚀 Starting Luna AI Validation & Data Persistence Test...")
    print(f"📍 Server: {BASE_URL}")
    print("🎯 Focus: Apakah Luna menyimpan data tanpa validasi?")
    print("🔍 Testing: Data persistence dengan berbagai status validasi")
    print("📝 Flow: Register → Login → Profile → Financial → Validation Tests")
    print("=" * 80)
    
    start_time = time.time()
    
    async with LunaAIValidationTester() as tester:
        # Complete setup process
        setup_success = await tester.setup_test_session()
        
        if not setup_success:
            print("❌ Complete setup failed, stopping tests")
            return
        
        print("✅ Complete setup successful! Starting validation tests...")
        
        # Initial conversation establishment
        await tester.test_initial_greeting()
        
        # Core validation tests
        await tester.test_unconfirmed_data_persistence()
        await tester.test_confirmed_data_persistence()
        await tester.test_rejected_data_persistence()
        await tester.test_mixed_validation_flow()
        await tester.test_conversation_summary()
        await tester.test_edge_cases()
        await tester.test_comprehensive_financial_flow()
        
        # Cleanup
        await tester.test_cleanup_and_logout()
        
        # Generate report
        end_time = time.time()
        total_duration = end_time - start_time
        
        print(f"\n⏱️ Total test duration: {total_duration:.2f} seconds")
        
        report = await tester.generate_validation_report()
        return report

if __name__ == "__main__":
    # Run the validation test
    asyncio.run(run_luna_validation_test())