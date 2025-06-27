// lib/features/dashboard/domain/usecases/get_financial_summary_usecase.dart
import '../../../../core/network/api_result.dart';
import '../../../../core/usecases/usecase.dart';
import '../entities/financial_summary.dart';
import '../repositories/dashboard_repository.dart';

class GetFinancialSummaryUseCase implements UseCase<FinancialSummary, FinancialSummaryParams> {
  final DashboardRepository repository;

  GetFinancialSummaryUseCase(this.repository);

  @override
  Future<ApiResult<FinancialSummary>> call(FinancialSummaryParams params) async {
    return await repository.getFinancialSummary(period: params.period);
  }
}

class FinancialSummaryParams {
  final String period;

  const FinancialSummaryParams({
    this.period = 'monthly',
  });
}