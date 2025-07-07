import 'dart:convert';
import 'dart:io';
import 'package:http/http.dart' as http;

import '../config/api_config.dart';
import '../config/app_config.dart';
import '../models/base_model.dart';
import '../models/user_model.dart';
import '../models/auth/register_data.dart';
import '../models/auth/auth_responses.dart';
import 'storage_service.dart';

class AuthService {
  static final AuthService _instance = AuthService._internal();
  factory AuthService() => _instance;
  AuthService._internal();

  late final http.Client _client;

  void init() {
    _client = http.Client();
  }

  void dispose() {
    _client.close();
  }

  // Get headers with auth token
  Map<String, String> _getHeaders({bool includeAuth = true}) {
    final headers = Map<String, String>.from(ApiConfig.defaultHeaders);
    
    if (includeAuth) {
      final token = StorageService.getAuthToken();
      if (token != null) {
        headers[ApiConfig.authorizationHeader] = '${ApiConfig.bearerPrefix}$token';
      }
    }
    
    return headers;
  }

  // Generic HTTP request method
  Future<ApiResponse<T>> _request<T>({
    required String method,
    required String endpoint,
    Map<String, String>? pathParams,
    Map<String, dynamic>? queryParams,
    Map<String, dynamic>? body,
    bool includeAuth = true,
    T Function(Map<String, dynamic>)? fromJson,
  }) async {
    try {
      // Build URL
      final url = Uri.parse(ApiConfig.buildUrl(endpoint, pathParams));
      final finalUrl = queryParams != null && queryParams.isNotEmpty
          ? url.replace(queryParameters: queryParams.map((k, v) => MapEntry(k, v.toString())))
          : url;

      // Prepare headers
      final headers = _getHeaders(includeAuth: includeAuth);

      // Prepare request
      late http.Response response;
      final jsonBody = body != null ? json.encode(body) : null;

      // Execute request based on method
      switch (method.toUpperCase()) {
        case 'GET':
          response = await _client.get(finalUrl, headers: headers)
              .timeout(Duration(seconds: AppConfig.apiTimeout));
          break;
        case 'POST':
          response = await _client.post(finalUrl, headers: headers, body: jsonBody)
              .timeout(Duration(seconds: AppConfig.apiTimeout));
          break;
        case 'PUT':
          response = await _client.put(finalUrl, headers: headers, body: jsonBody)
              .timeout(Duration(seconds: AppConfig.apiTimeout));
          break;
        case 'PATCH':
          response = await _client.patch(finalUrl, headers: headers, body: jsonBody)
              .timeout(Duration(seconds: AppConfig.apiTimeout));
          break;
        case 'DELETE':
          response = await _client.delete(finalUrl, headers: headers)
              .timeout(Duration(seconds: AppConfig.apiTimeout));
          break;
        default:
          throw AuthException('Unsupported HTTP method: $method');
      }

      // Parse response
      return _parseResponse<T>(response, fromJson);
    } on SocketException {
      throw AuthException('Tidak ada koneksi internet');
    } on HttpException {
      throw AuthException('Terjadi kesalahan koneksi');
    } on FormatException {
      throw AuthException('Format respons tidak valid');
    } catch (e) {
      if (e is AuthException) rethrow;
      throw AuthException('Terjadi kesalahan: ${e.toString()}');
    }
  }

  // Parse HTTP response
  ApiResponse<T> _parseResponse<T>(
    http.Response response,
    T Function(Map<String, dynamic>)? fromJson,
  ) {
    final statusCode = response.statusCode;
    final responseBody = response.body;

    // Try to parse JSON response
    Map<String, dynamic> jsonResponse;
    try {
      jsonResponse = json.decode(responseBody) as Map<String, dynamic>;
    } catch (e) {
      throw AuthException('Respons server tidak valid');
    }

    // Check if request was successful
    if (statusCode >= 200 && statusCode < 300) {
      return ApiResponse<T>.fromJson(jsonResponse, fromJson);
    } else {
      // Handle error response
      final errorResponse = ApiResponse<T>.fromJson(jsonResponse, fromJson);
      throw AuthException(
        errorResponse.message,
        statusCode: statusCode,
        errors: errorResponse.errors,
      );
    }
  }

  // REGISTER STEP METHODS

  // Register Step 1: Basic Information
  Future<ApiResponse<RegisterStepResponse>> registerStep1(RegisterStep1Data data) async {
    try {
      final response = await _request<RegisterStepResponse>(
        method: 'POST',
        endpoint: ApiConfig.registerStep1Endpoint,
        body: data.toJson(),
        includeAuth: false,
        fromJson: RegisterStepResponse.fromJson,
      );
      return response;
    } catch (e) {
      if (e is AuthException) rethrow;
      throw AuthException('Gagal mengirim data pribadi');
    }
  }

