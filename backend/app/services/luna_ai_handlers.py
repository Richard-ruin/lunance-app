# app/services/luna_ai_handlers.py - FIXED for Natural Language Priority
import random
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from bson import ObjectId

from ..config.database import get_database
from ..utils.timezone_utils import IndonesiaDatetime, now_for_db
from .luna_ai_base import LunaAIBase
from .finance_analyzer import FinanceAnalyzer
from .finance_advisor import FinanceAdvisor

import logging
logger = logging.getLogger(__name__)

class LunaAIHandlers(LunaAIBase):
    """FIXED Luna AI Handlers - Natural Language Priority"""
    
    def __init__(self):
        super().__init__()
        try:
            self.analyzer = FinanceAnalyzer()
            self.advisor = FinanceAdvisor()
        except Exception as e:
            logger.warning(f"Could not initialize analyzer/advisor: {e}")
            self.analyzer = None
            self.advisor = None
    
    # ==========================================
    # ENHANCED FINANCIAL DATA HANDLER
    # ==========================================
    
    async def handle_financial_data(self, user_id: str, conversation_id: str, message_id: str,
                                  transaction_type: str, amount: float, original_message: str) -> str:
        """ENHANCED: Handle financial data dengan natural language awareness"""
        
        logger.info(f"🎯 Processing financial data: type={transaction_type}, amount={amount}")
        logger.info(f"📝 Original message: '{original_message}'")
        
        # Get user's monthly income for budget calculation
        user_doc = self.db.users.find_one({"_id": ObjectId(user_id)})
        monthly_income = 0
        if user_doc and user_doc.get("financial_settings"):
            monthly_income = user_doc["financial_settings"].get("monthly_income", 0)
        
        # CRITICAL: Parse with full context untuk natural language
        parse_result = self.parser.parse_financial_data(original_message, monthly_income)
        
        if not parse_result["is_financial_data"]:
            logger.warning("⚠️ Parser says not financial data, but Luna detected it")
            # Fallback to Luna's detection
            parse_result = self._create_fallback_parse_result(transaction_type, amount, original_message)
        
        parsed_data = parse_result["parsed_data"]
        parsing_method = parse_result.get("parsing_method", "Unknown")
        
        logger.info(f"🔧 Parsing method: {parsing_method}")
        logger.info(f"📊 Parsed data: {parsed_data}")
        
        # ENHANCED: Natural language aware responses
        if transaction_type in ["income", "expense"]:
            return await self._handle_transaction_with_natural_context(
                user_id, conversation_id, message_id, transaction_type, 
                parsed_data, original_message, parsing_method
            )
        elif transaction_type == "savings_goal":
            return await self._handle_savings_goal_with_natural_context(
                user_id, conversation_id, message_id, 
                parsed_data, original_message, parsing_method
            )
        
        # Fallback
        return await self.handle_regular_message(original_message)
    
    def _create_fallback_parse_result(self, transaction_type: str, amount: float, original_message: str) -> Dict[str, Any]:
        """Create fallback parse result when ML parser fails"""
        if transaction_type in ["income", "expense"]:
            return {
                "is_financial_data": True,
                "confidence": 0.8,
                "data_type": transaction_type,
                "parsed_data": {
                    "type": transaction_type,
                    "amount": amount,
                    "category": "Lainnya" if transaction_type == "income" else "Lainnya (Wants)",
                    "budget_type": "income" if transaction_type == "income" else "wants",
                    "description": original_message[:100],
                    "date": datetime.now()
                },
                "parsing_method": "Luna_Fallback"
            }
        elif transaction_type == "savings_goal":
            return {
                "is_financial_data": True,
                "confidence": 0.8,
                "data_type": "savings_goal",
                "parsed_data": {
                    "item_name": self._extract_item_from_message(original_message),
                    "target_amount": amount,
                    "target_date": None,
                    "description": f"Target tabungan: {original_message[:100]}"
                },
                "parsing_method": "Luna_Fallback"
            }
    
    def _extract_item_from_message(self, message: str) -> str:
        """Extract item name from savings goal message"""
        # Remove common words and amount patterns
        clean_msg = message.lower()
        
        # Remove savings keywords
        for keyword in ['nabung', 'target', 'buat', 'beli', 'ingin', 'mau', 'pengen']:
            clean_msg = clean_msg.replace(keyword, '')
        
        # Remove amount patterns (simple)
        import re
        clean_msg = re.sub(r'\d+(?:[.,]\d+)?\s*(?:juta|ribu|rb|k|m)', '', clean_msg)
        clean_msg = re.sub(r'rp\.?\s*\d+', '', clean_msg)
        
        # Clean up
        clean_msg = re.sub(r'\s+', ' ', clean_msg).strip()
        
        return clean_msg.title()[:50] if clean_msg else "Target Baru"
    
    async def _handle_transaction_with_natural_context(self, user_id: str, conversation_id: str, 
                                                     message_id: str, transaction_type: str,
                                                     parsed_data: dict, original_message: str,
                                                     parsing_method: str) -> str:
        """Handle transaction dengan natural language context"""
        
        # Detect natural language patterns untuk response yang lebih personal
        message_lower = original_message.lower()
        
        # Natural language emotional context
        is_emotional = any(word in message_lower for word in [
            'alhamdulillah', 'syukur', 'senang', 'sedih', 'capek', 'gregetan', 
            'huhu', 'hehe', 'asli', 'parah', 'anjay'
        ])
        
        # Natural slang detection
        is_slang = any(word in message_lower for word in [
            'dapet', 'abis', 'pengen', 'bokap', 'nyokap', 'rebu', 'cuy', 'bro'
        ])
        
        # Modern payment context
        is_modern_payment = any(word in message_lower for word in [
            'gofood', 'grabfood', 'gopay', 'ovo', 'dana', 'spaylater'
        ])
        
        trans_type_id = "pemasukan" if transaction_type == "income" else "pengeluaran"
        
        # ENHANCED: More natural confirmation message
        if is_emotional or is_slang:
            # Use more casual tone for natural expressions
            confirmation_message = f"""💰 Oke, saya tangkap nih ada {trans_type_id}!

📋 **Yang saya pahami:**
• **Jenis**: {trans_type_id.title()}
• **Jumlah**: {self.format_currency(parsed_data['amount'])}
• **Kategori**: {parsed_data['category']}"""
        else:
            # Standard tone for formal expressions
            confirmation_message = f"""💰 Saya mendeteksi data {trans_type_id}:

📋 **Detail Transaksi:**
• **Jenis**: {trans_type_id.title()}
• **Jumlah**: {self.format_currency(parsed_data['amount'])}
• **Kategori**: {parsed_data['category']}"""

        # Add budget type for expenses
        if transaction_type == "expense" and parsed_data.get('budget_type'):
            budget_type = parsed_data['budget_type']
            budget_info = {
                "needs": "NEEDS (50%) - Kebutuhan Pokok",
                "wants": "WANTS (30%) - Keinginan & Lifestyle", 
                "savings": "SAVINGS (20%) - Tabungan Masa Depan"
            }.get(budget_type, budget_type)
            confirmation_message += f"\n• **Budget Type**: {budget_info}"

        confirmation_message += f"""
• **Keterangan**: {parsed_data['description']}
• **Tanggal**: {IndonesiaDatetime.format_date_only(parsed_data['date'])}

Apakah informasi ini sudah benar? Ketik **"ya"** untuk menyimpan atau **"tidak"** untuk membatalkan."""

        # Add contextual tips based on natural language patterns
        if is_modern_payment:
            confirmation_message += f"\n\n💡 **Tips Digital Payment**: Selalu cek transaksi digital untuk tracking yang akurat!"
        elif is_slang and transaction_type == "expense":
            confirmation_message += f"\n\n💡 **Tips Hemat**: Tracking pengeluaran jajan bisa menghemat Rp 200-500rb per bulan."
        elif is_emotional and transaction_type == "income":
            confirmation_message += f"\n\n💡 **Tips Syukur**: Alhamdulillah untuk rejeki! Jangan lupa sisihkan untuk tabungan ya."
        else:
            confirmation_message += f"\n\n💡 **Tips**: {random.choice(self.student_tips)}"
        
        # Add parsing method info for debugging
        if parsing_method != "Unknown":
            logger.info(f"🔧 Response generated using {parsing_method}")
        
        # Store pending data
        storage_data = parsed_data.copy()
        storage_data["date"] = self.datetime_to_iso(parsed_data["date"])
        
        pending_id = self.store_pending_data(
            user_id, conversation_id, message_id, transaction_type,
            storage_data, original_message, confirmation_message
        )
        
        logger.info(f"✅ Stored pending data with natural context: {pending_id}")
        return confirmation_message
    
    async def _handle_savings_goal_with_natural_context(self, user_id: str, conversation_id: str,
                                                      message_id: str, parsed_data: dict,
                                                      original_message: str, parsing_method: str) -> str:
        """Handle savings goal dengan natural language context"""
        
        message_lower = original_message.lower()
        
        # Detect aspirational language
        is_aspirational = any(word in message_lower for word in [
            'pengen banget', 'kepengen', 'mimpi', 'impian', 'cita-cita'
        ])
        
        # Detect timeline urgency
        is_urgent = any(word in message_lower for word in [
            'segera', 'cepat', 'buruan', 'mau', 'butuh'
        ])
        
        target_date_str = ""
        if parsed_data.get("target_date"):
            target_date_str = f"• **Target Waktu**: {IndonesiaDatetime.format_date_only(parsed_data['target_date'])}\n"
        
        # ENHANCED: More natural confirmation based on language context
        if is_aspirational:
            confirmation_message = f"""🎯 Wah, impian yang keren nih! Saya bantu wujudkan ya.

📋 **Target Tabungan Baru:**
• **Yang diinginkan**: {parsed_data['item_name']}
• **Target jumlah**: {self.format_currency(parsed_data['target_amount'])}
{target_date_str}• **Motivasi**: {parsed_data['description']}

Apakah target ini sudah sesuai impian kamu? Ketik **"ya"** untuk mulai menabung atau **"tidak"** untuk mengubah."""
        elif is_urgent:
            confirmation_message = f"""🎯 Oke, target yang perlu diprioritaskan nih!

📋 **Target Tabungan Prioritas:**
• **Yang dibutuhkan**: {parsed_data['item_name']}
• **Target jumlah**: {self.format_currency(parsed_data['target_amount'])}
{target_date_str}• **Alasan**: {parsed_data['description']}

Sudah benar target prioritasnya? Ketik **"ya"** untuk mulai atau **"tidak"** untuk revisi."""
        else:
            confirmation_message = f"""🎯 Saya mendeteksi target tabungan baru:

📋 **Detail Target Tabungan:**
• **Barang yang ingin dibeli**: {parsed_data['item_name']}
• **Target jumlah**: {self.format_currency(parsed_data['target_amount'])}
{target_date_str}• **Keterangan**: {parsed_data['description']}

Apakah informasi ini sudah benar? Ketik **"ya"** untuk menyimpan atau **"tidak"** untuk membatalkan."""

        # Add motivational tips based on context
        if is_aspirational:
            confirmation_message += f"\n\n🌟 **Motivasi**: Impian yang jelas adalah langkah pertama menuju kesuksesan!"
        elif is_urgent:
            confirmation_message += f"\n\n⚡ **Strategi Cepat**: Focus 100% budget WANTS ke target ini untuk hasil maksimal!"
        else:
            confirmation_message += f"\n\n💡 **Tips Target**: Bagi target besar jadi milestone kecil untuk motivasi yang konsisten."
        
        # Store pending data
        storage_data = parsed_data.copy()
        if parsed_data.get("target_date"):
            storage_data["target_date"] = self.datetime_to_iso(parsed_data["target_date"])
        
        pending_id = self.store_pending_data(
            user_id, conversation_id, message_id, "savings_goal",
            storage_data, original_message, confirmation_message
        )
        
        logger.info(f"✅ Stored savings goal with natural context: {pending_id}")
        return confirmation_message
    
    # ==========================================
    # ENHANCED REGULAR MESSAGE HANDLER
    # ==========================================
    
    async def handle_regular_message(self, user_message: str) -> str:
        """ENHANCED: Handle regular messages dengan natural language awareness"""
        message_lower = user_message.lower().strip()
        
        # ENHANCED: Detect natural Indonesian expressions that might be missed
        potential_financial_expressions = [
            'dapet', 'abis', 'pengen', 'bokap', 'nyokap', 'gofood', 'grabfood',
            'bayar', 'beli', 'nabung', 'transfer', 'kasih', 'kirim'
        ]
        
        has_financial_context = any(expr in message_lower for expr in potential_financial_expressions)
        has_amount_context = any(amt in message_lower for amt in ['rb', 'ribu', 'juta', 'k', 'm'])
        
        # If it looks financial but wasn't caught, provide helpful guidance
        if has_financial_context and has_amount_context:
            return f"""🤔 Sepertinya ada konteks keuangan dalam pesan Anda, tapi saya belum bisa memahami sepenuhnya.

**Pesan Anda**: "{user_message}"

💡 **Coba format yang lebih jelas:**
• Untuk pemasukan: *"Dapat 100rb dari freelance"*
• Untuk pengeluaran: *"Bayar makan 50rb"* 
• Untuk target tabungan: *"Mau nabung buat laptop 10 juta"*

🎯 **Tips**: Sebutkan jelas jumlah dan kegiatannya untuk hasil yang akurat!"""
        
        # Enhanced greeting responses with natural language awareness
        if any(word in message_lower for word in ['halo', 'hai', 'hi', 'hello', 'selamat']):
            greetings = [
                "Halo! Saya Luna, asisten keuangan yang ngerti bahasa natural mahasiswa Indonesia! 😊\n\n💬 **Langsung aja ya:**\n• \"Dapet 50rb dari freelance\"\n• \"Abis 25 rebu buat makan\"\n• \"Pengen nabung buat beli laptop\"",
                "Hai! Luna siap bantu ngatur duit mahasiswa dengan bahasa yang asik! 👋\n\n🗣️ **Ngomong aja natural:**\n• \"Bokap kasih jajan 100rb\"\n• \"Capek deh abis 75k coffee\"\n• \"Alhamdulillah dapet beasiswa\""
            ]
            return random.choice(greetings)
        
        # Enhanced help responses for natural language
        elif any(word in message_lower for word in ['bantuan', 'help', 'tolong', 'gimana', 'bagaimana']):
            return """🔰 **Luna AI - Asisten Keuangan Natural**

🗣️ **Ngomong Natural Aja:**
• *"Dapet 50rb dari freelance"* → Catat pemasukan
• *"Abis 25 rebu makan warteg"* → Catat pengeluaran
• *"Pengen nabung buat laptop gaming"* → Buat target

🎯 **Pake Bahasa Sehari-hari:**
• *"Bokap kasih jajan 100rb"* → Uang dari ortu
• *"Nyokap transfer 200 ribu"* → Transfer dari mama
• *"Capek deh bayar kos 800rb"* → Expense dengan emotion

💳 **Modern Payment:**
• *"Gofood ayam geprek 35rb"* → Digital payment
• *"Bayar via GoPay 28 ribu"* → E-wallet
• *"Spaylater 150rb beli sepatu"* → BNPL

📊 **Analisis:**
• *"Total tabungan saya"* → Cek saldo
• *"Budget performance bulan ini"* → Cek 50/30/20

💡 **Tips**: Semakin natural bahasanya, semakin akurat responsnya! 🚀"""
        
        # Enhanced financial context responses
        elif any(keyword in message_lower for keyword in ['budget', 'anggaran', 'uang', 'keuangan', 'tabungan', 'hemat']):
            return f"""💰 **Luna siap bantu financial planning mahasiswa!**

🎯 **Metode 50/30/20 (Natural Style):**
• **50% NEEDS**: "Bayar kos 800rb", "Transport kuliah 200rb"
• **30% WANTS**: "Nongkrong 100rb", "Beli baju 300rb"  
• **20% SAVINGS**: "Nabung masa depan", "Target laptop"

🗣️ **Ngomong aja santai:**
• "Dapet uang saku 2 juta dari ortu"
• "Abis 75k buat jajan bubble tea"
• "Pengen banget nabung buat iPhone"

Yuk mulai input transaksi dengan bahasa natural! 🚀"""
        
        # Enhanced emotional responses
        elif any(emotion in message_lower for emotion in ['sedih', 'senang', 'capek', 'gregetan', 'boros']):
            return f"""🤗 **Saya paham perasaan kamu!**

Sepertinya ada konteks emosional tentang keuangan. Luna siap bantu dengan empati! 

💡 **Coba ceritakan lebih detail:**
• Kalau sedih: "Sedih banget bayar kos naik jadi 1.2 juta"
• Kalau senang: "Alhamdulillah dapet beasiswa 5 juta"
• Kalau capek: "Capek deh abis 200rb transport"

🎯 **Luna ngerti emotions + finance**, jadi cerita aja natural! 💝"""
        
        # Default with natural language encouragement
        else:
            defaults = [
                "🤔 Hmm, belum terlalu paham nih. Coba pake bahasa yang lebih natural ya!\n\n💬 **Contoh yang Luna suka:**\n• \"Dapet 50rb dari ngajar\"\n• \"Abis 30rb buat makan siang\"\n• \"Pengen nabung motor 15 juta\"",
                "😅 Maaf, masih belajar memahami maksud kamu. Coba dengan bahasa sehari-hari aja!\n\n🗣️ **Format natural:**\n• \"Bokap kasih uang jajan 100rb\"\n• \"Grabfood pizza 120 ribu\"\n• \"Mau beli laptop tapi mahal banget\"",
                "🙏 Belum mengerti maksudnya. Yuk coba dengan bahasa yang lebih casual!\n\n💭 **Luna paham kalau:**\n• Pake slang: \"dapet\", \"abis\", \"pengen\"\n• Ada emotion: \"capek deh\", \"alhamdulillah\"\n• Natural amount: \"50rb\", \"2 juta\""
            ]
            return random.choice(defaults)
    
    # ==========================================
    # ENHANCED CONFIRMATION HANDLING
    # ==========================================
    
    async def confirm_financial_data(self, user_id: str, pending_data: dict) -> str:
        """ENHANCED: Konfirmasi dengan natural language response"""
        try:
            from .finance_service import FinanceService
            finance_service = FinanceService()
            
            pending_id = str(pending_data["_id"])
            result = finance_service.confirm_pending_data(pending_id, user_id, True)
            
            if result["success"]:
                data_type = result.get("type", pending_data["data_type"])
                created_data = result.get("data", {})
                
                # Get original message for context
                original_message = pending_data.get("original_message", "").lower()
                
                # Detect natural language context for personalized response
                is_emotional = any(word in original_message for word in [
                    'alhamdulillah', 'syukur', 'senang', 'sedih', 'capek'
                ])
                is_slang = any(word in original_message for word in [
                    'dapet', 'abis', 'pengen', 'bokap', 'nyokap'
                ])
                
                if data_type == "transaction" or data_type in ["income", "expense"]:
                    trans_type = "pemasukan" if created_data.get("type") == "income" else "pengeluaran"
                    
                    # Enhanced response based on language context
                    if is_emotional and trans_type == "pemasukan":
                        response = f"""✅ **Alhamdulillah, rejeki berhasil dicatat!** 🤲

💰 **Yang udah tersimpan:**
• **Jenis**: {trans_type.title()}
• **Jumlah**: {self.format_currency(created_data.get('amount', 0))}
• **Kategori**: {created_data.get('category', '')}
• **Tanggal**: {IndonesiaDatetime.format_date_only(created_data.get('date', now_for_db()))}

🤲 **Syukur**: Semoga berkah dan makin lancar rejekinya!"""
                    elif is_slang:
                        response = f"""✅ **Oke bro, udah kesave nih!** 👍

💰 **Data yang udah masuk:**
• **Jenis**: {trans_type.title()}
• **Jumlah**: {self.format_currency(created_data.get('amount', 0))}
• **Kategori**: {created_data.get('category', '')}
• **Tanggal**: {IndonesiaDatetime.format_date_only(created_data.get('date', now_for_db()))}

😎 **Nice**: Tracking keuangan makin rapi!"""
                    else:
                        response = f"""✅ **Data {trans_type} berhasil disimpan!**

💰 **Detail yang tersimpan:**
• **Jenis**: {trans_type.title()}
• **Jumlah**: {self.format_currency(created_data.get('amount', 0))}
• **Kategori**: {created_data.get('category', '')}
• **Tanggal**: {IndonesiaDatetime.format_date_only(created_data.get('date', now_for_db()))}"""
                    
                    # Add contextual advice
                    if is_emotional:
                        response += f"\n\n💡 **Tips**: Konsisten mencatat = berkah financial planning! 🌟"
                    elif is_slang:
                        response += f"\n\n💡 **Tips**: Keep it up! Konsistensi adalah kunci sukses financial! 🔥"
                    else:
                        response += f"\n\n💡 **Tips**: {random.choice(self.student_tips)}"
                    
                    response += "\n\nSilakan input transaksi lainnya atau tanyakan analisis keuangan Anda! 😊"
                    
                elif data_type == "savings_goal":
                    # Enhanced savings goal confirmation
                    original_aspirational = any(word in original_message for word in [
                        'pengen banget', 'impian', 'mimpi'
                    ])
                    
                    if original_aspirational:
                        response = f"""✅ **Target impian berhasil dibuat!** ⭐

🎯 **Impian yang akan diwujudkan:**
• **Barang**: {created_data.get('item_name', 'Target baru')}
• **Target**: {self.format_currency(created_data.get('target_amount', 0))}
• **Progress**: Rp 0 (0%) - Mari mulai!

🌟 **Motivasi**: Impian tanpa action hanya mimpi. Yuk wujudkan bareng Luna!"""
                    else:
                        response = f"""✅ **Target tabungan berhasil dibuat!**

🎯 **Detail Target:**
• **Barang**: {created_data.get('item_name', 'Target baru')}
• **Target**: {self.format_currency(created_data.get('target_amount', 0))}
• **Progress**: Rp 0 (0%)"""
                    
                    response += f"\n\n💪 **Strategi**: Dialokasikan dari budget WANTS (30%) untuk hasil optimal!\n\nSelamat menabung! Luna siap track progress kamu! 🏆"
                
                return response
            else:
                return f"❌ **Terjadi kesalahan**: {result.get('message', 'Tidak dapat menyimpan data')}"
        
        except Exception as e:
            logger.error(f"Error confirming financial data: {e}")
            return "😅 Maaf, terjadi kesalahan sistem. Coba input ulang ya!"
    
    async def cancel_financial_data(self, user_id: str, pending_data: dict) -> str:
        """ENHANCED: Cancel dengan natural language"""
        try:
            from .finance_service import FinanceService
            finance_service = FinanceService()
            
            pending_id = str(pending_data["_id"])
            result = finance_service.confirm_pending_data(pending_id, user_id, False)
            
            if result["success"]:
                return """❌ **Oke, data dibatalkan!**

Gak papa kok! Kalau mau input transaksi lagi, tinggal chat aja dengan bahasa natural.

💬 **Contoh yang Luna suka:**
• "Dapet 100rb dari freelance"
• "Abis 50rb makan siang"
• "Pengen nabung motor 15 juta"

Siap membantu kapan aja! 😊✨"""
            else:
                return f"⚠️ **Terjadi kesalahan**: {result.get('message', 'Tidak dapat membatalkan data')}"
        
        except Exception as e:
            logger.error(f"Error cancelling financial data: {e}")
            return "😅 Maaf, terjadi kesalahan. Coba lagi ya!"
    
    # ==========================================
    # KEEP OTHER METHODS UNCHANGED
    # ==========================================
    
    async def handle_confirmation(self, user_id: str, conversation_id: str, confirmed: bool) -> str:
        """Handle konfirmasi dengan async support"""
        logger.info(f"🔄 Processing confirmation: {confirmed}")
        
        pending_data = self.get_latest_pending_data(user_id, conversation_id)
        
        if not pending_data:
            logger.warning("❌ No pending data found")
            return "Saya tidak menemukan data yang perlu dikonfirmasi. Silakan coba input transaksi atau target tabungan baru."
        
        data_type = pending_data.get("data_type")
        
        if confirmed:
            if data_type in ["update_savings_goal", "delete_savings_goal"]:
                return await self.confirm_update_delete_action(user_id, pending_data)
            else:
                return await self.confirm_financial_data(user_id, pending_data)
        else:
            if data_type in ["update_savings_goal", "delete_savings_goal"]:
                return await self.cancel_update_delete_action(user_id, pending_data)
            else:
                return await self.cancel_financial_data(user_id, pending_data)
    
    # Include all other methods from original file...
    # (keeping the rest of the methods unchanged for now)
    
    async def handle_update_delete_command(self, user_id: str, conversation_id: str, message_id: str, command: Dict[str, Any]) -> str:
        """Handle perintah update/delete savings goal dengan async support"""
        action = command["action"]
        
        if action == "list":
            return await self.handle_list_savings_goals(user_id)
        
        item_name = command.get("item_name", "").strip()
        
        # Find matching savings goals
        matching_goals = await self.find_matching_savings_goals(user_id, item_name)
        
        if not matching_goals:
            return f"""🔍 **Target tabungan tidak ditemukan**

Saya tidak menemukan target tabungan dengan nama yang mirip dengan "*{item_name}*".

Untuk melihat semua target Anda, ketik: **"daftar target saya"**

Atau coba perintah dengan nama yang lebih spesifik, contoh:
• "ubah target laptop"
• "hapus target motor"
• "update target hp" """
        
        if len(matching_goals) > 1:
            # Multiple matches - ask user to specify
            goals_list = []
            for i, goal in enumerate(matching_goals[:5], 1):
                status_icon = "🟢" if goal["status"] == "active" else "🟡"
                goals_list.append(f"{i}. {status_icon} **{goal['item_name']}** - {self.format_currency(goal['target_amount'])}")
            
            return f"""🎯 **Beberapa target ditemukan untuk "{item_name}"**:

{chr(10).join(goals_list)}

Silakan sebutkan nama target yang lebih spesifik, atau gunakan perintah:
• "{'ubah' if action == 'update' else 'hapus'} target {matching_goals[0]['item_name']}"

Contoh: *"ubah target {matching_goals[0]['item_name']} jadi 15 juta"*"""
        
        # Single match found
        goal = matching_goals[0]
        
        if action == "update":
            return await self.handle_update_savings_goal(user_id, conversation_id, message_id, goal, command)
        elif action == "delete":
            return await self.handle_delete_savings_goal(user_id, conversation_id, message_id, goal, command)
    
    
    async def find_matching_savings_goals(self, user_id: str, search_term: str) -> List[Dict[str, Any]]:
        """Cari savings goals yang cocok dengan search term - async compatible"""
        try:
            # Get all active savings goals
            goals_cursor = self.db.savings_goals.find({
                "user_id": user_id,
                "status": {"$in": ["active", "paused"]}
            }).sort("created_at", -1)
            
            all_goals = list(goals_cursor)
            matching_goals = []
            
            search_lower = search_term.lower()
            
            for goal in all_goals:
                item_name_lower = goal["item_name"].lower()
                
                # Exact match
                if search_lower == item_name_lower:
                    matching_goals.insert(0, goal)
                # Contains match
                elif search_lower in item_name_lower or item_name_lower in search_lower:
                    matching_goals.append(goal)
                # Word match
                elif any(word in item_name_lower for word in search_lower.split() if len(word) > 2):
                    matching_goals.append(goal)
            
            return matching_goals
            
        except Exception as e:
            print(f"❌ Error finding matching savings goals: {e}")
            return []
    
    async def handle_list_savings_goals(self, user_id: str) -> str:
        """Handle request untuk list semua savings goals"""
        try:
            # Get all savings goals
            goals_cursor = self.db.savings_goals.find({
                "user_id": user_id,
                "status": {"$in": ["active", "paused", "completed"]}
            }).sort("created_at", -1)
            
            goals = list(goals_cursor)
            
            if not goals:
                return """🎯 **Belum Ada Target Tabungan**

Anda belum memiliki target tabungan. Yuk buat target pertama!

**Contoh membuat target:**
• "Mau nabung buat beli laptop 10 juta pada tanggal 22 januari 2026"
• "Target beli motor 25 juta dalam 1 tahun"
• "Pengen beli hp 5 juta"

💡 Target tabungan akan membantu Anda lebih fokus dan disiplin dalam menabung!"""
            
            # Group by status
            active_goals = [g for g in goals if g["status"] == "active"]
            completed_goals = [g for g in goals if g["status"] == "completed"]
            paused_goals = [g for g in goals if g["status"] == "paused"]
            
            response = "🎯 **Target Tabungan Anda**:\n\n"
            
            # Active goals
            if active_goals:
                response += "**🟢 Target Aktif:**\n"
                for goal in active_goals:
                    progress = (goal["current_amount"] / goal["target_amount"] * 100) if goal["target_amount"] > 0 else 0
                    progress_bar = "🟩" * int(progress // 10) + "⬜" * (10 - int(progress // 10))
                    
                    target_date_str = ""
                    if goal.get("target_date"):
                        target_date = goal["target_date"]
                        if isinstance(target_date, str):
                            try:
                                target_date = datetime.fromisoformat(target_date.replace('Z', '+00:00'))
                            except:
                                target_date = None
                        
                        if target_date:
                            days_remaining = (target_date - datetime.now()).days
                            if days_remaining > 0:
                                target_date_str = f" (⏰ {days_remaining} hari lagi)"
                            elif days_remaining == 0:
                                target_date_str = " (⏰ hari ini!)"
                            else:
                                target_date_str = f" (⚠️ lewat {abs(days_remaining)} hari)"
                    
                    response += f"• **{goal['item_name']}**{target_date_str}\n"
                    response += f"  {progress_bar} {progress:.1f}%\n"
                    response += f"  💰 {self.format_currency(goal['current_amount'])} / {self.format_currency(goal['target_amount'])}\n\n"
            
            # Completed goals
            if completed_goals:
                response += "**🎉 Target Tercapai:**\n"
                for goal in completed_goals[:3]:  # Show max 3
                    response += f"• **{goal['item_name']}** - {self.format_currency(goal['target_amount'])} ✅\n"
                if len(completed_goals) > 3:
                    response += f"• *...dan {len(completed_goals) - 3} target lainnya*\n"
                response += "\n"
            
            # Paused goals
            if paused_goals:
                response += "**⏸️ Target Dipause:**\n"
                for goal in paused_goals[:2]:  # Show max 2
                    progress = (goal["current_amount"] / goal["target_amount"] * 100) if goal["target_amount"] > 0 else 0
                    response += f"• **{goal['item_name']}** ({progress:.1f}%) - {self.format_currency(goal['target_amount'])}\n"
                response += "\n"
            
            response += """**🛠️ Perintah yang bisa digunakan:**
• *"ubah target [nama] tanggal [tanggal baru]"* - Ubah target waktu saja
• *"ubah target [nama] jadi [harga baru]"* - Ubah harga saja
• *"ganti nama [nama] jadi [nama baru]"* - Ubah nama saja
• *"hapus target [nama]"* - Hapus target
• *"progress tabungan"* - Lihat progress detail

⚠️ **INGAT**: Hanya 1 perubahan per pesan untuk hasil yang akurat!

💡 *Tip: Sebutkan nama barang yang spesifik untuk perintah yang lebih akurat*"""
            
            return response
            
        except Exception as e:
            print(f"❌ Error listing savings goals: {e}")
            return "😅 Maaf, terjadi kesalahan saat mengambil daftar target. Coba lagi ya!"
    
    async def handle_update_savings_goal(self, user_id: str, conversation_id: str, message_id: str, 
                                       goal: Dict[str, Any], command: Dict[str, Any]) -> str:
        """Handle update dengan validasi field tunggal"""
        update_fields = command.get("update_fields", {})
        update_type = command.get("update_type", "unknown")
        
        print(f"🔧 Processing update for goal: {goal['item_name']}")
        print(f"📋 Update fields: {update_fields}")
        print(f"🏷️ Update type: {update_type}")
        
        if not update_fields:
            # No specific fields detected, berikan contoh spesifik
            current_target_date = ""
            if goal.get("target_date"):
                try:
                    target_date = goal["target_date"]
                    if isinstance(target_date, str):
                        target_date = datetime.fromisoformat(target_date.replace('Z', '+00:00'))
                    current_target_date = f"\n• **Target Waktu**: {IndonesiaDatetime.format_date_only(target_date)}"
                except:
                    pass
            
            return f"""🔧 **Apa yang ingin diubah dari target "{goal['item_name']}"?**

**Data saat ini:**
• **Nama**: {goal['item_name']}
• **Target Harga**: {self.format_currency(goal['target_amount'])}{current_target_date}

**⚠️ PENTING: Hanya bisa ubah 1 hal per pesan**

**Contoh perintah:**
• *"ubah target {goal['item_name']} tanggal 31 desember 2025"* - Ubah deadline saja
• *"ubah target {goal['item_name']} jadi 15 juta"* - Ubah harga saja  
• *"ganti nama {goal['item_name']} jadi smartphone"* - Ubah nama saja

**🚫 JANGAN:** "ubah target laptop jadi 15 juta tanggal 31 desember"
**✅ LAKUKAN:** Dua pesan terpisah untuk dua perubahan

Ketik perintah yang ingin Anda lakukan! 😊"""
        
        # Validate hanya 1 field yang diupdate
        if len(update_fields) > 1:
            field_names = list(update_fields.keys())
            return f"""❌ **Terlalu banyak perubahan sekaligus!**

Anda mencoba mengubah: **{', '.join(field_names)}**

**Aturan: Hanya 1 perubahan per pesan**

Silakan lakukan perubahan satu per satu:

1️⃣ **Untuk mengubah harga:**
   *"ubah target {goal['item_name']} jadi [harga baru]"*

2️⃣ **Untuk mengubah tanggal:**  
   *"ubah target {goal['item_name']} tanggal [tanggal baru]"*

3️⃣ **Untuk mengubah nama:**
   *"ganti nama {goal['item_name']} jadi [nama baru]"*

Coba lagi dengan 1 perubahan saja ya! 😊"""
        
        # Prepare confirmation message untuk 1 field
        changes = []
        new_data = {}
        
        if "target_amount" in update_fields:
            old_amount = goal["target_amount"]
            new_amount = update_fields["target_amount"]
            changes.append(f"• **Harga**: {self.format_currency(old_amount)} → {self.format_currency(new_amount)}")
            new_data["target_amount"] = new_amount
            
            # Tambahan info untuk price update
            price_change = new_amount - old_amount
            if price_change > 0:
                changes.append(f"  📈 *Naik {self.format_currency(price_change)}*")
            else:
                changes.append(f"  📉 *Turun {self.format_currency(abs(price_change))}*")
        
        if "target_date" in update_fields:
            old_date = goal.get("target_date")
            new_date = update_fields["target_date"]
            
            old_date_str = "Tidak ada"
            if old_date:
                try:
                    if isinstance(old_date, str):
                        old_date = datetime.fromisoformat(old_date.replace('Z', '+00:00'))
                    old_date_str = IndonesiaDatetime.format_date_only(old_date)
                except:
                    old_date_str = "Tidak valid"
            
            new_date_str = IndonesiaDatetime.format_date_only(new_date)
            changes.append(f"• **Target Waktu**: {old_date_str} → {new_date_str}")
            new_data["target_date"] = self.datetime_to_iso(new_date)
            
            # Tambahan info untuk date update
            if old_date:
                try:
                    days_diff = (new_date - old_date).days
                    if days_diff > 0:
                        changes.append(f"  ⏰ *Diperpanjang {days_diff} hari*")
                    elif days_diff < 0:
                        changes.append(f"  ⚡ *Dipercepat {abs(days_diff)} hari*")
                    else:
                        changes.append(f"  📅 *Tanggal sama*")
                except:
                    pass
        
        if "item_name" in update_fields:
            old_name = goal["item_name"]
            new_name = update_fields["item_name"]
            changes.append(f"• **Nama**: {old_name} → {new_name}")
            new_data["item_name"] = new_name
        
        if not changes:
            return "🤔 Saya tidak bisa mendeteksi perubahan yang ingin dilakukan. Coba sebutkan dengan lebih jelas ya!"
        
        # Store pending update
        confirmation_message = f"""🔧 **Konfirmasi Perubahan Target Tabungan:**

**Target**: {goal['item_name']}

**Perubahan yang akan dilakukan:**
{chr(10).join(changes)}

Apakah perubahan ini sudah benar? Ketik **"ya"** untuk menyimpan atau **"tidak"** untuk membatalkan.

💡 *Setelah ini, Anda bisa melakukan perubahan lain jika diperlukan dengan pesan terpisah.*"""
        
        # Store pending update data
        pending_id = self.store_pending_update_delete(
            user_id, conversation_id, message_id, "update_savings_goal",
            {"goal_id": str(goal["_id"]), "updates": new_data},
            command["original_message"], confirmation_message
        )
        
        return confirmation_message
    
    async def handle_delete_savings_goal(self, user_id: str, conversation_id: str, message_id: str, 
                                       goal: Dict[str, Any], command: Dict[str, Any]) -> str:
        """Handle delete savings goal"""
        
        # Calculate progress info
        progress = (goal["current_amount"] / goal["target_amount"] * 100) if goal["target_amount"] > 0 else 0
        
        progress_info = ""
        if goal["current_amount"] > 0:
            progress_info = f"\n**Progress saat ini**: {self.format_currency(goal['current_amount'])} ({progress:.1f}%)"
        
        target_date_info = ""
        if goal.get("target_date"):
            try:
                target_date = goal["target_date"]
                if isinstance(target_date, str):
                    target_date = datetime.fromisoformat(target_date.replace('Z', '+00:00'))
                target_date_info = f"\n**Target Waktu**: {IndonesiaDatetime.format_date_only(target_date)}"
            except:
                pass
        
        # Store pending delete
        confirmation_message = f"""🗑️ **Konfirmasi Hapus Target Tabungan:**

**Target yang akan dihapus:**
• **Nama**: {goal['item_name']}
• **Target Harga**: {self.format_currency(goal['target_amount'])}{target_date_info}{progress_info}

⚠️ **Perhatian**: Data target dan progress tabungan akan hilang permanen!

Apakah Anda yakin ingin menghapus target ini? Ketik **"ya"** untuk menghapus atau **"tidak"** untuk membatalkan."""
        
        # Store pending delete data
        pending_id = self.store_pending_update_delete(
            user_id, conversation_id, message_id, "delete_savings_goal",
            {"goal_id": str(goal["_id"])},
            command["original_message"], confirmation_message
        )
        
        return confirmation_message
    
    async def confirm_update_delete_action(self, user_id: str, pending_data: dict) -> str:
        """Konfirmasi dan eksekusi update/delete savings goal"""
        try:
            data_type = pending_data["data_type"]
            action_data = pending_data["parsed_data"]
            goal_id = action_data["goal_id"]
            
            if data_type == "update_savings_goal":
                # Update savings goal
                updates = action_data["updates"]
                
                # Prepare update data
                update_data = {
                    "updated_at": now_for_db()
                }
                update_data.update(updates)
                
                # Convert ISO string back to datetime if needed
                if "target_date" in update_data and isinstance(update_data["target_date"], str):
                    try:
                        update_data["target_date"] = self.iso_to_datetime(update_data["target_date"])
                    except:
                        update_data["target_date"] = None
                
                # Update in database
                result = self.db.savings_goals.update_one(
                    {"_id": ObjectId(goal_id), "user_id": user_id},
                    {"$set": update_data}
                )
                
                if result.modified_count > 0:
                    # Get updated goal for response
                    updated_goal = self.db.savings_goals.find_one({"_id": ObjectId(goal_id)})
                    
                    # Determine what was updated for response
                    updated_field = ""
                    if "target_amount" in updates:
                        updated_field = "harga"
                    elif "target_date" in updates:
                        updated_field = "tanggal target"
                    elif "item_name" in updates:
                        updated_field = "nama"
                    
                    response = f"""✅ **Target tabungan berhasil diubah!**

**Target yang diperbarui:**
• **Nama**: {updated_goal['item_name']}
• **Target Harga**: {self.format_currency(updated_goal['target_amount'])}"""
                    
                    if updated_goal.get("target_date"):
                        try:
                            target_date = updated_goal["target_date"]
                            if isinstance(target_date, str):
                                target_date = datetime.fromisoformat(target_date.replace('Z', '+00:00'))
                            response += f"\n• **Target Waktu**: {IndonesiaDatetime.format_date_only(target_date)}"
                        except:
                            pass
                    
                    progress = (updated_goal["current_amount"] / updated_goal["target_amount"] * 100) if updated_goal["target_amount"] > 0 else 0
                    response += f"\n• **Progress**: {self.format_currency(updated_goal['current_amount'])} ({progress:.1f}%)"
                    
                    response += f"\n\n🎯 **{updated_field.title()} berhasil diperbarui!**"
                    
                    response += f"\n\n{random.choice(self.student_tips)}"
                    
                    # Mark as confirmed
                    self.db.pending_financial_data.update_one(
                        {"_id": ObjectId(pending_data["_id"])},
                        {"$set": {"is_confirmed": True, "confirmed_at": now_for_db()}}
                    )
                    
                    return response
                else:
                    return "⚠️ Target tidak ditemukan atau tidak ada perubahan yang dilakukan."
            
            elif data_type == "delete_savings_goal":
                # Delete savings goal
                result = self.db.savings_goals.delete_one(
                    {"_id": ObjectId(goal_id), "user_id": user_id}
                )
                
                if result.deleted_count > 0:
                    # Mark as confirmed
                    self.db.pending_financial_data.update_one(
                        {"_id": ObjectId(pending_data["_id"])},
                        {"$set": {"is_confirmed": True, "confirmed_at": now_for_db()}}
                    )
                    
                    return """✅ **Target tabungan berhasil dihapus!**

Target telah dihapus dari daftar Anda. Jangan khawatir, Anda masih bisa membuat target baru kapan saja!

**Contoh membuat target baru:**
• "Mau nabung buat beli laptop 10 juta pada tanggal 22 januari 2026"
• "Target beli motor 25 juta dalam 1 tahun"

Tetap semangat menabung! 💪"""
                else:
                    return "⚠️ Target tidak ditemukan atau sudah dihapus sebelumnya."
            
        except Exception as e:
            print(f"❌ Error confirming update/delete action: {e}")
            return "😅 Maaf, terjadi kesalahan saat memproses permintaan. Coba lagi ya!"
    
    async def cancel_update_delete_action(self, user_id: str, pending_data: dict) -> str:
        """Batalkan update/delete action"""
        try:
            data_type = pending_data["data_type"]
            
            # Delete pending data
            self.db.pending_financial_data.delete_one({"_id": ObjectId(pending_data["_id"])})
            
            if data_type == "update_savings_goal":
                return "❌ **Perubahan target dibatalkan.**\n\nTidak ada perubahan yang dilakukan pada target tabungan Anda."
            elif data_type == "delete_savings_goal":
                return "❌ **Penghapusan target dibatalkan.**\n\nTarget tabungan Anda tetap aman dan tidak dihapus."
            
        except Exception as e:
            print(f"❌ Error cancelling update/delete action: {e}")
            return "😅 Maaf, terjadi kesalahan. Coba lagi ya!"