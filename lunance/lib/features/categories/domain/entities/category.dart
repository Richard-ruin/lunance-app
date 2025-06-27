// lib/features/categories/domain/entities/category.dart
import 'package:equatable/equatable.dart';

class TypicalAmountRange extends Equatable {
  final double min;
  final double max;
  final double avg;

  const TypicalAmountRange({
    required this.min,
    required this.max,
    required this.avg,
  });

  @override
  List<Object> get props => [min, max, avg];
}

class Category extends Equatable {
  final String id;
  final String name;
  final String? parentId;
  final String type; // income, expense
  final String icon;
  final String color;
  final bool isSystem;
  final bool studentSpecific;
  final TypicalAmountRange? typicalAmountRange;
  final List<String> keywords;
  final DateTime createdAt;

  const Category({
    required this.id,
    required this.name,
    this.parentId,
    required this.type,
    required this.icon,
    required this.color,
    this.isSystem = false,
    this.studentSpecific = false,
    this.typicalAmountRange,
    this.keywords = const [],
    required this.createdAt,
  });

  bool get isIncome => type == 'income';
  bool get isExpense => type == 'expense';

  @override
  List<Object?> get props => [
        id,
        name,
        parentId,
        type,
        icon,
        color,
        isSystem,
        studentSpecific,
        typicalAmountRange,
        keywords,
        createdAt,
      ];
}

class CategoryWithStats extends Category {
  final int transactionCount;
  final double totalAmount;
  final double avgAmount;
  final DateTime? lastUsed;

  const CategoryWithStats({
    required super.id,
    required super.name,
    super.parentId,
    required super.type,
    required super.icon,
    required super.color,
    super.isSystem = false,
    super.studentSpecific = false,
    super.typicalAmountRange,
    super.keywords = const [],
    required super.createdAt,
    this.transactionCount = 0,
    this.totalAmount = 0.0,
    this.avgAmount = 0.0,
    this.lastUsed,
  });

  @override
  List<Object?> get props => [
        ...super.props,
        transactionCount,
        totalAmount,
        avgAmount,
        lastUsed,
      ];
}