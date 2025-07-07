import 'dart:convert';
import 'dart:io';
import 'package:http/http.dart' as http;

import '../config/api_config.dart';
import '../config/app_config.dart';
import '../models/base_model.dart';
import '../models/user_model.dart';
import '../models/university_model.dart';
import 'storage_service.dart';

class ApiService {
  static final ApiService _instance = ApiService._internal();
  factory ApiService() => _instance;
  ApiService._internal();

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
          throw ApiException('Unsupported HTTP method: $method');
      }

      // Parse response
      return _parseResponse<T>(response, fromJson);
    } on SocketException {
      throw ApiException('Tidak ada koneksi internet');
    } on HttpException {
      throw ApiException('Terjadi kesalahan koneksi');
    } on FormatException {
      throw ApiException('Format respons tidak valid');
    } catch (e) {
      if (e is ApiException) rethrow;
      throw ApiException('Terjadi kesalahan: ${e.toString()}');
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
      throw ApiException('Respons server tidak valid');
    }

    // Check if request was successful
    if (statusCode >= 200 && statusCode < 300) {
      return ApiResponse<T>.fromJson(jsonResponse, fromJson);
    } else {
      // Handle error response
      final errorResponse = ApiResponse<T>.fromJson(jsonResponse, fromJson);
      throw ApiException(
        errorResponse.message,
        statusCode: statusCode,
        errors: errorResponse.errors,
      );
    }
  }

  // Convenience methods for HTTP verbs
  Future<ApiResponse<T>> get<T>(
    String endpoint, {
    Map<String, String>? pathParams,
    Map<String, dynamic>? queryParams,
    bool includeAuth = true,
    T Function(Map<String, dynamic>)? fromJson,
  }) {
    return _request<T>(
      method: 'GET',
      endpoint: endpoint,
      pathParams: pathParams,
      queryParams: queryParams,
      includeAuth: includeAuth,
      fromJson: fromJson,
    );
  }

  Future<ApiResponse<T>> post<T>(
    String endpoint, {
    Map<String, String>? pathParams,
    Map<String, dynamic>? body,
    bool includeAuth = true,
    T Function(Map<String, dynamic>)? fromJson,
  }) {
    return _request<T>(
      method: 'POST',
      endpoint: endpoint,
      pathParams: pathParams,
      body: body,
      includeAuth: includeAuth,
      fromJson: fromJson,
    );
  }

  Future<ApiResponse<T>> put<T>(
    String endpoint, {
    Map<String, String>? pathParams,
    Map<String, dynamic>? body,
    bool includeAuth = true,
    T Function(Map<String, dynamic>)? fromJson,
  }) {
    return _request<T>(
      method: 'PUT',
      endpoint: endpoint,
      pathParams: pathParams,
      body: body,
      includeAuth: includeAuth,
      fromJson: fromJson,
    );
  }

  Future<ApiResponse<T>> patch<T>(
    String endpoint, {
    Map<String, String>? pathParams,
    Map<String, dynamic>? body,
    bool includeAuth = true,
    T Function(Map<String, dynamic>)? fromJson,
  }) {
    return _request<T>(
      method: 'PATCH',
      endpoint: endpoint,
      pathParams: pathParams,
      body: body,
      includeAuth: includeAuth,
      fromJson: fromJson,
    );
  }

  Future<ApiResponse<T>> delete<T>(
    String endpoint, {
    Map<String, String>? pathParams,
    bool includeAuth = true,
    T Function(Map<String, dynamic>)? fromJson,
  }) {
    return _request<T>(
      method: 'DELETE',
      endpoint: endpoint,
      pathParams: pathParams,
      includeAuth: includeAuth,
      fromJson: fromJson,
    );
  }

  // Auth API methods
  Future<ApiResponse<AuthResponse>> login(LoginRequest request) {
    return post<AuthResponse>(
      ApiConfig.loginEndpoint,
      body: request.toJson(),
      includeAuth: false,
      fromJson: AuthResponse.fromJson,
    );
  }

  // Note: Removed the old register method since we're using multi-step registration now
  // All registration is handled through AuthService with step-by-step endpoints

  Future<ApiResponse<Map<String, dynamic>>> logout() {
    return post<Map<String, dynamic>>(
      ApiConfig.logoutEndpoint,
      fromJson: (json) => json,
    );
  }

  Future<ApiResponse<User>> getProfile() {
    return get<User>(
      ApiConfig.profileEndpoint,
      fromJson: User.fromJson,
    );
  }

  Future<ApiResponse<Map<String, dynamic>>> forgotPassword(ForgotPasswordRequest request) {
    return post<Map<String, dynamic>>(
      ApiConfig.forgotPasswordEndpoint,
      body: request.toJson(),
      includeAuth: false,
      fromJson: (json) => json,
    );
  }

  // University API methods
  Future<ApiResponse<UniversitiesResponse>> getUniversities({
    int page = 1,
    int limit = 10,
    String? search,
  }) {
    final queryParams = <String, dynamic>{
      'page': page,
      'limit': limit,
    };
    
    if (search != null && search.isNotEmpty) {
      queryParams['search'] = search;
    }

    return get<UniversitiesResponse>(
      ApiConfig.universitiesEndpoint,
      queryParams: queryParams,
      fromJson: UniversitiesResponse.fromJson,
    );
  }

  Future<ApiResponse<University>> getUniversityById(String id) {
    return get<University>(
      ApiConfig.universityDetailEndpoint,
      pathParams: {'id': id},
      fromJson: University.fromJson,
    );
  }

  Future<ApiResponse<List<Fakultas>>> getUniversityFakultas(String universityId) {
    return get<List<Fakultas>>(
      ApiConfig.universityFakultasEndpoint,
      pathParams: {'id': universityId},
      fromJson: (json) => (json as List)
          .map((item) => Fakultas.fromJson(item as Map<String, dynamic>))
          .toList(),
    );
  }

  Future<ApiResponse<List<ProgramStudi>>> getFakultasProdi(String fakultasId) {
    return get<List<ProgramStudi>>(
      ApiConfig.fakultasProdiEndpoint,
      pathParams: {'id': fakultasId},
      fromJson: (json) => (json as List)
          .map((item) => ProgramStudi.fromJson(item as Map<String, dynamic>))
          .toList(),
    );
  }

  Future<ApiResponse<UniversityRequest>> createUniversityRequest(CreateUniversityRequest request) {
    return post<UniversityRequest>(
      ApiConfig.universityRequestEndpoint,
      body: request.toJson(),
      fromJson: UniversityRequest.fromJson,
    );
  }

  Future<ApiResponse<List<University>>> searchUniversities(String query) {
    return get<List<University>>(
      ApiConfig.universitySearchEndpoint,
      queryParams: {'q': query},
      fromJson: (json) => (json as List)
          .map((item) => University.fromJson(item as Map<String, dynamic>))
          .toList(),
    );
  }

  // Admin API methods
  Future<ApiResponse<List<UniversityRequest>>> getUniversityRequests({
    int page = 1,
    int limit = 10,
    RequestStatus? status,
  }) {
    final queryParams = <String, dynamic>{
      'page': page,
      'limit': limit,
    };
    
    if (status != null) {
      queryParams['status'] = status.value;
    }

    return get<List<UniversityRequest>>(
      ApiConfig.adminUniversityRequestsEndpoint,
      queryParams: queryParams,
      fromJson: (json) => (json as List)
          .map((item) => UniversityRequest.fromJson(item as Map<String, dynamic>))
          .toList(),
    );
  }

  Future<ApiResponse<UniversityRequest>> approveUniversityRequest(String requestId, {String? note}) {
    final body = <String, dynamic>{};
    if (note != null) body['catatan_admin'] = note;

    return post<UniversityRequest>(
      ApiConfig.adminApproveRequestEndpoint,
      pathParams: {'id': requestId},
      body: body,
      fromJson: UniversityRequest.fromJson,
    );
  }

  Future<ApiResponse<UniversityRequest>> rejectUniversityRequest(String requestId, {String? note}) {
    final body = <String, dynamic>{};
    if (note != null) body['catatan_admin'] = note;

    return post<UniversityRequest>(
      ApiConfig.adminRejectRequestEndpoint,
      pathParams: {'id': requestId},
      body: body,
      fromJson: UniversityRequest.fromJson,
    );
  }

  Future<ApiResponse<Map<String, dynamic>>> getAdminStatistics() {
    return get<Map<String, dynamic>>(
      ApiConfig.adminStatisticsEndpoint,
      fromJson: (json) => json,
    );
  }

  // Health check
  Future<ApiResponse<Map<String, dynamic>>> healthCheck() {
    return get<Map<String, dynamic>>(
      ApiConfig.healthCheckEndpoint,
      includeAuth: false,
      fromJson: (json) => json,
    );
  }
}

// Custom exception for API errors
class ApiException implements Exception {
  final String message;
  final int? statusCode;
  final ErrorDetails? errors;

  const ApiException(
    this.message, {
    this.statusCode,
    this.errors,
  });

  @override
  String toString() {
    return 'ApiException: $message';
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
        return 'Sesi Anda telah habis, silakan login kembali';
      case 403:
        return 'Anda tidak memiliki akses untuk melakukan aksi ini';
      case 404:
        return 'Data yang dicari tidak ditemukan';
      case 422:
      case 400:
        return message;
      case 429:
        return 'Terlalu banyak permintaan, silakan coba lagi nanti';
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