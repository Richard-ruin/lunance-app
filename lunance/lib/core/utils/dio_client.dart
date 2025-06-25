// lib/core/utils/dio_client.dart
import 'package:dio/dio.dart';
import 'package:flutter/foundation.dart';
import '../constants/api_endpoints.dart';
import '../constants/app_constants.dart';
import '../storage/local_storage.dart';
import '../network/network_exceptions.dart';

class DioClient {
  late Dio _dio;
  final LocalStorage _localStorage;

  DioClient(this._localStorage) {
    _dio = Dio();
    _initializeInterceptors();
  }

  void _initializeInterceptors() {
    _dio.interceptors.add(
      InterceptorsWrapper(
        onRequest: (options, handler) async {
          // Add authorization token if available
          final token = _localStorage.getString(AppConstants.accessTokenKey);
          if (token != null) {
            options.headers['Authorization'] = 'Bearer $token';
          }
          
          // Add default headers
          options.headers['Content-Type'] = 'application/json';
          options.headers['Accept'] = 'application/json';
          
          if (kDebugMode) {
            print('REQUEST[${options.method}] => PATH: ${options.path}');
            print('Headers: ${options.headers}');
            if (options.data != null) {
              print('Data: ${options.data}');
            }
          }
          
          handler.next(options);
        },
        onResponse: (response, handler) {
          if (kDebugMode) {
            print('RESPONSE[${response.statusCode}] => PATH: ${response.requestOptions.path}');
            print('Data: ${response.data}');
          }
          handler.next(response);
        },
        onError: (error, handler) async {
          if (kDebugMode) {
            print('ERROR[${error.response?.statusCode}] => PATH: ${error.requestOptions.path}');
            print('Error: ${error.message}');
            if (error.response?.data != null) {
              print('Error Data: ${error.response?.data}');
            }
          }

          // Handle token refresh on 401 error
          if (error.response?.statusCode == 401) {
            final refreshed = await _refreshToken();
            if (refreshed) {
              // Retry the original request
              final clonedRequest = await _dio.request(
                error.requestOptions.path,
                options: Options(
                  method: error.requestOptions.method,
                  headers: error.requestOptions.headers,
                ),
                data: error.requestOptions.data,
                queryParameters: error.requestOptions.queryParameters,
              );
              handler.resolve(clonedRequest);
              return;
            }
          }

          handler.next(_handleError(error));
        },
      ),
    );

    // Add logging interceptor in debug mode
    if (kDebugMode) {
      _dio.interceptors.add(LogInterceptor(
        requestBody: true,
        responseBody: true,
        error: true,
      ));
    }

    // Set timeouts
    _dio.options.connectTimeout = Duration(seconds: AppConstants.connectionTimeoutSeconds);
    _dio.options.receiveTimeout = Duration(seconds: AppConstants.receiveTimeoutSeconds);
    _dio.options.sendTimeout = Duration(seconds: AppConstants.connectionTimeoutSeconds);
  }

  Future<bool> _refreshToken() async {
    try {
      final refreshToken = _localStorage.getString(AppConstants.refreshTokenKey);
      if (refreshToken == null) return false;

      final response = await _dio.post(
        ApiEndpoints.refreshToken,
        data: {'refresh_token': refreshToken},
      );

      if (response.statusCode == 200) {
        final data = response.data;
        await _localStorage.saveString(AppConstants.accessTokenKey, data['access_token']);
        if (data['refresh_token'] != null) {
          await _localStorage.saveString(AppConstants.refreshTokenKey, data['refresh_token']);
        }
        return true;
      }
    } catch (e) {
      // Refresh failed, clear tokens
      await _localStorage.remove(AppConstants.accessTokenKey);
      await _localStorage.remove(AppConstants.refreshTokenKey);
      await _localStorage.remove(AppConstants.userDataKey);
    }
    return false;
  }