  // Register Step 2: University Information
  Future<ApiResponse<RegisterStepResponse>> registerStep2(RegisterStep2Data data) async {
    try {
      final response = await _request<RegisterStepResponse>(
        method: 'POST',
        endpoint: ApiConfig.registerStep2Endpoint,
        body: data.toJson(),
        includeAuth: false,
        fromJson: RegisterStepResponse.fromJson,
      );
      return response;
    } catch (e) {
      if (e is AuthException) rethrow;
      throw AuthException('Gagal menyimpan data akademik');
    }
  }

  // Register Step 3: OTP Verification
  Future<ApiResponse<RegisterStepResponse>> registerStep3(RegisterStep3Data data) async {
    try {
      final response = await _request<RegisterStepResponse>(
        method: 'POST',
        endpoint: ApiConfig.registerStep3Endpoint,
        body: data.toJson(),
        includeAuth: false,
        fromJson: RegisterStepResponse.fromJson,
      );
      return response;
    } catch (e) {
      if (e is AuthException) rethrow;
      throw AuthException('Kode OTP tidak valid');
    }
  }

  // Register Step 4: Initial Savings
  Future<ApiResponse<RegisterStepResponse>> registerStep4(RegisterStep4Data data) async {
    try {
      final response = await _request<RegisterStepResponse>(
        method: 'POST',
        endpoint: ApiConfig.registerStep4Endpoint,
        body: data.toJson(),
        includeAuth: false,
        fromJson: RegisterStepResponse.fromJson,
      );
      return response;
    } catch (e) {
      if (e is AuthException) rethrow;
      throw AuthException('Gagal menyimpan data tabungan');
    }
  }

  // Register Step 5: Complete Registration
  Future<ApiResponse<RegistrationCompleteResponse>> registerStep5(RegisterStep5Data data) async {
    try {
      final response = await _request<RegistrationCompleteResponse>(
        method: 'POST',
        endpoint: ApiConfig.registerStep5Endpoint,
        body: data.toJson(),
        includeAuth: false,
        fromJson: RegistrationCompleteResponse.fromJson,
      );
      return response;
    } catch (e) {
      if (e is AuthException) rethrow;
      throw AuthException('Gagal menyelesaikan registrasi');
    }
  }

  // LOGIN & AUTH METHODS

  // Login
  Future<ApiResponse<LoginResponse>> login(LoginRequest request) async {
    try {
      final response = await _request<LoginResponse>(
        method: 'POST',
        endpoint: ApiConfig.loginEndpoint,
        body: request.toJson(),
        includeAuth: false,
        fromJson: LoginResponse.fromJson,
      );
      return response;
    } catch (e) {
      if (e is AuthException) rethrow;
      throw AuthException('Gagal login');
    }
  }

  // Logout
  Future<ApiResponse<LogoutResponse>> logout() async {
    try {
      final response = await _request<LogoutResponse>(
        method: 'POST',
        endpoint: ApiConfig.logoutEndpoint,
        fromJson: LogoutResponse.fromJson,
      );
      return response;
    } catch (e) {
      if (e is AuthException) rethrow;
      throw AuthException('Gagal logout');
    }
  }

  // Get current user profile
  Future<ApiResponse<User>> getProfile() async {
    try {
      final response = await _request<User>(
        method: 'GET',
        endpoint: ApiConfig.profileEndpoint,
        fromJson: User.fromJson,
      );
      return response;
    } catch (e) {
      if (e is AuthException) rethrow;
      throw AuthException('Gagal mengambil profil');
    }
  }

  // Refresh token
  Future<ApiResponse<RefreshTokenResponse>> refreshToken(String refreshToken) async {
    try {
      final response = await _request<RefreshTokenResponse>(
        method: 'POST',
        endpoint: ApiConfig.refreshTokenEndpoint,
        body: {'refresh_token': refreshToken},
        includeAuth: false,
        fromJson: RefreshTokenResponse.fromJson,
      );
      return response;
    } catch (e) {
      if (e is AuthException) rethrow;
      throw AuthException('Gagal refresh token');
    }
  }

  // PASSWORD MANAGEMENT

  // Forgot password
  Future<ApiResponse<OtpResponse>> forgotPassword(ForgotPasswordRequest request) async {
    try {
      final response = await _request<OtpResponse>(
        method: 'POST',
        endpoint: ApiConfig.forgotPasswordEndpoint,
        body: request.toJson(),
        includeAuth: false,
        fromJson: OtpResponse.fromJson,
      );
      return response;
    } catch (e) {
      if (e is AuthException) rethrow;
      throw AuthException('Gagal mengirim email reset password');
    }
  }

