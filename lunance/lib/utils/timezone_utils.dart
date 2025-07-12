// lib/utils/timezone_utils.dart
import 'package:intl/intl.dart';
import 'package:intl/date_symbol_data_local.dart';

class IndonesiaTimeHelper {
  // Indonesia timezone offset (WIB = UTC+7)
  static const int timezoneOffsetHours = 7;
  
  // Flag untuk tracking initialization
  static bool _isInitialized = false;
  
  /// Initialize locale data - panggil di main.dart
  static Future<void> initialize() async {
    if (!_isInitialized) {
      try {
        // Initialize Indonesian locale
        await initializeDateFormatting('id_ID', null);
        _isInitialized = true;
        print('✅ Indonesian timezone and locale initialized successfully');
      } catch (e) {
        print('⚠️ Failed to initialize Indonesian locale: $e');
        // Try fallback initialization
        try {
          await initializeDateFormatting('en_US', null);
          _isInitialized = true;
          print('✅ Fallback locale (en_US) initialized');
        } catch (fallbackError) {
          print('⚠️ Fallback locale also failed: $fallbackError');
          print('🔄 Using manual formatting as ultimate fallback');
          _isInitialized = true; // Set true anyway untuk avoid infinite loops
        }
      }
    }
  }
  
  /// Get current DateTime in Indonesia timezone
  static DateTime now() {
    final utcNow = DateTime.now().toUtc();
    return utcNow.add(const Duration(hours: timezoneOffsetHours));
  }
  
  /// Convert UTC DateTime to Indonesia time
  static DateTime fromUtc(DateTime utcDateTime) {
    if (utcDateTime.isUtc) {
      return utcDateTime.add(const Duration(hours: timezoneOffsetHours));
    } else {
      // Assume it's already in UTC if not specified
      return utcDateTime.toUtc().add(const Duration(hours: timezoneOffsetHours));
    }
  }
  
  /// Convert Indonesia DateTime to UTC
  static DateTime toUtc(DateTime indonesiaDateTime) {
    return indonesiaDateTime.subtract(const Duration(hours: timezoneOffsetHours)).toUtc();
  }
  
  /// Parse ISO string from backend (assumed to be UTC) to Indonesia time
  static DateTime parseFromBackend(String isoString) {
    try {
      final utcDateTime = DateTime.parse(isoString);
      return fromUtc(utcDateTime);
    } catch (e) {
      print('⚠️ Failed to parse datetime: $isoString, error: $e');
      return now(); // Fallback to current time
    }
  }
  
  /// Format DateTime for display in Indonesia dengan multiple fallbacks
  static String format(DateTime dateTime, {String pattern = 'dd/MM/yyyy HH:mm'}) {
    // Ensure we're working with Indonesia time
    final indonesiaTime = dateTime.isUtc ? fromUtc(dateTime) : dateTime;
    
    try {
      // Try dengan locale Indonesia jika sudah diinisialisasi
      if (_isInitialized) {
        final formatter = DateFormat(pattern, 'id_ID');
        return formatter.format(indonesiaTime);
      } else {
        // Fallback tanpa locale
        final formatter = DateFormat(pattern);
        return formatter.format(indonesiaTime);
      }
    } catch (localeError) {
      try {
        // Try dengan locale default
        final formatter = DateFormat(pattern);
        return formatter.format(indonesiaTime);
      } catch (formatterError) {
        // Ultimate fallback - manual formatting
        return _manualFormat(indonesiaTime, pattern);
      }
    }
  }
  
