// lib/utils/constants.dart
class AppConstants {
  // API Configuration
  static const String baseUrl = 'http://192.168.101.5:8000';
  static const String apiVersion = '/api/v1';
  static const String authBaseUrl = '$baseUrl$apiVersion/auth';
  static const String categoriesBaseUrl = '$baseUrl$apiVersion/categories';
  static const String universitiesBaseUrl = '$baseUrl$apiVersion/universities';
  static const String transactionsBaseUrl = '$baseUrl$apiVersion/transactions';
  static const String universityRequestsBaseUrl = '$baseUrl$apiVersion/university-requests';
  
  // Storage Keys
  static const String accessTokenKey = 'access_token';
  static const String refreshTokenKey = 'refresh_token';
  static const String userDataKey = 'user_data';
  static const String themePreferenceKey = 'theme_preference';
  
  // App Configuration
  static const String appName = 'Lunance';
  static const String appVersion = '1.0.0';
  
  // Animation Durations
  static const Duration splashDuration = Duration(seconds: 3);
  static const Duration fadeAnimationDuration = Duration(milliseconds: 300);
  
  // Email Validation
  static const String academicEmailSuffix = '.ac.id';
  
  // Password Requirements
  static const int minPasswordLength = 8;
  
  // OTP Configuration
  static const int otpLength = 6;
  static const Duration otpExpiryDuration = Duration(minutes: 5);
  
  // Transaction Configuration
  static const double maxTransactionAmount = 999999999.99;
  static const int maxDescriptionLength = 255;
  static const int maxCategoryNameLength = 50;
  
  // Pagination
  static const int defaultPageSize = 20;
  static const int maxPageSize = 100;
  
  // Date Formats
  static const String dateFormat = 'yyyy-MM-dd';
  static const String displayDateFormat = 'dd/MM/yyyy';
  static const String displayDateTimeFormat = 'dd/MM/yyyy HH:mm';
  
  // Colors for categories (hex format)
  static const List<String> categoryColors = [
    '#3B82F6', '#EF4444', '#10B981', '#F59E0B',
    '#8B5CF6', '#EC4899', '#06B6D4', '#84CC16',
    '#F97316', '#6366F1', '#14B8A6', '#DC2626',
    '#9CA3AF', '#1F2937', '#7C3AED', '#059669',
  ];
  
  // Default icons for categories
  static const List<String> categoryIcons = [
    'restaurant', 'directions_car', 'school', 'local_hospital',
    'movie', 'shopping_cart', 'receipt', 'account_balance',
    'work', 'trending_up', 'home', 'flight',
    'phone', 'fitness_center', 'pets', 'gamepad',
  ];
  
  // University related constants
  static const int maxUniversityNameLength = 150;
  static const int maxFacultyNameLength = 100;
  static const int maxMajorNameLength = 100;
  
  // Request timeout durations
  static const Duration shortTimeout = Duration(seconds: 10);
  static const Duration mediumTimeout = Duration(seconds: 15);
  static const Duration longTimeout = Duration(seconds: 30);
}