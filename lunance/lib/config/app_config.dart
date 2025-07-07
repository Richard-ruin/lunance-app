class AppConfig {
  static const String appName = 'Lunance';
  static const String appVersion = '1.0.0';
  static const String appDescription = 'Aplikasi manajemen keuangan mahasiswa Indonesia';
  
  // Environment
  static const bool isProduction = bool.fromEnvironment('dart.vm.product');
  static const bool isDevelopment = !isProduction;
  
  // Storage Keys
  static const String authTokenKey = 'lunance_auth_token';
  static const String userDataKey = 'lunance_user_data';
  static const String themeKey = 'lunance_theme_mode';
  static const String languageKey = 'lunance_language';
  static const String onboardingKey = 'lunance_onboarding_shown';
  
  // Pagination
  static const int defaultPageSize = 10;
  static const int maxPageSize = 50;
  
  // Timeouts (in seconds)
  static const int apiTimeout = 30;
  static const int connectionTimeout = 10;
  static const int receiveTimeout = 30;
  
  // Validation Rules
  static const int minPasswordLength = 8;
  static const int maxPasswordLength = 128;
  static const int minNameLength = 2;      // Added missing property
  static const int maxNameLength = 100;    // Added missing property
  static const int minNimLength = 8;
  static const int maxNimLength = 20;
  
  // University Email Domain
  static const String requiredEmailDomain = '.ac.id';
  
  // Date Format
  static const String dateFormat = 'dd/MM/yyyy';
  static const String timeFormat = 'HH:mm';
  static const String dateTimeFormat = 'dd/MM/yyyy HH:mm';
  
  // Currency
  static const String currencySymbol = 'Rp';
  static const String currencyLocale = 'id_ID';
  
  // Assets
  static const String logoPath = 'assets/images/logo.png';
  static const String defaultAvatarPath = 'assets/images/default_avatar.png';
  
  // Navigation
  static const Duration navigationAnimationDuration = Duration(milliseconds: 300);
  
  // Refresh Intervals (in seconds)
  static const int dashboardRefreshInterval = 300; // 5 minutes
  static const int balanceRefreshInterval = 60; // 1 minute
}