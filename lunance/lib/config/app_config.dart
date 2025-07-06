class AppConfig {
  // App Information
  static const String appName = 'Lunance';
  static const String appVersion = '1.0.0';
  static const String appDescription = 'Aplikasi Manajemen Keuangan Mahasiswa Indonesia';
  
  // Environment Configuration
  static const bool isProduction = bool.fromEnvironment('dart.vm.product');
  static const bool isDebug = !isProduction;
  
  // API Configuration
  static const String devApiUrl = 'http://localhost:8000/api/v1';
  static const String prodApiUrl = 'https://api.lunance.app/api/v1';
  
  static String get apiUrl => isProduction ? prodApiUrl : devApiUrl;
  
  // WebSocket Configuration
  static const String devWsUrl = 'ws://localhost:8000/ws';
  static const String prodWsUrl = 'wss://api.lunance.app/ws';
  
  static String get wsUrl => isProduction ? prodWsUrl : devWsUrl;
  
  // Timeout Configuration
  static const Duration apiTimeout = Duration(seconds: 30);
  static const Duration uploadTimeout = Duration(minutes: 5);
  static const Duration websocketTimeout = Duration(seconds: 10);
  
  // Pagination Configuration
  static const int defaultPageSize = 10;
  static const int maxPageSize = 50;
  
  // Cache Configuration
  static const Duration cacheExpiry = Duration(hours: 1);
  static const int maxCacheSize = 100; // MB
  
  // Local Storage Keys
  static const String tokenKey = 'lunance_token';
  static const String refreshTokenKey = 'lunance_refresh_token';
  static const String userKey = 'lunance_user';
  static const String themeKey = 'lunance_theme';
  static const String languageKey = 'lunance_language';
  static const String onboardingKey = 'lunance_onboarding_completed';
  static const String biometricKey = 'lunance_biometric_enabled';
  
  // Hive Box Names
  static const String userBox = 'user_box';
  static const String settingsBox = 'settings_box';
  static const String cacheBox = 'cache_box';
  static const String universityBox = 'university_box';
  
  // Feature Flags
  static const bool enableBiometric = true;
  static const bool enableDarkMode = true;
  static const bool enableNotifications = true;
  static const bool enableWebSocket = true;
  static const bool enableOfflineMode = true;
  
  // Validation Rules
  static const int minPasswordLength = 8;
  static const int maxPasswordLength = 128;
  static const int minNimLength = 8;
  static const int maxNimLength = 20;
  static const String emailDomain = '.ac.id';
  
  // File Upload Configuration
  static const int maxFileSize = 5 * 1024 * 1024; // 5MB
  static const List<String> allowedImageTypes = ['jpg', 'jpeg', 'png', 'webp'];
  static const List<String> allowedDocumentTypes = ['pdf', 'doc', 'docx'];
  
  // Currency Configuration
  static const String defaultCurrency = 'IDR';
  static const String currencySymbol = 'Rp';
  static const String currencyLocale = 'id_ID';
  
  // Date Format Configuration
  static const String dateFormat = 'dd/MM/yyyy';
  static const String timeFormat = 'HH:mm';
  static const String dateTimeFormat = 'dd/MM/yyyy HH:mm';
  
  // Animation Configuration
  static const Duration shortAnimationDuration = Duration(milliseconds: 200);
  static const Duration mediumAnimationDuration = Duration(milliseconds: 300);
  static const Duration longAnimationDuration = Duration(milliseconds: 500);
  
  // UI Configuration
  static const double defaultPadding = 16.0;
  static const double smallPadding = 8.0;
  static const double largePadding = 24.0;
  static const double defaultBorderRadius = 12.0;
  static const double smallBorderRadius = 8.0;
  static const double largeBorderRadius = 16.0;
  
  // Error Messages
  static const String networkErrorMessage = 'Koneksi internet bermasalah. Silakan coba lagi.';
  static const String serverErrorMessage = 'Terjadi kesalahan server. Silakan coba lagi nanti.';
  static const String unknownErrorMessage = 'Terjadi kesalahan tidak dikenal. Silakan coba lagi.';
  static const String timeoutErrorMessage = 'Koneksi timeout. Silakan periksa koneksi internet Anda.';
  
  // Success Messages
  static const String loginSuccessMessage = 'Berhasil masuk ke akun Anda';
  static const String logoutSuccessMessage = 'Berhasil keluar dari akun';
  static const String registrationSuccessMessage = 'Pendaftaran berhasil. Silakan masuk ke akun Anda.';
  static const String updateSuccessMessage = 'Data berhasil diperbarui';
  static const String deleteSuccessMessage = 'Data berhasil dihapus';
  
  // University Configuration
  static const List<String> supportedUniversityTypes = [
    'Negeri',
    'Swasta',
    'Kedinasan',
    'Asing'
  ];
  
  static const List<String> supportedDegreeTypes = [
    'D3',
    'D4', 
    'S1',
    'S2',
    'S3'
  ];
  
  static const List<String> supportedAccreditations = [
    'A',
    'B',
    'C',
    'Unggul',
    'Baik Sekali',
    'Baik'
  ];
  
  // Contact Information
  static const String supportEmail = 'support@lunance.app';
  static const String feedbackEmail = 'feedback@lunance.app';
  static const String privacyPolicyUrl = 'https://lunance.app/privacy';
  static const String termsOfServiceUrl = 'https://lunance.app/terms';
  static const String helpUrl = 'https://help.lunance.app';
}