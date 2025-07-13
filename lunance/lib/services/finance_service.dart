import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import '../config/app_config.dart';

class FinanceService {
  static const String baseUrl = 'http://192.168.101.8:8000/api/v1'; // Ganti dengan IP backend Anda
  static const _storage = FlutterSecureStorage();

  Future<Map<String, String>> get _authHeaders async {
    final token = await _storage.read(key: 'access_token');
    return {
      'Content-Type': 'application/json',
      'Authorization': 'Bearer $token',
    };
  }

  // 1. Dashboard Summary
  Future<Map<String, dynamic>> getDashboardSummary() async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/finance/dashboard-summary'),
        headers: await _authHeaders,
      );
      return _handleResponse(response);
    } catch (e) {
      return {
        'success': false,
        'message': 'Gagal mengambil ringkasan dashboard: ${e.toString()}',
      };
    }
  }

  // 2. Transaction History with Filters
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
    try {
      final queryParams = <String, String>{
        'page': page.toString(),
        'limit': limit.toString(),
        'sort_by': sortBy,
        'sort_order': sortOrder,
      };

      if (type != null) queryParams['type'] = type;
      if (category != null) queryParams['category'] = category;
      if (startDate != null) queryParams['start_date'] = startDate.toIso8601String();
      if (endDate != null) queryParams['end_date'] = endDate.toIso8601String();
      if (minAmount != null) queryParams['min_amount'] = minAmount.toString();
      if (maxAmount != null) queryParams['max_amount'] = maxAmount.toString();
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
        'message': 'Gagal mengambil history transaksi: ${e.toString()}',
      };
    }
  }

  // 3. Charts Data - Time Series
  Future<Map<String, dynamic>> getTimeSeriesChartData({
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

      final uri = Uri.parse('$baseUrl/finance/charts/time-series').replace(queryParameters: queryParams);
      
      final response = await http.get(
        uri,
        headers: await _authHeaders,
      );
      return _handleResponse(response);
    } catch (e) {
      return {
        'success': false,
        'message': 'Gagal mengambil data chart time series: ${e.toString()}',
      };
    }
  }

  // 4. Charts Data - By Category
  Future<Map<String, dynamic>> getCategoryChartData({
    String type = 'expense',
    String period = 'monthly',
    DateTime? startDate,
    DateTime? endDate,
  }) async {
    try {
      final queryParams = <String, String>{
        'type': type,
        'period': period,
      };

      if (startDate != null) queryParams['start_date'] = startDate.toIso8601String();
      if (endDate != null) queryParams['end_date'] = endDate.toIso8601String();

      final uri = Uri.parse('$baseUrl/finance/charts/by-category').replace(queryParameters: queryParams);
      
      final response = await http.get(
        uri,
        headers: await _authHeaders,
      );
      return _handleResponse(response);
    } catch (e) {
      return {
        'success': false,
        'message': 'Gagal mengambil data chart kategori: ${e.toString()}',
      };
    }
  }

  // 5. Progress Data
  Future<Map<String, dynamic>> getProgressData() async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/finance/progress'),
        headers: await _authHeaders,
      );
      return _handleResponse(response);
    } catch (e) {
      return {
        'success': false,
        'message': 'Gagal mengambil data progress: ${e.toString()}',
      };
    }
  }

  // 6. Financial Predictions
  Future<Map<String, dynamic>> getFinancialPredictions({
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
        'message': 'Gagal mengambil prediksi keuangan: ${e.toString()}',
      };
    }
  }

  // 7. Available Categories
  Future<Map<String, dynamic>> getAvailableCategories() async {
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

  // 8. Basic Stats
  Future<Map<String, dynamic>> getBasicStats() async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/finance/stats'),
        headers: await _authHeaders,
      );
      return _handleResponse(response);
    } catch (e) {
      return {
        'success': false,
        'message': 'Gagal mengambil statistik dasar: ${e.toString()}',
      };
    }
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