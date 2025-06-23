// lib/features/dashboard/domain/repositories/dashboard_repository.dart
import '../entities/financial_summary.dart';
import '../entities/prediction.dart';

abstract class DashboardRepository {
  Future<FinancialSummary> getFinancialSummary();
  Future<List<Prediction>> getPredictions();
  Future<MonthlyPrediction> getMonthlyPrediction();
}