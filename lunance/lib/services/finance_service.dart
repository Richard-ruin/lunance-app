import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import '../config/app_config.dart';

class FinanceService {
  static const String baseUrl = 'http://192.168.101.3:8000/api/v1';
  static const _storage = FlutterSecureStorage();

  Future<Map<String, String>> get _authHeaders async {
    final token = await _storage.read(key: 'access_token');
    return {
      'Content-Type': 'application/json',
      'Authorization': 'Bearer $token',
    };
  }

  // ===== CLEANED: HANYA 3 ENDPOINTS YANG DIPAKAI DI TAB =====

  // 1. Dashboard dengan 50/30/20 Method (Dashboard Tab)
  Future<Map<String, dynamic>> getStudentDashboard() async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/finance/dashboard'),
        headers: await _authHeaders,
      );
      
      final result = _handleResponse(response);
      
      // FIXED: Add fallback mechanism untuk backward compatibility
      if (result['success'] == true && result['data'] != null) {
        final data = result['data'] as Map<String, dynamic>;
        
        // Ensure all required fields exist with safe defaults
        _ensureRequiredFields(data);
        
        return result;
      }
      
      return result;
    } catch (e) {
      return {
        'success': false,
        'message': 'Gagal mengambil dashboard 50/30/20: ${e.toString()}',
      };
    }
  }

  // 2. Analytics dengan Budget Type Analysis (Analytics Tab)
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

  // 3. History dengan Budget Type Filter (History Tab)
  Future<Map<String, dynamic>> getHistory({
    String? type,
    String? budgetType, // needs/wants/savings
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

  // ===== MINIMAL HELPER ENDPOINTS =====

  // 4. Categories (untuk dropdown di History Tab)
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

  // 5. Basic Stats (untuk Dashboard Tab)
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

  // ===== HELPER METHODS =====

  void _ensureRequiredFields(Map<String, dynamic> data) {
    // Ensure quick_stats exists
    if (data['quick_stats'] == null) {
      data['quick_stats'] = {
        'real_total_savings': 0.0,
        'monthly_income': 0.0,
        'current_month_spending': {
          'needs': 0.0,
          'wants': 0.0,
          'savings': 0.0,
        },
        'formatted_real_total_savings': 'Rp 0',
        'formatted_monthly_income': 'Rp 0',
        'formatted_spending': {
          'needs': 'Rp 0',
          'wants': 'Rp 0',
          'savings': 'Rp 0',
        }
      };
    }
    
    // Ensure financial_summary exists
    if (data['financial_summary'] == null) {
      final quickStats = data['quick_stats'];
      if (quickStats != null) {
        final monthlyIncome = _safeDouble(quickStats['monthly_income']);
        final spending = quickStats['current_month_spending'] ?? {};
        final totalExpense = _safeDouble(spending['needs']) + 
                            _safeDouble(spending['wants']) + 
                            _safeDouble(spending['savings']);
        final netBalance = monthlyIncome - totalExpense;
        final savingsRate = monthlyIncome > 0 ? (netBalance / monthlyIncome * 100) : 0.0;
        
        data['financial_summary'] = {
          'monthly_income': monthlyIncome,
          'monthly_expense': totalExpense,
          'net_balance': netBalance,
          'savings_rate': savingsRate,
        };
      }
    }
  }

  double _safeDouble(dynamic value) {
    if (value == null) return 0.0;
    if (value is double) return value;
    if (value is int) return value.toDouble();
    if (value is String) return double.tryParse(value) ?? 0.0;
    return 0.0;
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