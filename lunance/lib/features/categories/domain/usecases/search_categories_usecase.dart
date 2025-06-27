// lib/features/categories/domain/usecases/search_categories_usecase.dart
import '../../../../core/network/api_result.dart';
import '../repositories/category_repository.dart';
import '../entities/category.dart';
class SearchCategoriesUseCase {
  final CategoryRepository repository;

  SearchCategoriesUseCase(this.repository);

  Future<ApiResult<List<Category>>> call(String query, {String? type}) {
    return repository.searchCategories(query, type: type);
  }
}