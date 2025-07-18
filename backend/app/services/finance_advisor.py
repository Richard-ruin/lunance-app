# app/services/finance_advisor.py - Khusus untuk saran dan peringatan chatbot
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from bson import ObjectId

from ..config.database import get_database
from ..utils.timezone_utils import IndonesiaDatetime, now_for_db
from .finance_analyzer import FinanceAnalyzer


class FinanceAdvisor:
    """
    Advisor khusus untuk memberikan saran dan peringatan financial kepada user
    Terintegrasi dengan chatbot Luna AI
    """
    
    def __init__(self):
        self.db = get_database()
        self.analyzer = FinanceAnalyzer()
        
        # Saran berdasarkan level kesehatan keuangan
        self.health_based_advice = {
            "excellent": [
                "🎉 Financial management Anda sudah sangat baik! Pertimbangkan untuk mulai investasi jangka panjang",
                "💎 Dengan disiplin budget yang baik, Anda bisa mulai explore investasi reksadana atau saham",
                "🏆 Excellent! Bagikan tips budgeting 50/30/20 ke teman-teman mahasiswa lainnya",
                "🚀 Tingkatkan financial literacy dengan belajar tentang compound interest dan time value of money"
            ],
            "good": [
                "👍 Budget management Anda sudah baik! Pertahankan konsistensi ini",
                "📈 Pertimbangkan untuk meningkatkan alokasi savings dari 20% menjadi 25% jika memungkinkan",
                "💰 Dengan performance yang baik, Anda bisa mulai belajar investasi sederhana",
                "🎯 Excellent progress! Coba set target tabungan yang lebih challenging"
            ],
            "fair": [
                "📊 Financial health cukup baik, ada ruang untuk improvement",
                "🔧 Focus pada konsistensi budgeting 50/30/20 untuk hasil yang lebih optimal",
                "💡 Coba track pengeluaran harian untuk awareness yang lebih baik",
                "⚖️ Balance antara kebutuhan dan keinginan masih perlu diperbaiki"
            ],
            "needs_improvement": [
                "🆘 Saatnya serius dengan financial planning! Mulai dari budgeting 50/30/20",
                "🎯 Focus pada kategori NEEDS dulu: kos, makan, transport, pendidikan",
                "💪 Jangan menyerah! Setiap mahasiswa bisa sukses dengan budgeting yang benar",
                "📝 Mulai catat setiap pengeluaran untuk building awareness"
            ]
        }
        
        # Peringatan berdasarkan kondisi budget
        self.budget_warnings = {
            "needs_over": [
                "🚨 URGENT: Budget NEEDS (50%) sudah habis! Prioritaskan kebutuhan pokok saja",
                "⚠️ Pengeluaran kebutuhan pokok melebihi 50%. Cari cara untuk berhemat",
                "🔴 Budget NEEDS over limit! Evaluasi pengeluaran kos, makan, transport"
            ],
            "wants_over": [
                "💸 Budget WANTS (30%) sudah habis! Tahan keinginan sampai bulan depan",
                "🛑 Pengeluaran keinginan melebihi 30%. Pause dulu untuk jajan dan hiburan",
                "⏸️ Budget WANTS over! Fokus pada target tabungan yang sudah direncanakan"
            ],
            "savings_low": [
                "📉 Tabungan masih rendah! Usahakan minimal 20% dari pemasukan",
                "💰 Saving progress lambat. Alokasikan lebih dari budget WANTS untuk nabung",
                "🎯 Target tabungan belum tercapai. Kurangi pengeluaran yang tidak perlu"
            ],
            "total_over": [
                "🚨 CRITICAL: Total pengeluaran melebihi pemasukan! Immediate action needed",
                "⚠️ Spending over income! Potong drastis pengeluaran WANTS dan review NEEDS",
                "🔴 Budget crisis! Pertimbangkan cari tambahan income atau cut expenses"
            ]
        }
        
        # Tips contextual berdasarkan kategori pengeluaran
        self.category_tips = {
            "Makanan Pokok": [
                "🍚 Tip hemat: Masak sendiri bisa menghemat 40-60% budget makan",
                "🛒 Belanja groceries seminggu sekali untuk kontrol budget yang lebih baik",
                "👥 Masak bareng teman kos untuk efisiensi biaya dan waktu"
            ],
            "Jajan & Snack": [
                "🍕 Jajan adalah kategori WANTS - pastikan tidak melebihi 30% budget",
                "☕ Batasi kopi dan snack premium, pilih yang lebih ekonomis",
                "🥤 Bawa tumbler dan bekal untuk mengurangi jajan harian"
            ],
            "Transportasi Wajib": [
                "🚌 Maksimalkan transportasi umum untuk menghemat budget NEEDS",
                "🚲 Pertimbangkan sepeda untuk jarak dekat di sekitar kampus",
                "📱 Gunakan aplikasi transport sharing untuk efisiensi biaya"
            ],
            "Hiburan & Sosial": [
                "🎬 Hiburan masuk kategori WANTS - pastikan dalam batas 30%",
                "👥 Cari hiburan gratis atau murah: jalan-jalan, main games bareng",
                "🎊 Budget hiburan bulanan, jangan impulsive spending"
            ]
        }
        
        # Motivational quotes untuk financial discipline
        self.motivational_quotes = [
            "💪 'Disiplin adalah jembatan antara goals dan accomplishment' - Jim Rohn",
            "🎯 'Jangan save apa yang tersisa setelah spending, tapi spend apa yang tersisa setelah saving' - Warren Buffett",
            "⭐ 'Budgeting bukan tentang membatasi kebebasan, tapi tentang memberikan kebebasan' - Dave Ramsey",
            "🚀 'Investasi terbaik adalah investasi pada diri sendiri' - Warren Buffett",
            "💎 'Compound interest adalah keajaiban dunia kedelapan' - Albert Einstein"
        ]
    
    def format_currency(self, amount: float) -> str:
        """Format currency to Rupiah"""
        try:
            return f"Rp {amount:,.0f}".replace(',', '.')
        except:
            return f"Rp {amount}"
    
    # ==========================================
    # POST-TRANSACTION ADVICE METHODS
    # ==========================================
    
    async def generate_post_transaction_advice(self, user_id: str, transaction_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate advice setelah transaksi berhasil disimpan
        """
        try:
            # Analyze current financial status
            financial_analysis = await self.analyzer.analyze_user_financial_status(user_id)
            
            if financial_analysis["status"] != "analyzed":
                return {
                    "has_advice": False,
                    "message": "Belum bisa memberikan saran karena data finansial belum lengkap"
                }
            
            # Get transaction details
            transaction_type = transaction_data.get("type", "unknown")
            amount = transaction_data.get("amount", 0)
            category = transaction_data.get("category", "")
            budget_type = transaction_data.get("budget_type", "unknown")
            
            # Generate advice based on transaction and current status
            advice = self._generate_transaction_specific_advice(
                transaction_type, amount, category, budget_type, financial_analysis
            )
            
            # Add contextual warnings if needed
            warnings = self._generate_contextual_warnings(financial_analysis)
            
            # Add motivational element
            motivation = self._get_motivational_message(financial_analysis)
            
            return {
                "has_advice": True,
                "transaction_type": transaction_type,
                "amount": amount,
                "category": category,
                "budget_type": budget_type,
                "advice": advice,
                "warnings": warnings,
                "motivation": motivation,
                "financial_health": financial_analysis["health_score"]["level"],
                "budget_health": financial_analysis["budget_performance"]["budget_health"],
                "generated_at": now_for_db()
            }
            
        except Exception as e:
            print(f"Error generating post-transaction advice: {e}")
            return {
                "has_advice": False,
                "message": f"Gagal generate advice: {str(e)}"
            }
    
    def _generate_transaction_specific_advice(self, transaction_type: str, amount: float, 
                                            category: str, budget_type: str, 
                                            financial_analysis: Dict[str, Any]) -> List[str]:
        """Generate advice spesifik untuk transaksi"""
        advice = []
        
        if transaction_type == "income":
            # Advice untuk pemasukan
            advice.append(f"💰 Pemasukan {self.format_currency(amount)} berhasil dicatat!")
            
            # Suggest budget allocation
            monthly_income = financial_analysis["monthly_income"]
            if monthly_income > 0:
                needs_allocation = amount * 0.5
                wants_allocation = amount * 0.3
                savings_allocation = amount * 0.2
                
                advice.append(f"📊 Alokasi optimal: NEEDS {self.format_currency(needs_allocation)}, WANTS {self.format_currency(wants_allocation)}, SAVINGS {self.format_currency(savings_allocation)}")
            
            # Category-specific income advice
            if "uang saku" in category.lower():
                advice.append("👨‍👩‍👧‍👦 Uang saku dari ortu! Gunakan dengan bijak sesuai metode 50/30/20")
            elif "freelance" in category.lower() or "project" in category.lower():
                advice.append("🎯 Income dari freelance! Pertimbangkan untuk alokasi lebih besar ke SAVINGS")
            elif "beasiswa" in category.lower():
                advice.append("🎓 Beasiswa adalah berkah! Maksimalkan untuk pendidikan dan tabungan masa depan")
        
        elif transaction_type == "expense":
            # Advice untuk pengeluaran
            budget_performance = financial_analysis["budget_performance"]
            performance = budget_performance["performance"]
            
            if budget_type in performance:
                budget_info = performance[budget_type]
                remaining = budget_info["remaining"]
                percentage_used = budget_info["percentage_used"]
                
                advice.append(f"📉 Pengeluaran {self.format_currency(amount)} untuk {category}")
                advice.append(f"💳 Sisa budget {budget_type.upper()}: {self.format_currency(remaining)} ({100-percentage_used:.1f}% tersisa)")
                
                # Budget type specific advice
                if budget_type == "needs":
                    if percentage_used > 80:
                        advice.append("⚠️ Budget NEEDS hampir habis! Prioritaskan kebutuhan pokok saja")
                    else:
                        advice.append("✅ Pengeluaran NEEDS masih dalam batas normal")
                
                elif budget_type == "wants":
                    if percentage_used > 80:
                        advice.append("🛑 Budget WANTS hampir habis! Tahan keinginan sampai bulan depan")
                    else:
                        advice.append("🎯 Pengeluaran WANTS masih OK. Sisanya bisa untuk target tabungan")
                
                elif budget_type == "savings":
                    advice.append("📈 Bagus! Ini investasi untuk masa depan")
            
            # Category-specific expense advice
            if category in self.category_tips:
                random_tip = random.choice(self.category_tips[category])
                advice.append(random_tip)
        
        return advice
    
    def _generate_contextual_warnings(self, financial_analysis: Dict[str, Any]) -> List[str]:
        """Generate peringatan berdasarkan kondisi finansial current"""
        warnings = []
        
        budget_performance = financial_analysis["budget_performance"]
        performance = budget_performance["performance"]
        budget_health = budget_performance["budget_health"]
        
        # Check each budget category
        for budget_type, info in performance.items():
            percentage_used = info.get("percentage_used", 0)
            
            if percentage_used > 100:
                if budget_type == "needs":
                    warnings.extend(self.budget_warnings["needs_over"])
                elif budget_type == "wants":
                    warnings.extend(self.budget_warnings["wants_over"])
            elif percentage_used > 90:
                warnings.append(f"⚠️ Budget {budget_type.upper()} hampir habis ({percentage_used:.1f}%)")
        
        # Overall budget health warnings
        if budget_health == "critical":
            warnings.extend(self.budget_warnings["total_over"])
        elif budget_health == "warning":
            warnings.append("📊 Total pengeluaran mendekati batas! Evaluasi spending pattern")
        
        # Savings-specific warnings
        savings_analysis = financial_analysis["savings_analysis"]
        if savings_analysis["has_goals"]:
            urgent_goals = savings_analysis["urgent_goals"]
            if urgent_goals:
                warnings.append(f"⏰ {len(urgent_goals)} target tabungan deadline dalam 30 hari!")
            
            if savings_analysis["average_progress"] < 30:
                warnings.extend(self.budget_warnings["savings_low"])
        
        return warnings
    
    def _get_motivational_message(self, financial_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Get motivational message based on performance"""
        health_level = financial_analysis["health_score"]["level"]
        
        # Get health-based advice
        if health_level in self.health_based_advice:
            advice = random.choice(self.health_based_advice[health_level])
        else:
            advice = "💪 Tetap semangat mengelola keuangan dengan metode 50/30/20!"
        
        # Add motivational quote
        quote = random.choice(self.motivational_quotes)
        
        return {
            "advice": advice,
            "quote": quote,
            "health_level": health_level
        }
    
    # ==========================================
    # PURCHASE ADVICE METHODS
    # ==========================================
    
    async def generate_purchase_advice(self, user_id: str, item_name: str, price: float) -> Dict[str, Any]:
        """
        Generate advice untuk pertanyaan "Saya ingin membeli X seharga Y"
        """
        try:
            # Analyze purchase impact
            purchase_analysis = await self.analyzer.analyze_purchase_impact(user_id, item_name, price)
            
            if not purchase_analysis["can_analyze"]:
                return {
                    "can_advise": False,
                    "message": purchase_analysis.get("message", "Cannot analyze purchase"),
                    "setup_needed": True
                }
            
            # Get current financial status for context
            financial_analysis = await self.analyzer.analyze_user_financial_status(user_id)
            
            # Generate comprehensive advice
            advice = self._generate_purchase_decision_advice(purchase_analysis, financial_analysis)
            
            # Generate alternatives if not recommended
            alternatives = self._generate_purchase_alternatives(purchase_analysis)
            
            # Generate timeline advice
            timeline_advice = self._generate_purchase_timeline_advice(purchase_analysis)
            
            return {
                "can_advise": True,
                "item_name": item_name,
                "price": price,
                "formatted_price": self.format_currency(price),
                "budget_type": purchase_analysis["budget_type"],
                "category": purchase_analysis["category"],
                "feasibility": purchase_analysis["overall_assessment"]["feasibility"],
                "impact_level": purchase_analysis["budget_impact"]["impact_level"],
                "advice": advice,
                "alternatives": alternatives,
                "timeline_advice": timeline_advice,
                "detailed_analysis": {
                    "budget_impact": purchase_analysis["budget_impact"],
                    "savings_impact": purchase_analysis["savings_impact"],
                    "recommendations": purchase_analysis["recommendations"]
                },
                "generated_at": now_for_db()
            }
            
        except Exception as e:
            print(f"Error generating purchase advice: {e}")
            return {
                "can_advise": False,
                "message": f"Gagal generate purchase advice: {str(e)}"
            }
    
    def _generate_purchase_decision_advice(self, purchase_analysis: Dict[str, Any], 
                                         financial_analysis: Dict[str, Any]) -> List[str]:
        """Generate advice untuk keputusan pembelian"""
        advice = []
        
        feasibility = purchase_analysis["overall_assessment"]["feasibility"]
        budget_impact = purchase_analysis["budget_impact"]
        savings_impact = purchase_analysis["savings_impact"]
        budget_type = purchase_analysis["budget_type"]
        price = purchase_analysis["price"]
        
        # Main recommendation based on feasibility
        if feasibility == "not_recommended":
            advice.append("🚨 **TIDAK DIREKOMENDASIKAN** untuk dibeli sekarang")
            advice.append(f"❌ Alasan: Akan melebihi budget {budget_type.upper()} sebesar {self.format_currency(budget_impact.get('overspend_amount', 0))}")
        elif feasibility == "risky":
            advice.append("⚠️ **BERISIKO** - Pertimbangkan dengan matang")
            advice.append(f"🔍 Dampak: Akan menggunakan {budget_impact.get('after_purchase_percentage', 0):.1f}% dari budget {budget_type.upper()}")
        elif feasibility == "consider":
            advice.append("🤔 **PERTIMBANGKAN** - Bisa dibeli tapi dengan catatan")
            advice.append(f"📊 Dampak: Menggunakan {budget_impact.get('after_purchase_percentage', 0):.1f}% budget {budget_type.upper()}")
        elif feasibility == "recommended":
            advice.append("✅ **DIREKOMENDASIKAN** - Aman untuk dibeli")
            advice.append(f"💚 Dampak: Hanya {budget_impact.get('after_purchase_percentage', 0):.1f}% dari budget {budget_type.upper()}")
        
        # Budget-specific advice
        if budget_type == "needs":
            if budget_impact.get("after_purchase_percentage", 0) > 90:
                advice.append("⚠️ Ini kebutuhan pokok, tapi akan menghabiskan hampir seluruh budget NEEDS")
            else:
                advice.append("✅ Ini termasuk kebutuhan pokok yang wajar")
        elif budget_type == "wants":
            if budget_impact.get("after_purchase_percentage", 0) > 90:
                advice.append("🛑 Ini akan menghabiskan hampir seluruh budget WANTS bulan ini")
            else:
                advice.append("🎯 Ini masuk kategori keinginan dari budget WANTS (30%)")
        elif budget_type == "savings":
            advice.append("📈 Bagus! Ini investasi untuk masa depan dari budget SAVINGS")
        
        # Savings impact advice
        if savings_impact.get("has_impact") and savings_impact.get("delays_goals"):
            progress_reduction = savings_impact.get("progress_reduction", 0)
            advice.append(f"📉 Akan mengurangi progress target tabungan sebesar {progress_reduction:.1f}%")
            
            urgent_goals = savings_impact.get("urgent_goals_impact", [])
            if urgent_goals:
                advice.append(f"⏰ Akan mempengaruhi {len(urgent_goals)} target tabungan yang urgent")
        
        # Health-based advice
        health_level = financial_analysis["health_score"]["level"]
        if health_level in ["needs_improvement", "fair"] and feasibility in ["risky", "not_recommended"]:
            advice.append("🎯 Dengan kondisi finansial saat ini, lebih baik fokus pada stabilitas budget dulu")
        elif health_level in ["good", "excellent"] and feasibility == "recommended":
            advice.append("💪 Dengan financial health yang baik, pembelian ini tidak akan mengganggu rencana")
        
        return advice
    
    def _generate_purchase_alternatives(self, purchase_analysis: Dict[str, Any]) -> List[str]:
        """Generate alternatif jika pembelian tidak direkomendasikan"""
        alternatives = []
        
        feasibility = purchase_analysis["overall_assessment"]["feasibility"]
        budget_type = purchase_analysis["budget_type"]
        price = purchase_analysis["price"]
        item_name = purchase_analysis["item_name"]
        
        if feasibility in ["not_recommended", "risky"]:
            # General alternatives
            alternatives.append(f"💡 **Alternatif 1:** Tunda pembelian sampai bulan depan saat budget reset")
            alternatives.append(f"🎯 **Alternatif 2:** Buat target tabungan untuk {item_name} dari budget WANTS")
            alternatives.append(f"🔍 **Alternatif 3:** Cari versi lebih murah atau second-hand")
            
            # Budget-specific alternatives
            if budget_type == "wants":
                alternatives.append(f"📊 **Alternatif 4:** Alokasikan budget WANTS beberapa bulan ke depan")
                alternatives.append(f"🏆 **Alternatif 5:** Cari tambahan income untuk dedicated budget item ini")
            elif budget_type == "needs":
                alternatives.append(f"⚡ **Alternatif 4:** Cari promo atau diskon untuk kebutuhan ini")
                alternatives.append(f"👥 **Alternatif 5:** Sharing cost dengan teman jika memungkinkan")
        
        elif feasibility == "consider":
            alternatives.append(f"⏰ **Opsi 1:** Beli di akhir bulan jika budget masih aman")
            alternatives.append(f"🎯 **Opsi 2:** Beli sekarang tapi kurangi pengeluaran kategori lain")
            alternatives.append(f"📊 **Opsi 3:** Beli dengan payment plan jika tersedia")
        
        return alternatives
    
    def _generate_purchase_timeline_advice(self, purchase_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate advice tentang timing pembelian"""
        feasibility = purchase_analysis["overall_assessment"]["feasibility"]
        budget_impact = purchase_analysis["budget_impact"]
        budget_type = purchase_analysis["budget_type"]
        
        if feasibility == "not_recommended":
            return {
                "recommended_timing": "next_month",
                "reason": "Budget saat ini tidak mencukupi",
                "action": "Tunggu sampai budget reset tanggal 1 bulan depan"
            }
        elif feasibility == "risky":
            return {
                "recommended_timing": "end_of_month",
                "reason": "Berisiko terhadap budget, lebih baik tunggu evaluasi akhir bulan",
                "action": "Tunggu sampai akhir bulan untuk memastikan tidak ada pengeluaran urgent lain"
            }
        elif feasibility == "consider":
            return {
                "recommended_timing": "within_week",
                "reason": "Masih dalam batas yang dapat diterima",
                "action": "Bisa dibeli dalam seminggu ini, tapi monitor pengeluaran lain"
            }
        elif feasibility == "recommended":
            return {
                "recommended_timing": "anytime",
                "reason": "Aman untuk dibeli kapan saja",
                "action": "Silakan beli sekarang, tidak akan mengganggu budget"
            }
        
        return {
            "recommended_timing": "unknown",
            "reason": "Tidak dapat menentukan timing yang tepat",
            "action": "Evaluasi ulang kondisi finansial"
        }
    
    # ==========================================
    # GENERAL ADVICE METHODS
    # ==========================================
    
    async def generate_daily_financial_tips(self, user_id: str) -> Dict[str, Any]:
        """Generate tips harian berdasarkan kondisi finansial user"""
        try:
            financial_analysis = await self.analyzer.analyze_user_financial_status(user_id)
            
            if financial_analysis["status"] != "analyzed":
                return {
                    "has_tips": False,
                    "message": "Setup keuangan dulu untuk mendapatkan tips personal"
                }
            
            # Get contextual tips
            tips = self._generate_contextual_tips(financial_analysis)
            
            # Add motivational quote
            quote = random.choice(self.motivational_quotes)
            
            return {
                "has_tips": True,
                "tips": tips,
                "quote": quote,
                "financial_health": financial_analysis["health_score"]["level"],
                "generated_at": now_for_db()
            }
            
        except Exception as e:
            print(f"Error generating daily tips: {e}")
            return {
                "has_tips": False,
                "message": f"Gagal generate tips: {str(e)}"
            }
    
    def _generate_contextual_tips(self, financial_analysis: Dict[str, Any]) -> List[str]:
        """Generate tips berdasarkan kondisi finansial"""
        tips = []
        
        # Health-based tips
        health_level = financial_analysis["health_score"]["level"]
        if health_level in self.health_based_advice:
            tips.append(random.choice(self.health_based_advice[health_level]))
        
        # Budget-based tips
        budget_performance = financial_analysis["budget_performance"]
        performance = budget_performance["performance"]
        
        for budget_type, info in performance.items():
            percentage_used = info.get("percentage_used", 0)
            
            if percentage_used > 80:
                tips.append(f"⚠️ Budget {budget_type.upper()} hampir habis ({percentage_used:.1f}%). Hati-hati dengan spending selanjutnya")
            elif percentage_used < 30:
                if budget_type == "savings":
                    tips.append(f"📈 Budget {budget_type.upper()} masih banyak sisa. Bisa ditingkatkan untuk investasi masa depan")
                else:
                    tips.append(f"✅ Budget {budget_type.upper()} masih aman ({percentage_used:.1f}% terpakai)")
        
        # Savings-based tips
        savings_analysis = financial_analysis["savings_analysis"]
        if savings_analysis["has_goals"]:
            urgent_goals = savings_analysis["urgent_goals"]
            if urgent_goals:
                tips.append(f"⏰ Focus pada {len(urgent_goals)} target tabungan yang deadline-nya dekat")
            
            if savings_analysis["average_progress"] < 50:
                tips.append("📊 Progress tabungan masih bisa ditingkatkan. Alokasikan lebih dari budget WANTS")
        else:
            tips.append("🎯 Belum ada target tabungan. Yuk buat target untuk motivasi saving yang lebih baik")
        
        # Spending pattern tips
        spending_patterns = financial_analysis["spending_patterns"]
        top_categories = spending_patterns.get("top_categories", [])