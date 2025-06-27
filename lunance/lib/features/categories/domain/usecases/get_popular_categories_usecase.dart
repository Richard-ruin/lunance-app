// lib/features/categories/domain/usecases/get_popular_categories_usecase.dart
import '../../../../core/network/api_result.dart';
import '../repositories/category_repository.dart';
import '../entities/category.dart';
class GetPopularCategoriesUseCase {
  final CategoryRepository repository;

  GetPopularCategoriesUseCase(this.repository);

  Future<ApiResult<List<CategoryWithStats>>> call({String? type, int limit = 10}) {
    return repository.getPopularCategories(type: type, limit: limit);
  }
}
