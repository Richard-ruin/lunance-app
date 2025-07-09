// lib/models/transaction_model.dart
class Transaction {
  final String id;
  final String userId;
  final String categoryId;
  final String transactionType;
  final double amount;
  final String description;
  final DateTime transactionDate;
  final DateTime createdAt;
  final DateTime updatedAt;
  final String? categoryName;
  final String? categoryIcon;
  final String? categoryColor;

  Transaction({
    required this.id,
    required this.userId,
    required this.categoryId,
    required this.transactionType,
    required this.amount,
    required this.description,
    required this.transactionDate,
    required this.createdAt,
    required this.updatedAt,
    this.categoryName,
    this.categoryIcon,
    this.categoryColor,
  });

  factory Transaction.fromJson(Map<String, dynamic> json) {
    return Transaction(
      id: json['id'] ?? '',
      userId: json['user_id'] ?? '',
      categoryId: json['category_id'] ?? '',
      transactionType: json['transaction_type'] ?? 'expense',
      amount: (json['amount'] ?? 0.0).toDouble(),
      description: json['description'] ?? '',
      transactionDate: DateTime.parse(json['transaction_date'] ?? DateTime.now().toIso8601String()),
      createdAt: DateTime.parse(json['created_at'] ?? DateTime.now().toIso8601String()),
      updatedAt: DateTime.parse(json['updated_at'] ?? DateTime.now().toIso8601String()),
      categoryName: json['category_name'],
      categoryIcon: json['category_icon'],
      categoryColor: json['category_color'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'user_id': userId,
      'category_id': categoryId,
      'transaction_type': transactionType,
      'amount': amount,
      'description': description,
      'transaction_date': transactionDate.toIso8601String().split('T')[0],
      'created_at': createdAt.toIso8601String(),
      'updated_at': updatedAt.toIso8601String(),
      'category_name': categoryName,
      'category_icon': categoryIcon,
      'category_color': categoryColor,
    };
  }

  Transaction copyWith({
    String? id,
    String? userId,
    String? categoryId,
    String? transactionType,
    double? amount,
    String? description,
    DateTime? transactionDate,
    DateTime? createdAt,
    DateTime? updatedAt,
    String? categoryName,
    String? categoryIcon,
    String? categoryColor,
  }) {
    return Transaction(
      id: id ?? this.id,
      userId: userId ?? this.userId,
      categoryId: categoryId ?? this.categoryId,
      transactionType: transactionType ?? this.transactionType,
      amount: amount ?? this.amount,
      description: description ?? this.description,
      transactionDate: transactionDate ?? this.transactionDate,
      createdAt: createdAt ?? this.createdAt,
      updatedAt: updatedAt ?? this.updatedAt,
      categoryName: categoryName ?? this.categoryName,
      categoryIcon: categoryIcon ?? this.categoryIcon,
      categoryColor: categoryColor ?? this.categoryColor,
    );
  }

  bool get isIncome => transactionType == 'income';
  bool get isExpense => transactionType == 'expense';
}

class TransactionCreate {
  final String categoryId;
  final String transactionType;
  final double amount;
  final String description;
  final DateTime transactionDate;

  TransactionCreate({
    required this.categoryId,
    required this.transactionType,
    required this.amount,
    required this.description,
    required this.transactionDate,
  });

  Map<String, dynamic> toJson() {
    return {
      'category_id': categoryId,
      'transaction_type': transactionType,
      'amount': amount,
      'description': description,
      'transaction_date': transactionDate.toIso8601String().split('T')[0],
    };
  }
}

class TransactionUpdate {
  final String? categoryId;
  final String? transactionType;
  final double? amount;
  final String? description;
  final DateTime? transactionDate;

  TransactionUpdate({
    this.categoryId,
    this.transactionType,
    this.amount,
    this.description,
    this.transactionDate,
  });

  Map<String, dynamic> toJson() {
    final map = <String, dynamic>{};
    if (categoryId != null) map['category_id'] = categoryId;
    if (transactionType != null) map['transaction_type'] = transactionType;
    if (amount != null) map['amount'] = amount;
    if (description != null) map['description'] = description;
    if (transactionDate != null) map['transaction_date'] = transactionDate!.toIso8601String().split('T')[0];
    return map;
  }
}

class TransactionSummary {
  final double totalIncome;
  final double totalExpense;
  final double netAmount;
  final int transactionCount;
  final double averageTransaction;
  final double? largestExpense;
  final double? largestIncome;

  TransactionSummary({
    required this.totalIncome,
    required this.totalExpense,
    required this.netAmount,
    required this.transactionCount,
    required this.averageTransaction,
    this.largestExpense,
    this.largestIncome,
  });

