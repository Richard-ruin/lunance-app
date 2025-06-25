
// lib/shared/utils/currency_formatter.dart
import 'package:intl/intl.dart';

class CurrencyFormatter {
  static final _formatter = NumberFormat.currency(
    locale: 'id_ID',
    symbol: 'Rp ',
    decimalDigits: 0,
  );

  static String formatIDR(double amount) {
    return _formatter.format(amount);
  }

  static String formatIDRCompact(double amount) {
    if (amount >= 1000000000) {
      return 'Rp ${(amount / 1000000000).toStringAsFixed(1)}M';
    } else if (amount >= 1000000) {
      return 'Rp ${(amount / 1000000).toStringAsFixed(1)}jt';
    } else if (amount >= 1000) {
      return 'Rp ${(amount / 1000).toStringAsFixed(0)}rb';
    } else {
      return 'Rp ${amount.toStringAsFixed(0)}';
    }
  }

  static double parseIDR(String formattedAmount) {
    // Remove currency symbol and format
    final cleanAmount = formattedAmount
        .replaceAll('Rp', '')
        .replaceAll('.', '')
        .replaceAll(',', '.')
        .trim();
    
    return double.tryParse(cleanAmount) ?? 0.0;
  }
}

// lib/shared/utils/date_formatter.dart
class DateFormatter {
  static String formatTransactionDate(DateTime date) {
    final now = DateTime.now();
    final today = DateTime(now.year, now.month, now.day);
    final yesterday = today.subtract(const Duration(days: 1));
    final dateOnly = DateTime(date.year, date.month, date.day);

    if (dateOnly == today) {
      return 'Hari ini, ${DateFormat('HH:mm').format(date)}';
    } else if (dateOnly == yesterday) {
      return 'Kemarin, ${DateFormat('HH:mm').format(date)}';
    } else if (date.year == now.year) {
      return DateFormat('d MMMM, HH:mm', 'id_ID').format(date);
    } else {
      return DateFormat('d MMMM yyyy, HH:mm', 'id_ID').format(date);
    }
  }

  static String formatMonthYear(DateTime date) {
    return DateFormat('MMMM yyyy', 'id_ID').format(date);
  }

  static String formatDateOnly(DateTime date) {
    return DateFormat('d MMMM yyyy', 'id_ID').format(date);
  }
}