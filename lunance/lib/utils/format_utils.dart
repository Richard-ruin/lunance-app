import 'package:intl/intl.dart';

class FormatUtils {
  // Indonesian currency formatter
  static final NumberFormat _currencyFormatter = NumberFormat.currency(
    locale: 'id_ID',
    symbol: 'Rp ',
    decimalDigits: 0,
  );

  // Indonesian number formatter
  static final NumberFormat _numberFormatter = NumberFormat('#,##0', 'id_ID');

  // Indonesian date formatter
  static final DateFormat _dateFormatter = DateFormat('dd/MM/yyyy', 'id_ID');
  static final DateFormat _dateTimeFormatter = DateFormat('dd/MM/yyyy HH:mm', 'id_ID');
  static final DateFormat _timeFormatter = DateFormat('HH:mm', 'id_ID');

  // Currency formatting for Indonesian Rupiah
  static String formatCurrency(num amount) {
    return _currencyFormatter.format(amount);
  }

  // Format currency without symbol
  static String formatCurrencyWithoutSymbol(num amount) {
    return _numberFormatter.format(amount);
  }

  // Compact number formatting for charts
  static String formatCompactNumber(double value) {
    if (value >= 1000000000) {
      return '${(value / 1000000000).toStringAsFixed(1)}M';
    } else if (value >= 1000000) {
      return '${(value / 1000000).toStringAsFixed(1)}Jt';
    } else if (value >= 1000) {
      return '${(value / 1000).toStringAsFixed(1)}rb';
    } else {
      return value.toStringAsFixed(0);
    }
  }

  // Format percentage
  static String formatPercentage(double percentage, {int decimals = 1}) {
    return '${percentage.toStringAsFixed(decimals)}%';
  }

  // Date formatting
  static String formatDate(DateTime date) {
    return _dateFormatter.format(date);
  }

  static String formatDateTime(DateTime dateTime) {
    return _dateTimeFormatter.format(dateTime);
  }

  static String formatTime(DateTime time) {
    return _timeFormatter.format(time);
  }

  // Relative date formatting in Indonesian
  static String formatRelativeDate(DateTime date) {
    final now = DateTime.now();
    final difference = now.difference(date);

    if (difference.inDays > 7) {
      return formatDate(date);
    } else if (difference.inDays > 0) {
      return '${difference.inDays} hari lalu';
    } else if (difference.inHours > 0) {
      return '${difference.inHours} jam lalu';
    } else if (difference.inMinutes > 0) {
      return '${difference.inMinutes} menit lalu';
    } else {
      return 'Baru saja';
    }
  }

  // Month name in Indonesian
  static String getIndonesianMonthName(int month) {
    const months = [
      'Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni',
      'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember'
    ];
    return months[month - 1];
  }

  // Format month year in Indonesian
  static String formatMonthYear(DateTime date) {
    return '${getIndonesianMonthName(date.month)} ${date.year}';
  }

  // Format amount with student-friendly descriptions
  static String formatStudentAmount(num amount) {
    final formatted = formatCurrency(amount);
    
    if (amount >= 10000000) {
      return '$formatted (Sangat besar untuk mahasiswa)';
    } else if (amount >= 5000000) {
      return '$formatted (Besar untuk mahasiswa)';
    } else if (amount >= 1000000) {
      return '$formatted (Cukup besar)';
    } else if (amount >= 500000) {
      return '$formatted (Sedang)';
    } else if (amount >= 100000) {
      return '$formatted (Kecil)';
    } else {
      return '$formatted (Sangat kecil)';
    }
  }

  // Format savings goal progress for students
  static String formatSavingsProgress(num current, num target) {
    final percentage = (current / target * 100).clamp(0, 100);
    final remaining = target - current;
    
    if (percentage >= 100) {
      return 'Target tercapai! 🎉';
    } else if (percentage >= 75) {
      return 'Hampir tercapai (${formatCurrency(remaining)} lagi)';
    } else if (percentage >= 50) {
      return 'Setengah jalan (${formatCurrency(remaining)} lagi)';
    } else if (percentage >= 25) {
      return 'Sudah mulai (${formatCurrency(remaining)} lagi)';
    } else {
      return 'Baru mulai (${formatCurrency(remaining)} lagi)';
    }
  }

  // Format student financial level
  static String formatStudentLevel(num totalSavings) {
    if (totalSavings >= 10000000) {
      return 'Expert Keuangan 🏆';
    } else if (totalSavings >= 5000000) {
      return 'Mahir 🎯';
    } else if (totalSavings >= 2000000) {
      return 'Berkembang 📈';
    } else if (totalSavings >= 500000) {
      return 'Pemula 🌱';
    } else {
      return 'Baru Mulai 🚀';
    }
  }

