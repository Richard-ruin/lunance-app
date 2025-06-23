// lib/features/transactions/presentation/pages/add_transaction_page.dart
import 'package:flutter/material.dart';
import '../../../../core/theme/lunance_colors.dart';

class AddTransactionPage extends StatefulWidget {
  const AddTransactionPage({super.key});

  @override
  State<AddTransactionPage> createState() => _AddTransactionPageState();
}

class _AddTransactionPageState extends State<AddTransactionPage> {
  bool isIncome = true;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: LunanceColors.primaryBackground,
      appBar: AppBar(
        backgroundColor: isIncome ? LunanceColors.incomeGreen : LunanceColors.expenseRed,
        title: Text(
          isIncome ? 'Tambah Pemasukan' : 'Tambah Pengeluaran',
          style: const TextStyle(
            color: Colors.white,
            fontWeight: FontWeight.bold,
          ),
        ),
        elevation: 0,
        centerTitle: true,
      ),
      body: Column(
        children: [
          // Toggle Income/Expense
          Container(
            margin: const EdgeInsets.all(16),
            padding: const EdgeInsets.all(4),
            decoration: BoxDecoration(
              color: LunanceColors.cardBackground,
              borderRadius: BorderRadius.circular(12),
              boxShadow: [
                BoxShadow(
                  color: Colors.black.withOpacity(0.1),
                  blurRadius: 8,
                  offset: const Offset(0, 2),
                ),
              ],
            ),
            child: Row(
              children: [
                Expanded(
                  child: GestureDetector(
                    onTap: () => setState(() => isIncome = true),
                    child: Container(
                      padding: const EdgeInsets.symmetric(vertical: 12),
                      decoration: BoxDecoration(
                        color: isIncome ? LunanceColors.incomeGreen : Colors.transparent,
                        borderRadius: BorderRadius.circular(8),
                      ),
                      child: Text(
                        'Pemasukan',
                        textAlign: TextAlign.center,
                        style: TextStyle(
                          color: isIncome ? Colors.white : LunanceColors.primaryText,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ),
                  ),
                ),
                Expanded(
                  child: GestureDetector(
                    onTap: () => setState(() => isIncome = false),
                    child: Container(
                      padding: const EdgeInsets.symmetric(vertical: 12),
                      decoration: BoxDecoration(
                        color: !isIncome ? LunanceColors.expenseRed : Colors.transparent,
                        borderRadius: BorderRadius.circular(8),
                      ),
                      child: Text(
                        'Pengeluaran',
                        textAlign: TextAlign.center,
                        style: TextStyle(
                          color: !isIncome ? Colors.white : LunanceColors.primaryText,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ),
                  ),
                ),
              ],
            ),
          ),
          
          // Content
          Expanded(
            child: Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Icon(
                    isIncome ? Icons.trending_up : Icons.trending_down,
                    size: 100,
                    color: isIncome ? LunanceColors.incomeGreen : LunanceColors.expenseRed,
                  ),
                  const SizedBox(height: 20),
                  Text(
                    isIncome ? 'Tambah Pemasukan' : 'Tambah Pengeluaran',
                    style: const TextStyle(
                      fontSize: 24,
                      fontWeight: FontWeight.bold,
                      color: LunanceColors.primaryText,
                    ),
                  ),
                  const SizedBox(height: 10),
                  Text(
                    isIncome 
                        ? 'Halaman ini akan menampilkan form untuk menambah pemasukan'
                        : 'Halaman ini akan menampilkan form untuk menambah pengeluaran',
                    style: const TextStyle(
                      fontSize: 16,
                      color: LunanceColors.secondaryText,
                    ),
                    textAlign: TextAlign.center,
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}