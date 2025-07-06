import 'package:flutter/material.dart';

// App Routes
class Routes {
  static const String splash = '/';
  static const String login = '/login';
  static const String register = '/register';
  static const String forgotPassword = '/forgot-password';
  static const String resetPassword = '/reset-password';
  static const String studentMain = '/student';
  static const String adminMain = '/admin';
  static const String profile = '/profile';
  static const String settings = '/settings';
  static const String universityRequest = '/university-request';
  static const String universityDetail = '/university-detail';
  static const String notifications = '/notifications';
}

// User Roles
enum UserRole {
  student('student', 'Mahasiswa'),
  admin('admin', 'Admin');

  const UserRole(this.value, this.displayName);
  final String value;
  final String displayName;
}

// Theme Modes
enum AppThemeMode {
  light('light', 'Terang', Icons.light_mode),
  dark('dark', 'Gelap', Icons.dark_mode),
  system('system', 'Sistem', Icons.auto_mode);

  const AppThemeMode(this.value, this.displayName, this.icon);
  final String value;
  final String displayName;
  final IconData icon;
}

// Languages
enum AppLanguage {
  indonesian('id', 'ID', 'Bahasa Indonesia'),
  english('en', 'US', 'English');

  const AppLanguage(this.languageCode, this.countryCode, this.displayName);
  final String languageCode;
  final String countryCode;
  final String displayName;

  String get locale => '${languageCode}_$countryCode';
}

// University Request Status
enum UniversityRequestStatus {
  pending('pending', 'Menunggu', Colors.orange),
  approved('approved', 'Disetujui', Colors.green),
  rejected('rejected', 'Ditolak', Colors.red);

  const UniversityRequestStatus(this.value, this.displayName, this.color);
  final String value;
  final String displayName;
  final Color color;
}

// Degree Types
enum DegreeType {
  d3('D3', 'Diploma 3'),
  d4('D4', 'Diploma 4'),
  s1('S1', 'Sarjana'),
  s2('S2', 'Magister'),
  s3('S3', 'Doktor');

  const DegreeType(this.value, this.displayName);
  final String value;
  final String displayName;
}

// Accreditation Types
enum AccreditationType {
  a('A', 'A'),
  b('B', 'B'),
  c('C', 'C'),
  unggul('Unggul', 'Unggul'),
  baikSekali('Baik Sekali', 'Baik Sekali'),
  baik('Baik', 'Baik');

  const AccreditationType(this.value, this.displayName);
  final String value;
  final String displayName;
}

// Financial Categories (Future Implementation)
enum FinancialCategory {
  food('food', 'Makanan & Minuman', Icons.restaurant, Color(0xFF4CAF50)),
  transport('transport', 'Transportasi', Icons.directions_car, Color(0xFF2196F3)),
  education('education', 'Pendidikan', Icons.school, Color(0xFF9C27B0)),
  entertainment('entertainment', 'Hiburan', Icons.movie, Color(0xFFFF5722)),
  shopping('shopping', 'Belanja', Icons.shopping_bag, Color(0xFFE91E63)),
  health('health', 'Kesehatan', Icons.local_hospital, Color(0xFFF44336)),
  bills('bills', 'Tagihan', Icons.receipt, Color(0xFF607D8B)),
  savings('savings', 'Tabungan', Icons.savings, Color(0xFF8BC34A)),
  other('other', 'Lainnya', Icons.more_horiz, Color(0xFF9E9E9E));

  const FinancialCategory(this.value, this.displayName, this.icon, this.color);
  final String value;
  final String displayName;
  final IconData icon;
  final Color color;
}

// Transaction Types (Future Implementation)
enum TransactionType {
  income('income', 'Pemasukan', Icons.arrow_upward, Color(0xFF4CAF50)),
  expense('expense', 'Pengeluaran', Icons.arrow_downward, Color(0xFFF44336)),
  transfer('transfer', 'Transfer', Icons.swap_horiz, Color(0xFF2196F3));

  const TransactionType(this.value, this.displayName, this.icon, this.color);
  final String value;
  final String displayName;
  final IconData icon;
  final Color color;
}

