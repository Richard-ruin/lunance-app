// lib/features/dashboard/domain/repositories/dashboard_repository.dart
import '../../../../core/network/api_result.dart';
import '../entities/financial_summary.dart';
import '../entities/quick_stats.dart';
import '../entities/category_breakdown.dart';
import '../entities/recent_transactions.dart';
import '../entities/prediction.dart';
import '../entities/financial_insights.dart';

abstract class DashboardRepository {
  Future<ApiResult<FinancialSummary>> getFinancialSummary({
    String period = 'monthly',
  });

  Future<ApiResult<QuickStats>> getQuickStats();

  Future<ApiResult<CategoryBreakdown>> getCategoryBreakdown({
    String period = 'monthly',
    int limit = 5,
  });

  Future<ApiResult<RecentTransactions>> getRecentTransactions({
    int limit = 5,
  });

  Future<ApiResult<Prediction>> getPredictions({
    String predictionType = 'expense',
    int daysAhead = 30,
  });

  Future<ApiResult<FinancialInsights>> getFinancialInsights();
}