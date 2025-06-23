// lib/features/dashboard/data/models/financial_summary_model.dart
import '../../domain/entities/financial_summary.dart';

class FinancialSummaryModel extends FinancialSummary {
  const FinancialSummaryModel({
    required super.totalIncome,
    required super.totalExpense,
    required super.balance,
    required super.monthlyIncome,
    required super.monthlyExpense,
    required super.savingsGoal,
    required super.currentSavings,
    required super.topCategories,
    required super.recentTransactions,
  });

  factory FinancialSummaryModel.fromJson(Map<String, dynamic> json) {
    return FinancialSummaryModel(
      totalIncome: (json['totalIncome'] as num).toDouble(),
      totalExpense: (json['totalExpense'] as num).toDouble(),
      balance: (json['balance'] as num).toDouble(),
      monthlyIncome: (json['monthlyIncome'] as num).toDouble(),
      monthlyExpense: (json['monthlyExpense'] as num).toDouble(),
      savingsGoal: (json['savingsGoal'] as num).toDouble(),
      currentSavings: (json['currentSavings'] as num).toDouble(),
      topCategories: (json['topCategories'] as List)
          .map((e) => CategorySummaryModel.fromJson(e))
          .toList(),
      recentTransactions: (json['recentTransactions'] as List)
          .map((e) => RecentTransactionModel.fromJson(e))
          .toList(),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'totalIncome': totalIncome,
      'totalExpense': totalExpense,
      'balance': balance,
      'monthlyIncome': monthlyIncome,
      'monthlyExpense': monthlyExpense,
      'savingsGoal': savingsGoal,
      'currentSavings': currentSavings,
      'topCategories': topCategories.map((e) => (e as CategorySummaryModel).toJson()).toList(),
      'recentTransactions': recentTransactions.map((e) => (e as RecentTransactionModel).toJson()).toList(),
    };
  }
}

class CategorySummaryModel extends CategorySummary {
  const CategorySummaryModel({
    required super.name,
    required super.icon,
    required super.amount,
    required super.percentage,
    required super.color,
  });

  factory CategorySummaryModel.fromJson(Map<String, dynamic> json) {
    return CategorySummaryModel(
      name: json['name'] as String,
      icon: json['icon'] as String,
      amount: (json['amount'] as num).toDouble(),
      percentage: (json['percentage'] as num).toDouble(),
      color: json['color'] as String,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'name': name,
      'icon': icon,
      'amount': amount,
      'percentage': percentage,
      'color': color,
    };
  }
}

class RecentTransactionModel extends RecentTransaction {
  const RecentTransactionModel({
    required super.id,
    required super.title,
    required super.category,
    required super.amount,
    required super.isIncome,
    required super.date,
    super.description,
  });

  factory RecentTransactionModel.fromJson(Map<String, dynamic> json) {
    return RecentTransactionModel(
      id: json['id'] as String,
      title: json['title'] as String,
      category: json['category'] as String,
      amount: (json['amount'] as num).toDouble(),
      isIncome: json['isIncome'] as bool,
      date: DateTime.parse(json['date'] as String),
      description: json['description'] as String?,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'title': title,
      'category': category,
      'amount': amount,
      'isIncome': isIncome,
      'date': date.toIso8601String(),
      'description': description,
    };
  }
}