  factory TransactionSummary.fromJson(Map<String, dynamic> json) {
    return TransactionSummary(
      totalIncome: (json['total_income'] ?? 0.0).toDouble(),
      totalExpense: (json['total_expense'] ?? 0.0).toDouble(),
      netAmount: (json['net_amount'] ?? 0.0).toDouble(),
      transactionCount: json['transaction_count'] ?? 0,
      averageTransaction: (json['average_transaction'] ?? 0.0).toDouble(),
      largestExpense: json['largest_expense']?.toDouble(),
      largestIncome: json['largest_income']?.toDouble(),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'total_income': totalIncome,
      'total_expense': totalExpense,
      'net_amount': netAmount,
      'transaction_count': transactionCount,
      'average_transaction': averageTransaction,
      'largest_expense': largestExpense,
      'largest_income': largestIncome,
    };
  }
}

class MonthlySummary {
  final int year;
  final int month;
  final String monthName;
  final double totalIncome;
  final double totalExpense;
  final double netAmount;
  final int transactionCount;

  MonthlySummary({
    required this.year,
    required this.month,
    required this.monthName,
    required this.totalIncome,
    required this.totalExpense,
    required this.netAmount,
    required this.transactionCount,
  });

  factory MonthlySummary.fromJson(Map<String, dynamic> json) {
    return MonthlySummary(
      year: json['year'] ?? DateTime.now().year,
      month: json['month'] ?? DateTime.now().month,
      monthName: json['month_name'] ?? '',
      totalIncome: (json['total_income'] ?? 0.0).toDouble(),
      totalExpense: (json['total_expense'] ?? 0.0).toDouble(),
      netAmount: (json['net_amount'] ?? 0.0).toDouble(),
      transactionCount: json['transaction_count'] ?? 0,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'year': year,
      'month': month,
      'month_name': monthName,
      'total_income': totalIncome,
      'total_expense': totalExpense,
      'net_amount': netAmount,
      'transaction_count': transactionCount,
    };
  }
}

class CategorySummary {
  final String categoryId;
  final String categoryName;
  final String categoryIcon;
  final String categoryColor;
  final double totalAmount;
  final int transactionCount;
  final double percentage;
  final double averageAmount;

  CategorySummary({
    required this.categoryId,
    required this.categoryName,
    required this.categoryIcon,
    required this.categoryColor,
    required this.totalAmount,
    required this.transactionCount,
    required this.percentage,
    required this.averageAmount,
  });

  factory CategorySummary.fromJson(Map<String, dynamic> json) {
    return CategorySummary(
      categoryId: json['category_id'] ?? '',
      categoryName: json['category_name'] ?? '',
      categoryIcon: json['category_icon'] ?? '',
      categoryColor: json['category_color'] ?? '#000000',
      totalAmount: (json['total_amount'] ?? 0.0).toDouble(),
      transactionCount: json['transaction_count'] ?? 0,
      percentage: (json['percentage'] ?? 0.0).toDouble(),
      averageAmount: (json['average_amount'] ?? 0.0).toDouble(),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'category_id': categoryId,
      'category_name': categoryName,
      'category_icon': categoryIcon,
      'category_color': categoryColor,
      'total_amount': totalAmount,
      'transaction_count': transactionCount,
      'percentage': percentage,
      'average_amount': averageAmount,
    };
  }
}

class DailySummary {
  final DateTime transactionDate;
  final double totalIncome;
  final double totalExpense;
  final double netAmount;
  final int transactionCount;

  DailySummary({
    required this.transactionDate,
    required this.totalIncome,
    required this.totalExpense,
    required this.netAmount,
    required this.transactionCount,
  });

  factory DailySummary.fromJson(Map<String, dynamic> json) {
    return DailySummary(
      transactionDate: DateTime.parse(json['transaction_date'] ?? DateTime.now().toIso8601String()),
      totalIncome: (json['total_income'] ?? 0.0).toDouble(),
      totalExpense: (json['total_expense'] ?? 0.0).toDouble(),
      netAmount: (json['net_amount'] ?? 0.0).toDouble(),
      transactionCount: json['transaction_count'] ?? 0,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'transaction_date': transactionDate.toIso8601String().split('T')[0],
      'total_income': totalIncome,
      'total_expense': totalExpense,
      'net_amount': netAmount,
      'transaction_count': transactionCount,
    };
  }
}

class DashboardOverview {
  final MonthlyOverview currentMonth;
  final List<MonthlyTrend> monthlyTrends;
  final List<TopExpenseCategory> topExpenseCategories;
  final List<RecentTransaction> recentTransactions;

