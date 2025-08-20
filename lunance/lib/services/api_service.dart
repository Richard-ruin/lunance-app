import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import '../models/user_model.dart';
import '../config/app_config.dart';

class ApiService {
  static const String baseUrl =
      'http://192.168.101.7:8000/api/v1'; // Ganti dengan IP backend Anda
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

  /// Setup profile - Updated for Indonesian students
  Future<Map<String, dynamic>> setupProfile({
    required String fullName,
    String? phoneNumber,
    required String university, // Required field for university
    required String city, // Required field for city/district
    String? occupation, // Optional side job
    bool notificationsEnabled = true,
    bool voiceEnabled = true,
    bool darkMode = false,
  }) async {
    try {
      final body = <String, dynamic>{
        'full_name': fullName,
        'university': university,
        'city': city,
        'notifications_enabled': notificationsEnabled,
        'voice_enabled': voiceEnabled,
        'dark_mode': darkMode,
      };

      // Add optional fields only if they have values
      if (phoneNumber != null && phoneNumber.isNotEmpty) {
        body['phone_number'] = phoneNumber;
      }
      if (occupation != null && occupation.isNotEmpty) {
        body['occupation'] = occupation;
      }

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

  /// Setup financial with 50/30/20 method
  Future<Map<String, dynamic>> setupFinancial50302({
    required double currentSavings,
    required double monthlyIncome,
    required String primaryBank,
  }) async {
    try {
      final body = <String, dynamic>{
        'current_savings': currentSavings,
        'monthly_income': monthlyIncome,
        'primary_bank': primaryBank,
      };

      final response = await http.post(
        Uri.parse('$baseUrl/auth/setup-financial-50-30-20'),
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

  /// Update financial settings
  Future<Map<String, dynamic>> updateFinancialSettings({
    double? currentSavings,
    double? monthlyIncome,
    String? primaryBank,
  }) async {
    try {
      final body = <String, dynamic>{};

      if (currentSavings != null) {
        body['current_savings'] = currentSavings;
      }
      if (monthlyIncome != null) {
        body['monthly_income'] = monthlyIncome;
      }
      if (primaryBank != null) {
        body['primary_bank'] = primaryBank;
      }

      final response = await http.put(
        Uri.parse('$baseUrl/auth/financial-settings'),
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

  /// Get financial overview
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
        'message': 'Gagal terhubung ke server: ${e.toString()}',
      };
    }
  }

  /// Get budget status
  Future<Map<String, dynamic>> getBudgetStatus() async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/auth/budget-status'),
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

  /// Reset monthly budget
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
        'message': 'Gagal terhubung ke server: ${e.toString()}',
      };
    }
  }

  /// Get budget categories
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
        'message': 'Gagal terhubung ke server: ${e.toString()}',
      };
    }
  }

  /// Get student financial tips
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
        'message': 'Gagal terhubung ke server: ${e.toString()}',
      };
    }
  }

  /// Get onboarding status
  Future<Map<String, dynamic>> getOnboardingStatus() async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/auth/onboarding-status'),
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

  /// Update profile
  Future<Map<String, dynamic>> updateProfile({
    String? fullName,
    String? phoneNumber,
    String? university,
    String? city,
    String? occupation,
    bool? notificationsEnabled,
    bool? voiceEnabled,
    bool? darkMode,
    bool? autoCategorization,
  }) async {
    try {
      final body = <String, dynamic>{};

      if (fullName != null) body['full_name'] = fullName;
      if (phoneNumber != null) body['phone_number'] = phoneNumber;
      if (university != null) body['university'] = university;
      if (city != null) body['city'] = city;
      if (occupation != null) body['occupation'] = occupation;
      if (notificationsEnabled != null)
        body['notifications_enabled'] = notificationsEnabled;
      if (voiceEnabled != null) body['voice_enabled'] = voiceEnabled;
      if (darkMode != null) body['dark_mode'] = darkMode;
      if (autoCategorization != null)
        body['auto_categorization'] = autoCategorization;

      final response = await http.put(
        Uri.parse('$baseUrl/auth/update-profile'),
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

  /// Change password
  Future<Map<String, dynamic>> changePassword({
    required String currentPassword,
    required String newPassword,
    required String confirmPassword,
  }) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/auth/change-password'),
        headers: await _authHeaders,
        body: jsonEncode({
          'current_password': currentPassword,
          'new_password': newPassword,
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
      if (result['success'] == true &&
          result['data']?['access_token'] != null) {
        await _storage.write(
            key: _accessTokenKey, value: result['data']['access_token']);
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
