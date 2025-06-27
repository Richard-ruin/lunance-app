// lib/features/categories/domain/usecases/create_category_usecase.dart
import '../../../../core/network/api_result.dart';
import '../repositories/category_repository.dart';
import '../entities/category.dart';
class CreateCategoryUseCase {
  final CategoryRepository repository;

  CreateCategoryUseCase(this.repository);

  Future<ApiResult<Category>> call(CategoryCreate categoryData) {
    return repository.createCategory(categoryData);
  }
}
