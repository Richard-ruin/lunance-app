
// lib/features/dashboard/domain/entities/quick_stats.dart
import 'package:equatable/equatable.dart';

class QuickStats extends Equatable {
  final int totalTransactionsThisMonth;
  final int activeCategoriesCount;
  final double averageTransactionAmount;
  final int spendingStreakDays;
  final BudgetAdherence? budgetAdherence;

  const QuickStats({
    required this.totalTransactionsThisMonth,
    required this.activeCategoriesCount,
    required this.averageTransactionAmount,
    required this.spendingStreakDays,
    this.budgetAdherence,
  });

  @override
  List<Object?> get props => [
    totalTransactionsThisMonth,
    activeCategoriesCount,
    averageTransactionAmount,
    spendingStreakDays,
    budgetAdherence,
  ];
}

class BudgetAdherence extends Equatable {
  final double spent;
  final double budget;
  final double percentage;
  final double remaining;

  const BudgetAdherence({
    required this.spent,
    required this.budget,
    required this.percentage,
    required this.remaining,
  });

  bool get isOverBudget => percentage > 100;
  bool get isNearLimit => percentage > 80 && percentage <= 100;
  bool get isOnTrack => percentage <= 80;

  @override
  List<Object> get props => [spent, budget, percentage, remaining];
}