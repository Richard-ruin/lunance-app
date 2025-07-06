import 'dart:async';
import 'dart:convert';
import 'dart:io';
import 'package:dio/dio.dart';
import 'package:connectivity_plus/connectivity_plus.dart';
import '../config/api_config.dart';
import '../config/app_config.dart';
import '../models/base_model.dart';
import '../services/storage_service.dart';
import '../utils/constants.dart';

class ApiService {
  late final Dio _dio;
  late final StorageService _storageService;
  final Connectivity _connectivity = Connectivity();

  // Request interceptor for adding auth headers
  late final InterceptorsWrapper _authInterceptor;
  
  // Retry interceptor for handling retries
  late final InterceptorsWrapper _retryInterceptor;

  ApiService(this._storageService) {
    _initializeDio();
    _setupInterceptors();
  }

  void _initializeDio() {
    _dio = Dio(BaseOptions(
      baseUrl: ApiConfig.baseUrl,
      connectTimeout: AppConfig.apiTimeout,
      receiveTimeout: AppConfig.apiTimeout,
      sendTimeout: AppConfig.uploadTimeout,
      headers: ApiConfig.defaultHeaders,
      responseType: ResponseType.json,
      validateStatus: (status) => status != null && status < 500,
    ));
  }

  void _setupInterceptors() {
    // Auth Interceptor
    _authInterceptor = InterceptorsWrapper(
      onRequest: (options, handler) async {
        final token = _storageService.getAccessToken();
        if (token != null && token.isNotEmpty) {
          options.headers['Authorization'] = '${ApiConfig.bearerTokenType} $token';
        }
        handler.next(options);
      },
      onError: (error, handler) async {
        if (error.response?.statusCode == ApiConfig.statusUnauthorized) {
          // Try to refresh token
          final refreshed = await _refreshToken();
          if (refreshed) {
            // Retry original request with new token
            final options = error.requestOptions;
            final token = _storageService.getAccessToken();
            if (token != null) {
              options.headers['Authorization'] = '${ApiConfig.bearerTokenType} $token';
            }
            
            try {
              final response = await _dio.fetch(options);
              handler.resolve(response);
            } catch (e) {
              handler.next(error);
            }
          } else {
            // Refresh failed, clear auth data and redirect to login
            await _storageService.clearAuthData();
            handler.next(error);
          }
        } else {
          handler.next(error);
        }
      },
    );

    // Retry Interceptor
    _retryInterceptor = InterceptorsWrapper(
      onError: (error, handler) async {
        final statusCode = error.response?.statusCode;
        if (statusCode != null && 
            ApiConfig.isRetryableError(statusCode) && 
            error.requestOptions.extra['retryCount'] == null) {
          
          error.requestOptions.extra['retryCount'] = 0;
          await _retryRequest(error, handler);
        } else {
          handler.next(error);
        }
      },
    );

    _dio.interceptors.addAll([
      _authInterceptor,
      _retryInterceptor,
      if (AppConfig.isDebug) LogInterceptor(
        requestBody: true,
        responseBody: true,
        error: true,
        requestHeader: true,
        responseHeader: false,
      ),
    ]);
  }

  Future<void> _retryRequest(DioException error, ErrorInterceptorHandler handler) async {
    final retryCount = error.requestOptions.extra['retryCount'] as int;
    
    if (retryCount < ApiConfig.maxRetries) {
      error.requestOptions.extra['retryCount'] = retryCount + 1;
      
      // Wait before retry with exponential backoff
      final delay = Duration(
        milliseconds: ApiConfig.retryDelay.inMilliseconds * (retryCount + 1),
      );
      await Future.delayed(delay);
      
      try {
        final response = await _dio.fetch(error.requestOptions);
        handler.resolve(response);
      } catch (e) {
        if (e is DioException) {
          await _retryRequest(e, handler);
        } else {
          handler.next(error);
        }
      }
    } else {
      handler.next(error);
    }
  }

  Future<bool> _refreshToken() async {
    try {
      final refreshToken = _storageService.getRefreshToken();
      if (refreshToken == null || refreshToken.isEmpty) {
        return false;
      }

      final response = await _dio.post(
        ApiConfig.refreshToken,
        data: {'refresh_token': refreshToken},
        options: Options(
          headers: {...ApiConfig.defaultHeaders},
        ),
      );

      if (response.statusCode == ApiConfig.statusOk && response.data['success'] == true) {
        final data = response.data['data'];
        await _storageService.setAccessToken(data['access_token']);
        if (data['refresh_token'] != null) {
          await _storageService.setRefreshToken(data['refresh_token']);
        }
        return true;
      }
      return false;
    } catch (e) {
      return false;
    }
  }

