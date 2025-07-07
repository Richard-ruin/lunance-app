import 'package:flutter/material.dart';

// App Constants
class AppConstants {
  // App Information
  static const String appName = 'Lunance';
  static const String appTagline = 'Manajemen Keuangan Mahasiswa Indonesia';
  static const String appDescription = 'Aplikasi untuk membantu mahasiswa mengelola keuangan dengan mudah dan efektif';
  
  // Navigation
  static const String initialRoute = '/';
  static const String loginRoute = '/login';
  static const String registerRoute = '/register';
  static const String forgotPasswordRoute = '/forgot-password';
  static const String studentRoute = '/student';
  static const String adminRoute = '/admin';
  static const String onboardingRoute = '/onboarding';
  
  // Bottom Navigation Items
  static const int dashboardIndex = 0;
  static const int historyIndex = 1;
  static const int transactionIndex = 2;
  static const int categoryIndex = 3;
  static const int settingsIndex = 4;
  
  // Animation Durations
  static const Duration shortAnimation = Duration(milliseconds: 200);
  static const Duration mediumAnimation = Duration(milliseconds: 300);
  static const Duration longAnimation = Duration(milliseconds: 500);
  
  // Delays
  static const Duration splashDelay = Duration(seconds: 2);
  static const Duration debounceDelay = Duration(milliseconds: 500);
  
  // Form Validation
  static const int minPasswordLength = 8;
  static const int maxPasswordLength = 128;
  static const int minNimLength = 8;
  static const int maxNimLength = 20;
  static const int minNameLength = 2;
  static const int maxNameLength = 100;
  
  // File Sizes (in bytes)
  static const int maxImageSize = 5 * 1024 * 1024; // 5MB
  static const int maxDocumentSize = 10 * 1024 * 1024; // 10MB
  
  // Pagination
  static const int defaultPageSize = 10;
  static const int maxPageSize = 50;
  static const int searchPageSize = 20;
  
  // Currency
  static const String currencySymbol = 'Rp';
  static const String currencyCode = 'IDR';
  static const String currencyLocale = 'id_ID';
  
  // Date Formats
  static const String dateFormat = 'dd/MM/yyyy';
  static const String timeFormat = 'HH:mm';
  static const String dateTimeFormat = 'dd/MM/yyyy HH:mm';
  static const String apiDateFormat = 'yyyy-MM-ddTHH:mm:ss.SSSZ';
  
  // Regex Patterns
  static const String emailPattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$';
  static const String phonePattern = r'^(\+62|62|0)[2-9][0-9]{7,11}$';
  static const String nimPattern = r'^[0-9]{8,20}$';
  static const String passwordPattern = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[a-zA-Z\d@$!%*?&]{8,}$';
  
  // University Email Domain
  static const String universityEmailDomain = '.ac.id';
  
  // Error Messages
  static const String networkError = 'Tidak ada koneksi internet';
  static const String serverError = 'Terjadi kesalahan server';
  static const String unknownError = 'Terjadi kesalahan tidak terduga';
  static const String timeoutError = 'Koneksi timeout, silakan coba lagi';
  static const String invalidDataError = 'Data tidak valid';
  
  // Success Messages
  static const String loginSuccess = 'Login berhasil';
  static const String registerSuccess = 'Registrasi berhasil';
  static const String logoutSuccess = 'Logout berhasil';
  static const String updateSuccess = 'Data berhasil diperbarui';
  static const String deleteSuccess = 'Data berhasil dihapus';
  static const String saveSuccess = 'Data berhasil disimpan';
  
  // General Messages
  static const String noDataFound = 'Tidak ada data ditemukan';
  static const String loadingData = 'Memuat data...';
  static const String pleaseWait = 'Mohon tunggu...';
  static const String tryAgain = 'Coba lagi';
  static const String comingSoon = 'Segera hadir';
  
  // Form Labels
  static const String emailLabel = 'Email';
  static const String passwordLabel = 'Password';
  static const String confirmPasswordLabel = 'Konfirmasi Password';
  static const String nameLabel = 'Nama Lengkap';
  static const String nimLabel = 'NIM';
  static const String universityLabel = 'Universitas';
  static const String fakultasLabel = 'Fakultas';
  static const String prodiLabel = 'Program Studi';
  
