// lib/core/constants/app_constants.dart
class AppConstants {
  // App Info
  static const String appName = 'Lunance';
  static const String appVersion = '1.0.0';
  static const String appDescription = 'Kelola Keuangan Mahasiswa dengan Mudah';
  
  // Storage Keys
  static const String accessTokenKey = 'access_token';
  static const String refreshTokenKey = 'refresh_token';
  static const String userDataKey = 'user_data';
  static const String isFirstLaunchKey = 'is_first_launch';
  static const String themeKey = 'theme_mode';
  static const String languageKey = 'language';
  
  // OTP Types
  static const String otpRegistration = 'registration';
  static const String otpForgotPassword = 'forgot_password';
  static const String otpEmailVerification = 'email_verification';
  
  // Transaction Types
  static const String incomeType = 'income';
  static const String expenseType = 'expense';
  
  // Categories
  static const List<String> defaultIncomeCategories = [
    'Uang Jajan',
    'Beasiswa',
    'Part Time',
    'Freelance',
    'Lainnya',
  ];
  
  static const List<String> defaultExpenseCategories = [
    'Makanan',
    'Transportasi',
    'Buku & Alat Tulis',
    'Hiburan',
    'Kesehatan',
    'Pakaian',
    'Internet',
    'Lainnya',
  ];
  
  // Timeout Settings
  static const int connectionTimeoutSeconds = 30;
  static const int receiveTimeoutSeconds = 30;
  
  // Validation
  static const int minPasswordLength = 8;
  static const int maxPasswordLength = 128;
  static const int otpLength = 6;
  static const int otpExpiryMinutes = 10;
  
  // File Upload
  static const int maxFileSize = 5 * 1024 * 1024; // 5MB
  static const List<String> allowedImageFormats = ['jpg', 'jpeg', 'png'];
  
  // Indonesian Universities (sample)
  static const List<String> popularUniversities = [
    'Universitas Logistik dan Bisnis Internasional'
    'Universitas Indonesia',
    'Institut Teknologi Bandung',
    'Universitas Gadjah Mada',
    'Institut Teknologi Sepuluh Nopember',
    'Universitas Brawijaya',
    'Universitas Diponegoro',
    'Universitas Padjadjaran',
    'Universitas Airlangga',
    'Universitas Sebelas Maret',
    'Universitas Negeri Yogyakarta',
    'Institut Pertanian Bogor',
    'Universitas Hasanuddin',
    'Universitas Andalas',
    'Universitas Sumatera Utara',
    'Universitas Lampung',
  ];
}
