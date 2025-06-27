// lib/features/categories/domain/usecases/get_categories_with_stats_usecase.dart
import '../../../../core/network/api_result.dart';
import '../repositories/category_repository.dart';
import '../entities/category.dart';
class GetCategoriesWithStatsUseCase {
  final CategoryRepository repository;

  GetCategoriesWithStatsUseCase(this.repository);

  Future<ApiResult<List<CategoryWithStats>>> call({String? type}) {
    return repository.getCategoriesWithStats(type: type);
  }
}