  DashboardOverview({
    required this.currentMonth,
    required this.monthlyTrends,
    required this.topExpenseCategories,
    required this.recentTransactions,
  });

  factory DashboardOverview.fromJson(Map<String, dynamic> json) {
    return DashboardOverview(
      currentMonth: MonthlyOverview.fromJson(json['current_month'] ?? {}),
      monthlyTrends: (json['monthly_trends'] as List<dynamic>?)
          ?.map((item) => MonthlyTrend.fromJson(item))
          .toList() ?? [],
      topExpenseCategories: (json['top_expense_categories'] as List<dynamic>?)
          ?.map((item) => TopExpenseCategory.fromJson(item))
          .toList() ?? [],
      recentTransactions: (json['recent_transactions'] as List<dynamic>?)
          ?.map((item) => RecentTransaction.fromJson(item))
          .toList() ?? [],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'current_month': currentMonth.toJson(),
      'monthly_trends': monthlyTrends.map((item) => item.toJson()).toList(),
      'top_expense_categories': topExpenseCategories.map((item) => item.toJson()).toList(),
      'recent_transactions': recentTransactions.map((item) => item.toJson()).toList(),
    };
  }
}

class MonthlyOverview {
  final double totalIncome;
  final double totalExpense;
  final double netAmount;
  final int transactionCount;

  MonthlyOverview({
    required this.totalIncome,
    required this.totalExpense,
    required this.netAmount,
    required this.transactionCount,
  });

  factory MonthlyOverview.fromJson(Map<String, dynamic> json) {
    return MonthlyOverview(
      totalIncome: (json['total_income'] ?? 0.0).toDouble(),
      totalExpense: (json['total_expense'] ?? 0.0).toDouble(),
      netAmount: (json['net_amount'] ?? 0.0).toDouble(),
      transactionCount: json['transaction_count'] ?? 0,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'total_income': totalIncome,
      'total_expense': totalExpense,
      'net_amount': netAmount,
      'transaction_count': transactionCount,
    };
  }
}

class MonthlyTrend {
  final String month;
  final int year;
  final double income;
  final double expense;
  final double net;

  MonthlyTrend({
    required this.month,
    required this.year,
    required this.income,
    required this.expense,
    required this.net,
  });

  factory MonthlyTrend.fromJson(Map<String, dynamic> json) {
    return MonthlyTrend(
      month: json['month'] ?? '',
      year: json['year'] ?? DateTime.now().year,
      income: (json['income'] ?? 0.0).toDouble(),
      expense: (json['expense'] ?? 0.0).toDouble(),
      net: (json['net'] ?? 0.0).toDouble(),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'month': month,
      'year': year,
      'income': income,
      'expense': expense,
      'net': net,
    };
  }
}

class TopExpenseCategory {
  final String name;
  final double amount;
  final double percentage;
  final String color;

  TopExpenseCategory({
    required this.name,
    required this.amount,
    required this.percentage,
    required this.color,
  });

  factory TopExpenseCategory.fromJson(Map<String, dynamic> json) {
    return TopExpenseCategory(
      name: json['name'] ?? '',
      amount: (json['amount'] ?? 0.0).toDouble(),
      percentage: (json['percentage'] ?? 0.0).toDouble(),
      color: json['color'] ?? '#000000',
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'name': name,
      'amount': amount,
      'percentage': percentage,
      'color': color,
    };
  }
}

class RecentTransaction {
  final String id;
  final String description;
  final double amount;
  final String type;
  final String category;
  final DateTime date;
  final String categoryColor;

  RecentTransaction({
    required this.id,
    required this.description,
    required this.amount,
    required this.type,
    required this.category,
    required this.date,
    required this.categoryColor,
  });

  factory RecentTransaction.fromJson(Map<String, dynamic> json) {
    return RecentTransaction(
      id: json['id'] ?? '',
      description: json['description'] ?? '',
      amount: (json['amount'] ?? 0.0).toDouble(),
      type: json['type'] ?? 'expense',
      category: json['category'] ?? '',
      date: DateTime.parse(json['date'] ?? DateTime.now().toIso8601String()),
      categoryColor: json['category_color'] ?? '#000000',
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'description': description,
      'amount': amount,
      'type': type,
      'category': category,
      'date': date.toIso8601String().split('T')[0],
      'category_color': categoryColor,
    };
  }
}

class BulkTransactionRequest {
  final List<TransactionCreate> transactions;

  BulkTransactionRequest({
    required this.transactions,
  });

