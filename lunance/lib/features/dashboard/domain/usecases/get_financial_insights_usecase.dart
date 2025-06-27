
// lib/features/dashboard/domain/usecases/get_financial_insights_usecase.dart
import '../../../../core/network/api_result.dart';
import '../../../../core/usecases/usecase.dart';
import '../entities/financial_insights.dart';
import '../repositories/dashboard_repository.dart';

class GetFinancialInsightsUseCase implements UseCase<FinancialInsights, NoParams> {
  final DashboardRepository repository;

  GetFinancialInsightsUseCase(this.repository);

  @override
  Future<ApiResult<FinancialInsights>> call(NoParams params) async {
    return await repository.getFinancialInsights();
  }
}
