// lib/features/dashboard/data/models/recent_transactions_model.dart
import '../../domain/entities/recent_transactions.dart';

class RecentTransactionsModel extends RecentTransactions {
  const RecentTransactionsModel({
    required super.transactions,
    required super.count,
  });

  factory RecentTransactionsModel.fromJson(Map<String, dynamic> json) {
    return RecentTransactionsModel(
      transactions: (json['transactions'] as List<dynamic>?)
          ?.map((item) => TransactionItemModel.fromJson(item))
          .toList() ?? [],
      count: json['count'] ?? 0,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'transactions': transactions.map((item) => (item as TransactionItemModel).toJson()).toList(),
      'count': count,
    };
  }
}

class TransactionItemModel extends TransactionItem {
  const TransactionItemModel({
    required super.id,
    required super.type,
    required super.amount,
    required super.title,
    required super.transactionDate,
    required super.paymentMethod,
    required super.category,
    super.location,
    super.notes,
  });

  factory TransactionItemModel.fromJson(Map<String, dynamic> json) {
    return TransactionItemModel(
      id: json['id'] ?? '',
      type: json['type'] ?? '',
      amount: (json['amount'] ?? 0).toDouble(),
      title: json['title'] ?? '',
      transactionDate: DateTime.parse(json['transaction_date'] ?? DateTime.now().toIso8601String()),
      paymentMethod: json['payment_method'] ?? '',
      category: TransactionCategoryModel.fromJson(json['category'] ?? {}),
      location: json['location'] != null 
          ? TransactionLocationModel.fromJson(json['location'])
          : null,
      notes: json['notes'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'type': type,
      'amount': amount,
      'title': title,
      'transaction_date': transactionDate.toIso8601String(),
      'payment_method': paymentMethod,
      'category': (category as TransactionCategoryModel).toJson(),
      'location': location != null 
          ? (location as TransactionLocationModel).toJson()
          : null,
      'notes': notes,
    };
  }
}

class TransactionCategoryModel extends TransactionCategory {
  const TransactionCategoryModel({
    required super.id,
    required super.name,
    required super.icon,
    required super.color,
  });

  factory TransactionCategoryModel.fromJson(Map<String, dynamic> json) {
    return TransactionCategoryModel(
      id: json['id'] ?? '',
      name: json['name'] ?? 'Unknown',
      icon: json['icon'] ?? '💰',
      color: json['color'] ?? '#3498db',
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      'icon': icon,
      'color': color,
    };
  }
}

class TransactionLocationModel extends TransactionLocation {
  const TransactionLocationModel({
    required super.name,
    required super.type,
  });

  factory TransactionLocationModel.fromJson(Map<String, dynamic> json) {
    return TransactionLocationModel(
      name: json['name'] ?? '',
      type: json['type'] ?? '',
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'name': name,
      'type': type,
    };
  }
}