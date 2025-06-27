
// lib/features/dashboard/data/models/quick_stats_model.dart
import '../../domain/entities/quick_stats.dart';

class QuickStatsModel extends QuickStats {
  const QuickStatsModel({
    required super.totalTransactionsThisMonth,
    required super.activeCategoriesCount,
    required super.averageTransactionAmount,
    required super.spendingStreakDays,
    super.budgetAdherence,
  });

  factory QuickStatsModel.fromJson(Map<String, dynamic> json) {
    return QuickStatsModel(
      totalTransactionsThisMonth: json['total_transactions_this_month'] ?? 0,
      activeCategoriesCount: json['active_categories_count'] ?? 0,
      averageTransactionAmount: (json['average_transaction_amount'] ?? 0).toDouble(),
      spendingStreakDays: json['spending_streak_days'] ?? 0,
      budgetAdherence: json['budget_adherence'] != null
          ? BudgetAdherenceModel.fromJson(json['budget_adherence'])
          : null,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'total_transactions_this_month': totalTransactionsThisMonth,
      'active_categories_count': activeCategoriesCount,
      'average_transaction_amount': averageTransactionAmount,
      'spending_streak_days': spendingStreakDays,
      'budget_adherence': budgetAdherence != null
          ? (budgetAdherence as BudgetAdherenceModel).toJson()
          : null,
    };
  }
}

class BudgetAdherenceModel extends BudgetAdherence {
  const BudgetAdherenceModel({
    required super.spent,
    required super.budget,
    required super.percentage,
    required super.remaining,
  });

  factory BudgetAdherenceModel.fromJson(Map<String, dynamic> json) {
    return BudgetAdherenceModel(
      spent: (json['spent'] ?? 0).toDouble(),
      budget: (json['budget'] ?? 0).toDouble(),
      percentage: (json['percentage'] ?? 0).toDouble(),
      remaining: (json['remaining'] ?? 0).toDouble(),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'spent': spent,
      'budget': budget,
      'percentage': percentage,
      'remaining': remaining,
    };
  }
}
