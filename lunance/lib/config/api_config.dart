import 'app_config.dart';

class ApiConfig {
  // Base URLs
  static String get baseUrl => AppConfig.apiUrl;
  static String get healthCheckUrl => AppConfig.isProduction 
      ? 'https://api.lunance.app/health'
      : 'http://localhost:8000/health';
  
  // Authentication Endpoints
  static const String authBase = '/auth';
  static const String login = '$authBase/login';
  static const String register = '$authBase/register';
  static const String logout = '$authBase/logout';
  static const String refreshToken = '$authBase/refresh';
  static const String profile = '$authBase/me';
  static const String updateProfile = '$authBase/profile';
  static const String changePassword = '$authBase/change-password';
  static const String forgotPassword = '$authBase/forgot-password';
  static const String resetPassword = '$authBase/reset-password';
  static const String verifyEmail = '$authBase/verify-email';
  
  // University Endpoints
  static const String universitiesBase = '/universities';
  static const String universities = universitiesBase;
  static const String universityDetail = '$universitiesBase/{id}';
  static const String universityFakultas = '$universitiesBase/{id}/fakultas';
  static const String fakultasProdi = '$universitiesBase/fakultas/{id}/prodi';
  static const String universityRequest = '$universitiesBase/request';
  static const String universitySearch = '$universitiesBase/search';
  
  // Admin Endpoints
  static const String adminBase = '/admin';
  static const String adminUniversityRequests = '$adminBase/university-requests';
  static const String adminUniversityRequestDetail = '$adminBase/university-requests/{id}';
  static const String adminApproveRequest = '$adminBase/university-requests/{id}/approve';
  static const String adminRejectRequest = '$adminBase/university-requests/{id}/reject';
  static const String adminStatistics = '$adminBase/statistics';
  static const String adminUsers = '$adminBase/users';
  static const String adminUserDetail = '$adminBase/users/{id}';
  
  // Budget & Finance Endpoints (Future Implementation)
  static const String budgetBase = '/budget';
  static const String budgets = budgetBase;
  static const String budgetDetail = '$budgetBase/{id}';
  static const String budgetCategories = '$budgetBase/categories';
  static const String transactions = '/transactions';
  static const String transactionDetail = '/transactions/{id}';
  static const String reports = '/reports';
  static const String analytics = '/analytics';
  
  // Notification Endpoints (Future Implementation)
  static const String notificationsBase = '/notifications';
  static const String notifications = notificationsBase;
  static const String notificationDetail = '$notificationsBase/{id}';
  static const String markAsRead = '$notificationsBase/{id}/read';
  static const String markAllAsRead = '$notificationsBase/read-all';
  
  // File Upload Endpoints
  static const String uploadBase = '/upload';
  static const String uploadImage = '$uploadBase/image';
  static const String uploadDocument = '$uploadBase/document';
  static const String uploadAvatar = '$uploadBase/avatar';
  
  // HTTP Headers
  static const Map<String, String> defaultHeaders = {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    'User-Agent': 'Lunance-App/1.0.0',
  };
  
  static const Map<String, String> multipartHeaders = {
    'Content-Type': 'multipart/form-data',
    'Accept': 'application/json',
    'User-Agent': 'Lunance-App/1.0.0',
  };
  
  // HTTP Status Codes
  static const int statusOk = 200;
  static const int statusCreated = 201;
  static const int statusNoContent = 204;
  static const int statusBadRequest = 400;
  static const int statusUnauthorized = 401;
  static const int statusForbidden = 403;
  static const int statusNotFound = 404;
  static const int statusConflict = 409;
  static const int statusUnprocessableEntity = 422;
  static const int statusTooManyRequests = 429;
  static const int statusInternalServerError = 500;
  static const int statusBadGateway = 502;
  static const int statusServiceUnavailable = 503;
  
  // Error Types
  static const String validationError = 'validation_error';
  static const String authenticationError = 'authentication_error';
  static const String authorizationError = 'authorization_error';
  static const String notFoundError = 'not_found_error';
  static const String serverError = 'server_error';
  static const String networkError = 'network_error';
  static const String timeoutError = 'timeout_error';
  static const String unknownError = 'unknown_error';
  
  // Pagination Parameters
  static const String pageParam = 'page';
  static const String limitParam = 'limit';
  static const String searchParam = 'search';
  static const String sortParam = 'sort';
  static const String orderParam = 'order';
  
  // Default Values
  static const int defaultPage = 1;
  static const int defaultLimit = 10;
  static const String defaultSort = 'created_at';
  static const String defaultOrder = 'desc';
  
  // Retry Configuration
  static const int maxRetries = 3;
  static const Duration retryDelay = Duration(seconds: 1);
  static const List<int> retryableStatusCodes = [
    statusInternalServerError,
    statusBadGateway,
    statusServiceUnavailable,
  ];
  
  // Cache Configuration
  static const Duration cacheExpiry = Duration(minutes: 5);
  static const List<String> cacheableEndpoints = [
    universities,
    universityFakultas,
    fakultasProdi,
    budgetCategories,
  ];
  
  // Request Types
  enum RequestType {
    get,
    post,
    put,
    patch,
    delete,
  }
  
  // Content Types
  static const String jsonContentType = 'application/json';
  static const String formContentType = 'application/x-www-form-urlencoded';
  static const String multipartContentType = 'multipart/form-data';
  
  // Auth Token Types
  static const String bearerTokenType = 'Bearer';
  
  // Helper Methods
  static String buildUrl(String endpoint, {Map<String, dynamic>? pathParams}) {
    String url = baseUrl + endpoint;
    
    if (pathParams != null) {
      pathParams.forEach((key, value) {
        url = url.replaceAll('{$key}', value.toString());
      });
    }
    
    return url;
  }
  
  static Map<String, String> buildQueryParams({
    int? page,
    int? limit,
    String? search,
    String? sort,
    String? order,
    Map<String, dynamic>? additionalParams,
  }) {
    final params = <String, String>{};
    
    if (page != null) params[pageParam] = page.toString();
    if (limit != null) params[limitParam] = limit.toString();
    if (search != null && search.isNotEmpty) params[searchParam] = search;
    if (sort != null) params[sortParam] = sort;
    if (order != null) params[orderParam] = order;
    
    if (additionalParams != null) {
      additionalParams.forEach((key, value) {
        if (value != null) {
          params[key] = value.toString();
        }
      });
    }
    
    return params;
  }
  
  static Map<String, String> getAuthHeaders(String? token) {
    final headers = Map<String, String>.from(defaultHeaders);
    if (token != null && token.isNotEmpty) {
      headers['Authorization'] = '$bearerTokenType $token';
    }
    return headers;
  }
  
  static bool isSuccessStatusCode(int statusCode) {
    return statusCode >= 200 && statusCode < 300;
  }
  
  static bool isRetryableError(int statusCode) {
    return retryableStatusCodes.contains(statusCode);
  }
  
  static bool isCacheableEndpoint(String endpoint) {
    return cacheableEndpoints.any((cacheableEndpoint) => 
        endpoint.contains(cacheableEndpoint));
  }
}