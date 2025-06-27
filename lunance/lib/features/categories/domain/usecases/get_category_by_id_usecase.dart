// lib/features/categories/domain/usecases/get_category_by_id_usecase.dart
import '../../../../core/network/api_result.dart';
import '../entities/category.dart';
import '../repositories/category_repository.dart';
class GetCategoryByIdUseCase {
  final CategoryRepository repository;

  GetCategoryByIdUseCase(this.repository);

  Future<ApiResult<Category>> call(String id) {
    return repository.getCategoryById(id);
  }
}