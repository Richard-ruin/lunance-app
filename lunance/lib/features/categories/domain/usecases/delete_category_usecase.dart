// lib/features/categories/domain/usecases/delete_category_usecase.dart
import '../../../../core/network/api_result.dart';
import '../repositories/category_repository.dart';
class DeleteCategoryUseCase {
  final CategoryRepository repository;

  DeleteCategoryUseCase(this.repository);

  Future<ApiResult<void>> call(String id) {
    return repository.deleteCategory(id);
  }
}

