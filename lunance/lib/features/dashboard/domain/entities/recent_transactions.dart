
// lib/features/dashboard/domain/entities/recent_transactions.dart
import 'package:equatable/equatable.dart';

class RecentTransactions extends Equatable {
  final List<TransactionItem> transactions;
  final int count;

  const RecentTransactions({
    required this.transactions,
    required this.count,
  });

  @override
  List<Object> get props => [transactions, count];
}

class TransactionItem extends Equatable {
  final String id;
  final String type;
  final double amount;
  final String title;
  final DateTime transactionDate;
  final String paymentMethod;
  final TransactionCategory category;
  final TransactionLocation? location;
  final String? notes;

  const TransactionItem({
    required this.id,
    required this.type,
    required this.amount,
    required this.title,
    required this.transactionDate,
    required this.paymentMethod,
    required this.category,
    this.location,
    this.notes,
  });

  bool get isIncome => type == 'income';
  bool get isExpense => type == 'expense';

  @override
  List<Object?> get props => [
    id,
    type,
    amount,
    title,
    transactionDate,
    paymentMethod,
    category,
    location,
    notes,
  ];
}

class TransactionCategory extends Equatable {
  final String id;
  final String name;
  final String icon;
  final String color;

  const TransactionCategory({
    required this.id,
    required this.name,
    required this.icon,
    required this.color,
  });

  @override
  List<Object> get props => [id, name, icon, color];
}

class TransactionLocation extends Equatable {
  final String name;
  final String type;

  const TransactionLocation({
    required this.name,
    required this.type,
  });

  @override
  List<Object> get props => [name, type];
}