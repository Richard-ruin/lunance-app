import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import '../config/app_config.dart';

class FinanceService {
  static const String baseUrl = 'http://192.168.101.8:8000/api/v1';
  static const _storage = FlutterSecureStorage();

  Future<Map<String, String>> get _authHeaders async {
    final token = await _storage.read(key: 'access_token');
    return {
      'Content-Type': 'application/json',
      'Authorization': 'Bearer $token',
    };
  }

  // ===== 50/30/20 METHOD - UPDATED ENDPOINTS =====

  // 1. Dashboard dengan 50/30/20 Method
  Future<Map<String, dynamic>> getStudentDashboard() async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/finance/dashboard'),
        headers: await _authHeaders,
      );
      return _handleResponse(response);
    } catch (e) {
      return {
        'success': false,
        'message': 'Gagal mengambil dashboard 50/30/20: ${e.toString()}',
      };
    }
  }

  // 2. Analytics dengan Budget Type Analysis
  Future<Map<String, dynamic>> getAnalytics({
    String period = 'monthly',
    DateTime? startDate,
    DateTime? endDate,
  }) async {
    try {
      final queryParams = <String, String>{
        'period': period,
      };

      if (startDate != null) queryParams['start_date'] = startDate.toIso8601String();
      if (endDate != null) queryParams['end_date'] = endDate.toIso8601String();

      final uri = Uri.parse('$baseUrl/finance/analytics').replace(queryParameters: queryParams);
      
      final response = await http.get(
        uri,
        headers: await _authHeaders,
      );
      return _handleResponse(response);
    } catch (e) {
      return {
        'success': false,
        'message': 'Gagal mengambil analytics: ${e.toString()}',
      };
    }
  }

  // 3. History dengan Budget Type Filter
  Future<Map<String, dynamic>> getHistory({
    String? type,
    String? budgetType, // NEW: needs/wants/savings
    String? category,
    DateTime? startDate,
    DateTime? endDate,
    String? search,
    int page = 1,
    int limit = 20,
    String sortBy = 'date',
    String sortOrder = 'desc',
  }) async {
    try {
      final queryParams = <String, String>{
        'page': page.toString(),
        'limit': limit.toString(),
        'sort_by': sortBy,
        'sort_order': sortOrder,
      };

      if (type != null) queryParams['type'] = type;
      if (budgetType != null) queryParams['budget_type'] = budgetType;
      if (category != null) queryParams['category'] = category;
      if (startDate != null) queryParams['start_date'] = startDate.toIso8601String();
      if (endDate != null) queryParams['end_date'] = endDate.toIso8601String();
      if (search != null) queryParams['search'] = search;

      final uri = Uri.parse('$baseUrl/finance/history').replace(queryParameters: queryParams);
      
      final response = await http.get(
        uri,
        headers: await _authHeaders,
      );
      return _handleResponse(response);
    } catch (e) {
      return {
        'success': false,
        'message': 'Gagal mengambil history: ${e.toString()}',
      };
    }
  }

  // 4. Budget Status 50/30/20
  Future<Map<String, dynamic>> getBudgetStatus() async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/finance/budget-status'),
        headers: await _authHeaders,
      );
      return _handleResponse(response);
    } catch (e) {
      return {
        'success': false,
        'message': 'Gagal mengambil status budget: ${e.toString()}',
      };
    }
  }

  // 5. Categories dengan Budget Type Classification
  Future<Map<String, dynamic>> getCategories() async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/finance/categories'),
        headers: await _authHeaders,
      );
      return _handleResponse(response);
    } catch (e) {
      return {
        'success': false,
        'message': 'Gagal mengambil kategori: ${e.toString()}',
      };
    }
  }

  // 6. Basic Stats dengan Budget Breakdown
  Future<Map<String, dynamic>> getStats() async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/finance/stats'),
        headers: await _authHeaders,
      );
      return _handleResponse(response);
    } catch (e) {
      return {
        'success': false,
        'message': 'Gagal mengambil statistik: ${e.toString()}',
      };
    }
  }

  // 7. Progress Data dengan Savings Goals
  Future<Map<String, dynamic>> getProgress() async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/finance/progress'),
        headers: await _authHeaders,
      );
      return _handleResponse(response);
    } catch (e) {
      return {
        'success': false,
        'message': 'Gagal mengambil progress: ${e.toString()}',
      };
    }
  }

  // 8. Financial Predictions
  Future<Map<String, dynamic>> getPredictions({
    int daysAhead = 30,
    String type = 'both',
  }) async {
    try {
      final queryParams = <String, String>{
        'days_ahead': daysAhead.toString(),
        'type': type,
      };

      final uri = Uri.parse('$baseUrl/finance/predictions').replace(queryParameters: queryParams);
      
      final response = await http.get(
        uri,
        headers: await _authHeaders,
      );
      return _handleResponse(response);
    } catch (e) {
      return {
        'success': false,
        'message': 'Gagal mengambil prediksi: ${e.toString()}',
      };
    }
  }

  // 9. Export Data
  Future<Map<String, dynamic>> exportData({
    String format = 'csv',
    String? type,
    DateTime? startDate,
    DateTime? endDate,
  }) async {
    try {
      final queryParams = <String, String>{
        'format': format,
      };

      if (type != null) queryParams['type'] = type;
      if (startDate != null) queryParams['start_date'] = startDate.toIso8601String();
      if (endDate != null) queryParams['end_date'] = endDate.toIso8601String();

      final uri = Uri.parse('$baseUrl/finance/history/export').replace(queryParameters: queryParams);
      
      final response = await http.get(
        uri,
        headers: await _authHeaders,
      );
      return _handleResponse(response);
    } catch (e) {
      return {
        'success': false,
        'message': 'Gagal export data: ${e.toString()}',
      };
    }
  }

  // ===== AUTH ENDPOINTS - 50/30/20 Financial Setup =====

  // 10. Financial Overview
  Future<Map<String, dynamic>> getFinancialOverview() async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/auth/financial-overview'),
        headers: await _authHeaders,
      );
      return _handleResponse(response);
    } catch (e) {
      return {
        'success': false,
        'message': 'Gagal mengambil overview keuangan: ${e.toString()}',
      };
    }
  }

  // 11. Update Financial Settings
  Future<Map<String, dynamic>> updateFinancialSettings({
    double? currentSavings,
    double? monthlyIncome,
    String? primaryBank,
  }) async {
    try {
      final Map<String, dynamic> body = {};
      
      if (currentSavings != null) body['current_savings'] = currentSavings;
      if (monthlyIncome != null) body['monthly_income'] = monthlyIncome;
      if (primaryBank != null) body['primary_bank'] = primaryBank;

      final response = await http.put(
        Uri.parse('$baseUrl/auth/financial-settings'),
        headers: await _authHeaders,
        body: jsonEncode(body),
      );
      return _handleResponse(response);
    } catch (e) {
      return {
        'success': false,
        'message': 'Gagal update pengaturan keuangan: ${e.toString()}',
      };
    }
  }

  // 12. Reset Monthly Budget
  Future<Map<String, dynamic>> resetMonthlyBudget() async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/auth/reset-monthly-budget'),
        headers: await _authHeaders,
      );
      return _handleResponse(response);
    } catch (e) {
      return {
        'success': false,
        'message': 'Gagal reset budget bulanan: ${e.toString()}',
      };
    }
  }

  // 13. Budget Categories
  Future<Map<String, dynamic>> getBudgetCategories() async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/auth/budget-categories'),
        headers: await _authHeaders,
      );
      return _handleResponse(response);
    } catch (e) {
      return {
        'success': false,
        'message': 'Gagal mengambil kategori budget: ${e.toString()}',
      };
    }
  }

  // 14. Student Financial Tips
  Future<Map<String, dynamic>> getStudentFinancialTips() async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/auth/student-financial-tips'),
        headers: await _authHeaders,
      );
      return _handleResponse(response);
    } catch (e) {
      return {
        'success': false,
        'message': 'Gagal mengambil tips keuangan: ${e.toString()}',
      };
    }
  }

  // ===== LEGACY SUPPORT =====

  // Legacy methods for backward compatibility
  @Deprecated('Use getStudentDashboard() instead')
  Future<Map<String, dynamic>> getDashboardSummary() async {
    return await getStudentDashboard();
  }

  @Deprecated('Use getCategories() instead')
  Future<Map<String, dynamic>> getAvailableCategories() async {
    return await getCategories();
  }

  @Deprecated('Use getHistory() instead')
  Future<Map<String, dynamic>> getTransactionHistory({
    String? type,
    String? category,
    DateTime? startDate,
    DateTime? endDate,
    double? minAmount,
    double? maxAmount,
    String? search,
    int page = 1,
    int limit = 20,
    String sortBy = 'date',
    String sortOrder = 'desc',
  }) async {
    return await getHistory(
      type: type,
      category: category,
      startDate: startDate,
      endDate: endDate,
      search: search,
      page: page,
      limit: limit,
      sortBy: sortBy,
      sortOrder: sortOrder,
    );
  }

  // Helper method to handle HTTP responses
  Map<String, dynamic> _handleResponse(http.Response response) {
    try {
      final Map<String, dynamic> data = jsonDecode(response.body);
      
      if (response.statusCode >= 200 && response.statusCode < 300) {
        return data;
      } else {
        String errorMessage = data['message'] ?? 'Terjadi kesalahan';
        
        if (response.statusCode == 400) {
          errorMessage = data['message'] ?? 'Data yang dikirim tidak valid';
        } else if (response.statusCode == 401) {
          errorMessage = 'Tidak memiliki akses. Silakan login kembali';
        } else if (response.statusCode == 404) {
          errorMessage = 'Endpoint tidak ditemukan';
        } else if (response.statusCode >= 500) {
          errorMessage = 'Terjadi kesalahan pada server';
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
        'message': 'Gagal memproses response dari server',
        'error': e.toString(),
        'status_code': response.statusCode,
      };
    }
  }
}