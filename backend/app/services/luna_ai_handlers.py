# app/services/luna_ai_handlers.py - Transaction & CRUD Operations untuk Luna AI
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from bson import ObjectId

from ..config.database import get_database
from ..utils.timezone_utils import IndonesiaDatetime, now_for_db
from .luna_ai_base import LunaAIBase
from .finance_analyzer import FinanceAnalyzer
from .finance_advisor import FinanceAdvisor


class LunaAIHandlers(LunaAIBase):
    """Luna AI Handlers untuk transaction input & savings goal CRUD operations"""
    
    def __init__(self):
        super().__init__()
        self.analyzer = FinanceAnalyzer()
        self.advisor = FinanceAdvisor()
    
    # ==========================================
    # FINANCIAL DATA INPUT HANDLERS
    # ==========================================
    
    async def handle_financial_data(self, user_id: str, conversation_id: str, message_id: str,
                                  transaction_type: str, amount: float, original_message: str) -> str:
        """Handle financial data input dengan enhanced parsing dan advice"""
        
        parse_result = self.parser.parse_financial_data(original_message)
        
        if not parse_result["is_financial_data"]:
            return await self.handle_regular_message(original_message)
        
        parsed_data = parse_result["parsed_data"]
        suggestions = parse_result.get("suggestions", [])
        
        if transaction_type in ["income", "expense"]:
            trans_type_id = "pemasukan" if transaction_type == "income" else "pengeluaran"
            
            confirmation_message = f"""💰 Saya mendeteksi data {trans_type_id}:

📋 **Detail Transaksi:**
• Jenis: {trans_type_id.title()}
• Jumlah: {self.format_currency(amount)}
• Kategori: {parsed_data['category']}
• Keterangan: {parsed_data['description']}
• Tanggal: {IndonesiaDatetime.format_date_only(parsed_data['date'])}

Apakah informasi ini sudah benar? Ketik **"ya"** untuk menyimpan atau **"tidak"** untuk membatalkan."""

            if suggestions:
                confirmation_message += f"\n\n💡 {suggestions[0]}"
            
            # Convert datetime to ISO string for storage
            storage_data = parsed_data.copy()
            storage_data["date"] = self.datetime_to_iso(parsed_data["date"])

        elif transaction_type == "savings_goal":
            target_date_str = ""
            if parsed_data.get("target_date"):
                target_date_str = f"• Target Waktu: {IndonesiaDatetime.format_date_only(parsed_data['target_date'])}\n"
            
            confirmation_message = f"""🎯 Saya mendeteksi target tabungan baru:

📋 **Detail Target Tabungan:**
• Barang yang ingin dibeli: {parsed_data['item_name']}
• Target jumlah: {self.format_currency(parsed_data['target_amount'])}
{target_date_str}• Keterangan: {parsed_data['description']}

Apakah informasi ini sudah benar? Ketik **"ya"** untuk menyimpan atau **"tidak"** untuk membatalkan."""

            if suggestions:
                confirmation_message += f"\n\n💡 {suggestions[0]}"
            
            # Convert datetime to ISO string for storage
            storage_data = parsed_data.copy()
            if parsed_data.get("target_date"):
                storage_data["target_date"] = self.datetime_to_iso(parsed_data["target_date"])

        # Store pending data
        pending_id = self.store_pending_data(
            user_id, conversation_id, message_id, transaction_type,
            storage_data, original_message, confirmation_message
        )
        
        return confirmation_message
    
    # ==========================================
    # SAVINGS GOAL CRUD HANDLERS
    # ==========================================
    
    async def handle_update_delete_command(self, user_id: str, conversation_id: str, message_id: str, command: Dict[str, Any]) -> str:
        """Handle perintah update/delete savings goal"""
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
        """Cari savings goals yang cocok dengan search term"""
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
    
    # ==========================================
    # CONFIRMATION HANDLERS
    # ==========================================
    
    async def handle_confirmation(self, user_id: str, conversation_id: str, confirmed: bool) -> str:
        """Handle konfirmasi dari user untuk data keuangan atau update/delete"""
        print(f"🔄 Processing confirmation: {confirmed}")
        
        # Get latest pending data
        pending_data = self.get_latest_pending_data(user_id, conversation_id)
        
        if not pending_data:
            print("❌ No pending data found")
            return await self.handle_regular_message("ya" if confirmed else "tidak")
        
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
    
    async def confirm_financial_data(self, user_id: str, pending_data: dict) -> str:
        """Konfirmasi dan simpan data keuangan dengan post-transaction advice"""
        try:
            # Import finance service
            from .finance_service import FinanceService
            finance_service = FinanceService()
            
            pending_id = str(pending_data["_id"])
            result = finance_service.confirm_pending_data(pending_id, user_id, True)
            
            if result["success"]:
                data_type = result.get("type", pending_data["data_type"])
                created_data = result.get("data", {})
                
                if data_type == "transaction" or data_type in ["income", "expense"]:
                    # Generate post-transaction advice
                    post_advice = await self.advisor.generate_post_transaction_advice(user_id, created_data)
                    
                    trans_type = "pemasukan" if created_data.get("type") == "income" else "pengeluaran"
                    
                    response = f"""✅ **{trans_type.title()} berhasil disimpan!**

💰 {self.format_currency(created_data.get('amount', 0))} - {created_data.get('category', '')}
📝 {created_data.get('description', '')}
📅 {IndonesiaDatetime.format_date_only(created_data.get('date', now_for_db()))}

"""
                    
                    # Add post-transaction advice
                    if post_advice["has_advice"]:
                        # Add main advice
                        if post_advice["advice"]:
                            response += "💡 **Saran untuk Anda:**\n"
                            for advice in post_advice["advice"][:3]:  # Limit to 3 points
                                response += f"• {advice}\n"
                            response += "\n"
                        
                        # Add warnings if any
                        if post_advice["warnings"]:
                            response += "⚠️ **Peringatan:**\n"
                            for warning in post_advice["warnings"][:2]:  # Limit to 2 warnings
                                response += f"• {warning}\n"
                            response += "\n"
                        
                        # Add motivation
                        if post_advice["motivation"]:
                            response += f"🎯 **Motivasi:** {post_advice['motivation']['advice']}\n\n"
                            response += f"💪 *{post_advice['motivation']['quote']}*"
                    else:
                        # Fallback motivation
                        response += f"{random.choice(self.student_tips)}"
                    
                elif data_type == "savings_goal":
                    response = f"""🎯 **Target tabungan berhasil dibuat!**

🛍️ **{created_data.get('item_name', 'Target baru')}**
💰 Target: {self.format_currency(created_data.get('target_amount', 0))}
📊 Progress: Rp 0 (0%)

Mulai menabung sekarang untuk mencapai target Anda! 💪

💡 *Untuk mengubah target ini nanti, gunakan: "ubah target [nama] ..."*

{random.choice(self.student_tips)}"""
                
                return response
            else:
                return f"⚠️ **Terjadi kesalahan:** {result.get('message', 'Tidak dapat menyimpan data')}"
        
        except Exception as e:
            print(f"❌ Error confirming financial data: {e}")
            return "😅 Maaf, terjadi kesalahan saat menyimpan data. Coba lagi ya!"
    
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
    
    async def cancel_financial_data(self, user_id: str, pending_data: dict) -> str:
        """Batalkan data keuangan"""
        try:
            # Import finance service
            from .finance_service import FinanceService
            finance_service = FinanceService()
            
            pending_id = str(pending_data["_id"])
            result = finance_service.confirm_pending_data(pending_id, user_id, False)
            
            if result["success"]:
                return "❌ **Data dibatalkan.**\n\nTidak masalah! Jika ada transaksi atau target tabungan lain yang ingin dicatat, silakan beritahu saya kapan saja."
            else:
                return f"⚠️ **Terjadi kesalahan:** {result.get('message', 'Tidak dapat membatalkan data')}"
        
        except Exception as e:
            print(f"❌ Error cancelling financial data: {e}")
            return "😅 Maaf, terjadi kesalahan. Coba lagi ya!"
    
    # ==========================================
    # REGULAR MESSAGE HANDLER
    # ==========================================
    
    async def handle_regular_message(self, user_message: str) -> str:
        """Handle pesan regular (non-financial)"""
        message_lower = user_message.lower()
        
        # Greeting responses
        if any(word in message_lower for word in ['halo', 'hai', 'hi', 'hello', 'selamat']):
            return random.choice(self.greetings)
            
        # Thank you responses
        elif any(word in message_lower for word in ['terima kasih', 'thanks', 'makasih', 'thx']):
            return "Sama-sama! Senang bisa membantu Anda mengelola keuangan mahasiswa. Ada lagi yang ingin dibahas?"
            
        # Help requests
        elif any(word in message_lower for word in ['bantuan', 'help', 'tolong', 'gimana', 'bagaimana']):
            return """Tentu! Saya bisa membantu Anda dengan:

📊 **Mencatat Keuangan Mahasiswa:**
• Catat pemasukan: "Dapat uang saku 1 juta"
• Catat pengeluaran: "Bayar kos 500 ribu"
• Target tabungan: "Mau nabung buat beli laptop 10 juta pada tanggal 22 januari 2026"

📈 **Tanya Data Keuangan:**
• "Total tabungan saya"
• "Kesehatan keuangan saya"
• "Performa budget bulan ini"
• "Progress tabungan"
• "Daftar target saya"

🛒 **Analisis Pembelian:**
• "Saya ingin membeli laptop seharga 10 juta"
• "Mau beli motor 25 juta, gimana?"

🔧 **Kelola Target Tabungan (1 perubahan per pesan):**
• "Ubah target laptop tanggal 31 desember 2025"
• "Ubah target laptop jadi 15 juta"
• "Ganti nama laptop jadi smartphone"
• "Hapus target motor"

💡 **Tips Keuangan Mahasiswa:**
• Budgeting metode 50/30/20
• Tips menghemat uang saku
• Perencanaan keuangan

Ada yang ingin dicoba sekarang?"""
            
        # Question about Luna
        elif any(word in message_lower for word in ['luna', 'kamu', 'anda', 'siapa']):
            return "Saya Luna, asisten AI yang dirancang khusus untuk membantu mahasiswa Indonesia mengelola keuangan. Saya paham betul tantangan keuangan mahasiswa dan bisa membantu Anda dengan budgeting 50/30/20, tips menghemat, tracking pengeluaran, mencatat transaksi, analisis pembelian, dan mengelola target tabungan dengan sistem yang akurat!"
            
        # Financial keyword responses
        elif any(keyword in message_lower for keyword in ['budget', 'anggaran', 'uang', 'keuangan', 'tabungan', 'hemat', 'mahasiswa']):
            response = "Saya bisa membantu Anda dengan manajemen keuangan mahasiswa yang lebih baik!"
            
            # Add specific tips based on keywords
            if any(word in message_lower for word in ['budget', 'anggaran']):
                response += "\n\n📋 **Tips Budget Mahasiswa:**\n• 50% untuk kebutuhan (makan, transport, kos)\n• 30% untuk keinginan (hiburan, jajan)\n• 20% untuk tabungan dan dana darurat"
            elif 'tabungan' in message_lower:
                response += "\n\n🏦 **Tips Menabung Mahasiswa:**\n• Sisihkan 15-20% uang saku untuk tabungan\n• Buat target tabungan yang spesifik\n• Gunakan rekening terpisah untuk tabungan"
            elif 'hemat' in message_lower:
                response += "\n\n💡 **Tips Hemat Mahasiswa:**\n• Masak sendiri atau makan bersama teman kos\n• Manfaatkan diskon dan promo mahasiswa\n• Gunakan transportasi umum\n• Beli buku bekas atau pinjam dari perpustakaan"
            
            # Add random student tip
            response += f"\n\n{random.choice(self.student_tips)}"
            return response
        
        # Default responses with helpful tips
        else:
            response = "Saya di sini untuk membantu Anda dengan keuangan mahasiswa. Ada yang ingin dibahas tentang budgeting, tabungan, atau analisis pengeluaran?"
            
            # Sometimes add a helpful tip
            if random.choice([True, False]):
                response += f"\n\n{random.choice(self.student_tips)}"
            
            return response