// Navigation Items for Students
enum StudentNavigation {
  dashboard(0, 'Dashboard', Icons.dashboard, 'dashboard'),
  transactions(1, 'Transaksi', Icons.receipt_long, 'transactions'),
  budget(2, 'Anggaran', Icons.account_balance_wallet, 'budget'),
  reports(3, 'Laporan', Icons.analytics, 'reports'),
  profile(4, 'Profil', Icons.person, 'profile');

  const StudentNavigation(this.index, this.label, this.icon, this.route);
  final int index;
  final String label;
  final IconData icon;
  final String route;
}

// Navigation Items for Admin
enum AdminNavigation {
  dashboard(0, 'Dashboard', Icons.dashboard, 'dashboard'),
  universities(1, 'Universitas', Icons.school, 'universities'),
  requests(2, 'Permintaan', Icons.pending_actions, 'requests'),
  users(3, 'Pengguna', Icons.people, 'users'),
  settings(4, 'Pengaturan', Icons.settings, 'settings');

  const AdminNavigation(this.index, this.label, this.icon, this.route);
  final int index;
  final String label;
  final IconData icon;
  final String route;
}

// Validation Patterns
class ValidationPatterns {
  static const String email = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$';
  static const String academicEmail = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.ac\.id$';
  static const String nim = r'^[0-9]{8,20}$';
  static const String phone = r'^(\+62|62|0)[0-9]{8,13}$';
  static const String password = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$';
  static const String universityCode = r'^[A-Z]{2,10}$';
  static const String facultyCode = r'^[A-Z]{2,10}$';
  static const String prodiCode = r'^[A-Z]{2,10}$';
}

// Error Messages
class ErrorMessages {
  // Network Errors
  static const String networkError = 'Tidak ada koneksi internet';
  static const String timeoutError = 'Koneksi timeout';
  static const String serverError = 'Terjadi kesalahan server';
  static const String unknownError = 'Terjadi kesalahan tidak dikenal';
  
  // Authentication Errors
  static const String invalidCredentials = 'Email atau password salah';
  static const String accountNotFound = 'Akun tidak ditemukan';
  static const String accountDisabled = 'Akun telah dinonaktifkan';
  static const String sessionExpired = 'Sesi telah berakhir';
  static const String unauthorizedAccess = 'Akses tidak diizinkan';
  
  // Validation Errors
  static const String emailRequired = 'Email wajib diisi';
  static const String emailInvalid = 'Format email tidak valid';
  static const String emailAcademicRequired = 'Gunakan email akademik (.ac.id)';
  static const String passwordRequired = 'Password wajib diisi';
  static const String passwordTooShort = 'Password minimal 8 karakter';
  static const String passwordWeak = 'Password harus mengandung huruf besar, kecil, angka, dan simbol';
  static const String passwordMismatch = 'Password tidak sama';
  static const String nimRequired = 'NIM wajib diisi';
  static const String nimInvalid = 'NIM harus 8-20 digit angka';
  static const String nameRequired = 'Nama wajib diisi';
  static const String universityRequired = 'Universitas wajib dipilih';
  static const String facultyRequired = 'Fakultas wajib dipilih';
  static const String prodiRequired = 'Program studi wajib dipilih';
  
  // Data Errors
  static const String dataNotFound = 'Data tidak ditemukan';
  static const String dataAlreadyExists = 'Data sudah ada';
  static const String dataInvalid = 'Data tidak valid';
  static const String dataCorrupted = 'Data rusak atau tidak dapat dibaca';
  
  // File Errors
  static const String fileRequired = 'File wajib dipilih';
  static const String fileTooLarge = 'Ukuran file terlalu besar';
  static const String fileTypeNotSupported = 'Tipe file tidak didukung';
  static const String fileUploadFailed = 'Gagal mengunggah file';
}

// Success Messages
class SuccessMessages {
  static const String loginSuccess = 'Berhasil masuk';
  static const String logoutSuccess = 'Berhasil keluar';
  static const String registerSuccess = 'Pendaftaran berhasil';
  static const String updateSuccess = 'Data berhasil diperbarui';
  static const String deleteSuccess = 'Data berhasil dihapus';
  static const String createSuccess = 'Data berhasil dibuat';
  static const String saveSuccess = 'Data berhasil disimpan';
  static const String requestSubmitted = 'Permintaan berhasil dikirim';
  static const String requestApproved = 'Permintaan berhasil disetujui';
  static const String requestRejected = 'Permintaan berhasil ditolak';
  static const String passwordChanged = 'Password berhasil diubah';
  static const String emailVerified = 'Email berhasil diverifikasi';
  static const String dataImported = 'Data berhasil diimpor';
  static const String dataExported = 'Data berhasil diekspor';
}

