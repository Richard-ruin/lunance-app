// lib/features/dashboard/domain/entities/financial_summary.dart
class FinancialSummary {
  final double totalIncome;
  final double totalExpense;
  final double balance;
  final double monthlyIncome;
  final double monthlyExpense;
  final double savingsGoal;
  final double currentSavings;
  final List<CategorySummary> topCategories;
  final List<RecentTransaction> recentTransactions;

  const FinancialSummary({
    required this.totalIncome,
    required this.totalExpense,
    required this.balance,
    required this.monthlyIncome,
    required this.monthlyExpense,
    required this.savingsGoal,
    required this.currentSavings,
    required this.topCategories,
    required this.recentTransactions,
  });
}

class CategorySummary {
  final String name;
  final String icon;
  final double amount;
  final double percentage;
  final String color;

  const CategorySummary({
    required this.name,
    required this.icon,
    required this.amount,
    required this.percentage,
    required this.color,
  });
}

class RecentTransaction {
  final String id;
  final String title;
  final String category;
  final double amount;
  final bool isIncome;
  final DateTime date;
  final String? description;

  const RecentTransaction({
    required this.id,
    required this.title,
    required this.category,
    required this.amount,
    required this.isIncome,
    required this.date,
    this.description,
  });
}