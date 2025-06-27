// lib/features/categories/domain/usecases/update_category_usecase.dart
import '../../../../core/network/api_result.dart';
import '../repositories/category_repository.dart';
import '../entities/category.dart';

class UpdateCategoryUseCase {
  final CategoryRepository repository;

  UpdateCategoryUseCase(this.repository);

  Future<ApiResult<Category>> call(String id, CategoryUpdate categoryData) {
    return repository.updateCategory(id, categoryData);
  }
}