  // Validation Messages
  static const String fieldRequiredMsg = 'Field ini wajib diisi';
  static const String emailInvalidMsg = 'Format email tidak valid';
  static const String emailDomainMsg = 'Email harus menggunakan domain .ac.id';
  static const String passwordMinLengthMsg = 'Password minimal 8 karakter';
  static const String passwordPatternMsg = 'Password harus mengandung huruf besar, huruf kecil, dan angka';
  static const String passwordMismatchMsg = 'Konfirmasi password tidak cocok';
  static const String nimInvalidMsg = 'NIM harus terdiri dari 8-20 digit angka';
  static const String nameMinLengthMsg = 'Nama minimal 2 karakter';
  static const String phoneInvalidMsg = 'Format nomor telepon tidak valid';
  
  // Button Labels
  static const String loginButton = 'Masuk';
  static const String registerButton = 'Daftar';
  static const String logoutButton = 'Keluar';
  static const String saveButton = 'Simpan';
  static const String cancelButton = 'Batal';
  static const String submitButton = 'Kirim';
  static const String editButton = 'Ubah';
  static const String deleteButton = 'Hapus';
  static const String refreshButton = 'Refresh';
  static const String searchButton = 'Cari';
  static const String clearButton = 'Bersihkan';
  static const String selectButton = 'Pilih';
  static const String confirmButton = 'Konfirmasi';
  static const String backButton = 'Kembali';
  static const String nextButton = 'Selanjutnya';
  static const String skipButton = 'Lewati';
  static const String doneButton = 'Selesai';
  
  // Navigation Labels
  static const String dashboardLabel = 'Dashboard';
  static const String historyLabel = 'Riwayat';
  static const String transactionLabel = 'Transaksi';
  static const String categoryLabel = 'Kategori';
  static const String settingsLabel = 'Pengaturan';
  
  // Theme Labels
  static const String lightThemeLabel = 'Terang';
  static const String darkThemeLabel = 'Gelap';
  static const String systemThemeLabel = 'Sistem';
  
  // Settings Labels
  static const String profileSettings = 'Profil';
  static const String securitySettings = 'Keamanan';
  static const String notificationSettings = 'Notifikasi';
  static const String themeSettings = 'Tema';
  static const String languageSettings = 'Bahasa';
  static const String aboutSettings = 'Tentang';
  static const String helpSettings = 'Bantuan';
  static const String privacySettings = 'Privasi';
  static const String termsSettings = 'Syarat & Ketentuan';
  
  // Status Labels
  static const String activeStatus = 'Aktif';
  static const String inactiveStatus = 'Tidak Aktif';
  static const String pendingStatus = 'Menunggu';
  static const String approvedStatus = 'Disetujui';
  static const String rejectedStatus = 'Ditolak';
  static const String completedStatus = 'Selesai';
  static const String cancelledStatus = 'Dibatalkan';
  
  // File Types
  static const List<String> imageExtensions = ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp'];
  static const List<String> documentExtensions = ['pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx'];
  
  // Social Media URLs (if needed)
  static const String websiteUrl = 'https://lunance.app';
  static const String supportEmail = 'support@lunance.app';
  static const String privacyPolicyUrl = 'https://lunance.app/privacy';
  static const String termsOfServiceUrl = 'https://lunance.app/terms';
  
  // Firebase Collections (if using Firebase)
  static const String usersCollection = 'users';
  static const String transactionsCollection = 'transactions';
  static const String categoriesCollection = 'categories';
  static const String budgetsCollection = 'budgets';
  
  // Notification Types
  static const String transactionNotification = 'transaction';
  static const String budgetNotification = 'budget';
  static const String reminderNotification = 'reminder';
  static const String systemNotification = 'system';
  
  // Transaction Types
  static const String incomeType = 'income';
  static const String expenseType = 'expense';
  static const String transferType = 'transfer';
  
  // Budget Types
  static const String monthlyBudget = 'monthly';
  static const String weeklyBudget = 'weekly';
  static const String yearlyBudget = 'yearly';
  
  // Chart Types
  static const String pieChart = 'pie';
  static const String barChart = 'bar';
  static const String lineChart = 'line';
  static const String doughnutChart = 'doughnut';
}

// Icon Constants
class AppIcons {
  // Navigation Icons
  static const IconData dashboard = Icons.dashboard;
  static const IconData history = Icons.history;
  static const IconData transaction = Icons.add_circle_outline;
  static const IconData category = Icons.category;
  static const IconData settings = Icons.settings;
  
  // Auth Icons
  static const IconData login = Icons.login;
  static const IconData logout = Icons.logout;
  static const IconData register = Icons.person_add;
  static const IconData forgotPassword = Icons.lock_reset;
  
  // Form Icons
  static const IconData email = Icons.email;
  static const IconData password = Icons.lock;
  static const IconData person = Icons.person;
  static const IconData university = Icons.school;
  static const IconData phone = Icons.phone;
  
