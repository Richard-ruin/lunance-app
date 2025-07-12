import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import '../models/user_model.dart';
import '../config/app_config.dart';

class ApiService {
  static const String baseUrl = 'http://192.168.101.8:8000/api/v1'; // Ganti dengan IP backend Anda
  static const _storage = FlutterSecureStorage();

  // Storage keys
  static const String _accessTokenKey = 'access_token';
  static const String _refreshTokenKey = 'refresh_token';

  // Headers
  Map<String, String> get _headers => {
    'Content-Type': 'application/json',
  };

  Future<Map<String, String>> get _authHeaders async {
    final token = await _storage.read(key: _accessTokenKey);
    return {
      'Content-Type': 'application/json',
      'Authorization': 'Bearer $token',
    };
  }

  // Auth methods
  Future<String?> getAccessToken() async {
    return await _storage.read(key: _accessTokenKey);
  }

  Future<void> saveTokens(String accessToken, String refreshToken) async {
    await _storage.write(key: _accessTokenKey, value: accessToken);
    await _storage.write(key: _refreshTokenKey, value: refreshToken);
  }

  Future<void> clearTokens() async {
    await _storage.delete(key: _accessTokenKey);
    await _storage.delete(key: _refreshTokenKey);
  }

  // API Calls
  Future<Map<String, dynamic>> register({
    required String username,
    required String email,
    required String password,
    required String confirmPassword,
  }) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/auth/register'),
        headers: _headers,
        body: jsonEncode({
          'username': username,
          'email': email,
          'password': password,
          'confirm_password': confirmPassword,
        }),
      );

      return _handleResponse(response);
    } catch (e) {
      return {
        'success': false,
        'message': 'Gagal terhubung ke server: ${e.toString()}',
      };
    }
  }

  Future<Map<String, dynamic>> login({
    required String email,
    required String password,
  }) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/auth/login'),
        headers: _headers,
        body: jsonEncode({
          'email': email,
          'password': password,
        }),
      );

      final result = _handleResponse(response);
      
      // Save tokens if login successful
      if (result['success'] == true && result['data']?['tokens'] != null) {
        final tokens = result['data']['tokens'];
        await saveTokens(tokens['access_token'], tokens['refresh_token']);
      }

      return result;
    } catch (e) {
      return {
        'success': false,
        'message': 'Gagal terhubung ke server: ${e.toString()}',
      };
    }
  }

  Future<Map<String, dynamic>> getCurrentUser() async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/auth/me'),
        headers: await _authHeaders,
      );

      return _handleResponse(response);
    } catch (e) {
      return {
        'success': false,
        'message': 'Gagal terhubung ke server: ${e.toString()}',
      };
    }
  }

  Future<Map<String, dynamic>> setupProfile({
    required String fullName,
    String? phoneNumber,
    DateTime? dateOfBirth,
    String? occupation,
    String? city,
    String language = 'id',
    String currency = 'IDR',
    bool notificationsEnabled = true,
    bool voiceEnabled = true,
    bool darkMode = false,
  }) async {
    try {
      final body = <String, dynamic>{
        'full_name': fullName,
        'language': language,
        'currency': currency,
        'notifications_enabled': notificationsEnabled,
        'voice_enabled': voiceEnabled,
        'dark_mode': darkMode,
      };

      if (phoneNumber != null) body['phone_number'] = phoneNumber;
      if (dateOfBirth != null) body['date_of_birth'] = dateOfBirth.toIso8601String();
      if (occupation != null) body['occupation'] = occupation;
      if (city != null) body['city'] = city;

      final response = await http.post(
        Uri.parse('$baseUrl/auth/setup-profile'),
        headers: await _authHeaders,
        body: jsonEncode(body),
      );

      return _handleResponse(response);
    } catch (e) {
      return {
        'success': false,
        'message': 'Gagal terhubung ke server: ${e.toString()}',
      };
    }
  }

  Future<Map<String, dynamic>> setupFinancial({
    required double monthlyIncome,
    double? monthlyBudget,
    double savingsGoalPercentage = 20.0,
    double? emergencyFundTarget,
    String? primaryBank,
  }) async {
    try {
      final body = <String, dynamic>{
        'monthly_income': monthlyIncome,
        'savings_goal_percentage': savingsGoalPercentage,
      };

      if (monthlyBudget != null) body['monthly_budget'] = monthlyBudget;
      if (emergencyFundTarget != null) body['emergency_fund_target'] = emergencyFundTarget;
      if (primaryBank != null) body['primary_bank'] = primaryBank;

      final response = await http.post(
        Uri.parse('$baseUrl/auth/initial-financial-setup'),
        headers: await _authHeaders,
        body: jsonEncode(body),
      );

      return _handleResponse(response);
    } catch (e) {
      return {
        'success': false,
        'message': 'Gagal terhubung ke server: ${e.toString()}',
      };
    }
  }

  Future<Map<String, dynamic>> logout() async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/auth/logout'),
        headers: await _authHeaders,
      );

      if (response.statusCode == 200) {
        await clearTokens();
      }

      return _handleResponse(response);
    } catch (e) {
      // Even if logout API fails, clear local tokens
      await clearTokens();
      return {
        'success': true,
        'message': 'Logout berhasil',
      };
    }
  }

  Future<Map<String, dynamic>> refreshToken() async {
    try {
      final refreshToken = await _storage.read(key: _refreshTokenKey);
      if (refreshToken == null) {
        throw Exception('No refresh token available');
      }

      final response = await http.post(
        Uri.parse('$baseUrl/auth/refresh-token'),
        headers: _headers,
        body: jsonEncode({
          'refresh_token': refreshToken,
        }),
      );

      final result = _handleResponse(response);
      
      // Save new access token
      if (result['success'] == true && result['data']?['access_token'] != null) {
        await _storage.write(key: _accessTokenKey, value: result['data']['access_token']);
      }

      return result;
    } catch (e) {
      return {
        'success': false,
        'message': 'Gagal refresh token: ${e.toString()}',
      };
    }
  }

  Future<Map<String, dynamic>> healthCheck() async {
    try {
      final response = await http.get(
        Uri.parse('${baseUrl.replaceAll('/api/v1', '')}/health'),
        headers: _headers,
      );
      return _handleResponse(response);
    } catch (e) {
      return {
        'success': false,
        'message': 'Failed to connect to server',
        'error': e.toString(),
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
        // Handle different error status codes
        String errorMessage = data['message'] ?? 'Terjadi kesalahan';
        
        if (response.statusCode == 400) {
          errorMessage = data['message'] ?? 'Data yang dikirim tidak valid';
        } else if (response.statusCode == 401) {
          errorMessage = 'Tidak memiliki akses. Silakan login kembali';
        } else if (response.statusCode == 404) {
          errorMessage = 'Endpoint tidak ditemukan';
        } else if (response.statusCode == 422) {
          // Handle validation errors
          if (data['detail'] != null && data['detail'] is List) {
            final errors = data['detail'] as List;
            if (errors.isNotEmpty) {
              errorMessage = errors.first['msg'] ?? errorMessage;
            }
          }
        } else if (response.statusCode >= 500) {
          errorMessage = 'Terjadi kesalahan pada server';
        }
        
        return {
          'success': false,
          'message': errorMessage,
          'errors': data['errors'],
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