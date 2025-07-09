// lib/utils/extensions.dart
import 'package:intl/intl.dart';

extension DateTimeExtensions on DateTime {
  String toDateString() {
    return DateFormat('yyyy-MM-dd').format(this);
  }
  
  String toDisplayString() {
    return DateFormat('dd/MM/yyyy').format(this);
  }
  
  String toDisplayDateTimeString() {
    return DateFormat('dd/MM/yyyy HH:mm').format(this);
  }
  
  String toIndonesianString() {
    return DateFormat('dd MMMM yyyy', 'id_ID').format(this);
  }
  
  bool isSameDay(DateTime other) {
    return year == other.year && month == other.month && day == other.day;
  }
  
  bool isToday() {
    final now = DateTime.now();
    return isSameDay(now);
  }
  
  bool isYesterday() {
    final yesterday = DateTime.now().subtract(const Duration(days: 1));
    return isSameDay(yesterday);
  }
  
  String toRelativeString() {
    final now = DateTime.now();
    final difference = now.difference(this);
    
    if (isToday()) {
      return 'Hari ini';
    } else if (isYesterday()) {
      return 'Kemarin';
    } else if (difference.inDays < 7) {
      return '${difference.inDays} hari lalu';
    } else if (difference.inDays < 30) {
      return '${(difference.inDays / 7).floor()} minggu lalu';
    } else if (difference.inDays < 365) {
      return '${(difference.inDays / 30).floor()} bulan lalu';
    } else {
      return '${(difference.inDays / 365).floor()} tahun lalu';
    }
  }
}

extension StringExtensions on String {
  bool get isValidEmail {
    return RegExp(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$').hasMatch(this);
  }
  
  bool get isAcademicEmail {
    return endsWith('.ac.id') && isValidEmail;
  }
  
  String capitalize() {
    if (isEmpty) return this;
    return '${this[0].toUpperCase()}${substring(1)}';
  }
  
  String toTitleCase() {
    return split(' ').map((word) => word.capitalize()).join(' ');
  }
  
  String truncate(int maxLength) {
    if (length <= maxLength) return this;
    return '${substring(0, maxLength)}...';
  }
}

extension DoubleExtensions on double {
  String toCurrency({bool withSymbol = true}) {
    final formatter = NumberFormat.currency(
      locale: 'id_ID',
      symbol: withSymbol ? 'Rp ' : '',
      decimalDigits: 0,
    );
    return formatter.format(this);
  }
  
  String toFormattedString() {
    return NumberFormat('#,##0', 'id_ID').format(this);
  }
  
  bool isValidAmount() {
    return this > 0 && this <= 999999999.99;
  }
}

extension ListExtensions<T> on List<T> {
  List<T> separatedBy(T separator) {
    if (isEmpty) return this;
    
    final result = <T>[];
    for (int i = 0; i < length; i++) {
      result.add(this[i]);
      if (i < length - 1) {
        result.add(separator);
      }
    }
    return result;
  }
  
  T? firstWhereOrNull(bool Function(T) test) {
    for (final element in this) {
      if (test(element)) return element;
    }
    return null;
  }
}