  // ======================
  // HTTP Methods
  // ======================

  Future<ApiResponse<T>> get<T>(
    String endpoint, {
    Map<String, dynamic>? queryParameters,
    Map<String, String>? headers,
    T Function(dynamic)? fromJson,
    bool useCache = false,
    Duration? cacheExpiry,
  }) async {
    await _checkConnectivity();
    
    // Check cache first if enabled
    if (useCache && ApiConfig.isCacheableEndpoint(endpoint)) {
      final cacheKey = _getCacheKey(endpoint, queryParameters);
      final cachedData = _storageService.getCache<Map<String, dynamic>>(cacheKey);
      if (cachedData != null) {
        return ApiResponse<T>.fromJson(cachedData, fromJson);
      }
    }

    try {
      final response = await _dio.get(
        endpoint,
        queryParameters: queryParameters,
        options: Options(headers: headers),
      );

      final apiResponse = _handleResponse<T>(response, fromJson);
      
      // Cache successful responses if enabled
      if (useCache && apiResponse.success && ApiConfig.isCacheableEndpoint(endpoint)) {
        final cacheKey = _getCacheKey(endpoint, queryParameters);
        await _storageService.setCache(
          cacheKey,
          response.data,
          expiry: cacheExpiry ?? ApiConfig.cacheExpiry,
        );
      }

      return apiResponse;
    } catch (e) {
      return _handleError<T>(e);
    }
  }

  Future<ApiResponse<T>> post<T>(
    String endpoint, {
    dynamic data,
    Map<String, dynamic>? queryParameters,
    Map<String, String>? headers,
    T Function(dynamic)? fromJson,
  }) async {
    await _checkConnectivity();

    try {
      final response = await _dio.post(
        endpoint,
        data: data,
        queryParameters: queryParameters,
        options: Options(headers: headers),
      );

      return _handleResponse<T>(response, fromJson);
    } catch (e) {
      return _handleError<T>(e);
    }
  }

  Future<ApiResponse<T>> put<T>(
    String endpoint, {
    dynamic data,
    Map<String, dynamic>? queryParameters,
    Map<String, String>? headers,
    T Function(dynamic)? fromJson,
  }) async {
    await _checkConnectivity();

    try {
      final response = await _dio.put(
        endpoint,
        data: data,
        queryParameters: queryParameters,
        options: Options(headers: headers),
      );

      return _handleResponse<T>(response, fromJson);
    } catch (e) {
      return _handleError<T>(e);
    }
  }

  Future<ApiResponse<T>> patch<T>(
    String endpoint, {
    dynamic data,
    Map<String, dynamic>? queryParameters,
    Map<String, String>? headers,
    T Function(dynamic)? fromJson,
  }) async {
    await _checkConnectivity();

    try {
      final response = await _dio.patch(
        endpoint,
        data: data,
        queryParameters: queryParameters,
        options: Options(headers: headers),
      );

      return _handleResponse<T>(response, fromJson);
    } catch (e) {
      return _handleError<T>(e);
    }
  }

  Future<ApiResponse<T>> delete<T>(
    String endpoint, {
    dynamic data,
    Map<String, dynamic>? queryParameters,
    Map<String, String>? headers,
    T Function(dynamic)? fromJson,
  }) async {
    await _checkConnectivity();

    try {
      final response = await _dio.delete(
        endpoint,
        data: data,
        queryParameters: queryParameters,
        options: Options(headers: headers),
      );

      return _handleResponse<T>(response, fromJson);
    } catch (e) {
      return _handleError<T>(e);
    }
  }

  // ======================
  // File Upload Methods
  // ======================

  Future<ApiResponse<T>> uploadFile<T>(
    String endpoint,
    File file, {
    String fieldName = 'file',
    Map<String, dynamic>? data,
    T Function(dynamic)? fromJson,
    void Function(int, int)? onSendProgress,
  }) async {
    await _checkConnectivity();

    try {
      final fileName = file.path.split('/').last;
      final formData = FormData.fromMap({
        fieldName: await MultipartFile.fromFile(file.path, filename: fileName),
        ...?data,
      });

      final response = await _dio.post(
        endpoint,
        data: formData,
        options: Options(
          headers: ApiConfig.multipartHeaders,
          sendTimeout: AppConfig.uploadTimeout,
        ),
        onSendProgress: onSendProgress,
      );

      return _handleResponse<T>(response, fromJson);
    } catch (e) {
      return _handleError<T>(e);
    }
  }

