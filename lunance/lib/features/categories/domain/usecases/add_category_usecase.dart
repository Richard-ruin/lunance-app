// lib/features/categories/domain/usecases/get_categories_usecase.dart
import '../../../../core/network/api_result.dart';
import '../entities/category.dart';
import '../repositories/category_repository.dart';

class GetCategoriesUseCase {
  final CategoryRepository repository;

  GetCategoriesUseCase(this.repository);

  Future<ApiResult<List<Category>>> call({String? type}) {
    return repository.getCategories(type: type);
  }
}