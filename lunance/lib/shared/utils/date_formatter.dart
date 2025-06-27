
// lib/core/utils/date_formatter.dart
import 'package:intl/intl.dart';

class DateFormatter {
  static final DateFormat _dayMonth = DateFormat('dd MMM', 'id_ID');
  static final DateFormat _dayMonthYear = DateFormat('dd MMM yyyy', 'id_ID');
  static final DateFormat _fullDate = DateFormat('EEEE, dd MMMM yyyy', 'id_ID');
  static final DateFormat _time = DateFormat('HH:mm', 'id_ID');
  static final DateFormat _dateTime = DateFormat('dd MMM yyyy HH:mm', 'id_ID');

  static String formatTransactionDate(DateTime date) {
    final now = DateTime.now();
    final today = DateTime(now.year, now.month, now.day);
    final yesterday = today.subtract(const Duration(days: 1));
    final transactionDate = DateTime(date.year, date.month, date.day);

    if (transactionDate == today) {
      return 'Hari ini ${_time.format(date)}';
    } else if (transactionDate == yesterday) {
      return 'Kemarin ${_time.format(date)}';
    } else if (date.year == now.year) {
      return _dayMonth.format(date);
    } else {
      return _dayMonthYear.format(date);
    }
  }

  static String formatFullDate(DateTime date) {
    return _fullDate.format(date);
  }

  static String formatDateTime(DateTime date) {
    return _dateTime.format(date);
  }

  static String formatDateOnly(DateTime date) {
    return _dayMonthYear.format(date);
  }

  static String formatTimeOnly(DateTime date) {
    return _time.format(date);
  }

  static String formatRelativeDate(DateTime date) {
    final now = DateTime.now();
    final difference = now.difference(date);

    if (difference.inDays == 0) {
      if (difference.inHours == 0) {
        if (difference.inMinutes == 0) {
          return 'Baru saja';
        } else {
          return '${difference.inMinutes} menit yang lalu';
        }
      } else {
        return '${difference.inHours} jam yang lalu';
      }
    } else if (difference.inDays == 1) {
      return 'Kemarin';
    } else if (difference.inDays < 7) {
      return '${difference.inDays} hari yang lalu';
    } else {
      return formatDateOnly(date);
    }
  }
}