  Future<ApiResponse<T>> uploadMultipleFiles<T>(
    String endpoint,
    List<File> files, {
    String fieldName = 'files',
    Map<String, dynamic>? data,
    T Function(dynamic)? fromJson,
    void Function(int, int)? onSendProgress,
  }) async {
    await _checkConnectivity();

    try {
      final multipartFiles = <MultipartFile>[];
      for (final file in files) {
        final fileName = file.path.split('/').last;
        multipartFiles.add(
          await MultipartFile.fromFile(file.path, filename: fileName),
        );
      }

      final formData = FormData.fromMap({
        fieldName: multipartFiles,
        ...?data,
      });

      final response = await _dio.post(
        endpoint,
        data: formData,
        options: Options(
          headers: ApiConfig.multipartHeaders,
          sendTimeout: AppConfig.uploadTimeout,
        ),
        onSendProgress: onSendProgress,
      );

      return _handleResponse<T>(response, fromJson);
    } catch (e) {
      return _handleError<T>(e);
    }
  }

  // ======================
  // Helper Methods
  // ======================

  ApiResponse<T> _handleResponse<T>(Response response, T Function(dynamic)? fromJson) {
    if (ApiConfig.isSuccessStatusCode(response.statusCode ?? 0)) {
      return ApiResponse<T>.fromJson(response.data, fromJson);
    } else {
      final errorData = response.data;
      return ApiResponse<T>(
        success: false,
        message: errorData['message'] ?? ErrorMessages.serverError,
        timestamp: DateTime.now().toIso8601String(),
        errors: errorData['errors'],
      );
    }
  }

  ApiResponse<T> _handleError<T>(dynamic error) {
    if (error is DioException) {
      switch (error.type) {
        case DioExceptionType.connectionTimeout:
        case DioExceptionType.sendTimeout:
        case DioExceptionType.receiveTimeout:
          return ApiResponse<T>(
            success: false,
            message: ErrorMessages.timeoutError,
            timestamp: DateTime.now().toIso8601String(),
          );
        case DioExceptionType.connectionError:
          return ApiResponse<T>(
            success: false,
            message: ErrorMessages.networkError,
            timestamp: DateTime.now().toIso8601String(),
          );
        case DioExceptionType.badResponse:
          final response = error.response;
          if (response?.data != null) {
            return ApiResponse<T>.fromJson(response!.data, null);
          }
          return ApiResponse<T>(
            success: false,
            message: ErrorMessages.serverError,
            timestamp: DateTime.now().toIso8601String(),
          );
        default:
          return ApiResponse<T>(
            success: false,
            message: ErrorMessages.unknownError,
            timestamp: DateTime.now().toIso8601String(),
          );
      }
    } else {
      return ApiResponse<T>(
        success: false,
        message: error.toString(),
        timestamp: DateTime.now().toIso8601String(),
      );
    }
  }

  Future<void> _checkConnectivity() async {
    final connectivityResult = await _connectivity.checkConnectivity();
    if (connectivityResult == ConnectivityResult.none) {
      throw DioException(
        requestOptions: RequestOptions(path: ''),
        type: DioExceptionType.connectionError,
        message: ErrorMessages.networkError,
      );
    }
  }

  String _getCacheKey(String endpoint, Map<String, dynamic>? queryParameters) {
    final uri = Uri(path: endpoint, queryParameters: queryParameters?.map(
      (key, value) => MapEntry(key, value.toString()),
    ));
    return 'api_cache_${uri.toString().hashCode}';
  }

  // ======================
  // Health Check
  // ======================

  Future<bool> checkHealth() async {
    try {
      final response = await _dio.get('/health');
      return response.statusCode == ApiConfig.statusOk;
    } catch (e) {
      return false;
    }
  }

  // ======================
  // Cache Management
  // ======================

  Future<void> clearCache() async {
    await _storageService.clearCache();
  }

  Future<void> clearExpiredCache() async {
    await _storageService.clearExpiredCache();
  }

  // ======================
  // Configuration
  // ======================

  void updateBaseUrl(String baseUrl) {
    _dio.options.baseUrl = baseUrl;
  }

  void updateTimeout(Duration timeout) {
    _dio.options.connectTimeout = timeout;
    _dio.options.receiveTimeout = timeout;
  }

  // ======================
  // Cleanup
  // ======================

  void dispose() {
    _dio.close();
  }
}