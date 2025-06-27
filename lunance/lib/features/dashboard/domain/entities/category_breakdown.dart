
// lib/features/dashboard/domain/entities/category_breakdown.dart
import 'package:equatable/equatable.dart';

class CategoryBreakdown extends Equatable {
  final String period;
  final double totalExpense;
  final List<CategoryItem> breakdown;

  const CategoryBreakdown({
    required this.period,
    required this.totalExpense,
    required this.breakdown,
  });

  @override
  List<Object> get props => [period, totalExpense, breakdown];
}

class CategoryItem extends Equatable {
  final String categoryId;
  final String categoryName;
  final String categoryIcon;
  final String categoryColor;
  final double totalAmount;
  final int transactionCount;
  final double averageAmount;
  final double percentage;

  const CategoryItem({
    required this.categoryId,
    required this.categoryName,
    required this.categoryIcon,
    required this.categoryColor,
    required this.totalAmount,
    required this.transactionCount,
    required this.averageAmount,
    required this.percentage,
  });

  @override
  List<Object> get props => [
    categoryId,
    categoryName,
    categoryIcon,
    categoryColor,
    totalAmount,
    transactionCount,
    averageAmount,
    percentage,
  ];
}