  // Reset password
  Future<ApiResponse<PasswordResetResponse>> resetPassword(ResetPasswordRequest request) async {
    try {
      final response = await _request<PasswordResetResponse>(
        method: 'POST',
        endpoint: ApiConfig.resetPasswordEndpoint,
        body: request.toJson(),
        includeAuth: false,
        fromJson: PasswordResetResponse.fromJson,
      );
      return response;
    } catch (e) {
      if (e is AuthException) rethrow;
      throw AuthException('Gagal reset password');
    }
  }

  // Change password
  Future<ApiResponse<Map<String, dynamic>>> changePassword(ChangePasswordRequest request) async {
    try {
      final response = await _request<Map<String, dynamic>>(
        method: 'POST',
        endpoint: ApiConfig.changePasswordEndpoint,
        body: request.toJson(),
        fromJson: (json) => json,
      );
      return response;
    } catch (e) {
      if (e is AuthException) rethrow;
      throw AuthException('Gagal mengubah password');
    }
  }

  // UTILITY METHODS

  // Resend OTP
  Future<ApiResponse<OtpResponse>> resendOtp(ResendOtpRequest request) async {
    try {
      final response = await _request<OtpResponse>(
        method: 'POST',
        endpoint: ApiConfig.verifyOtpEndpoint,
        body: request.toJson(),
        includeAuth: false,
        fromJson: OtpResponse.fromJson,
      );
      return response;
    } catch (e) {
      if (e is AuthException) rethrow;
      throw AuthException('Gagal mengirim ulang OTP');
    }
  }

  // Check email availability
  Future<ApiResponse<EmailCheckResponse>> checkEmailAvailability(String email) async {
    try {
      final response = await _request<EmailCheckResponse>(
        method: 'GET',
        endpoint: '${ApiConfig.checkEmailEndpoint}/$email',
        includeAuth: false,
        fromJson: EmailCheckResponse.fromJson,
      );
      return response;
    } catch (e) {
      if (e is AuthException) rethrow;
      throw AuthException('Gagal memeriksa ketersediaan email');
    }
  }

  // Verify OTP status
  Future<ApiResponse<VerificationStatusResponse>> verifyOtpStatus(String email) async {
    try {
      final response = await _request<VerificationStatusResponse>(
        method: 'GET',
        endpoint: '/auth/verify-status/$email',
        includeAuth: false,
        fromJson: VerificationStatusResponse.fromJson,
      );
      return response;
    } catch (e) {
      if (e is AuthException) rethrow;
      throw AuthException('Gagal memeriksa status verifikasi');
    }
  }

  // Validate token
  Future<ApiResponse<TokenValidationResponse>> validateToken(String token) async {
    try {
      final response = await _request<TokenValidationResponse>(
        method: 'POST',
        endpoint: '/auth/validate-token',
        body: {'token': token},
        includeAuth: false,
        fromJson: TokenValidationResponse.fromJson,
      );
      return response;
    } catch (e) {
      if (e is AuthException) rethrow;
      throw AuthException('Gagal validasi token');
    }
  }

  // Update profile
  Future<ApiResponse<ProfileUpdateResponse>> updateProfile(UpdateProfileRequest request) async {
    try {
      final response = await _request<ProfileUpdateResponse>(
        method: 'PATCH',
        endpoint: '/auth/profile',
        body: request.toJson(),
        fromJson: ProfileUpdateResponse.fromJson,
      );
      return response;
    } catch (e) {
      if (e is AuthException) rethrow;
      throw AuthException('Gagal memperbarui profil');
    }
  }
}

// Custom exception for authentication errors
class AuthException implements Exception {
  final String message;
  final int? statusCode;
  final ErrorDetails? errors;

  const AuthException(
    this.message, {
    this.statusCode,
    this.errors,
  });

  @override
  String toString() {
    return 'AuthException: $message';
  }

  // Check if it's a specific type of error
  bool get isNetworkError => statusCode == null;
  bool get isClientError => statusCode != null && statusCode! >= 400 && statusCode! < 500;
  bool get isServerError => statusCode != null && statusCode! >= 500;
  bool get isUnauthorized => statusCode == 401;
  bool get isForbidden => statusCode == 403;
  bool get isNotFound => statusCode == 404;
  bool get isValidationError => statusCode == 422 || statusCode == 400;

  // Get user-friendly error message
  String get userMessage {
    switch (statusCode) {
      case 401:
        return 'Email atau password salah';
      case 403:
        return 'Akses ditolak';
      case 404:
        return 'Data tidak ditemukan';
      case 422:
      case 400:
        return message;
      case 429:
        return 'Terlalu banyak percobaan, silakan coba lagi nanti';
      case 500:
        return 'Terjadi kesalahan server, silakan coba lagi';
      case 502:
        return 'Server sedang tidak tersedia';
      case 503:
        return 'Layanan sedang dalam pemeliharaan';
      default:
        return message.isNotEmpty ? message : 'Terjadi kesalahan tidak terduga';
    }
  }
}