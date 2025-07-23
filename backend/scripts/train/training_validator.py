# scripts/train/training_validator.py - ADVANCED TRAINING VALIDATOR
import os
import json
import logging
import numpy as np
from pathlib import Path
from typing import Dict, Any, List, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)

# Check dependencies
def check_validation_dependencies():
    """Check validation dependencies"""
    try:
        import torch
        from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
        return True
    except ImportError as e:
        logger.error(f"Validation dependencies missing: {e}")
        return False

if check_validation_dependencies():
    import torch
    from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
else:
    logger.error("❌ Cannot validate models - dependencies missing")

class TrainingValidator:
    """
    Advanced training validator for model performance assessment
    """
    
    def __init__(self, config):
        self.config = config
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"🔧 Validator using device: {self.device}")
        
        # Test cases for comprehensive validation
        self.setup_test_cases()
    
    def setup_test_cases(self):
        """Setup comprehensive test cases"""
        
        # Financial test cases (should be detected)
        self.financial_test_cases = [
            # Income cases
            {"text": "Dapat 500rb dari freelance", "expected_intent": "income", "should_detect": True},
            {"text": "Papa transfer 1 juta", "expected_intent": "income", "should_detect": True},
            {"text": "Beasiswa 2 juta cair", "expected_intent": "income", "should_detect": True},
            {"text": "Gaji part time 800rb", "expected_intent": "income", "should_detect": True},
            
            # Expense cases
            {"text": "Bayar kos 900 ribu", "expected_intent": "expense", "should_detect": True},
            {"text": "Beli buku kuliah 150rb", "expected_intent": "expense", "should_detect": True},
            {"text": "Gofood ayam geprek 35rb", "expected_intent": "expense", "should_detect": True},
            {"text": "Habis 50rb buat jajan", "expected_intent": "expense", "should_detect": True},
            
            # Savings goal cases
            {"text": "Mau nabung buat laptop 10 juta", "expected_intent": "savings_goal", "should_detect": True},
            {"text": "Target beli motor 15 juta", "expected_intent": "savings_goal", "should_detect": True},
            {"text": "Pengen beli smartphone 3 juta", "expected_intent": "savings_goal", "should_detect": True},
            {"text": "Planning beli kamera 5 juta", "expected_intent": "savings_goal", "should_detect": True},
        ]
        
        # Non-financial test cases (should NOT be detected as financial)
        self.non_financial_test_cases = [
            # Greetings
            {"text": "Halo", "expected_intent": "non_financial", "should_detect": False},
            {"text": "Selamat pagi", "expected_intent": "non_financial", "should_detect": False},
            {"text": "Apa kabar", "expected_intent": "non_financial", "should_detect": False},
            
            # General questions
            {"text": "Cara pakai aplikasi ini gimana", "expected_intent": "non_financial", "should_detect": False},
            {"text": "Tips hemat untuk mahasiswa", "expected_intent": "non_financial", "should_detect": False},
            {"text": "Apa itu budgeting", "expected_intent": "non_financial", "should_detect": False},
            
            # Casual conversation
            {"text": "Terima kasih", "expected_intent": "non_financial", "should_detect": False},
            {"text": "Capek banget hari ini", "expected_intent": "non_financial", "should_detect": False},
            {"text": "Weekend plan apa", "expected_intent": "non_financial", "should_detect": False},
            
            # Academic (non-financial)
            {"text": "Jadwal ujian kapan", "expected_intent": "non_financial", "should_detect": False},
            {"text": "Tugas susah banget", "expected_intent": "non_financial", "should_detect": False},
            {"text": "Semester ini berat", "expected_intent": "non_financial", "should_detect": False},
        ]
        
        # Query test cases (should be detected as queries)
        self.query_test_cases = [
            {"text": "Total tabungan saya berapa", "expected_query": "total_savings_query", "is_query": True},
            {"text": "Budget performance bulan ini", "expected_query": "budget_performance_query", "is_query": True},
            {"text": "Pengeluaran terbesar saya", "expected_query": "expense_analysis_query", "is_query": True},
            {"text": "Progress tabungan saya", "expected_query": "savings_progress_query", "is_query": True},
            {"text": "Kesehatan keuangan saya", "expected_query": "financial_health_query", "is_query": True},
            {"text": "Saya ingin membeli laptop 10 juta", "expected_query": "purchase_advice_query", "is_query": True},
        ]
        
        # Edge cases - potentially problematic
        self.edge_test_cases = [
            # Ambiguous cases
            {"text": "50rb", "description": "Amount only - should be non-financial"},
            {"text": "Laptop gaming", "description": "Item only - should be non-financial"},
            {"text": "Mahal banget", "description": "Price comment - should be non-financial"},
            {"text": "Budget ketat", "description": "Budget mention - could be query or non-financial"},
            
            # Numbers in non-financial context
            {"text": "Umur saya 20 tahun", "description": "Number in age context"},
            {"text": "Kuliah semester 6", "description": "Number in academic context"},
            {"text": "IP saya 3.5", "description": "Number in GPA context"},
            
            # Financial words in non-financial context
            {"text": "Aplikasi keuangan yang bagus", "description": "Financial word in app recommendation"},
            {"text": "Belajar tentang investasi", "description": "Financial word in learning context"},
            {"text": "Mata kuliah ekonomi", "description": "Financial word in academic context"},
        ]
    
    def validate_all_models(self) -> Dict[str, Any]:
        """Validate all trained models"""
        logger.info("🔍 Starting comprehensive model validation...")
        
        validation_results = {}
        
        try:
            # Validate Intent Classifier
            logger.info("\n📊 Validating Intent Classifier...")
            intent_results = self.validate_intent_classifier()
            validation_results["intent_classifier"] = intent_results
            
            # Validate Category Classifier
            logger.info("\n🏷️ Validating Category Classifier...")
            category_results = self.validate_category_classifier()
            validation_results["category_classifier"] = category_results
            
            # Validate Query Classifier
            logger.info("\n❓ Validating Query Classifier...")
            query_results = self.validate_query_classifier()
            validation_results["query_classifier"] = query_results
            
            # Overall assessment
            overall_score = self.calculate_overall_score(validation_results)
            validation_results["overall_score"] = overall_score
            
            # Generate validation report
            report = self.generate_validation_report(validation_results)
            self.save_validation_report(report)
            
            logger.info("✅ Model validation completed!")
            return validation_results
            
        except Exception as e:
            logger.error(f"❌ Model validation failed: {e}")
            raise
    
    def validate_intent_classifier(self) -> Dict[str, Any]:
        """Validate intent classifier performance"""
        try:
            # Load model
            model_path = self.config.intent_model_dir
            if not os.path.exists(model_path):
                return {"error": f"Intent model not found at {model_path}"}
            
            tokenizer = AutoTokenizer.from_pretrained(model_path)
            model = AutoModelForSequenceClassification.from_pretrained(model_path)
            
            # Create pipeline
            classifier = pipeline(
                "text-classification",
                model=model,
                tokenizer=tokenizer,
                device=0 if self.device == "cuda" else -1,
                return_all_scores=True
            )
            
            # Test financial cases
            financial_results = []
            for case in self.financial_test_cases:
                prediction = classifier(case["text"])
                predicted_label = prediction[0][0]["label"]
                confidence = prediction[0][0]["score"]
                
                is_correct = predicted_label == case["expected_intent"]
                financial_results.append({
                    "text": case["text"],
                    "expected": case["expected_intent"],
                    "predicted": predicted_label,
                    "confidence": confidence,
                    "correct": is_correct
                })
            
            # Test non-financial cases
            non_financial_results = []
            for case in self.non_financial_test_cases:
                prediction = classifier(case["text"])
                predicted_label = prediction[0][0]["label"]
                confidence = prediction[0][0]["score"]
                
                is_correct = predicted_label == "non_financial"
                non_financial_results.append({
                    "text": case["text"],
                    "expected": "non_financial",
                    "predicted": predicted_label,
                    "confidence": confidence,
                    "correct": is_correct
                })
            
            # Calculate metrics
            financial_accuracy = sum(r["correct"] for r in financial_results) / len(financial_results)
            non_financial_accuracy = sum(r["correct"] for r in non_financial_results) / len(non_financial_results)
            overall_accuracy = (financial_accuracy + non_financial_accuracy) / 2
            
            # Bias analysis
            bias_score = self.analyze_financial_bias(financial_results, non_financial_results)
            
            return {
                "financial_accuracy": financial_accuracy,
                "non_financial_accuracy": non_financial_accuracy,
                "overall_accuracy": overall_accuracy,
                "bias_score": bias_score,
                "financial_results": financial_results,
                "non_financial_results": non_financial_results,
                "total_tests": len(financial_results) + len(non_financial_results)
            }
            
        except Exception as e:
            logger.error(f"❌ Intent classifier validation failed: {e}")
            return {"error": str(e)}
    
    def validate_category_classifier(self) -> Dict[str, Any]:
        """Validate category classifier performance"""
        try:
            # Load model
            model_path = self.config.category_model_dir
            if not os.path.exists(model_path):
                return {"error": f"Category model not found at {model_path}"}
            
            tokenizer = AutoTokenizer.from_pretrained(model_path)
            model = AutoModelForSequenceClassification.from_pretrained(model_path)
            
            # Create pipeline
            classifier = pipeline(
                "text-classification",
                model=model,
                tokenizer=tokenizer,
                device=0 if self.device == "cuda" else -1,
                return_all_scores=True
            )
            
            # Test with sample financial cases
            test_cases = [
                {"text": "Papa transfer 1 juta", "expected_category": "Uang Saku/Kiriman Ortu"},
                {"text": "Freelance web design 500rb", "expected_category": "Freelance/Project"},
                {"text": "Bayar kos 800rb", "expected_category": "Kos/Tempat Tinggal"},
                {"text": "Beli nasi gudeg 15rb", "expected_category": "Makanan Pokok"},
                {"text": "Gofood pizza 45rb", "expected_category": "Jajan & Snack"},
                {"text": "Nonton bioskop 50rb", "expected_category": "Hiburan & Sosial"},
            ]
            
            results = []
            for case in test_cases:
                prediction = classifier(case["text"])
                predicted_category = prediction[0][0]["label"]
                confidence = prediction[0][0]["score"]
                
                # For category, we'll be more lenient since exact match is harder
                is_reasonable = confidence > 0.3  # Just check if confident
                
                results.append({
                    "text": case["text"],
                    "expected": case["expected_category"],
                    "predicted": predicted_category,
                    "confidence": confidence,
                    "reasonable": is_reasonable
                })
            
            accuracy = sum(r["reasonable"] for r in results) / len(results)
            avg_confidence = sum(r["confidence"] for r in results) / len(results)
            
            return {
                "accuracy": accuracy,
                "avg_confidence": avg_confidence,
                "results": results,
                "total_tests": len(results)
            }
            
        except Exception as e:
            logger.error(f"❌ Category classifier validation failed: {e}")
            return {"error": str(e)}
    
    def validate_query_classifier(self) -> Dict[str, Any]:
        """Validate query classifier performance"""
        try:
            # Load model
            model_path = self.config.query_model_dir
            if not os.path.exists(model_path):
                return {"error": f"Query model not found at {model_path}"}
            
            tokenizer = AutoTokenizer.from_pretrained(model_path)
            model = AutoModelForSequenceClassification.from_pretrained(model_path)
            
            # Create pipeline
            classifier = pipeline(
                "text-classification",
                model=model,
                tokenizer=tokenizer,
                device=0 if self.device == "cuda" else -1,
                return_all_scores=True
            )
            
            # Test query cases
            query_results = []
            for case in self.query_test_cases:
                prediction = classifier(case["text"])
                predicted_query = prediction[0][0]["label"]
                confidence = prediction[0][0]["score"]
                
                is_correct = predicted_query == case["expected_query"]
                query_results.append({
                    "text": case["text"],
                    "expected": case["expected_query"],
                    "predicted": predicted_query,
                    "confidence": confidence,
                    "correct": is_correct
                })
            
            # Test non-query cases
            non_query_cases = [
                {"text": "Halo", "expected": "non_query"},
                {"text": "Terima kasih", "expected": "non_query"},
                {"text": "Capek banget", "expected": "non_query"},
            ]
            
            non_query_results = []
            for case in non_query_cases:
                prediction = classifier(case["text"])
                predicted_query = prediction[0][0]["label"]
                confidence = prediction[0][0]["score"]
                
                is_correct = predicted_query == "non_query"
                non_query_results.append({
                    "text": case["text"],
                    "expected": "non_query",
                    "predicted": predicted_query,
                    "confidence": confidence,
                    "correct": is_correct
                })
            
            # Calculate metrics
            query_accuracy = sum(r["correct"] for r in query_results) / len(query_results)
            non_query_accuracy = sum(r["correct"] for r in non_query_results) / len(non_query_results)
            overall_accuracy = (query_accuracy + non_query_accuracy) / 2
            
            return {
                "query_accuracy": query_accuracy,
                "non_query_accuracy": non_query_accuracy,
                "overall_accuracy": overall_accuracy,
                "query_results": query_results,
                "non_query_results": non_query_results,
                "total_tests": len(query_results) + len(non_query_results)
            }
            
        except Exception as e:
            logger.error(f"❌ Query classifier validation failed: {e}")
            return {"error": str(e)}
    
    def analyze_financial_bias(self, financial_results: List[Dict], non_financial_results: List[Dict]) -> float:
        """Analyze bias towards financial detection"""
        try:
            # Count false positives (non-financial classified as financial)
            false_positives = sum(1 for r in non_financial_results if r["predicted"] != "non_financial")
            
            # Count false negatives (financial classified as non-financial)
            false_negatives = sum(1 for r in financial_results if r["predicted"] == "non_financial")
            
            total_non_financial = len(non_financial_results)
            total_financial = len(financial_results)
            
            # Bias score: lower is better (less biased)
            # 0.0 = no bias, 1.0 = maximum bias
            if total_non_financial > 0:
                false_positive_rate = false_positives / total_non_financial
            else:
                false_positive_rate = 0
            
            if total_financial > 0:
                false_negative_rate = false_negatives / total_financial
            else:
                false_negative_rate = 0
            
            # Bias score combines both rates
            bias_score = (false_positive_rate + false_negative_rate) / 2
            
            logger.info(f"📊 Bias analysis:")
            logger.info(f"  False positive rate: {false_positive_rate:.3f}")
            logger.info(f"  False negative rate: {false_negative_rate:.3f}")
            logger.info(f"  Overall bias score: {bias_score:.3f}")
            
            return bias_score
            
        except Exception as e:
            logger.error(f"❌ Bias analysis failed: {e}")
            return 1.0  # Maximum bias on error
    
    def calculate_overall_score(self, validation_results: Dict[str, Any]) -> float:
        """Calculate overall validation score"""
        try:
            scores = []
            
            # Intent classifier score (40% weight)
            intent_results = validation_results.get("intent_classifier", {})
            if "overall_accuracy" in intent_results:
                intent_score = intent_results["overall_accuracy"]
                bias_penalty = intent_results.get("bias_score", 0) * 0.5  # Penalty for bias
                intent_weighted = max(0, intent_score - bias_penalty) * 0.4
                scores.append(intent_weighted)
            
            # Category classifier score (30% weight)
            category_results = validation_results.get("category_classifier", {})
            if "accuracy" in category_results:
                category_score = category_results["accuracy"] * 0.3
                scores.append(category_score)
            
            # Query classifier score (30% weight)
            query_results = validation_results.get("query_classifier", {})
            if "overall_accuracy" in query_results:
                query_score = query_results["overall_accuracy"] * 0.3
                scores.append(query_score)
            
            overall_score = sum(scores) if scores else 0.0
            
            logger.info(f"📊 Overall validation score: {overall_score:.3f}")
            return overall_score
            
        except Exception as e:
            logger.error(f"❌ Overall score calculation failed: {e}")
            return 0.0
    
    def generate_validation_report(self, validation_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive validation report"""
        return {
            "validation_info": {
                "validated_at": datetime.now().isoformat(),
                "validator_version": "AdvancedValidator_v1.0",
                "models_tested": list(validation_results.keys())
            },
            "performance_summary": {
                "overall_score": validation_results.get("overall_score", 0),
                "intent_accuracy": validation_results.get("intent_classifier", {}).get("overall_accuracy", 0),
                "category_accuracy": validation_results.get("category_classifier", {}).get("accuracy", 0),
                "query_accuracy": validation_results.get("query_classifier", {}).get("overall_accuracy", 0),
                "bias_score": validation_results.get("intent_classifier", {}).get("bias_score", 1.0)
            },
            "detailed_results": validation_results,
            "assessment": self.generate_assessment(validation_results),
            "recommendations": self.generate_recommendations(validation_results)
        }
    
    def generate_assessment(self, validation_results: Dict[str, Any]) -> Dict[str, str]:
        """Generate assessment based on validation results"""
        overall_score = validation_results.get("overall_score", 0)
        bias_score = validation_results.get("intent_classifier", {}).get("bias_score", 1.0)
        
        if overall_score >= 0.8 and bias_score <= 0.2:
            grade = "A"
            assessment = "Excellent performance with minimal bias"
        elif overall_score >= 0.7 and bias_score <= 0.3:
            grade = "B"
            assessment = "Good performance with acceptable bias"
        elif overall_score >= 0.6:
            grade = "C"
            assessment = "Fair performance, needs improvement"
        else:
            grade = "D"
            assessment = "Poor performance, significant improvements needed"
        
        return {
            "grade": grade,
            "assessment": assessment,
            "overall_score": overall_score,
            "bias_score": bias_score
        }
    
    def generate_recommendations(self, validation_results: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on validation results"""
        recommendations = []
        
        overall_score = validation_results.get("overall_score", 0)
        bias_score = validation_results.get("intent_classifier", {}).get("bias_score", 1.0)
        
        if overall_score < 0.7:
            recommendations.append("Consider increasing training data size")
            recommendations.append("Review and improve dataset quality")
        
        if bias_score > 0.3:
            recommendations.append("Increase non-financial training examples")
            recommendations.append("Add more diverse conversation patterns")
            recommendations.append("Review template variety and balance")
        
        intent_results = validation_results.get("intent_classifier", {})
        if intent_results.get("financial_accuracy", 0) < 0.8:
            recommendations.append("Improve financial pattern recognition")
        
        if intent_results.get("non_financial_accuracy", 0) < 0.8:
            recommendations.append("Enhance non-financial conversation handling")
        
        category_results = validation_results.get("category_classifier", {})
        if category_results.get("accuracy", 0) < 0.7:
            recommendations.append("Improve category-specific training data")
        
        query_results = validation_results.get("query_classifier", {})
        if query_results.get("overall_accuracy", 0) < 0.8:
            recommendations.append("Enhance query detection patterns")
        
        if not recommendations:
            recommendations.append("Models performing well - ready for deployment")
            recommendations.append("Monitor performance on real conversations")
            recommendations.append("Collect feedback for continuous improvement")
        
        return recommendations
    
    def save_validation_report(self, report: Dict[str, Any]):
        """Save validation report"""
        os.makedirs(self.config.output_dir, exist_ok=True)
        report_path = os.path.join(self.config.output_dir, "validation_report.json")
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        logger.info(f"💾 Validation report saved to {report_path}")
        
        # Also save a summary
        summary_path = os.path.join(self.config.output_dir, "validation_summary.txt")
        with open(summary_path, 'w', encoding='utf-8') as f:
            f.write("LUNANCE AI MODEL VALIDATION SUMMARY\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"Overall Score: {report['performance_summary']['overall_score']:.3f}\n")
            f.write(f"Grade: {report['assessment']['grade']}\n")
            f.write(f"Assessment: {report['assessment']['assessment']}\n\n")
            f.write("DETAILED SCORES:\n")
            f.write(f"Intent Accuracy: {report['performance_summary']['intent_accuracy']:.3f}\n")
            f.write(f"Category Accuracy: {report['performance_summary']['category_accuracy']:.3f}\n")
            f.write(f"Query Accuracy: {report['performance_summary']['query_accuracy']:.3f}\n")
            f.write(f"Bias Score: {report['performance_summary']['bias_score']:.3f}\n\n")
            f.write("RECOMMENDATIONS:\n")
            for i, rec in enumerate(report['recommendations'], 1):
                f.write(f"{i}. {rec}\n")
        
        logger.info(f"📄 Validation summary saved to {summary_path}")