  // Format time remaining for goals
  static String formatTimeRemaining(DateTime targetDate) {
    final now = DateTime.now();
    final difference = targetDate.difference(now);

    if (difference.isNegative) {
      return 'Terlambat ${difference.inDays.abs()} hari';
    } else if (difference.inDays > 365) {
      final years = difference.inDays ~/ 365;
      return '$years tahun lagi';
    } else if (difference.inDays > 30) {
      final months = difference.inDays ~/ 30;
      return '$months bulan lagi';
    } else if (difference.inDays > 7) {
      final weeks = difference.inDays ~/ 7;
      return '$weeks minggu lagi';
    } else if (difference.inDays > 0) {
      return '${difference.inDays} hari lagi';
    } else {
      return 'Hari ini!';
    }
  }

  // Format urgency for students
  static String formatUrgency(DateTime? targetDate, double progressPercentage) {
    if (targetDate == null) return 'Tidak mendesak';
    
    final now = DateTime.now();
    final daysRemaining = targetDate.difference(now).inDays;
    
    if (daysRemaining <= 0) {
      return 'Sudah lewat waktu!';
    } else if (daysRemaining <= 7 && progressPercentage < 80) {
      return 'Sangat mendesak!';
    } else if (daysRemaining <= 30 && progressPercentage < 50) {
      return 'Mendesak';
    } else if (daysRemaining <= 90 && progressPercentage < 25) {
      return 'Perlu perhatian';
    } else {
      return 'Masih aman';
    }
  }

  // Format recommendation priority
  static String formatRecommendationPriority(String priority) {
    switch (priority.toLowerCase()) {
      case 'high':
        return 'Prioritas Tinggi 🔴';
      case 'medium':
        return 'Prioritas Sedang 🟡';
      case 'low':
        return 'Prioritas Rendah 🟢';
      default:
        return 'Biasa';
    }
  }

  // Format financial health score for students
  static String formatFinancialHealth(double score) {
    if (score >= 80) {
      return 'Sangat Sehat 💪 (${score.toStringAsFixed(0)}/100)';
    } else if (score >= 60) {
      return 'Sehat 👍 (${score.toStringAsFixed(0)}/100)';
    } else if (score >= 40) {
      return 'Cukup 😐 (${score.toStringAsFixed(0)}/100)';
    } else if (score >= 20) {
      return 'Perlu Perbaikan 😟 (${score.toStringAsFixed(0)}/100)';
    } else {
      return 'Butuh Perhatian Serius 😰 (${score.toStringAsFixed(0)}/100)';
    }
  }

  // Parse currency string back to number (for input fields)
  static double? parseCurrency(String value) {
    try {
      // Remove currency symbol and formatting
      final cleanValue = value
          .replaceAll('Rp', '')
          .replaceAll(' ', '')
          .replaceAll('.', '')
          .replaceAll(',', '.');
      
      return double.tryParse(cleanValue);
    } catch (e) {
      return null;
    }
  }

  // Format input currency (as user types)
  static String formatInputCurrency(String value) {
    if (value.isEmpty) return '';
    
    // Remove non-digits
    final digitsOnly = value.replaceAll(RegExp(r'[^\d]'), '');
    if (digitsOnly.isEmpty) return '';
    
    // Convert to number and format
    final number = int.tryParse(digitsOnly);
    if (number == null) return '';
    
    return formatCurrencyWithoutSymbol(number);
  }

  // Validate Indonesian phone number format
  static bool isValidIndonesianPhone(String phone) {
    // Indonesian phone patterns: 08xx-xxxx-xxxx or +62-8xx-xxxx-xxxx
    final phoneRegex = RegExp(r'^(\+62|62|0)8[1-9][0-9]{6,9}$');
    final cleanPhone = phone.replaceAll(RegExp(r'[\s\-\(\)]'), '');
    return phoneRegex.hasMatch(cleanPhone);
  }

  // Format Indonesian phone number
  static String formatIndonesianPhone(String phone) {
    final cleanPhone = phone.replaceAll(RegExp(r'[\s\-\(\)]'), '');
    
    if (cleanPhone.startsWith('0')) {
      // 08xx-xxxx-xxxx
      if (cleanPhone.length >= 11) {
        return '${cleanPhone.substring(0, 4)}-${cleanPhone.substring(4, 8)}-${cleanPhone.substring(8)}';
      }
    } else if (cleanPhone.startsWith('628') || cleanPhone.startsWith('+628')) {
      // +62-8xx-xxxx-xxxx
      final number = cleanPhone.startsWith('+') ? cleanPhone.substring(1) : cleanPhone;
      if (number.length >= 11) {
        return '+${number.substring(0, 2)}-${number.substring(2, 5)}-${number.substring(5, 9)}-${number.substring(9)}';
      }
    }
    
    return phone; // Return original if can't format
  }
}