// lib/features/dashboard/data/repositories/dashboard_repository_impl.dart
import '../../domain/entities/financial_summary.dart';
import '../../domain/entities/prediction.dart';
import '../../domain/repositories/dashboard_repository.dart';
import '../datasources/dashboard_remote_datasource.dart';

class DashboardRepositoryImpl implements DashboardRepository {
  final DashboardRemoteDataSource remoteDataSource;

  DashboardRepositoryImpl({required this.remoteDataSource});

  @override
  Future<FinancialSummary> getFinancialSummary() async {
    try {
      final result = await remoteDataSource.getFinancialSummary();
      return result;
    } catch (e) {
      throw Exception('Failed to get financial summary: $e');
    }
  }

  @override
  Future<List<Prediction>> getPredictions() async {
    try {
      final result = await remoteDataSource.getPredictions();
      return result;
    } catch (e) {
      throw Exception('Failed to get predictions: $e');
    }
  }

  @override
  Future<MonthlyPrediction> getMonthlyPrediction() async {
    try {
      final result = await remoteDataSource.getMonthlyPrediction();
      return result;
    } catch (e) {
      throw Exception('Failed to get monthly prediction: $e');
    }
  }
}
