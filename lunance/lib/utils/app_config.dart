
// lib/utils/app_config.dart
class AppConfig {
  static const bool isDebug = true;
  static const bool enableLogging = true;
  static const bool enableCrashlytics = false;
  static const bool enableAnalytics = false;
  
  // API Configuration
  static const int apiTimeoutSeconds = 30;
  static const int maxRetryAttempts = 3;
  static const int retryDelaySeconds = 2;
  
  // UI Configuration
  static const double defaultPadding = 16.0;
  static const double defaultMargin = 16.0;
  static const double defaultBorderRadius = 8.0;
  static const double cardElevation = 2.0;
  
  // Animation Configuration
  static const Duration defaultAnimationDuration = Duration(milliseconds: 300);
  static const Duration longAnimationDuration = Duration(milliseconds: 500);
  static const Duration shortAnimationDuration = Duration(milliseconds: 150);
  
  // Cache Configuration
  static const Duration cacheExpiration = Duration(hours: 1);
  static const Duration tokenRefreshThreshold = Duration(minutes: 5);
  
  // Feature Flags
  static const bool enableDarkMode = true;
  static const bool enableBiometricAuth = false;
  static const bool enableOfflineMode = false;
  static const bool enableNotifications = true;
  static const bool enableExport = true;
  static const bool enableBulkOperations = true;
  static const bool enableUniversityRequests = true;
  
  // Validation Configuration
  static const int maxFileSize = 10 * 1024 * 1024; // 10MB
  static const List<String> allowedFileTypes = ['jpg', 'jpeg', 'png', 'pdf'];
  static const int maxSearchResults = 50;
  static const int maxBulkOperations = 100;
  
  // Pagination Configuration
  static const int defaultPageSize = 20;
  static const int maxPageSize = 100;
  static const int minPageSize = 5;
  
  // Security Configuration
  static const int sessionTimeoutMinutes = 30;
  static const int maxLoginAttempts = 5;
  static const int lockoutDurationMinutes = 15;
  
  // University Configuration
  static const int maxUniversityNameLength = 150;
  static const int maxFacultyNameLength = 100;
  static const int maxMajorNameLength = 100;
  static const int minNameLength = 2;
}