  DioException _handleError(DioException error) {
    String message = 'Terjadi kesalahan yang tidak diketahui';
    
    switch (error.type) {
      case DioExceptionType.connectionTimeout:
      case DioExceptionType.sendTimeout:
      case DioExceptionType.receiveTimeout:
        message = 'Koneksi timeout. Periksa koneksi internet Anda.';
        break;
      case DioExceptionType.badResponse:
        final statusCode = error.response?.statusCode;
        final errorData = error.response?.data;
        
        switch (statusCode) {
          case 400:
            message = _extractErrorMessage(errorData) ?? 'Permintaan tidak valid';
            break;
          case 401:
            message = 'Sesi Anda telah berakhir. Silakan login kembali.';
            break;
          case 403:
            message = 'Anda tidak memiliki akses untuk melakukan tindakan ini';
            break;
          case 404:
            message = 'Data yang diminta tidak ditemukan';
            break;
          case 422:
            message = _extractErrorMessage(errorData) ?? 'Data yang Anda masukkan tidak valid';
            break;
          case 500:
            message = 'Terjadi kesalahan pada server. Silakan coba lagi nanti.';
            break;
          default:
            message = _extractErrorMessage(errorData) ?? 'Terjadi kesalahan pada server';
        }
        break;
      case DioExceptionType.cancel:
        message = 'Permintaan dibatalkan';
        break;
      case DioExceptionType.unknown:
        if (error.message?.contains('SocketException') == true) {
          message = 'Tidak ada koneksi internet';
        } else {
          message = 'Terjadi kesalahan koneksi';
        }
        break;
      default:
        message = 'Terjadi kesalahan yang tidak diketahui';
    }

    return DioException(
      requestOptions: error.requestOptions,
      response: error.response,
      type: error.type,
      error: message,
      message: message,
    );
  }

  String? _extractErrorMessage(dynamic errorData) {
    if (errorData is Map<String, dynamic>) {
      // Try to extract error message from different possible fields
      return errorData['detail'] ??
             errorData['message'] ??
             errorData['error'] ??
             errorData['msg'];
    } else if (errorData is String) {
      return errorData;
    }
    return null;
  }

  // GET Request
  Future<Response> get(
    String path, {
    Map<String, dynamic>? queryParameters,
    Options? options,
    CancelToken? cancelToken,
    ProgressCallback? onReceiveProgress,
  }) async {
    try {
      final response = await _dio.get(
        path,
        queryParameters: queryParameters,
        options: options,
        cancelToken: cancelToken,
        onReceiveProgress: onReceiveProgress,
      );
      return response;
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  // POST Request
  Future<Response> post(
    String path, {
    dynamic data,
    Map<String, dynamic>? queryParameters,
    Options? options,
    CancelToken? cancelToken,
    ProgressCallback? onSendProgress,
    ProgressCallback? onReceiveProgress,
  }) async {
    try {
      final response = await _dio.post(
        path,
        data: data,
        queryParameters: queryParameters,
        options: options,
        cancelToken: cancelToken,
        onSendProgress: onSendProgress,
        onReceiveProgress: onReceiveProgress,
      );
      return response;
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  // PUT Request
  Future<Response> put(
    String path, {
    dynamic data,
    Map<String, dynamic>? queryParameters,
    Options? options,
    CancelToken? cancelToken,
    ProgressCallback? onSendProgress,
    ProgressCallback? onReceiveProgress,
  }) async {
    try {
      final response = await _dio.put(
        path,
        data: data,
        queryParameters: queryParameters,
        options: options,
        cancelToken: cancelToken,
        onSendProgress: onSendProgress,
        onReceiveProgress: onReceiveProgress,
      );
      return response;
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  // DELETE Request
  Future<Response> delete(
    String path, {
    dynamic data,
    Map<String, dynamic>? queryParameters,
    Options? options,
    CancelToken? cancelToken,
  }) async {
    try {
      final response = await _dio.delete(
        path,
        data: data,
        queryParameters: queryParameters,
        options: options,
        cancelToken: cancelToken,
      );
      return response;
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  // PATCH Request
  Future<Response> patch(
    String path, {
    dynamic data,
    Map<String, dynamic>? queryParameters,
    Options? options,
    CancelToken? cancelToken,
    ProgressCallback? onSendProgress,
    ProgressCallback? onReceiveProgress,
  }) async {
    try {
      final response = await _dio.patch(
        path,
        data: data,
        queryParameters: queryParameters,
        options: options,
        cancelToken: cancelToken,
        onSendProgress: onSendProgress,
        onReceiveProgress: onReceiveProgress,
      );
      return response;
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  // File Upload
  Future<Response> uploadFile(
    String path,
    String filePath, {
    String fileName = 'file',
    Map<String, dynamic>? data,
    ProgressCallback? onSendProgress,
  }) async {
    try {
      final formData = FormData.fromMap({
        fileName: await MultipartFile.fromFile(filePath),
        ...?data,
      });

      final response = await _dio.post(
        path,
        data: formData,
        onSendProgress: onSendProgress,
      );
      return response;
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  // Download File
  Future<Response> downloadFile(
    String path,
    String savePath, {
    ProgressCallback? onReceiveProgress,
    Map<String, dynamic>? queryParameters,
    CancelToken? cancelToken,
  }) async {
    try {
      final response = await _dio.download(
        path,
        savePath,
        onReceiveProgress: onReceiveProgress,
        queryParameters: queryParameters,
        cancelToken: cancelToken,
      );
      return response;
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }
}