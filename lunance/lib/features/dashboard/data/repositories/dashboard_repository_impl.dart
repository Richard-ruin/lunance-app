
// lib/features/dashboard/data/repositories/dashboard_repository_impl.dart
import '../../../../core/network/network_info.dart';
import '../../../../core/network/api_result.dart';
import '../../domain/repositories/dashboard_repository.dart';
import '../../domain/entities/financial_summary.dart';
import '../../domain/entities/quick_stats.dart';
import '../../domain/entities/category_breakdown.dart';
import '../../domain/entities/recent_transactions.dart';
import '../../domain/entities/prediction.dart';
import '../../domain/entities/financial_insights.dart';
import '../datasources/dashboard_remote_datasource.dart';

class DashboardRepositoryImpl implements DashboardRepository {
  final DashboardRemoteDataSource remoteDataSource;
  final NetworkInfo networkInfo;

  DashboardRepositoryImpl({
    required this.remoteDataSource,
    required this.networkInfo,
  });

  @override
  Future<ApiResult<FinancialSummary>> getFinancialSummary({
    String period = 'monthly',
  }) async {
    if (await networkInfo.isConnected) {
      try {
        final result = await remoteDataSource.getFinancialSummary(period: period);
        return ApiResult.success(result);
      } catch (e) {
        return ApiResult.failure(e.toString());
      }
    } else {
      return  ApiResult.failure('Tidak ada koneksi internet');
    }
  }

  @override
  Future<ApiResult<QuickStats>> getQuickStats() async {
    if (await networkInfo.isConnected) {
      try {
        final result = await remoteDataSource.getQuickStats();
        return ApiResult.success(result);
      } catch (e) {
        return ApiResult.failure(e.toString());
      }
    } else {
      return  ApiResult.failure('Tidak ada koneksi internet');
    }
  }

  @override
  Future<ApiResult<CategoryBreakdown>> getCategoryBreakdown({
    String period = 'monthly',
    int limit = 5,
  }) async {
    if (await networkInfo.isConnected) {
      try {
        final result = await remoteDataSource.getCategoryBreakdown(
          period: period,
          limit: limit,
        );
        return ApiResult.success(result);
      } catch (e) {
        return ApiResult.failure(e.toString());
      }
    } else {
      return  ApiResult.failure('Tidak ada koneksi internet');
    }
  }

  @override
  Future<ApiResult<RecentTransactions>> getRecentTransactions({
    int limit = 5,
  }) async {
    if (await networkInfo.isConnected) {
      try {
        final result = await remoteDataSource.getRecentTransactions(limit: limit);
        return ApiResult.success(result);
      } catch (e) {
        return ApiResult.failure(e.toString());
      }
    } else {
      return  ApiResult.failure('Tidak ada koneksi internet');
    }
  }

  @override
  Future<ApiResult<Prediction>> getPredictions({
    String predictionType = 'expense',
    int daysAhead = 30,
  }) async {
    if (await networkInfo.isConnected) {
      try {
        final result = await remoteDataSource.getPredictions(
          predictionType: predictionType,
          daysAhead: daysAhead,
        );
        return ApiResult.success(result);
      } catch (e) {
        return ApiResult.failure(e.toString());
      }
    } else {
      return  ApiResult.failure('Tidak ada koneksi internet');
    }
  }

  @override
  Future<ApiResult<FinancialInsights>> getFinancialInsights() async {
    if (await networkInfo.isConnected) {
      try {
        final result = await remoteDataSource.getFinancialInsights();
        return ApiResult.success(result);
      } catch (e) {
        return ApiResult.failure(e.toString());
      }
    } else {
      return ApiResult.failure('Tidak ada koneksi internet');
    }
  }
}