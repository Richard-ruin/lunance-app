// lib/features/categories/data/models/category_model.dart
import '../../domain/entities/category.dart';

class TypicalAmountRangeModel extends TypicalAmountRange {
  const TypicalAmountRangeModel({
    required super.min,
    required super.max,
    required super.avg,
  });

  factory TypicalAmountRangeModel.fromJson(Map<String, dynamic> json) {
    return TypicalAmountRangeModel(
      min: (json['min'] as num).toDouble(),
      max: (json['max'] as num).toDouble(),
      avg: (json['avg'] as num).toDouble(),
    );
  }

  Map<String, dynamic> toJson() => {
        'min': min,
        'max': max,
        'avg': avg,
      };
}

class CategoryModel extends Category {
  const CategoryModel({
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
  });

  factory CategoryModel.fromJson(Map<String, dynamic> json) {
    return CategoryModel(
      id: json['_id'] ?? json['id'] ?? '',
      name: json['name'] ?? '',
      parentId: json['parent_id'],
      type: json['type'] ?? '',
      icon: json['icon'] ?? '📂',
      color: json['color'] ?? '#757575',
      isSystem: json['is_system'] ?? false,
      studentSpecific: json['student_specific'] ?? false,
      typicalAmountRange: json['typical_amount_range'] != null
          ? TypicalAmountRangeModel.fromJson(json['typical_amount_range'])
          : null,
      keywords: List<String>.from(json['keywords'] ?? []),
      createdAt: DateTime.parse(json['created_at'] ?? DateTime.now().toIso8601String()),
    );
  }

  Map<String, dynamic> toJson() => {
        'id': id,
        'name': name,
        'parent_id': parentId,
        'type': type,
        'icon': icon,
        'color': color,
        'is_system': isSystem,
        'student_specific': studentSpecific,
        'typical_amount_range': typicalAmountRange != null
            ? TypicalAmountRangeModel(
                min: typicalAmountRange!.min,
                max: typicalAmountRange!.max,
                avg: typicalAmountRange!.avg,
              ).toJson()
            : null,
        'keywords': keywords,
        'created_at': createdAt.toIso8601String(),
      };

  Category toEntity() => Category(
        id: id,
        name: name,
        parentId: parentId,
        type: type,
        icon: icon,
        color: color,
        isSystem: isSystem,
        studentSpecific: studentSpecific,
        typicalAmountRange: typicalAmountRange,
        keywords: keywords,
        createdAt: createdAt,
      );
}

class CategoryWithStatsModel extends CategoryWithStats {
  const CategoryWithStatsModel({
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
    super.transactionCount = 0,
    super.totalAmount = 0.0,
    super.avgAmount = 0.0,
    super.lastUsed,
  });

  factory CategoryWithStatsModel.fromJson(Map<String, dynamic> json) {
    return CategoryWithStatsModel(
      id: json['_id'] ?? json['id'] ?? '',
      name: json['name'] ?? '',
      parentId: json['parent_id'],
      type: json['type'] ?? '',
      icon: json['icon'] ?? '📂',
      color: json['color'] ?? '#757575',
      isSystem: json['is_system'] ?? false,
      studentSpecific: json['student_specific'] ?? false,
      typicalAmountRange: json['typical_amount_range'] != null
          ? TypicalAmountRangeModel.fromJson(json['typical_amount_range'])
          : null,
      keywords: List<String>.from(json['keywords'] ?? []),
      createdAt: DateTime.parse(json['created_at'] ?? DateTime.now().toIso8601String()),
      transactionCount: json['transaction_count'] ?? 0,
      totalAmount: (json['total_amount'] ?? 0).toDouble(),
      avgAmount: (json['avg_amount'] ?? 0).toDouble(),
      lastUsed: json['last_used'] != null ? DateTime.parse(json['last_used']) : null,
    );
  }

  Map<String, dynamic> toJson() => {
        'id': id,
        'name': name,
        'parent_id': parentId,
        'type': type,
        'icon': icon,
        'color': color,
        'is_system': isSystem,
        'student_specific': studentSpecific,
        'typical_amount_range': typicalAmountRange != null
            ? TypicalAmountRangeModel(
                min: typicalAmountRange!.min,
                max: typicalAmountRange!.max,
                avg: typicalAmountRange!.avg,
              ).toJson()
            : null,
        'keywords': keywords,
        'created_at': createdAt.toIso8601String(),
        'transaction_count': transactionCount,
        'total_amount': totalAmount,
        'avg_amount': avgAmount,
        'last_used': lastUsed?.toIso8601String(),
      };

  CategoryWithStats toEntity() => CategoryWithStats(
        id: id,
        name: name,
        parentId: parentId,
        type: type,
        icon: icon,
        color: color,
        isSystem: isSystem,
        studentSpecific: studentSpecific,
        typicalAmountRange: typicalAmountRange,
        keywords: keywords,
        createdAt: createdAt,
        transactionCount: transactionCount,
        totalAmount: totalAmount,
        avgAmount: avgAmount,
        lastUsed: lastUsed,
      );
}