  Map<String, dynamic> toJson() {
    return {
      'transactions': transactions.map((t) => t.toJson()).toList(),
    };
  }
}

class BulkTransactionResponse {
  final bool success;
  final String message;
  final BulkTransactionData data;

  BulkTransactionResponse({
    required this.success,
    required this.message,
    required this.data,
  });

  factory BulkTransactionResponse.fromJson(Map<String, dynamic> json) {
    return BulkTransactionResponse(
      success: json['success'] ?? false,
      message: json['message'] ?? '',
      data: BulkTransactionData.fromJson(json['data'] ?? {}),
    );
  }
}

class BulkTransactionData {
  final int successCount;
  final int failureCount;
  final int totalCount;
  final List<BulkTransactionResult> createdTransactions;
  final List<BulkTransactionResult> failedTransactions;

  BulkTransactionData({
    required this.successCount,
    required this.failureCount,
    required this.totalCount,
    required this.createdTransactions,
    required this.failedTransactions,
  });

  factory BulkTransactionData.fromJson(Map<String, dynamic> json) {
    return BulkTransactionData(
      successCount: json['success_count'] ?? 0,
      failureCount: json['failure_count'] ?? 0,
      totalCount: json['total_count'] ?? 0,
      createdTransactions: (json['created_transactions'] as List<dynamic>?)
          ?.map((item) => BulkTransactionResult.fromJson(item))
          .toList() ?? [],
      failedTransactions: (json['failed_transactions'] as List<dynamic>?)
          ?.map((item) => BulkTransactionResult.fromJson(item))
          .toList() ?? [],
    );
  }
}

class BulkTransactionResult {
  final int index;
  final String? id;
  final Map<String, dynamic> data;
  final String? error;

  BulkTransactionResult({
    required this.index,
    this.id,
    required this.data,
    this.error,
  });

  factory BulkTransactionResult.fromJson(Map<String, dynamic> json) {
    return BulkTransactionResult(
      index: json['index'] ?? 0,
      id: json['id'],
      data: json['data'] ?? {},
      error: json['error'],
    );
  }
}

class PaginatedTransactions {
  final List<Transaction> items;
  final int total;
  final int page;
  final int perPage;
  final int totalPages;
  final bool hasNext;
  final bool hasPrev;

  PaginatedTransactions({
    required this.items,
    required this.total,
    required this.page,
    required this.perPage,
    required this.totalPages,
    required this.hasNext,
    required this.hasPrev,
  });

  factory PaginatedTransactions.fromJson(Map<String, dynamic> json) {
    return PaginatedTransactions(
      items: (json['items'] as List<dynamic>?)
          ?.map((item) => Transaction.fromJson(item))
          .toList() ?? [],
      total: json['total'] ?? 0,
      page: json['page'] ?? 1,
      perPage: json['per_page'] ?? 20,
      totalPages: json['total_pages'] ?? 0,
      hasNext: json['has_next'] ?? false,
      hasPrev: json['has_prev'] ?? false,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'items': items.map((item) => item.toJson()).toList(),
      'total': total,
      'page': page,
      'per_page': perPage,
      'total_pages': totalPages,
      'has_next': hasNext,
      'has_prev': hasPrev,
    };
  }
}

// Response models
class TransactionResponse {
  final bool success;
  final String message;
  final PaginatedTransactions? data;

  TransactionResponse({
    required this.success,
    required this.message,
    this.data,
  });
}

class TransactionDetailResponse {
  final bool success;
  final String message;
  final Transaction? data;

  TransactionDetailResponse({
    required this.success,
    required this.message,
    this.data,
  });
}

class TransactionSummaryResponse {
  final bool success;
  final String message;
  final TransactionSummary? data;

  TransactionSummaryResponse({
    required this.success,
    required this.message,
    this.data,
  });
}

class MonthlySummaryResponse {
  final bool success;
  final String message;
  final List<MonthlySummary>? data;

  MonthlySummaryResponse({
    required this.success,
    required this.message,
    this.data,
  });
}

class CategorySummaryResponse {
  final bool success;
  final String message;
  final List<CategorySummary>? data;

  CategorySummaryResponse({
    required this.success,
    required this.message,
    this.data,
  });
}

class DailySummaryResponse {
  final bool success;
  final String message;
  final List<DailySummary>? data;

  DailySummaryResponse({
    required this.success,
    required this.message,
    this.data,
  });
}

class DashboardOverviewResponse {
  final bool success;
  final String message;
  final DashboardOverview? data;

  DashboardOverviewResponse({
    required this.success,
    required this.message,
    this.data,
  });
}