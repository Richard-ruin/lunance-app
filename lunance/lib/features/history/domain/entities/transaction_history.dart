
// lib/features/history/domain/entities/transaction_history.dart
class TransactionHistory {
  final String id;
  final String title;
  final String description;
  final double amount;
  final String type; // 'income' or 'expense'
  final String category;
  final DateTime date;
  final String status;
  final String? notes;

  const TransactionHistory({
    required this.id,
    required this.title,
    required this.description,
    required this.amount,
    required this.type,
    required this.category,
    required this.date,
    required this.status,
    this.notes,
  });

  bool get isIncome => type.toLowerCase() == 'income';
  bool get isExpense => type.toLowerCase() == 'expense';
}