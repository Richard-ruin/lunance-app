class ApiConfig {
  // Base URLs
  static const String _devBaseUrl = 'http://192.168.190.195:8000/api/v1';
  static const String _prodBaseUrl = 'https://api.lunance.app/api/v1';
  
  // Current environment base URL
  static String get baseUrl => _getBaseUrl();
  
  static String _getBaseUrl() {
    const bool isProduction = bool.fromEnvironment('dart.vm.product');
    return isProduction ? _prodBaseUrl : _devBaseUrl;
  }
  
  // Auth Endpoints
  static const String loginEndpoint = '/auth/login';
  static const String logoutEndpoint = '/auth/logout';
  static const String profileEndpoint = '/auth/me';
  static const String refreshTokenEndpoint = '/auth/refresh';
  static const String forgotPasswordEndpoint = '/auth/forgot-password';
  static const String resetPasswordEndpoint = '/auth/reset-password';
  static const String changePasswordEndpoint = '/auth/change-password';
  static const String checkEmailEndpoint = '/auth/check-email';
  
  // Multi-step Registration Endpoints - Updated sesuai dengan API spec
  static const String registerStep1Endpoint = '/auth/register/step1';
  static const String registerStep2Endpoint = '/auth/register/step2';
  static const String registerStep3Endpoint = '/auth/register/step3';
  static const String registerStep4Endpoint = '/auth/register/step4';
  static const String registerStep5Endpoint = '/auth/register/step5';
  static const String verifyOtpEndpoint = '/auth/verify-otp';
  
  // University Endpoints
  static const String universitiesEndpoint = '/universities';
  static const String universityDetailEndpoint = '/universities/{id}';
  static const String universityFakultasEndpoint = '/universities/{id}/fakultas';
  static const String fakultasProdiEndpoint = '/universities/fakultas/{id}/prodi';
  static const String universityRequestEndpoint = '/universities/request';
  static const String universitySearchEndpoint = '/universities/search';
  
  // Admin Endpoints
  static const String adminUniversityRequestsEndpoint = '/admin/university-requests';
  static const String adminUniversityRequestDetailEndpoint = '/admin/university-requests/{id}';
  static const String adminApproveRequestEndpoint = '/admin/university-requests/{id}/approve';
  static const String adminRejectRequestEndpoint = '/admin/university-requests/{id}/reject';
  static const String adminStatisticsEndpoint = '/admin/statistics';
  
  // Health Check
  static const String healthCheckEndpoint = '/health';
  static const String rootEndpoint = '/';
  
  // HTTP Headers
  static const String contentTypeHeader = 'Content-Type';
  static const String authorizationHeader = 'Authorization';
  static const String acceptHeader = 'Accept';
  static const String userAgentHeader = 'User-Agent';
  
  // Header Values
  static const String jsonContentType = 'application/json';
  static const String bearerPrefix = 'Bearer ';
  static const String acceptJson = 'application/json';
  static const String userAgent = 'Lunance-Flutter/1.0.0';
  
  // HTTP Status Codes
  static const int successOk = 200;
  static const int successCreated = 201;
  static const int successNoContent = 204;
  static const int badRequest = 400;
  static const int unauthorized = 401;
  static const int forbidden = 403;
  static const int notFound = 404;
  static const int conflict = 409;
  static const int unprocessableEntity = 422;
  static const int tooManyRequests = 429;
  static const int internalServerError = 500;
  static const int badGateway = 502;
  static const int serviceUnavailable = 503;
  
  // Request Parameters
  static const String pageParam = 'page';
  static const String limitParam = 'limit';
  static const String searchParam = 'q';
  static const String sortParam = 'sort';
  static const String orderParam = 'order';
  
  // Helper methods
  static String buildUrl(String endpoint, [Map<String, String>? pathParams]) {
    String url = baseUrl + endpoint;
    
    if (pathParams != null) {
      pathParams.forEach((key, value) {
        url = url.replaceAll('{$key}', value);
      });
    }
    
    return url;
  }
  
  static String buildQueryString(Map<String, dynamic> params) {
    if (params.isEmpty) return '';
    
    final queryParams = params.entries
        .where((entry) => entry.value != null)
        .map((entry) => '${entry.key}=${Uri.encodeComponent(entry.value.toString())}')
        .join('&');
    
    return queryParams.isNotEmpty ? '?$queryParams' : '';
  }
  
  static Map<String, String> get defaultHeaders => {
    contentTypeHeader: jsonContentType,
    acceptHeader: acceptJson,
    userAgentHeader: userAgent,
  };
}