// lib/core/constants/api_endpoints.dart
class ApiEndpoints {
  // Base URL - should be loaded from environment
  static const String baseUrl = 'http://192.168.190.195:8000';
  static const String apiVersion = '/api/v1';
  
  // Auth endpoints
  static const String login = '$baseUrl$apiVersion/login';
  static const String register = '$baseUrl$apiVersion/register';
  static const String logout = '$baseUrl$apiVersion/logout';
  static const String forgotPassword = '$baseUrl$apiVersion/forgot-password';
  static const String verifyOtp = '$baseUrl$apiVersion/verify-otp';
  static const String resetPassword = '$baseUrl$apiVersion/reset-password';
  static const String requestOtp = '$baseUrl$apiVersion/request-otp';
  static const String me = '$baseUrl$apiVersion/me';
  static const String refreshToken = '$baseUrl$apiVersion/refresh';
  
  // Student endpoints
  static const String students = '$baseUrl$apiVersion/students';
  static const String myProfile = '$baseUrl$apiVersion/students/me';
  static const String updateProfile = '$baseUrl$apiVersion/students/me/profile';
  static const String uploadProfilePicture = '$baseUrl$apiVersion/students/me/profile-picture';
  
  // Transaction endpoints
  static const String transactions = '$baseUrl$apiVersion/transactions';
  static const String addTransaction = '$baseUrl$apiVersion/transactions';
  
  // Category endpoints
  static const String categories = '$baseUrl$apiVersion/categories';
  
  // Analytics endpoints
  static const String analytics = '$baseUrl$apiVersion/analytics';
  
  // Dashboard endpoints
  static const String dashboard = '$baseUrl$apiVersion/dashboard';
  
  // Health check
  static const String health = '$baseUrl/health';
}
