
import 'extensions.dart';
// lib/utils/validators.dart
class Validators {
  static String? validateEmail(String? value) {
    if (value == null || value.isEmpty) {
      return 'Email tidak boleh kosong';
    }
    
    if (!value.isValidEmail) {
      return 'Format email tidak valid';
    }
    
    return null;
  }
  
  static String? validateAcademicEmail(String? value) {
    if (value == null || value.isEmpty) {
      return 'Email tidak boleh kosong';
    }
    
    if (!value.isAcademicEmail) {
      return 'Harus menggunakan email akademik (.ac.id)';
    }
    
    return null;
  }
  
  static String? validatePassword(String? value) {
    if (value == null || value.isEmpty) {
      return 'Password tidak boleh kosong';
    }
    
    if (value.length < 8) {
      return 'Password minimal 8 karakter';
    }
    
    if (!value.contains(RegExp(r'[A-Z]'))) {
      return 'Password harus mengandung huruf besar';
    }
    
    if (!value.contains(RegExp(r'[a-z]'))) {
      return 'Password harus mengandung huruf kecil';
    }
    
    if (!value.contains(RegExp(r'[0-9]'))) {
      return 'Password harus mengandung angka';
    }
    
    return null;
  }
  
  static String? validateName(String? value) {
    if (value == null || value.isEmpty) {
      return 'Nama tidak boleh kosong';
    }
    
    if (value.length < 2) {
      return 'Nama minimal 2 karakter';
    }
    
    if (value.length > 50) {
      return 'Nama maksimal 50 karakter';
    }
    
    return null;
  }
  
  static String? validatePhoneNumber(String? value) {
    if (value == null || value.isEmpty) {
      return 'Nomor telepon tidak boleh kosong';
    }
    
    if (!RegExp(r'^(\+62|62|0)[0-9]{8,13}$').hasMatch(value)) {
      return 'Format nomor telepon tidak valid';
    }
    
    return null;
  }
  
  static String? validateTransactionAmount(String? value) {
    if (value == null || value.isEmpty) {
      return 'Jumlah tidak boleh kosong';
    }
    
    final amount = double.tryParse(value);
    if (amount == null) {
      return 'Jumlah harus berupa angka';
    }
    
    if (!amount.isValidAmount()) {
      return 'Jumlah tidak valid';
    }
    
    return null;
  }
  
  static String? validateTransactionDescription(String? value) {
    if (value == null || value.isEmpty) {
      return 'Deskripsi tidak boleh kosong';
    }
    
    if (value.length > 255) {
      return 'Deskripsi maksimal 255 karakter';
    }
    
    return null;
  }
  
  static String? validateCategoryName(String? value) {
    if (value == null || value.isEmpty) {
      return 'Nama kategori tidak boleh kosong';
    }
    
    if (value.length < 2 || value.length > 50) {
      return 'Nama kategori harus 2-50 karakter';
    }
    
    if (!RegExp(r'^[a-zA-Z0-9\s&-]+$').hasMatch(value)) {
      return 'Nama kategori hanya boleh mengandung huruf, angka, spasi, &, dan -';
    }
    
    return null;
  }
  
  static String? validateRequired(String? value, String fieldName) {
    if (value == null || value.isEmpty) {
      return '$fieldName tidak boleh kosong';
    }
    return null;
  }
}

// lib/utils/app_localizations.dart
class AppLocalizations {
  static const Map<String, String> id = {
    // Common
    'loading': 'Memuat...',
    'error': 'Terjadi kesalahan',
    'success': 'Berhasil',
    'cancel': 'Batal',
    'save': 'Simpan',
    'edit': 'Edit',
    'delete': 'Hapus',
    'add': 'Tambah',
    'search': 'Cari',
    'filter': 'Filter',
    'clear': 'Hapus',
    'refresh': 'Refresh',
    'retry': 'Coba Lagi',
    'close': 'Tutup',
    'confirm': 'Konfirmasi',
    'apply': 'Terapkan',
    'reset': 'Reset',
    
    // Navigation
    'dashboard': 'Dashboard',
    'transactions': 'Transaksi',
    'history': 'Riwayat',
    'categories': 'Kategori',
    'settings': 'Pengaturan',
    
    // Transaction Types
    'income': 'Pemasukan',
    'expense': 'Pengeluaran',
    'all_transactions': 'Semua Transaksi',
    
    // Time
    'today': 'Hari ini',
    'yesterday': 'Kemarin',
    'this_week': 'Minggu ini',
    'this_month': 'Bulan ini',
    'this_year': 'Tahun ini',
    
    // Months
    'january': 'Januari',
    'february': 'Februari',
    'march': 'Maret',
    'april': 'April',
    'may': 'Mei',
    'june': 'Juni',
    'july': 'Juli',
    'august': 'Agustus',
    'september': 'September',
    'october': 'Oktober',
    'november': 'November',
    'december': 'Desember',
    
    // Error Messages
    'network_error': 'Kesalahan jaringan',
    'session_expired': 'Sesi telah berakhir',
    'invalid_data': 'Data tidak valid',
    'permission_denied': 'Akses ditolak',
    'not_found': 'Data tidak ditemukan',
    'server_error': 'Kesalahan server',
    
    // Success Messages
    'transaction_created': 'Transaksi berhasil dibuat',
    'transaction_updated': 'Transaksi berhasil diperbarui',
    'transaction_deleted': 'Transaksi berhasil dihapus',
    'category_created': 'Kategori berhasil dibuat',
    'category_updated': 'Kategori berhasil diperbarui',
    'category_deleted': 'Kategori berhasil dihapus',
  };
  
  static String get(String key) {
    return id[key] ?? key;
  }
}
