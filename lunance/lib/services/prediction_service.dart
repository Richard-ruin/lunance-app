// lib/services/prediction_service.dart
import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import '../config/app_config.dart';

class PredictionService {
  static const String baseUrl = 'http://192.168.236.195:8000/api/v1';
  static const _storage = FlutterSecureStorage();

  Future<Map<String, String>> get _authHeaders async {
    final token = await _storage.read(key: 'access_token');
    return {
      'Content-Type': 'application/json',
      'Authorization': 'Bearer $token',
    };
  }

  // ===== INCOME PREDICTIONS =====

  /// Prediksi pemasukan user menggunakan Prophet AI
  Future<Map<String, dynamic>> predictIncome({
    int forecastDays = 30,
  }) async {
    try {
      final queryParams = {
        'forecast_days': forecastDays.toString(),
      };

      final uri = Uri.parse('$baseUrl/predictions/income').replace(
        queryParameters: queryParams,
      );

      final response = await http.get(
        uri,
        headers: await _authHeaders,
      );

      return _handleResponse(response);
    } catch (e) {
      return {
        'success': false,
        'message': 'Gagal memprediksi pemasukan: ${e.toString()}',
      };
    }
  }

  // ===== EXPENSE PREDICTIONS BY BUDGET TYPE =====

  /// Prediksi pengeluaran berdasarkan budget type (needs/wants/savings)
  Future<Map<String, dynamic>> predictExpenseByBudgetType({
    required String budgetType,
    int forecastDays = 30,
  }) async {
    try {
      final queryParams = {
        'forecast_days': forecastDays.toString(),
      };

      final uri = Uri.parse('$baseUrl/predictions/expense/$budgetType').replace(
        queryParameters: queryParams,
      );

      final response = await http.get(
        uri,
        headers: await _authHeaders,
      );

      return _handleResponse(response);
    } catch (e) {
      return {
        'success': false,
        'message': 'Gagal memprediksi pengeluaran $budgetType: ${e.toString()}',
      };
    }
  }

  // ===== COMPREHENSIVE BUDGET PERFORMANCE =====

  /// Prediksi performa budget 50/30/20 secara komprehensif
  Future<Map<String, dynamic>> predictBudgetPerformance({
    int forecastDays = 30,
  }) async {
    try {
      final queryParams = {
        'forecast_days': forecastDays.toString(),
      };

      final uri = Uri.parse('$baseUrl/predictions/budget-performance').replace(
        queryParameters: queryParams,
      );

      final response = await http.get(
        uri,
        headers: await _authHeaders,
      );

      return _handleResponse(response);
    } catch (e) {
      return {
        'success': false,
        'message': 'Gagal memprediksi performa budget: ${e.toString()}',
      };
    }
  }

  // ===== SAVINGS GOAL ACHIEVEMENT =====

  /// Prediksi kapan target tabungan akan tercapai
  Future<Map<String, dynamic>> predictSavingsGoalAchievement({
    required String goalId,
  }) async {
    try {
      final uri = Uri.parse('$baseUrl/predictions/savings-goal/$goalId');

      final response = await http.get(
        uri,
        headers: await _authHeaders,
      );

      return _handleResponse(response);
    } catch (e) {
      return {
        'success': false,
        'message': 'Gagal memprediksi pencapaian target: ${e.toString()}',
      };
    }
  }

  // ===== PREDICTION ANALYTICS =====