  /// Manual formatting sebagai ultimate fallback
  static String _manualFormat(DateTime dateTime, String pattern) {
    try {
      final day = dateTime.day.toString().padLeft(2, '0');
      final month = dateTime.month.toString().padLeft(2, '0');
      final year = dateTime.year.toString();
      final hour = dateTime.hour.toString().padLeft(2, '0');
      final minute = dateTime.minute.toString().padLeft(2, '0');
      final second = dateTime.second.toString().padLeft(2, '0');
      
      // Simple pattern matching
      if (pattern.contains('dd/MM/yyyy HH:mm:ss')) {
        return '$day/$month/$year $hour:$minute:$second';
      } else if (pattern.contains('dd/MM/yyyy HH:mm')) {
        return '$day/$month/$year $hour:$minute';
      } else if (pattern.contains('HH:mm:ss')) {
        return '$hour:$minute:$second';
      } else if (pattern.contains('HH:mm')) {
        return '$hour:$minute';
      } else if (pattern.contains('dd/MM/yyyy')) {
        return '$day/$month/$year';
      } else if (pattern.contains('dd/MM/yy')) {
        final shortYear = year.substring(2);
        return '$day/$month/$shortYear';
      } else if (pattern.contains('dd/MM HH:mm')) {
        return '$day/$month $hour:$minute';
      }
      
      // Default fallback
      return '$day/$month/$year $hour:$minute';
    } catch (e) {
      // Ultimate ultimate fallback
      return dateTime.toString().substring(0, 16); // YYYY-MM-DD HH:MM
    }
  }
  
  /// Format time only (HH:mm) dengan fallback
  static String formatTimeOnly(DateTime dateTime) {
    return format(dateTime, pattern: 'HH:mm');
  }
  
  /// Format date only (dd/MM/yyyy) dengan fallback
  static String formatDateOnly(DateTime dateTime) {
    return format(dateTime, pattern: 'dd/MM/yyyy');
  }
  
  /// Format relative time (e.g., "2 jam lalu") - Extra safe version
  static String formatRelative(DateTime dateTime) {
    try {
      final now = IndonesiaTimeHelper.now();
      
      // Ensure both times are in Indonesia timezone
      final indonesiaTime = dateTime.isUtc ? fromUtc(dateTime) : dateTime;
      final difference = now.difference(indonesiaTime);
      
      // Handle future dates
      if (difference.isNegative) {
        final futureDiff = indonesiaTime.difference(now);
        if (futureDiff.inMinutes < 5) {
          return 'Baru saja';
        }
        return 'Beberapa saat lagi';
      }
      
      if (difference.inDays > 0) {
        if (difference.inDays == 1) {
          return '1 hari lalu';
        } else if (difference.inDays < 7) {
          return '${difference.inDays} hari lalu';
        } else if (difference.inDays < 30) {
          final weeks = (difference.inDays / 7).floor();
          if (weeks == 1) {
            return '1 minggu lalu';
          }
          return '$weeks minggu lalu';
        } else if (difference.inDays < 365) {
          final months = (difference.inDays / 30).floor();
          if (months == 1) {
            return '1 bulan lalu';
          }
          return '$months bulan lalu';
        } else {
          final years = (difference.inDays / 365).floor();
          if (years == 1) {
            return '1 tahun lalu';
          }
          return '$years tahun lalu';
        }
      } else if (difference.inHours > 0) {
        if (difference.inHours == 1) {
          return '1 jam lalu';
        }
        return '${difference.inHours} jam lalu';
      } else if (difference.inMinutes > 0) {
        if (difference.inMinutes == 1) {
          return '1 menit lalu';
        }
        return '${difference.inMinutes} menit lalu';
      } else {
        return 'Baru saja';
      }
    } catch (e) {
      print('⚠️ Error in formatRelative: $e');
      // Fallback jika ada error
      return 'Beberapa waktu lalu';
    }
  }
  
