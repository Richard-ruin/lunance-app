# test_luna_enhanced_natural_language.py - Test Luna AI After Enhanced Training
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

class LunaEnhancedNaturalLanguageTester:
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
            "username": f"lunaenhanced_{timestamp}_{random_str}",
            "email": f"luna_enhanced_{timestamp}_{random_str}@test.com",
            "password": "LunaEnhanced123",
            "confirm_password": "LunaEnhanced123"
        }
        return self.test_account
    
    def log_result(self, test_name: str, success: bool, conversation_id: str = None, 
                  user_message: str = None, luna_response: str = None, 
                  error: str = None, duration: float = None, test_category: str = None,
                  intent_detected: str = None, category_detected: str = None,
                  natural_language_score: float = None, enhanced_features: List[str] = None):
        """Enhanced logging for natural language testing"""
        result = {
            "test_name": test_name,
            "success": success,
            "conversation_id": conversation_id,
            "user_message": user_message,
            "luna_response": luna_response[:300] + "..." if luna_response and len(luna_response) > 300 else luna_response,
            "timestamp": datetime.now().isoformat(),
            "error": error,
            "duration": duration,
            "test_category": test_category,
            "intent_detected": intent_detected,
            "category_detected": category_detected,
            "natural_language_score": natural_language_score,
            "enhanced_features": enhanced_features or []
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        conv_info = f" [Conv: {conversation_id[:8]}...]" if conversation_id else ""
        category_info = f" [{test_category}]" if test_category else ""
        
        print(f"{status} | {test_name}{conv_info}{category_info}")
        if user_message:
            print(f"    📝 User: '{user_message}'")
        if luna_response:
            print(f"    🤖 Luna: '{luna_response[:100]}...'")
        if intent_detected:
            print(f"    🎯 Intent: {intent_detected}")
        if category_detected:
            print(f"    📂 Category: {category_detected}")
        if natural_language_score:
            print(f"    🌟 Natural Score: {natural_language_score:.1f}/10")
        if enhanced_features:
            print(f"    ✨ Enhanced Features: {', '.join(enhanced_features[:3])}")
        if duration:
            print(f"    ⏱️ Duration: {duration:.2f}s")
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
    
    async def send_enhanced_message(self, message: str, conversation_id: str = None):
        """Send message and analyze Luna's enhanced natural language understanding"""
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
                
                # Analyze Luna's understanding
                response_analysis = self.analyze_enhanced_response(message, luna_response, financial_data)
                
                return {
                    "success": True,
                    "conversation_id": conversation_id,
                    "luna_response": luna_response["content"],
                    "message_type": luna_response["message_type"],
                    "financial_data": financial_data,
                    "duration": result.get("duration", 0),
                    **response_analysis
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
    
    def analyze_enhanced_response(self, user_message: str, luna_response: Dict, financial_data: Dict = None):
        """Analyze Luna's response for enhanced natural language understanding"""
        analysis = {
            "intent_detected": None,
            "category_detected": None,
            "natural_language_score": 0,
            "enhanced_features": []
        }
        
        # Check if financial data was properly detected
        if financial_data:
            analysis["intent_detected"] = financial_data.get("intent", "unknown")
            analysis["category_detected"] = financial_data.get("category", "unknown")
        
        # Analyze natural language understanding based on response content
        response_content = luna_response["content"].lower()
        user_msg_lower = user_message.lower()
        
        # Check for enhanced features understanding
        enhanced_features_detected = []
        
        # 1. Slang and informal language
        slang_terms = ["dapet", "abis", "pengen", "bokap", "nyokap", "capek", "boros", "gregetan"]
        if any(term in user_msg_lower for term in slang_terms):
            if any(term in response_content for term in ["memahami", "mengerti", "tercatat"]):
                enhanced_features_detected.append("Slang Understanding")
        
        # 2. Regional terms
        regional_terms = ["bude", "pakde", "eyang", "mamah", "papah", "om", "tante"]
        if any(term in user_msg_lower for term in regional_terms):
            if financial_data or "keluarga" in response_content:
                enhanced_features_detected.append("Regional Terms")
        
        # 3. Modern payment methods
        modern_payments = ["gopay", "ovo", "dana", "spaylater", "gofood", "grab", "shopee"]
        if any(term in user_msg_lower for term in modern_payments):
            if financial_data or any(term in response_content for term in ["digital", "online", "aplikasi"]):
                enhanced_features_detected.append("Modern Payments")
        
        # 4. Emotional expressions
        emotions = ["alhamdulillah", "huhu", "sedih", "senang", "capek", "gregetan"]
        if any(term in user_msg_lower for term in emotions):
            if any(term in response_content for term in ["perasaan", "emosi", "memahami"]):
                enhanced_features_detected.append("Emotional Context")
        
        # 5. Natural amounts (ribu, rebu, k, juta, M)
        natural_amounts = ["ribu", "rebu", "juta", "jutaan", "k", "rb", "m"]
        if any(term in user_msg_lower for term in natural_amounts):
            if financial_data:
                enhanced_features_detected.append("Natural Amounts")
        
        # 6. Student context
        student_terms = ["kuliah", "kampus", "kos", "ukt", "spp", "tugas", "skripsi", "wisuda"]
        if any(term in user_msg_lower for term in student_terms):
            if any(term in response_content for term in ["mahasiswa", "kuliah", "pendidikan"]):
                enhanced_features_detected.append("Student Context")
        
        # 7. Contemporary brands
        brands = ["uniqlo", "h&m", "zara", "starbucks", "chatime", "mcd", "kfc"]
        if any(term in user_msg_lower for term in brands):
            if financial_data or "brand" in response_content:
                enhanced_features_detected.append("Brand Recognition")
        
        analysis["enhanced_features"] = enhanced_features_detected
        
        # Calculate natural language score
        score = 0
        
        # Base score for successful response
        if financial_data and luna_response["message_type"] != "error":
            score += 3
        elif luna_response["message_type"] != "error":
            score += 2
        
        # Bonus for enhanced features
        score += len(enhanced_features_detected) * 1.5
        
        # Bonus for contextual understanding
        if "memahami" in response_content or "mengerti" in response_content:
            score += 1
        
        # Bonus for proper intent detection
        if financial_data and financial_data.get("intent") in ["income", "expense", "savings_goal"]:
            score += 2
        
        # Cap at 10
        analysis["natural_language_score"] = min(score, 10)
        
        return analysis
    
    # ==================== SETUP PHASE ====================
    
    async def setup_test_account(self):
        """Setup test account for enhanced natural language testing"""
        print("🔧 Setting up enhanced test account...")
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
            "full_name": "Luna Enhanced Test User",
            "phone_number": "+6281234567890",
            "university": "Universitas Gadjah Mada",
            "city": "Yogyakarta",
            "occupation": "Mahasiswa Teknik Informatika",
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
        
        # 5. Financial Setup
        financial_data = {
            "current_savings": 5000000,  # 5 juta
            "monthly_income": 3000000,   # 3 juta per bulan
            "primary_bank": "BCA Mobile"
        }
        result = await self.make_request("POST", "/api/v1/auth/setup-financial-50-30-20", financial_data)
        success = result["status_code"] == 200 and result["data"]["success"]
        self.log_result("Setup: Financial 50/30/20", success,
                      error=None if success else f"Status: {result['status_code']}")
        
        return success
    
    # ==================== ENHANCED NATURAL LANGUAGE TESTS ====================
    
    async def test_slang_and_informal_language(self):
        """Test: Slang and informal Indonesian language understanding"""
        print(f"\n🗣️ Testing: Slang & Informal Language Understanding")
        print("=" * 70)
        
        conversation_id = await self.create_conversation()
        if not conversation_id:
            self.log_result("Slang Test", False, error="Failed to create conversation")
            return
        
        slang_expressions = [
            {
                "message": "Dapet 50rb dari freelance",
                "expected_intent": "income",
                "description": "Slang 'dapet' for received"
            },
            {
                "message": "Abis 25 rebu buat makan warteg",
                "expected_intent": "expense", 
                "description": "Slang 'abis' and 'rebu' for spent"
            },
            {
                "message": "Pengen nabung buat beli laptop gaming",
                "expected_intent": "savings_goal",
                "description": "Slang 'pengen' for want"
            },
            {
                "message": "Bokap kasih jajan 100rb",
                "expected_intent": "income",
                "description": "Slang 'bokap' for father"
            },
            {
                "message": "Nyokap transfer 200 ribu",
                "expected_intent": "income", 
                "description": "Slang 'nyokap' for mother"
            },
            {
                "message": "Boros banget bulan ini",
                "expected_intent": "non_financial",
                "description": "Slang 'boros' for wasteful"
            },
            {
                "message": "Capek deh abis 75k di coffee shop",
                "expected_intent": "expense",
                "description": "Multiple slang terms"
            },
            {
                "message": "Gregetan sama pengeluaran transport",
                "expected_intent": "non_financial",
                "description": "Slang 'gregetan' for frustrated"
            }
        ]
        
        for i, test_case in enumerate(slang_expressions, 1):
            result = await self.send_enhanced_message(test_case["message"], conversation_id)
            
            if result and result["success"]:
                intent_correct = result["intent_detected"] == test_case["expected_intent"]
                has_slang_feature = "Slang Understanding" in result["enhanced_features"]
                
                self.log_result(
                    f"Slang Test {i}: {test_case['description']}",
                    result["success"] and (intent_correct or test_case["expected_intent"] == "non_financial"),
                    conversation_id,
                    test_case["message"],
                    result["luna_response"],
                    duration=result["duration"],
                    test_category="Slang & Informal",
                    intent_detected=result["intent_detected"],
                    category_detected=result["category_detected"],
                    natural_language_score=result["natural_language_score"],
                    enhanced_features=result["enhanced_features"]
                )
            else:
                self.log_result(
                    f"Slang Test {i}: {test_case['description']}",
                    False,
                    conversation_id,
                    test_case["message"],
                    error=result.get("error") if result else "No response",
                    test_category="Slang & Informal"
                )
            
            await asyncio.sleep(1.0)
    
    async def test_regional_variations(self):
        """Test: Regional Indonesian language variations"""
        print(f"\n🏝️ Testing: Regional Language Variations")
        print("=" * 70)
        
        conversation_id = await self.create_conversation()
        if not conversation_id:
            self.log_result("Regional Test", False, error="Failed to create conversation")
            return
        
        regional_expressions = [
            {
                "message": "Bude transfer 150 ribu",
                "expected_intent": "income",
                "description": "Javanese 'bude' for aunt"
            },
            {
                "message": "Pakde kasih uang bensin 50rb",
                "expected_intent": "income",
                "description": "Javanese 'pakde' for uncle"
            },
            {
                "message": "Eyang kirim duit 300 ribu",
                "expected_intent": "income",
                "description": "Javanese 'eyang' for grandparent"
            },
            {
                "message": "Mamah beliin pulsa 25rb",
                "expected_intent": "income",
                "description": "Sundanese 'mamah' for mother"
            },
            {
                "message": "Papah bayarin UKT 5 juta",
                "expected_intent": "expense",
                "description": "Sundanese 'papah' for father"
            },
            {
                "message": "Om kasih duit jajan 75 ribu",
                "expected_intent": "income",
                "description": "Common 'om' for uncle"
            },
            {
                "message": "Tante transfer 100rb buat beli buku",
                "expected_intent": "income",
                "description": "Common 'tante' for aunt"
            }
        ]
        
        for i, test_case in enumerate(regional_expressions, 1):
            result = await self.send_enhanced_message(test_case["message"], conversation_id)
            
            if result and result["success"]:
                intent_correct = result["intent_detected"] == test_case["expected_intent"]
                has_regional_feature = "Regional Terms" in result["enhanced_features"]
                
                self.log_result(
                    f"Regional Test {i}: {test_case['description']}",
                    result["success"] and intent_correct,
                    conversation_id,
                    test_case["message"],
                    result["luna_response"],
                    duration=result["duration"],
                    test_category="Regional Variations",
                    intent_detected=result["intent_detected"],
                    category_detected=result["category_detected"],
                    natural_language_score=result["natural_language_score"],
                    enhanced_features=result["enhanced_features"]
                )
            else:
                self.log_result(
                    f"Regional Test {i}: {test_case['description']}",
                    False,
                    conversation_id,
                    test_case["message"],
                    error=result.get("error") if result else "No response",
                    test_category="Regional Variations"
                )
            
            await asyncio.sleep(1.0)
    
    async def test_modern_payment_methods(self):
        """Test: Modern payment methods and digital transactions"""
        print(f"\n💳 Testing: Modern Payment Methods")
        print("=" * 70)
        
        conversation_id = await self.create_conversation()
        if not conversation_id:
            self.log_result("Modern Payment Test", False, error="Failed to create conversation")
            return
        
        modern_payment_expressions = [
            {
                "message": "Gofood ayam geprek 35rb",
                "expected_intent": "expense",
                "description": "GoFood delivery order"
            },
            {
                "message": "Bayar via GoPay 28 ribu bubble tea",
                "expected_intent": "expense",
                "description": "GoPay payment method"
            },
            {
                "message": "Transfer OVO 45rb buat grab",
                "expected_intent": "expense",
                "description": "OVO digital wallet"
            },
            {
                "message": "Top up DANA 100 ribu",
                "expected_intent": "expense",
                "description": "DANA wallet top-up"
            },
            {
                "message": "Spaylater 150rb beli sepatu di shopee",
                "expected_intent": "expense",
                "description": "SPayLater buy now pay later"
            },
            {
                "message": "COD tokped 85rb skincare",
                "expected_intent": "expense",
                "description": "Tokopedia cash on delivery"
            },
            {
                "message": "Grabfood pizza 120 ribu",
                "expected_intent": "expense",
                "description": "GrabFood order"
            },
            {
                "message": "Cashback DANA 15rb dari belanja",
                "expected_intent": "income",
                "description": "Digital wallet cashback"
            }
        ]
        
        for i, test_case in enumerate(modern_payment_expressions, 1):
            result = await self.send_enhanced_message(test_case["message"], conversation_id)
            
            if result and result["success"]:
                intent_correct = result["intent_detected"] == test_case["expected_intent"]
                has_modern_payment = "Modern Payments" in result["enhanced_features"]
                
                self.log_result(
                    f"Modern Payment Test {i}: {test_case['description']}",
                    result["success"] and intent_correct,
                    conversation_id,
                    test_case["message"],
                    result["luna_response"],
                    duration=result["duration"],
                    test_category="Modern Payments",
                    intent_detected=result["intent_detected"],
                    category_detected=result["category_detected"],
                    natural_language_score=result["natural_language_score"],
                    enhanced_features=result["enhanced_features"]
                )
            else:
                self.log_result(
                    f"Modern Payment Test {i}: {test_case['description']}",
                    False,
                    conversation_id,
                    test_case["message"],
                    error=result.get("error") if result else "No response",
                    test_category="Modern Payments"
                )
            
            await asyncio.sleep(1.0)
    
    async def test_emotional_expressions(self):
        """Test: Emotional context and expressions"""
        print(f"\n😊 Testing: Emotional Expressions & Context")
        print("=" * 70)
        
        conversation_id = await self.create_conversation()
        if not conversation_id:
            self.log_result("Emotional Test", False, error="Failed to create conversation")
            return
        
        emotional_expressions = [
            {
                "message": "Alhamdulillah dapet beasiswa 5 juta",
                "expected_intent": "income",
                "description": "Grateful expression with income"
            },
            {
                "message": "Huhu abis 200rb laptop charger rusak",
                "expected_intent": "expense",
                "description": "Sad expression with expense"
            },
            {
                "message": "Sedih banget uang transport 30rb per hari",
                "expected_intent": "expense",
                "description": "Sad about daily expense"
            },
            {
                "message": "Senang banget part time honor 800rb",
                "expected_intent": "income",
                "description": "Happy about part-time income"
            },
            {
                "message": "Capek deh bayar kos 1.2 juta",
                "expected_intent": "expense",
                "description": "Tired expression with rent"
            },
            {
                "message": "Gregetan sama harga bubble tea mahal",
                "expected_intent": "non_financial",
                "description": "Frustrated about prices"
            },
            {
                "message": "Syukur alhamdulillah freelance 1.5 juta masuk",
                "expected_intent": "income",
                "description": "Thankful for freelance income"
            }
        ]
        
        for i, test_case in enumerate(emotional_expressions, 1):
            result = await self.send_enhanced_message(test_case["message"], conversation_id)
            
            if result and result["success"]:
                intent_correct = result["intent_detected"] == test_case["expected_intent"]
                has_emotional_context = "Emotional Context" in result["enhanced_features"]
                
                self.log_result(
                    f"Emotional Test {i}: {test_case['description']}",
                    result["success"] and (intent_correct or test_case["expected_intent"] == "non_financial"),
                    conversation_id,
                    test_case["message"],
                    result["luna_response"],
                    duration=result["duration"],
                    test_category="Emotional Context",
                    intent_detected=result["intent_detected"],
                    category_detected=result["category_detected"],
                    natural_language_score=result["natural_language_score"],
                    enhanced_features=result["enhanced_features"]
                )
            else:
                self.log_result(
                    f"Emotional Test {i}: {test_case['description']}",
                    False,
                    conversation_id,
                    test_case["message"],
                    error=result.get("error") if result else "No response",
                    test_category="Emotional Context"
                )
            
            await asyncio.sleep(1.0)
    
    async def test_student_specific_vocabulary(self):
        """Test: Student-specific vocabulary and context"""
        print(f"\n🎓 Testing: Student-Specific Vocabulary")
        print("=" * 70)
        
        conversation_id = await self.create_conversation()
        if not conversation_id:
            self.log_result("Student Vocab Test", False, error="Failed to create conversation")
            return
        
        student_expressions = [
            {
                "message": "Bayar UKT semester ini 7.5 juta",
                "expected_intent": "expense",
                "description": "University tuition (UKT)"
            },
            {
                "message": "Uang kos bulanan 800rb",
                "expected_intent": "expense",
                "description": "Monthly boarding house rent"
            },
            {
                "message": "Beli buku kuliah algoritma 150rb",
                "expected_intent": "expense",
                "description": "University textbook"
            },
            {
                "message": "Print skripsi sama jilid 85rb",
                "expected_intent": "expense",
                "description": "Thesis printing and binding"
            },
            {
                "message": "Les privat programming dapet 500rb",
                "expected_intent": "income",
                "description": "Private tutoring income"
            },
            {
                "message": "Organisasi event gathering 45rb",
                "expected_intent": "expense",
                "description": "Student organization event"
            },
            {
                "message": "Nabung buat wisuda tahun depan",
                "expected_intent": "savings_goal",
                "description": "Saving for graduation"
            },
            {
                "message": "Transport PP kampus 25rb per hari",
                "expected_intent": "expense",
                "description": "Daily campus transportation"
            }
        ]
        
        for i, test_case in enumerate(student_expressions, 1):
            result = await self.send_enhanced_message(test_case["message"], conversation_id)
            
            if result and result["success"]:
                intent_correct = result["intent_detected"] == test_case["expected_intent"]
                has_student_context = "Student Context" in result["enhanced_features"]
                
                self.log_result(
                    f"Student Vocab Test {i}: {test_case['description']}",
                    result["success"] and intent_correct,
                    conversation_id,
                    test_case["message"],
                    result["luna_response"],
                    duration=result["duration"],
                    test_category="Student Vocabulary",
                    intent_detected=result["intent_detected"],
                    category_detected=result["category_detected"],
                    natural_language_score=result["natural_language_score"],
                    enhanced_features=result["enhanced_features"]
                )
            else:
                self.log_result(
                    f"Student Vocab Test {i}: {test_case['description']}",
                    False,
                    conversation_id,
                    test_case["message"],
                    error=result.get("error") if result else "No response",
                    test_category="Student Vocabulary"
                )
            
            await asyncio.sleep(1.0)
    
    async def test_contemporary_brands_and_products(self):
        """Test: Contemporary brands and products recognition"""
        print(f"\n🏪 Testing: Contemporary Brands & Products")
        print("=" * 70)
        
        conversation_id = await self.create_conversation()
        if not conversation_id:
            self.log_result("Brands Test", False, error="Failed to create conversation")
            return
        
        brand_expressions = [
            {
                "message": "Beli hoodie Uniqlo 299rb",
                "expected_intent": "expense",
                "description": "Uniqlo clothing brand"
            },
            {
                "message": "Nongkrong Starbucks 65rb",
                "expected_intent": "expense",
                "description": "Starbucks coffee"
            },
            {
                "message": "Bubble tea Chatime 28rb",
                "expected_intent": "expense",
                "description": "Chatime bubble tea"
            },
            {
                "message": "Beli iPhone 14 second 8 juta",
                "expected_intent": "expense",
                "description": "iPhone specific model"
            },
            {
                "message": "Sneakers Nike Air Force 1.8 juta",
                "expected_intent": "expense",
                "description": "Nike sneakers specific model"
            },
            {
                "message": "Laptop MacBook Air M2 16 juta",
                "expected_intent": "expense",
                "description": "MacBook specific model"
            },
            {
                "message": "Makan KFC 45rb",
                "expected_intent": "expense",
                "description": "KFC fast food"
            },
            {
                "message": "Skincare Somethinc 120rb",
                "expected_intent": "expense",
                "description": "Local skincare brand"
            }
        ]
        
        for i, test_case in enumerate(brand_expressions, 1):
            result = await self.send_enhanced_message(test_case["message"], conversation_id)
            
            if result and result["success"]:
                intent_correct = result["intent_detected"] == test_case["expected_intent"]
                has_brand_recognition = "Brand Recognition" in result["enhanced_features"]
                
                self.log_result(
                    f"Brands Test {i}: {test_case['description']}",
                    result["success"] and intent_correct,
                    conversation_id,
                    test_case["message"],
                    result["luna_response"],
                    duration=result["duration"],
                    test_category="Brands & Products",
                    intent_detected=result["intent_detected"],
                    category_detected=result["category_detected"],
                    natural_language_score=result["natural_language_score"],
                    enhanced_features=result["enhanced_features"]
                )
            else:
                self.log_result(
                    f"Brands Test {i}: {test_case['description']}",
                    False,
                    conversation_id,
                    test_case["message"],
                    error=result.get("error") if result else "No response",
                    test_category="Brands & Products"
                )
            
            await asyncio.sleep(1.0)
    
    async def test_natural_amount_formats(self):
        """Test: Natural Indonesian amount formats"""
        print(f"\n💰 Testing: Natural Amount Formats")
        print("=" * 70)
        
        conversation_id = await self.create_conversation()
        if not conversation_id:
            self.log_result("Amount Format Test", False, error="Failed to create conversation")
            return
        
        amount_expressions = [
            {
                "message": "Dapat 50 rebu dari ngajar",
                "expected_intent": "income",
                "description": "Casual 'rebu' format"
            },
            {
                "message": "Abis lima ribu parkir",
                "expected_intent": "expense", 
                "description": "Written out amount"
            },
            {
                "message": "Transfer 1.5 juta ke tabungan",
                "expected_intent": "expense",
                "description": "Decimal juta format"
            },
            {
                "message": "Freelance project 2M selesai",
                "expected_intent": "income",
                "description": "M for million shorthand"
            },
            {
                "message": "Beli headphone 500k",
                "expected_intent": "expense",
                "description": "K for thousand shorthand"
            },
            {
                "message": "Uang jajan satu setengah juta",
                "expected_intent": "income",
                "description": "Mixed written format"
            },
            {
                "message": "Bayar 1,200,000 kontrak kos",
                "expected_intent": "expense",
                "description": "Formal comma format"
            },
            {
                "message": "Dapat bonus 750rb",
                "expected_intent": "income",
                "description": "Abbreviated ribu"
            }
        ]
        
        for i, test_case in enumerate(amount_expressions, 1):
            result = await self.send_enhanced_message(test_case["message"], conversation_id)
            
            if result and result["success"]:
                intent_correct = result["intent_detected"] == test_case["expected_intent"]
                has_natural_amounts = "Natural Amounts" in result["enhanced_features"]
                
                self.log_result(
                    f"Amount Format Test {i}: {test_case['description']}",
                    result["success"] and intent_correct,
                    conversation_id,
                    test_case["message"],
                    result["luna_response"],
                    duration=result["duration"],
                    test_category="Natural Amounts",
                    intent_detected=result["intent_detected"],
                    category_detected=result["category_detected"],
                    natural_language_score=result["natural_language_score"],
                    enhanced_features=result["enhanced_features"]
                )
            else:
                self.log_result(
                    f"Amount Format Test {i}: {test_case['description']}",
                    False,
                    conversation_id,
                    test_case["message"],
                    error=result.get("error") if result else "No response",
                    test_category="Natural Amounts"
                )
            
            await asyncio.sleep(1.0)
    
    async def test_complex_natural_sentences(self):
        """Test: Complex natural sentence understanding"""
        print(f"\n🔤 Testing: Complex Natural Sentences")
        print("=" * 70)
        
        conversation_id = await self.create_conversation()
        if not conversation_id:
            self.log_result("Complex Sentences Test", False, error="Failed to create conversation")
            return
        
        complex_expressions = [
            {
                "message": "Alhamdulillah bokap transfer 2 juta buat bayar UKT semester ini",
                "expected_intent": "income",
                "description": "Complex sentence with multiple elements"
            },
            {
                "message": "Capek deh tadi abis 120rb gofood pizza soalnya hujan",
                "expected_intent": "expense",
                "description": "Complex with reasoning and emotion"
            },
            {
                "message": "Pengen banget nabung 15 juta buat beli motor Yamaha Nmax tahun depan",
                "expected_intent": "savings_goal",
                "description": "Complex savings goal with timeline"
            },
            {
                "message": "Kemarin part time design poster dapet 400rb alhamdulillah",
                "expected_intent": "income",
                "description": "Complex with time and gratitude"
            },
            {
                "message": "Sedih banget bayar kos naik jadi 1.5 juta per bulan mulai bulan depan",
                "expected_intent": "expense",
                "description": "Complex with emotion and future tense"
            },
            {
                "message": "Mau beli laptop gaming ASUS ROG tapi mahal banget 25 juta",
                "expected_intent": "savings_goal",
                "description": "Complex with brand and hesitation"
            }
        ]
        
        for i, test_case in enumerate(complex_expressions, 1):
            result = await self.send_enhanced_message(test_case["message"], conversation_id)
            
            if result and result["success"]:
                intent_correct = result["intent_detected"] == test_case["expected_intent"]
                high_score = result["natural_language_score"] >= 7
                
                self.log_result(
                    f"Complex Sentences Test {i}: {test_case['description']}",
                    result["success"] and intent_correct and high_score,
                    conversation_id,
                    test_case["message"],
                    result["luna_response"],
                    duration=result["duration"],
                    test_category="Complex Sentences",
                    intent_detected=result["intent_detected"],
                    category_detected=result["category_detected"],
                    natural_language_score=result["natural_language_score"],
                    enhanced_features=result["enhanced_features"]
                )
            else:
                self.log_result(
                    f"Complex Sentences Test {i}: {test_case['description']}",
                    False,
                    conversation_id,
                    test_case["message"],
                    error=result.get("error") if result else "No response",
                    test_category="Complex Sentences"
                )
            
            await asyncio.sleep(1.2)
    
    # ==================== CLEANUP & REPORTING ====================
    
    async def cleanup_test_data(self):
        """Cleanup test conversations and logout"""
        print(f"\n🧹 Cleaning up enhanced test data...")
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
                      error=None if cleanup_failed == 0 and logout_success else f"Cleanup failed: {cleanup_failed}")
        
        print(f"✅ Cleaned {cleanup_success} conversations")
        print(f"❌ Failed to clean {cleanup_failed} conversations") 
        print(f"🚪 Logout: {'Success' if logout_success else 'Failed'}")
    
    async def generate_enhanced_test_report(self):
        """Generate comprehensive enhanced natural language test report"""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        overall_success_rate = float((passed_tests / total_tests * 100)) if total_tests > 0 else 0.0
        
        # Categorize by test type
        test_categories = {
            "Setup Phase": [r for r in self.test_results if r["test_name"].startswith("Setup:")],
            "Slang & Informal": [r for r in self.test_results if r.get("test_category") == "Slang & Informal"],
            "Regional Variations": [r for r in self.test_results if r.get("test_category") == "Regional Variations"],
            "Modern Payments": [r for r in self.test_results if r.get("test_category") == "Modern Payments"],
            "Emotional Context": [r for r in self.test_results if r.get("test_category") == "Emotional Context"],
            "Student Vocabulary": [r for r in self.test_results if r.get("test_category") == "Student Vocabulary"],
            "Brands & Products": [r for r in self.test_results if r.get("test_category") == "Brands & Products"],
            "Natural Amounts": [r for r in self.test_results if r.get("test_category") == "Natural Amounts"],
            "Complex Sentences": [r for r in self.test_results if r.get("test_category") == "Complex Sentences"],
            "System Operations": [r for r in self.test_results if r["test_name"] in ["Cleanup & Logout"]]
        }
        
        # Analyze enhanced features
        all_enhanced_features = []
        for result in self.test_results:
            if result.get("enhanced_features") and isinstance(result["enhanced_features"], list):
                all_enhanced_features.extend(result["enhanced_features"])
        
        feature_counts = {}
        for feature in all_enhanced_features:
            feature_counts[feature] = feature_counts.get(feature, 0) + 1
        
        # Calculate average scores
        nl_scores = [r.get("natural_language_score", 0) or 0 for r in self.test_results if r.get("natural_language_score") is not None]
        avg_nl_score = sum(nl_scores) / len(nl_scores) if nl_scores else 0
        
        response_times = [r["duration"] for r in self.test_results if r.get("duration")]
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        
        # Intent detection accuracy
        intent_tests = [r for r in self.test_results if r.get("intent_detected")]
        intent_accuracy = float(len([r for r in intent_tests if r["success"]]) / len(intent_tests) * 100) if intent_tests else 0.0
        
        report = {
            "test_summary": {
                "test_type": "ENHANCED_NATURAL_LANGUAGE",
                "description": "Testing Luna AI after enhanced IndoRoBERTa training",
                "total_tests": total_tests,
                "passed": passed_tests,
                "failed": failed_tests,
                "success_rate": f"{overall_success_rate:.1f}%",
                "conversations_created": len(self.conversations_created),
                "test_account": self.test_account,
                "avg_response_time": f"{avg_response_time:.2f}s"
            },
            "natural_language_analysis": {
                "average_nl_score": f"{avg_nl_score:.1f}/10",
                "intent_detection_accuracy": f"{intent_accuracy:.1f}%",
                "enhanced_features_detected": feature_counts,
                "total_feature_detections": sum(feature_counts.values()),
                "unique_features_found": len(feature_counts)
            },
            "category_breakdown": {
                category: {
                    "total": len(results),
                    "passed": sum(1 for r in results if r["success"]),
                    "failed": sum(1 for r in results if not r["success"]),
                    "success_rate": f"{float((sum(1 for r in results if r['success']) / len(results) * 100)):.1f}%" if results else "0%",
                    "avg_nl_score": f"{sum(r.get('natural_language_score', 0) or 0 for r in results) / len(results):.1f}" if results else "0"
                }
                for category, results in test_categories.items()
            },
            "enhanced_features_performance": {
                feature: {
                    "detections": count,
                    "success_rate": f"{float(len([r for r in self.test_results if r.get('enhanced_features') and feature in r.get('enhanced_features', []) and r['success']]) / count * 100):.1f}%" if count > 0 else "0%"
                }
                for feature, count in feature_counts.items()
            },
            "detailed_results": self.test_results,
            "enhancement_insights": {
                "strongest_enhancements": [],
                "improvement_areas": [],
                "recommendations": []
            },
            "server_url": self.base_url,
            "generated_at": datetime.now().isoformat()
        }
        
        # Generate enhancement insights
        for category, stats in report["category_breakdown"].items():
            if category != "System Operations" and category != "Setup Phase":
                category_success_rate = float(stats["success_rate"].replace("%", ""))
                nl_score = float(stats["avg_nl_score"])
                
                if category_success_rate >= 90 and nl_score >= 8:
                    report["enhancement_insights"]["strongest_enhancements"].append(f"{category} (Success: {stats['success_rate']}, NL Score: {stats['avg_nl_score']})")
                elif category_success_rate < 70 or nl_score < 6:
                    report["enhancement_insights"]["improvement_areas"].append(f"{category} (Success: {stats['success_rate']}, NL Score: {stats['avg_nl_score']})")
        
        # Generate recommendations
        if avg_nl_score < 7:
            report["enhancement_insights"]["recommendations"].append(f"Improve natural language understanding (current: {avg_nl_score:.1f}/10)")
        if intent_accuracy < 85:
            report["enhancement_insights"]["recommendations"].append(f"Enhance intent detection accuracy (current: {intent_accuracy:.1f}%)")
        if len(feature_counts) < 5:
            report["enhancement_insights"]["recommendations"].append("Train model on more diverse enhanced features")
        if avg_response_time > 3.0:
            report["enhancement_insights"]["recommendations"].append(f"Optimize response time (current: {avg_response_time:.2f}s)")
        
        if not report["enhancement_insights"]["recommendations"]:
            report["enhancement_insights"]["recommendations"].append("Excellent enhanced performance! Model training was successful.")
        
        # Save reports
        os.makedirs("logs", exist_ok=True)
        
        # Detailed JSON report
        with open("logs/luna_enhanced_natural_language_report.json", "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        # Summary text report
        with open("logs/luna_enhanced_natural_language_summary.txt", "w", encoding="utf-8") as f:
            f.write("=" * 80 + "\n")
            f.write("LUNA AI ENHANCED NATURAL LANGUAGE TEST REPORT\n")
            f.write("After Enhanced IndoRoBERTa Training\n")
            f.write("=" * 80 + "\n")
            f.write(f"Test Account: {self.test_account['email']}\n")
            f.write(f"Server URL: {self.base_url}\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Test Type: Enhanced Natural Indonesian Language Understanding\n")
            f.write("\n")
            f.write("OVERALL SUMMARY:\n")
            f.write(f"Total Tests: {total_tests}\n")
            f.write(f"Passed: {passed_tests}\n") 
            f.write(f"Failed: {failed_tests}\n")
            f.write(f"Success Rate: {overall_success_rate:.1f}%\n")
            f.write(f"Average Natural Language Score: {avg_nl_score:.1f}/10\n")
            f.write(f"Intent Detection Accuracy: {intent_accuracy:.1f}%\n")
            f.write(f"Average Response Time: {avg_response_time:.2f}s\n")
            f.write("\n")
            f.write("ENHANCED FEATURES ANALYSIS:\n")
            f.write(f"Total Feature Detections: {sum(feature_counts.values())}\n")
            f.write(f"Unique Features Found: {len(feature_counts)}\n")
            f.write("Feature Detection Counts:\n")
            for feature, count in sorted(feature_counts.items(), key=lambda x: x[1], reverse=True):
                success_rate = report["enhanced_features_performance"][feature]["success_rate"]
                f.write(f"  {feature}: {count} detections ({success_rate} success)\n")
            f.write("\n")
            
            f.write("CATEGORY BREAKDOWN:\n")
            f.write("-" * 50 + "\n")
            for category, stats in report["category_breakdown"].items():
                if category not in ["Setup Phase", "System Operations"]:
                    f.write(f"{category}:\n")
                    f.write(f"  Total: {stats['total']}, Passed: {stats['passed']}, Failed: {stats['failed']}\n")
                    f.write(f"  Success Rate: {stats['success_rate']}\n")
                    f.write(f"  Avg NL Score: {stats['avg_nl_score']}/10\n")
                    f.write("\n")
            
            f.write("ENHANCEMENT INSIGHTS:\n")
            f.write("-" * 50 + "\n")
            insights = report["enhancement_insights"]
            if insights["strongest_enhancements"]:
                f.write("✅ Strongest Enhanced Areas:\n")
                for area in insights["strongest_enhancements"]:
                    f.write(f"  - {area}\n")
                f.write("\n")
            
            if insights["improvement_areas"]:
                f.write("⚠️ Areas for Enhancement:\n")
                for area in insights["improvement_areas"]:
                    f.write(f"  - {area}\n")
                f.write("\n")
            
            f.write("💡 Recommendations:\n")
            for rec in insights["recommendations"]:
                f.write(f"  - {rec}\n")
            f.write("\n")
            
            f.write("DETAILED TEST RESULTS:\n")
            f.write("-" * 50 + "\n")
            for result in self.test_results:
                if result.get("test_category") and result["test_category"] not in ["Setup Phase", "System Operations"]:
                    status = "PASS" if result["success"] else "FAIL"
                    f.write(f"[{status}] {result['test_name']}\n")
                    if result.get("user_message"):
                        f.write(f"  Message: {result['user_message']}\n")
                    if result.get("intent_detected"):
                        f.write(f"  Intent: {result['intent_detected']}\n")
                    if result.get("natural_language_score"):
                        f.write(f"  NL Score: {result['natural_language_score']}/10\n")
                    if result.get("enhanced_features"):
                        f.write(f"  Features: {', '.join(result['enhanced_features'])}\n")
                    if result["error"]:
                        f.write(f"  Error: {result['error']}\n")
                    f.write("\n")
        
        print("=" * 80)
        print("LUNA AI ENHANCED NATURAL LANGUAGE TEST COMPLETED")
        print("=" * 80)
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {overall_success_rate:.1f}%")
        print(f"Average Natural Language Score: {avg_nl_score:.1f}/10")
        print(f"Intent Detection Accuracy: {intent_accuracy:.1f}%")
        print(f"Test Account: {self.test_account['email']}")
        print(f"Enhanced Features Detected: {len(feature_counts)} types")
        print(f"Total Feature Detections: {sum(feature_counts.values())}")
        print("\nTop Enhanced Features:")
        for feature, count in sorted(feature_counts.items(), key=lambda x: x[1], reverse=True)[:5]:
            success_rate = report["enhanced_features_performance"][feature]["success_rate"]
            print(f"  - {feature}: {count} ({success_rate})")
        print("\nReports saved to:")
        print("  - logs/luna_enhanced_natural_language_report.json")
        print("  - logs/luna_enhanced_natural_language_summary.txt")
        print("=" * 80)
        
        return report

async def run_enhanced_luna_test():
    """Run enhanced natural language Luna AI test"""
    print("🚀 Starting ENHANCED Luna AI Natural Language Test...")
    print(f"📍 Server: {BASE_URL}")
    print("🎭 Testing enhanced IndoRoBERTa model capabilities")
    print("🇮🇩 Focus: Natural Indonesian language understanding")
    print("✨ Enhanced features: Slang, regional terms, modern payments, emotions")
    print("=" * 80)
    
    start_time = time.time()
    
    async with LunaEnhancedNaturalLanguageTester() as tester:
        # Phase 1: Setup test account
        setup_success = await tester.setup_test_account()
        
        if not setup_success:
            print("❌ Enhanced test account setup failed, stopping tests")
            return
        
        print("\n✅ Enhanced test account setup completed!")
        print("🤖 Luna AI ready for enhanced natural language testing")
        
        # Phase 2: Enhanced natural language tests
        await tester.test_slang_and_informal_language()
        await tester.test_regional_variations()
        await tester.test_modern_payment_methods()
        await tester.test_emotional_expressions()
        await tester.test_student_specific_vocabulary()
        await tester.test_contemporary_brands_and_products()
        await tester.test_natural_amount_formats()
        await tester.test_complex_natural_sentences()
        
        # Phase 3: Cleanup
        await tester.cleanup_test_data()
        
        # Generate comprehensive report
        end_time = time.time()
        total_duration = end_time - start_time
        
        print(f"\n⏱️ Total enhanced test duration: {total_duration:.2f} seconds")
        
        report = await tester.generate_enhanced_test_report()
        return report

if __name__ == "__main__":
    # Run the enhanced natural language test
    asyncio.run(run_enhanced_luna_test())