// Loading Messages
class LoadingMessages {
  static const String loading = 'Memuat...';
  static const String loggingIn = 'Sedang masuk...';
  static const String registering = 'Sedang mendaftar...';
  static const String saving = 'Sedang menyimpan...';
  static const String deleting = 'Sedang menghapus...';
  static const String uploading = 'Sedang mengunggah...';
  static const String downloading = 'Sedang mengunduh...';
  static const String processing = 'Sedang memproses...';
  static const String synchronizing = 'Sedang sinkronisasi...';
  static const String connecting = 'Sedang menghubungkan...';
  static const String loadingData = 'Memuat data...';
}

// Storage Keys
class StorageKeys {
  static const String accessToken = 'access_token';
  static const String refreshToken = 'refresh_token';
  static const String userProfile = 'user_profile';
  static const String themeMode = 'theme_mode';
  static const String language = 'language';
  static const String biometricEnabled = 'biometric_enabled';
  static const String onboardingCompleted = 'onboarding_completed';
  static const String lastSyncTime = 'last_sync_time';
  static const String cacheData = 'cache_data';
  static const String notificationEnabled = 'notification_enabled';
  static const String autoSyncEnabled = 'auto_sync_enabled';
}

// Animation Durations
class AnimationDurations {
  static const Duration fast = Duration(milliseconds: 150);
  static const Duration normal = Duration(milliseconds: 300);
  static const Duration slow = Duration(milliseconds: 500);
  static const Duration page = Duration(milliseconds: 250);
  static const Duration fade = Duration(milliseconds: 200);
  static const Duration slide = Duration(milliseconds: 300);
  static const Duration scale = Duration(milliseconds: 200);
  static const Duration rotate = Duration(milliseconds: 400);
}

// Spacing Constants
class Spacing {
  static const double xs = 4.0;
  static const double sm = 8.0;
  static const double md = 16.0;
  static const double lg = 24.0;
  static const double xl = 32.0;
  static const double xxl = 48.0;
}

// Border Radius Constants
class BorderRadiusValues {
  static const double xs = 4.0;
  static const double sm = 8.0;
  static const double md = 12.0;
  static const double lg = 16.0;
  static const double xl = 24.0;
  static const double circular = 9999.0;
}

// Icon Sizes
class IconSizes {
  static const double xs = 12.0;
  static const double sm = 16.0;
  static const double md = 24.0;
  static const double lg = 32.0;
  static const double xl = 48.0;
  static const double xxl = 64.0;
}

// University Status
enum UniversityStatus {
  active('active', 'Aktif', Colors.green),
  inactive('inactive', 'Tidak Aktif', Colors.red);

  const UniversityStatus(this.value, this.displayName, this.color);
  final String value;
  final String displayName;
  final Color color;
}

// Priority Levels
enum Priority {
  low('low', 'Rendah', Colors.green),
  medium('medium', 'Sedang', Colors.orange),
  high('high', 'Tinggi', Colors.red);

  const Priority(this.value, this.displayName, this.color);
  final String value;
  final String displayName;
  final Color color;
}

// Date Format Patterns
class DateFormats {
  static const String dateOnly = 'dd/MM/yyyy';
  static const String timeOnly = 'HH:mm';
  static const String dateTime = 'dd/MM/yyyy HH:mm';
  static const String dateTimeWithSeconds = 'dd/MM/yyyy HH:mm:ss';
  static const String apiDateTime = "yyyy-MM-dd'T'HH:mm:ss.SSS'Z'";
  static const String displayDate = 'dd MMMM yyyy';
  static const String displayDateTime = 'dd MMMM yyyy, HH:mm';
  static const String monthYear = 'MMMM yyyy';
  static const String dayMonthYear = 'EEEE, dd MMMM yyyy';
}

// Currency Format
class CurrencyFormat {
  static const String symbol = 'Rp';
  static const String locale = 'id_ID';
  static const int decimalDigits = 0;
  static const String thousandSeparator = '.';
  static const String decimalSeparator = ',';
}