  // Action Icons
  static const IconData add = Icons.add;
  static const IconData edit = Icons.edit;
  static const IconData delete = Icons.delete;
  static const IconData save = Icons.save;
  static const IconData cancel = Icons.cancel;
  static const IconData search = Icons.search;
  static const IconData filter = Icons.filter_list;
  static const IconData sort = Icons.sort;
  static const IconData refresh = Icons.refresh;
  
  // Status Icons
  static const IconData success = Icons.check_circle;
  static const IconData error = Icons.error;
  static const IconData warning = Icons.warning;
  static const IconData info = Icons.info;
  static const IconData pending = Icons.hourglass_empty;
  
  // Financial Icons
  static const IconData money = Icons.attach_money;
  static const IconData wallet = Icons.account_balance_wallet;
  static const IconData income = Icons.trending_up;
  static const IconData expense = Icons.trending_down;
  static const IconData budget = Icons.pie_chart;
  static const IconData savings = Icons.savings;
  
  // Theme Icons
  static const IconData lightTheme = Icons.brightness_high;
  static const IconData darkTheme = Icons.brightness_low;
  static const IconData systemTheme = Icons.brightness_auto;
  
  // Visibility Icons
  static const IconData visibility = Icons.visibility;
  static const IconData visibilityOff = Icons.visibility_off;
  
  // Navigation Icons
  static const IconData back = Icons.arrow_back;
  static const IconData forward = Icons.arrow_forward;
  static const IconData up = Icons.keyboard_arrow_up;
  static const IconData down = Icons.keyboard_arrow_down;
  static const IconData close = Icons.close;
  
  // Menu Icons
  static const IconData menu = Icons.menu;
  static const IconData moreVert = Icons.more_vert;
  static const IconData moreHoriz = Icons.more_horiz;
  
  // Content Icons
  static const IconData image = Icons.image;
  static const IconData document = Icons.description;
  static const IconData download = Icons.download;
  static const IconData upload = Icons.upload;
  static const IconData share = Icons.share;
  
  // Communication Icons
  static const IconData notification = Icons.notifications;
  static const IconData chat = Icons.chat;
  static const IconData call = Icons.call;
  static const IconData message = Icons.message;
  
  // Time Icons
  static const IconData calendar = Icons.calendar_today;
  static const IconData time = Icons.access_time;
  static const IconData date = Icons.date_range;
  
  // Location Icons
  static const IconData location = Icons.location_on;
  static const IconData map = Icons.map;
  
  // Security Icons
  static const IconData security = Icons.security;
  static const IconData verified = Icons.verified;
  static const IconData shield = Icons.shield;
  
  // Help Icons
  static const IconData help = Icons.help;
  static const IconData support = Icons.support;
  static const IconData faq = Icons.quiz;
  
  // Social Icons
  static const IconData favorite = Icons.favorite;
  static const IconData star = Icons.star;
  static const IconData thumb_up = Icons.thumb_up;
  
  // Connectivity Icons
  static const IconData wifi = Icons.wifi;
  static const IconData offline = Icons.wifi_off;
  static const IconData sync = Icons.sync;
}

// Color Constants (in addition to theme colors)
class AppColors {
  // Status Colors
  static const Color success = Color(0xFF10B981); // Green-500
  static const Color error = Color(0xFFEF4444); // Red-500
  static const Color warning = Color(0xFFF59E0B); // Amber-500
  static const Color info = Color(0xFF3B82F6); // Blue-500
  
  // Financial Colors
  static const Color income = Color(0xFF10B981); // Green-500
  static const Color expense = Color(0xFFEF4444); // Red-500
  static const Color transfer = Color(0xFF6366F1); // Indigo-500
  static const Color budget = Color(0xFF8B5CF6); // Violet-500
  
  // Category Colors (for charts)
  static const List<Color> chartColors = [
    Color(0xFF3B82F6), // Blue
    Color(0xFF10B981), // Green
    Color(0xFFEF4444), // Red
    Color(0xFFF59E0B), // Amber
    Color(0xFF8B5CF6), // Violet
    Color(0xFFEC4899), // Pink
    Color(0xFF06B6D4), // Cyan
    Color(0xFF84CC16), // Lime
    Color(0xFFF97316), // Orange
    Color(0xFF6366F1), // Indigo
  ];
  
  // Neutral Colors
  static const Color transparent = Colors.transparent;
  static const Color white = Colors.white;
  static const Color black = Colors.black;
  
  // Overlay Colors
  static const Color overlay = Color(0x80000000); // Black with 50% opacity
  static const Color lightOverlay = Color(0x40000000); // Black with 25% opacity
}