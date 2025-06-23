// lib/features/history/data/models/transaction_history_model.dart
import '../../domain/entities/transaction_history.dart';

class TransactionHistoryModel extends TransactionHistory {
  const TransactionHistoryModel({
    required super.id,
    required super.title,
    required super.description,
    required super.amount,
    required super.type,
    required super.category,
    required super.date,
    required super.status,
    super.notes,
  });

  factory TransactionHistoryModel.fromJson(Map<String, dynamic> json) {
    return TransactionHistoryModel(
      id: json['id'] ?? '',
      title: json['title'] ?? '',
      description: json['description'] ?? '',
      amount: (json['amount'] ?? 0).toDouble(),
      type: json['type'] ?? 'expense',
      category: json['category'] ?? '',
      date: DateTime.parse(json['date'] ?? DateTime.now().toIso8601String()),
      status: json['status'] ?? 'completed',
      notes: json['notes'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'title': title,
      'description': description,
      'amount': amount,
      'type': type,
      'category': category,
      'date': date.toIso8601String(),
      'status': status,
      'notes': notes,
    };
  }

  factory TransactionHistoryModel.fromEntity(TransactionHistory entity) {
    return TransactionHistoryModel(
      id: entity.id,
      title: entity.title,
      description: entity.description,
      amount: entity.amount,
      type: entity.type,
      category: entity.category,
      date: entity.date,
      status: entity.status,
      notes: entity.notes,
    );
  }
}