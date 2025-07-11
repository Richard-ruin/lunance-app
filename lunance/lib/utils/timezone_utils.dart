// lib/utils/timezone_utils.dart
import 'package:intl/intl.dart';

class IndonesiaTimeHelper {
  // Indonesia timezone offset (WIB = UTC+7)
  static const int timezoneOffsetHours = 7;
  
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
    final utcDateTime = DateTime.parse(isoString);
    return fromUtc(utcDateTime);
  }
  
  /// Format DateTime for display in Indonesia
  static String format(DateTime dateTime, {String pattern = 'dd/MM/yyyy HH:mm'}) {
    // Ensure we're working with Indonesia time
    final indonesiaTime = dateTime.isUtc ? fromUtc(dateTime) : dateTime;
    final formatter = DateFormat(pattern, 'id_ID');
    return formatter.format(indonesiaTime);
  }
  
  /// Format time only (HH:mm)
  static String formatTimeOnly(DateTime dateTime) {
    return format(dateTime, pattern: 'HH:mm');
  }
  
  /// Format date only (dd/MM/yyyy)
  static String formatDateOnly(DateTime dateTime) {
    return format(dateTime, pattern: 'dd/MM/yyyy');
  }
  
  /// Format relative time (e.g., "2 jam lalu")
  static String formatRelative(DateTime dateTime) {
    final now = IndonesiaTimeHelper.now();
    
    // Ensure both times are in Indonesia timezone
    final indonesiaTime = dateTime.isUtc ? fromUtc(dateTime) : dateTime;
    final difference = now.difference(indonesiaTime);
    
    if (difference.inDays > 0) {
      if (difference.inDays == 1) {
        return '1 hari lalu';
      } else if (difference.inDays < 7) {
        return '${difference.inDays} hari lalu';
      } else if (difference.inDays < 30) {
        final weeks = (difference.inDays / 7).floor();
        return '$weeks minggu lalu';
      } else {
        final months = (difference.inDays / 30).floor();
        return '$months bulan lalu';
      }
    } else if (difference.inHours > 0) {
      return '${difference.inHours} jam lalu';
    } else if (difference.inMinutes > 0) {
      return '${difference.inMinutes} menit lalu';
    } else {
      return 'Baru saja';
    }
  }
  
  /// Format for chat messages (time only if today, date if older)
  static String formatForChat(DateTime dateTime) {
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
  }
  
  /// Debug: Show timezone info
  static Map<String, String> getTimezoneInfo() {
    final now = DateTime.now();
    final utcNow = now.toUtc();
    final indonesiaNow = IndonesiaTimeHelper.now();
    
    return {
      'local_time': now.toString(),
      'utc_time': utcNow.toString(),
      'indonesia_time': indonesiaNow.toString(),
      'timezone': 'WIB (UTC+7)',
      'offset_hours': '+7',
    };
  }
  
  /// Check if a date is today (Indonesia time)
  static bool isToday(DateTime dateTime) {
    final now = IndonesiaTimeHelper.now();
    final indonesiaTime = dateTime.isUtc ? fromUtc(dateTime) : dateTime;
    
    return now.year == indonesiaTime.year &&
           now.month == indonesiaTime.month &&
           now.day == indonesiaTime.day;
  }
  
  /// Check if a date is yesterday (Indonesia time)
  static bool isYesterday(DateTime dateTime) {
    final now = IndonesiaTimeHelper.now();
    final yesterday = now.subtract(const Duration(days: 1));
    final indonesiaTime = dateTime.isUtc ? fromUtc(dateTime) : dateTime;
    
    return yesterday.year == indonesiaTime.year &&
           yesterday.month == indonesiaTime.month &&
           yesterday.day == indonesiaTime.day;
  }
  
  /// Get start of day in Indonesia time
  static DateTime startOfDay(DateTime dateTime) {
    final indonesiaTime = dateTime.isUtc ? fromUtc(dateTime) : dateTime;
    return DateTime(indonesiaTime.year, indonesiaTime.month, indonesiaTime.day);
  }
  
  /// Get end of day in Indonesia time
  static DateTime endOfDay(DateTime dateTime) {
    final indonesiaTime = dateTime.isUtc ? fromUtc(dateTime) : dateTime;
    return DateTime(indonesiaTime.year, indonesiaTime.month, indonesiaTime.day, 23, 59, 59, 999);
  }
}