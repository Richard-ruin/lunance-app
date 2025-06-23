// lib/features/dashboard/domain/usecases/get_financial_summary_usecase.dart
import '../entities/financial_summary.dart';
import '../repositories/dashboard_repository.dart';

class GetFinancialSummaryUseCase {
  final DashboardRepository repository;

  GetFinancialSummaryUseCase(this.repository);

  Future<FinancialSummary> call() async {
    return await repository.getFinancialSummary();
  }
}