  /// Format for chat messages (time only if today, date if older) dengan fallback
  static String formatForChat(DateTime dateTime) {
    try {
      final now = IndonesiaTimeHelper.now();
      final indonesiaTime = dateTime.isUtc ? fromUtc(dateTime) : dateTime;
      
      // Check if it's today
      if (now.year == indonesiaTime.year &&
          now.month == indonesiaTime.month &&
          now.day == indonesiaTime.day) {
        return formatTimeOnly(indonesiaTime);
      } else {
        // Check if it's this year
        if (now.year == indonesiaTime.year) {
          return format(indonesiaTime, pattern: 'dd/MM HH:mm');
        } else {
          return format(indonesiaTime, pattern: 'dd/MM/yy');
        }
      }
    } catch (e) {
      print('⚠️ Error in formatForChat: $e');
      return formatTimeOnly(dateTime);
    }
  }
  
  /// Debug: Show timezone info dengan comprehensive error handling
  static Map<String, String> getTimezoneInfo() {
    try {
      final now = DateTime.now();
      final utcNow = now.toUtc();
      final indonesiaNow = IndonesiaTimeHelper.now();
      
      return {
        'local_time': now.toString(),
        'utc_time': utcNow.toString(),
        'indonesia_time': indonesiaNow.toString(),
        'indonesia_formatted': format(indonesiaNow),
        'timezone': 'WIB (UTC+7)',
        'offset_hours': '+7',
        'locale_initialized': _isInitialized.toString(),
        'current_time_wib': format(indonesiaNow, pattern: 'dd/MM/yyyy HH:mm:ss'),
      };
    } catch (e) {
      return {
        'error': e.toString(),
        'timezone': 'WIB (UTC+7)',
        'offset_hours': '+7',
        'locale_initialized': _isInitialized.toString(),
        'fallback_time': DateTime.now().toString(),
      };
    }
  }
  
  /// Check if a date is today (Indonesia time) dengan error handling
  static bool isToday(DateTime dateTime) {
    try {
      final now = IndonesiaTimeHelper.now();
      final indonesiaTime = dateTime.isUtc ? fromUtc(dateTime) : dateTime;
      
      return now.year == indonesiaTime.year &&
             now.month == indonesiaTime.month &&
             now.day == indonesiaTime.day;
    } catch (e) {
      print('⚠️ Error in isToday: $e');
      return false;
    }
  }
  
  /// Check if a date is yesterday (Indonesia time) dengan error handling
  static bool isYesterday(DateTime dateTime) {
    try {
      final now = IndonesiaTimeHelper.now();
      final yesterday = now.subtract(const Duration(days: 1));
      final indonesiaTime = dateTime.isUtc ? fromUtc(dateTime) : dateTime;
      
      return yesterday.year == indonesiaTime.year &&
             yesterday.month == indonesiaTime.month &&
             yesterday.day == indonesiaTime.day;
    } catch (e) {
      print('⚠️ Error in isYesterday: $e');
      return false;
    }
  }
  
  /// Get start of day in Indonesia time dengan error handling
  static DateTime startOfDay(DateTime dateTime) {
    try {
      final indonesiaTime = dateTime.isUtc ? fromUtc(dateTime) : dateTime;
      return DateTime(indonesiaTime.year, indonesiaTime.month, indonesiaTime.day);
    } catch (e) {
      print('⚠️ Error in startOfDay: $e');
      return dateTime;
    }
  }
  
  /// Get end of day in Indonesia time dengan error handling
  static DateTime endOfDay(DateTime dateTime) {
    try {
      final indonesiaTime = dateTime.isUtc ? fromUtc(dateTime) : dateTime;
      return DateTime(indonesiaTime.year, indonesiaTime.month, indonesiaTime.day, 23, 59, 59, 999);
    } catch (e) {
      print('⚠️ Error in endOfDay: $e');
      return dateTime;
    }
  }
  
  /// Utility: Get timezone offset string
  static String getTimezoneOffset() {
    return '+${timezoneOffsetHours.toString().padLeft(2, '0')}:00';
  }
  
  /// Utility: Check if initialization was successful
  static bool get isInitialized => _isInitialized;
  
  /// Utility: Force re-initialization (untuk debugging)
  static Future<void> forceReinitialize() async {
    _isInitialized = false;
    await initialize();
  }
}