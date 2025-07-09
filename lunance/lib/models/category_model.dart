// lib/models/category_model.dart
class Category {
  final String id;
  final String name;
  final String icon;
  final String color;
  final bool isGlobal;
  final String? userId;
  final DateTime createdAt;
  final DateTime updatedAt;

  Category({
    required this.id,
    required this.name,
    required this.icon,
    required this.color,
    required this.isGlobal,
    this.userId,
    required this.createdAt,
    required this.updatedAt,
  });

  factory Category.fromJson(Map<String, dynamic> json) {
    return Category(
      id: json['id'] ?? '',
      name: json['name'] ?? '',
      icon: json['icon'] ?? '',
      color: json['color'] ?? '#000000',
      isGlobal: json['is_global'] ?? false,
      userId: json['user_id'],
      createdAt: DateTime.parse(json['created_at'] ?? DateTime.now().toIso8601String()),
      updatedAt: DateTime.parse(json['updated_at'] ?? DateTime.now().toIso8601String()),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      'icon': icon,
      'color': color,
      'is_global': isGlobal,
      'user_id': userId,
      'created_at': createdAt.toIso8601String(),
      'updated_at': updatedAt.toIso8601String(),
    };
  }

  Category copyWith({
    String? id,
    String? name,
    String? icon,
    String? color,
    bool? isGlobal,
    String? userId,
    DateTime? createdAt,
    DateTime? updatedAt,
  }) {
    return Category(
      id: id ?? this.id,
      name: name ?? this.name,
      icon: icon ?? this.icon,
      color: color ?? this.color,
      isGlobal: isGlobal ?? this.isGlobal,
      userId: userId ?? this.userId,
      createdAt: createdAt ?? this.createdAt,
      updatedAt: updatedAt ?? this.updatedAt,
    );
  }
}

class CategoryWithStats extends Category {
  final int transactionCount;
  final double totalAmount;
  final DateTime? lastUsed;

  CategoryWithStats({
    required super.id,
    required super.name,
    required super.icon,
    required super.color,
    required super.isGlobal,
    super.userId,
    required super.createdAt,
    required super.updatedAt,
    required this.transactionCount,
    required this.totalAmount,
    this.lastUsed,
  });

  factory CategoryWithStats.fromJson(Map<String, dynamic> json) {
    return CategoryWithStats(
      id: json['id'] ?? '',
      name: json['name'] ?? '',
      icon: json['icon'] ?? '',
      color: json['color'] ?? '#000000',
      isGlobal: json['is_global'] ?? false,
      userId: json['user_id'],
      createdAt: DateTime.parse(json['created_at'] ?? DateTime.now().toIso8601String()),
      updatedAt: DateTime.parse(json['updated_at'] ?? DateTime.now().toIso8601String()),
      transactionCount: json['transaction_count'] ?? 0,
      totalAmount: (json['total_amount'] ?? 0.0).toDouble(),
      lastUsed: json['last_used'] != null 
          ? DateTime.parse(json['last_used']) 
          : null,
    );
  }

  @override
  Map<String, dynamic> toJson() {
    final map = super.toJson();
    map.addAll({
      'transaction_count': transactionCount,
      'total_amount': totalAmount,
      'last_used': lastUsed?.toIso8601String(),
    });
    return map;
  }
}

class CategoryCreate {
  final String name;
  final String icon;
  final String color;

  CategoryCreate({
    required this.name,
    required this.icon,
    required this.color,
  });

  Map<String, dynamic> toJson() {
    return {
      'name': name,
      'icon': icon,
      'color': color,
    };
  }
}

class CategoryUpdate {
  final String? name;
  final String? icon;
  final String? color;

  CategoryUpdate({
    this.name,
    this.icon,
    this.color,
  });

  Map<String, dynamic> toJson() {
    final map = <String, dynamic>{};
    if (name != null) map['name'] = name;
    if (icon != null) map['icon'] = icon;
    if (color != null) map['color'] = color;
    return map;
  }
}

class CategoryStats {
  final int totalCategories;
  final int globalCategories;
  final int personalCategories;
  final List<MostUsedCategory> mostUsedCategories;
  final double categoriesByUser;

  CategoryStats({
    required this.totalCategories,
    required this.globalCategories,
    required this.personalCategories,
    required this.mostUsedCategories,
    required this.categoriesByUser,
  });

  factory CategoryStats.fromJson(Map<String, dynamic> json) {
    return CategoryStats(
      totalCategories: json['total_categories'] ?? 0,
      globalCategories: json['global_categories'] ?? 0,
      personalCategories: json['personal_categories'] ?? 0,
      mostUsedCategories: (json['most_used_categories'] as List<dynamic>?)
          ?.map((item) => MostUsedCategory.fromJson(item))
          .toList() ?? [],
      categoriesByUser: (json['categories_by_user'] ?? 0.0).toDouble(),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'total_categories': totalCategories,
      'global_categories': globalCategories,
      'personal_categories': personalCategories,
      'most_used_categories': mostUsedCategories.map((item) => item.toJson()).toList(),
      'categories_by_user': categoriesByUser,
    };
  }
}

class MostUsedCategory {
  final String name;
  final int usageCount;

  MostUsedCategory({
    required this.name,
    required this.usageCount,
  });

  factory MostUsedCategory.fromJson(Map<String, dynamic> json) {
    return MostUsedCategory(
      name: json['name'] ?? '',
      usageCount: json['usage_count'] ?? 0,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'name': name,
      'usage_count': usageCount,
    };
  }
}

class PaginatedCategories {
  final List<Category> items;
  final int total;
  final int page;
  final int perPage;
  final int totalPages;
  final bool hasNext;
  final bool hasPrev;

  PaginatedCategories({
    required this.items,
    required this.total,
    required this.page,
    required this.perPage,
    required this.totalPages,
    required this.hasNext,
    required this.hasPrev,
  });

  factory PaginatedCategories.fromJson(Map<String, dynamic> json) {
    return PaginatedCategories(
      items: (json['items'] as List<dynamic>?)
          ?.map((item) => Category.fromJson(item))
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
class CategoryResponse {
  final bool success;
  final String message;
  final PaginatedCategories? data;

  CategoryResponse({
    required this.success,
    required this.message,
    this.data,
  });
}

class CategorySearchResponse {
  final bool success;
  final String message;
  final List<Category>? data;

  CategorySearchResponse({
    required this.success,
    required this.message,
    this.data,
  });
}

class CategoryWithStatsResponse {
  final bool success;
  final String message;
  final List<CategoryWithStats>? data;

  CategoryWithStatsResponse({
    required this.success,
    required this.message,
    this.data,
  });
}

class CategoryDetailResponse {
  final bool success;
  final String message;
  final Category? data;

  CategoryDetailResponse({
    required this.success,
    required this.message,
    this.data,
  });
}

class CategoryStatsResponse {
  final bool success;
  final String message;
  final CategoryStats? data;

  CategoryStatsResponse({
    required this.success,
    required this.message,
    this.data,
  });
}