
// lib/features/dashboard/data/datasources/dashboard_remote_datasource.dart
import 'package:dio/dio.dart';
import '../../../../core/constants/api_endpoints.dart';
import '../../../../core/utils/dio_client.dart';
import '../models/financial_summary_model.dart';
import '../models/quick_stats_model.dart';
import '../models/category_breakdown_model.dart';
import '../models/recent_transactions_model.dart';
import '../models/prediction_model.dart';
import '../models/financial_insights_model.dart';

abstract class DashboardRemoteDataSource {
  Future<FinancialSummaryModel> getFinancialSummary({
    String period = 'monthly',
  });

  Future<QuickStatsModel> getQuickStats();

  Future<CategoryBreakdownModel> getCategoryBreakdown({
    String period = 'monthly',
    int limit = 5,
  });

  Future<RecentTransactionsModel> getRecentTransactions({
    int limit = 5,
  });

  Future<PredictionModel> getPredictions({
    String predictionType = 'expense',
    int daysAhead = 30,
  });

  Future<FinancialInsightsModel> getFinancialInsights();
}

class DashboardRemoteDataSourceImpl implements DashboardRemoteDataSource {
  final DioClient client;

  DashboardRemoteDataSourceImpl(this.client);

  @override
  Future<FinancialSummaryModel> getFinancialSummary({
    String period = 'monthly',
  }) async {
    try {
      final response = await client.get(
        ApiEndpoints.financialSummary,
        queryParameters: {'period': period},
      );

      if (response.statusCode == 200) {
        return FinancialSummaryModel.fromJson(response.data);
      } else {
        throw Exception(response.data['detail'] ?? 'Failed to get financial summary');
      }
    } on DioException catch (e) {
      throw Exception(e.message ?? 'Network error occurred');
    } catch (e) {
      throw Exception('Unexpected error occurred');
    }
  }

  @override
  Future<QuickStatsModel> getQuickStats() async {
    try {
      final response = await client.get(ApiEndpoints.quickStats);

      if (response.statusCode == 200) {
        return QuickStatsModel.fromJson(response.data);
      } else {
        throw Exception(response.data['detail'] ?? 'Failed to get quick stats');
      }
    } on DioException catch (e) {
      throw Exception(e.message ?? 'Network error occurred');
    } catch (e) {
      throw Exception('Unexpected error occurred');
    }
  }

  @override
  Future<CategoryBreakdownModel> getCategoryBreakdown({
    String period = 'monthly',
    int limit = 5,
  }) async {
    try {
      final response = await client.get(
        ApiEndpoints.categoryBreakdown,
        queryParameters: {
          'period': period,
          'limit': limit,
        },
      );

      if (response.statusCode == 200) {
        return CategoryBreakdownModel.fromJson(response.data);
      } else {
        throw Exception(response.data['detail'] ?? 'Failed to get category breakdown');
      }
    } on DioException catch (e) {
      throw Exception(e.message ?? 'Network error occurred');
    } catch (e) {
      throw Exception('Unexpected error occurred');
    }
  }

  @override
  Future<RecentTransactionsModel> getRecentTransactions({
    int limit = 5,
  }) async {
    try {
      final response = await client.get(
        ApiEndpoints.recentTransactions,
        queryParameters: {'limit': limit},
      );

      if (response.statusCode == 200) {
        return RecentTransactionsModel.fromJson(response.data);
      } else {
        throw Exception(response.data['detail'] ?? 'Failed to get recent transactions');
      }
    } on DioException catch (e) {
      throw Exception(e.message ?? 'Network error occurred');
    } catch (e) {
      throw Exception('Unexpected error occurred');
    }
  }

  @override
  Future<PredictionModel> getPredictions({
    String predictionType = 'expense',
    int daysAhead = 30,
  }) async {
    try {
      final response = await client.get(
        ApiEndpoints.predictions,
        queryParameters: {
          'prediction_type': predictionType,
          'days_ahead': daysAhead,
        },
      );

      if (response.statusCode == 200) {
        return PredictionModel.fromJson(response.data);
      } else {
        throw Exception(response.data['detail'] ?? 'Failed to get predictions');
      }
    } on DioException catch (e) {
      throw Exception(e.message ?? 'Network error occurred');
    } catch (e) {
      throw Exception('Unexpected error occurred');
    }
  }

  @override
  Future<FinancialInsightsModel> getFinancialInsights() async {
    try {
      final response = await client.get(ApiEndpoints.insights);

      if (response.statusCode == 200) {
        return FinancialInsightsModel.fromJson(response.data);
      } else {
        throw Exception(response.data['detail'] ?? 'Failed to get financial insights');
      }
    } on DioException catch (e) {
      throw Exception(e.message ?? 'Network error occurred');
    } catch (e) {
      throw Exception('Unexpected error occurred');
    }
  }
}
