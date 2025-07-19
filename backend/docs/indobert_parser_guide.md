# IndoBERT Financial Parser - Usage Guide

## Overview
IndoBERT Financial Parser adalah enhanced version dari financial parser yang menggunakan fine-tuned IndoBERT model untuk parsing data keuangan mahasiswa Indonesia dengan akurasi tinggi.

## Features
- ML-based Intent Classification: Klasifikasi income/expense/savings_goal menggunakan fine-tuned IndoBERT
- Smart Category Detection: Kategorisasi otomatis berdasarkan konteks Indonesia
- 50/30/20 Budget Integration: Mendukung metode budgeting Elizabeth Warren
- Fallback Mechanism: Otomatis fallback ke rule-based jika model tidak tersedia
- Enhanced Amount Parsing: Parsing jumlah uang dengan format Indonesia

## Installation

### 1. Install Dependencies
```bash
pip install torch transformers datasets scikit-learn
```

### 2. Run Integration Script
```bash
python scripts/integrate_indobert_parser.py
```

### 3. Train Models (Optional)
```bash
python scripts/train_indobert_financial.py
```

### 4. Test Integration
```bash
python scripts/test_integration.py
```

## Usage

### Basic Usage
```python
from app.services.indoroberta_financial_parser import IndoRoBERTaFinancialParser

# Initialize parser
parser = IndoRoBERTaFinancialParser()

# Parse financial data
result = parser.parse_financial_data("Bayar kos 800 ribu")
print(result)
```

### Advanced Usage
```python
# Parse with monthly income context for budget guidance
result = parser.parse_financial_data(
    "Jajan bubble tea 25rb", 
    monthly_income=2000000
)

# Extract specific components
amount = parser.parse_amount("Freelance dapat 500rb")
transaction_type = parser.detect_transaction_type("Mau nabung buat beli laptop")
target_date = parser.parse_target_date("dalam 6 bulan")
```

## Model Training

### 1. Generate Training Data
```python
from scripts.train_indobert_financial import FinancialDatasetGenerator

generator = FinancialDatasetGenerator()
dataset = generator.generate_training_data(num_samples=20000)
```

### 2. Train Models
```python
from scripts.train_indobert_financial import IndoBERTFineTuner

trainer = IndoBERTFineTuner()
trainer.train_intent_classifier(dataset)
trainer.train_category_classifier(category_dataset)
```

### 3. Model Files
Trained models will be saved in:
- `models/indobert-financial/intent_classifier/`
- `models/indobert-financial/category_classifier/`

## Fallback Mechanism

Parser otomatis menggunakan fallback:
1. **Primary**: Fine-tuned IndoBERT models
2. **Secondary**: Rule-based classification
3. **Tertiary**: Enhanced financial parser

## Supported Formats

### Input Examples
- **Income**: "Dapat uang saku 2 juta dari ortu"
- **Expense**: "Bayar kos 800 ribu"
- **Savings Goal**: "Mau nabung buat beli laptop 10 juta"

### Amount Formats
- `50rb`, `500 ribu`, `1 juta`, `2.5 juta`
- `1.500.000`, `2.000.000` (Indonesian format)
- `50000`, `1500000` (plain numbers)

### Category Mapping
- **NEEDS (50%)**: Kos, makan, transport, pendidikan
- **WANTS (30%)**: Hiburan, jajan, fashion, target tabungan
- **SAVINGS (20%)**: Tabungan, dana darurat, investasi

## Performance

### Expected Accuracy
- **Intent Classification**: >90%
- **Category Detection**: >85%
- **Amount Parsing**: >95%

### Fallback Performance
- **Rule-based Intent**: ~80%
- **Rule-based Category**: ~75%
- **Amount Parsing**: ~90%

## Troubleshooting

### Common Issues

1. **ImportError: No module named 'transformers'**
   ```bash
   pip install transformers torch
   ```

2. **Model not found error**
   - Run training script to generate models
   - Parser will automatically fall back to rule-based

3. **CUDA out of memory**
   - Reduce batch size in training
   - Use CPU instead of GPU

4. **Path errors on Windows**
   - Use forward slashes in paths
   - Ensure models directory exists

### Debug Mode
```python
import logging
logging.basicConfig(level=logging.DEBUG)

parser = IndoRoBERTaFinancialParser()
```

## Integration with Luna AI

Parser terintegrasi dengan Luna AI system:
- Automatic data parsing dari chat messages
- Confirmation flow untuk transaction data
- Budget guidance berdasarkan 50/30/20 method
- Real-time financial analysis

## License

MIT License - see LICENSE file for details
