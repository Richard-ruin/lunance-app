// lib/features/categories/domain/repositories/category_repository.dart
import '../../../../core/network/api_result.dart';
import '../entities/category.dart';

abstract class CategoryRepository {
  Future<ApiResult<List<Category>>> getCategories({String? type});
  Future<ApiResult<List<CategoryWithStats>>> getCategoriesWithStats({String? type});
  Future<ApiResult<List<CategoryWithStats>>> getPopularCategories({String? type, int limit = 10});
  Future<ApiResult<List<Category>>> searchCategories(String query, {String? type});
  Future<ApiResult<Category>> getCategoryById(String id);
  Future<ApiResult<Category>> createCategory(CategoryCreate categoryData);
  Future<ApiResult<Category>> updateCategory(String id, CategoryUpdate categoryData);
  Future<ApiResult<void>> deleteCategory(String id);
}

// Create category data class
class CategoryCreate {
  final String name;
  final String? parentId;
  final String type;
  final String icon;
  final String color;
  final bool isSystem;
  final bool studentSpecific;
  final TypicalAmountRange? typicalAmountRange;
  final List<String> keywords;

  const CategoryCreate({
    required this.name,
    this.parentId,
    required this.type,
    required this.icon,
    required this.color,
    this.isSystem = false,
    this.studentSpecific = false,
    this.typicalAmountRange,
    this.keywords = const [],
  });

  Map<String, dynamic> toJson() => {
        'name': name,
        'parent_id': parentId,
        'type': type,
        'icon': icon,
        'color': color,
        'is_system': isSystem,
        'student_specific': studentSpecific,
        'typical_amount_range': typicalAmountRange != null
            ? {
                'min': typicalAmountRange!.min,
                'max': typicalAmountRange!.max,
                'avg': typicalAmountRange!.avg,
              }
            : null,
        'keywords': keywords,
      };
}

// Update category data class
class CategoryUpdate {
  final String? name;
  final String? parentId;
  final String? icon;
  final String? color;
  final bool? studentSpecific;
  final TypicalAmountRange? typicalAmountRange;
  final List<String>? keywords;

  const CategoryUpdate({
    this.name,
    this.parentId,
    this.icon,
    this.color,
    this.studentSpecific,
    this.typicalAmountRange,
    this.keywords,
  });

  Map<String, dynamic> toJson() {
    final Map<String, dynamic> data = {};
    if (name != null) data['name'] = name;
    if (parentId != null) data['parent_id'] = parentId;
    if (icon != null) data['icon'] = icon;
    if (color != null) data['color'] = color;
    if (studentSpecific != null) data['student_specific'] = studentSpecific;
    if (typicalAmountRange != null) {
      data['typical_amount_range'] = {
        'min': typicalAmountRange!.min,
        'max': typicalAmountRange!.max,
        'avg': typicalAmountRange!.avg,
      };
    }
    if (keywords != null) data['keywords'] = keywords;
    return data;
  }
}