  /// Comprehensive analytics dari semua prediksi keuangan user
  Future<Map<String, dynamic>> getPredictionAnalytics() async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/predictions/analytics'),
        headers: await _authHeaders,
      );

      return _handleResponse(response);
    } catch (e) {
      return {
        'success': false,
        'message': 'Gagal mengambil analytics prediksi: ${e.toString()}',
      };
    }
  }

  // ===== PREDICTION HISTORY =====

  /// History prediksi yang pernah dibuat user
  Future<Map<String, dynamic>> getPredictionHistory({
    String? predictionType,
    int limit = 10,
  }) async {
    try {
      final queryParams = <String, String>{
        'limit': limit.toString(),
      };

      if (predictionType != null) {
        queryParams['prediction_type'] = predictionType;
      }

      final uri = Uri.parse('$baseUrl/predictions/history').replace(
        queryParameters: queryParams,
      );

      final response = await http.get(
        uri,
        headers: await _authHeaders,
      );

      return _handleResponse(response);
    } catch (e) {
      return {
        'success': false,
        'message': 'Gagal mengambil history prediksi: ${e.toString()}',
      };
    }
  }

  // ===== PREDICTION INFO =====

  /// Informasi tentang sistem prediksi keuangan
  Future<Map<String, dynamic>> getPredictionInfo() async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/predictions/info'),
        headers: await _authHeaders,
      );

      return _handleResponse(response);
    } catch (e) {
      return {
        'success': false,
        'message': 'Gagal mengambil info prediksi: ${e.toString()}',
      };
    }
  }

  // ===== HELPER METHODS =====

  /// Handle HTTP responses dengan comprehensive error handling
  Map<String, dynamic> _handleResponse(http.Response response) {
    try {
      final Map<String, dynamic> data = jsonDecode(response.body);

      if (response.statusCode >= 200 && response.statusCode < 300) {
        return data;
      } else {
        String errorMessage = data['message'] ?? 'Terjadi kesalahan';

        if (response.statusCode == 400) {
          errorMessage = data['message'] ?? 'Data tidak valid';
        } else if (response.statusCode == 401) {
          errorMessage = 'Tidak memiliki akses. Silakan login kembali';
        } else if (response.statusCode == 404) {
          errorMessage = 'Endpoint prediksi tidak ditemukan';
        } else if (response.statusCode >= 500) {
          errorMessage = 'Server sedang bermasalah';
        }

        return {
          'success': false,
          'message': errorMessage,
          'status_code': response.statusCode,
        };
      }
    } catch (e) {
      return {
        'success': false,
        'message': 'Gagal memproses response prediksi',
        'error': e.toString(),
        'status_code': response.statusCode,
      };
    }
  }

  // ===== BATCH PREDICTIONS =====

  /// Load multiple predictions sekaligus untuk dashboard prediksi
  Future<Map<String, Map<String, dynamic>>> loadAllPredictions({
    int forecastDays = 30,
  }) async {
    try {
      final results = <String, Map<String, dynamic>>{};

      // Load income prediction
      try {
        final incomeResult = await predictIncome(forecastDays: forecastDays);
        results['income'] = incomeResult;
      } catch (e) {
        results['income'] = {
          'success': false,
          'message': 'Gagal load income prediction: $e'
        };
      }

      // Load budget performance prediction
      try {
        final budgetResult =
            await predictBudgetPerformance(forecastDays: forecastDays);
        results['budget_performance'] = budgetResult;
      } catch (e) {
        results['budget_performance'] = {
          'success': false,
          'message': 'Gagal load budget performance: $e'
        };
      }

      // Load individual budget type predictions
      for (final budgetType in ['needs', 'wants', 'savings']) {
        try {
          final expenseResult = await predictExpenseByBudgetType(
            budgetType: budgetType,
            forecastDays: forecastDays,
          );
          results['${budgetType}_expense'] = expenseResult;
        } catch (e) {
          results['${budgetType}_expense'] = {
            'success': false,
            'message': 'Gagal load $budgetType prediction: $e'
          };
        }
      }

      return results;
    } catch (e) {
      return {
        'error': {
          'success': false,
          'message': 'Gagal load semua prediksi: ${e.toString()}'
        }
      };
    }
  }

  // ===== VALIDATION HELPERS =====

  /// Validate budget type
  bool isValidBudgetType(String budgetType) {
    return ['needs', 'wants', 'savings'].contains(budgetType.toLowerCase());
  }

  /// Validate forecast days range
  bool isValidForecastDays(int forecastDays) {
    return forecastDays >= 7 && forecastDays <= 90;
  }

  /// Get budget type color untuk UI
  String getBudgetTypeColorHex(String budgetType) {
    switch (budgetType.toLowerCase()) {
      case 'needs':
        return '#22C55E'; // Green
      case 'wants':
        return '#F59E0B'; // Orange
      case 'savings':
        return '#3B82F6'; // Blue
      default:
        return '#6B7280'; // Gray
    }
  }

  /// Get budget type name untuk display
  String getBudgetTypeName(String budgetType) {
    switch (budgetType.toLowerCase()) {
      case 'needs':
        return 'Kebutuhan (50%)';
      case 'wants':
        return 'Keinginan (30%)';
      case 'savings':
        return 'Tabungan (20%)';
      default:
        return 'Lainnya';
    }
  }

  /// Get prediction confidence level
  String getConfidenceLevel(double confidence) {
    if (confidence >= 85) {
      return 'Tinggi';
    } else if (confidence >= 70) {
      return 'Menengah';
    } else {
      return 'Rendah';
    }
  }

  /// Format prediction insights untuk display
  List<String> formatInsights(List<dynamic>? insights) {
    if (insights == null || insights.isEmpty) {
      return ['Belum ada insight yang tersedia'];
    }

    return insights
        .where((insight) => insight != null)
        .map((insight) => insight.toString())
        .take(5) // Limit to 5 insights
        .toList();
  }

  /// Format recommendations untuk display
  List<String> formatRecommendations(List<dynamic>? recommendations) {
    if (recommendations == null || recommendations.isEmpty) {
      return ['Belum ada rekomendasi yang tersedia'];
    }

    return recommendations
        .where((rec) => rec != null)
        .map((rec) => rec.toString())
        .take(5) // Limit to 5 recommendations
        .toList();
  }
}
