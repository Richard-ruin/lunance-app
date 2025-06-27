
// lib/features/dashboard/data/models/category_breakdown_model.dart
import '../../domain/entities/category_breakdown.dart';

class CategoryBreakdownModel extends CategoryBreakdown {
  const CategoryBreakdownModel({
    required super.period,
    required super.totalExpense,
    required super.breakdown,
  });

  factory CategoryBreakdownModel.fromJson(Map<String, dynamic> json) {
    return CategoryBreakdownModel(
      period: json['period'] ?? 'monthly',
      totalExpense: (json['total_expense'] ?? 0).toDouble(),
      breakdown: (json['breakdown'] as List<dynamic>?)
          ?.map((item) => CategoryItemModel.fromJson(item))
          .toList() ?? [],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'period': period,
      'total_expense': totalExpense,
      'breakdown': breakdown.map((item) => (item as CategoryItemModel).toJson()).toList(),
    };
  }
}

class CategoryItemModel extends CategoryItem {
  const CategoryItemModel({
    required super.categoryId,
    required super.categoryName,
    required super.categoryIcon,
    required super.categoryColor,
    required super.totalAmount,
    required super.transactionCount,
    required super.averageAmount,
    required super.percentage,
  });

  factory CategoryItemModel.fromJson(Map<String, dynamic> json) {
    return CategoryItemModel(
      categoryId: json['category_id'] ?? '',
      categoryName: json['category_name'] ?? '',
      categoryIcon: json['category_icon'] ?? '💰',
      categoryColor: json['category_color'] ?? '#3498db',
      totalAmount: (json['total_amount'] ?? 0).toDouble(),
      transactionCount: json['transaction_count'] ?? 0,
      averageAmount: (json['average_amount'] ?? 0).toDouble(),
      percentage: (json['percentage'] ?? 0).toDouble(),
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
      'average_amount': averageAmount,
      'percentage': percentage,
    };
  }
}

