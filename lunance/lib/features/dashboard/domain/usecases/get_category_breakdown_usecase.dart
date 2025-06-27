// lib/features/dashboard/domain/usecases/get_category_breakdown_usecase.dart
import '../../../../core/network/api_result.dart';
import '../../../../core/usecases/usecase.dart';
import '../entities/category_breakdown.dart';
import '../repositories/dashboard_repository.dart';

class GetCategoryBreakdownUseCase implements UseCase<CategoryBreakdown, CategoryBreakdownParams> {
  final DashboardRepository repository;

  GetCategoryBreakdownUseCase(this.repository);

  @override
  Future<ApiResult<CategoryBreakdown>> call(CategoryBreakdownParams params) async {
    return await repository.getCategoryBreakdown(
      period: params.period,
      limit: params.limit,
    );
  }
}

class CategoryBreakdownParams {
  final String period;
  final int limit;

  const CategoryBreakdownParams({
    this.period = 'monthly',
    this.limit = 5,
  });
}