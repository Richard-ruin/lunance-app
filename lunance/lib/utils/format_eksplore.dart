// lib/utils/format_eksplore.dart - FINAL FIX untuk type safety
import 'package:intl/intl.dart';

class FormatUtils {
  static const String _locale = 'id_ID';

  // ===== CURRENCY FORMATTING =====
  
  /// Format currency to Indonesian Rupiah
  static String formatCurrency(double amount, {bool showSymbol = true}) {
    try {
      final formatter = NumberFormat.currency(
        locale: _locale,
        symbol: showSymbol ? 'Rp ' : '',
        decimalDigits: 0,
      );
      return formatter.format(amount);
    } catch (e) {
      // Fallback formatting jika locale tidak tersedia
      if (showSymbol) {
        return 'Rp ${_formatNumber(amount)}';
      } else {
        return _formatNumber(amount);
      }
    }
  }

  /// Helper untuk format number tanpa locale
  static String _formatNumber(double amount) {
    return amount.toStringAsFixed(0).replaceAllMapped(
      RegExp(r'(\d{1,3})(?=(\d{3})+(?!\d))'), 
      (Match m) => '${m[1]}.'
    );
  }

  // ===== SAFE DATA ACCESS HELPERS - ULTIMATE FIX =====
  
  /// ULTIMATE FIX: Safely get double value dengan comprehensive null safety
  static double safeDouble(dynamic value, [double defaultValue = 0.0]) {
    if (value == null) return defaultValue;
    
    try {
      if (value is double) return value;
      if (value is int) return value.toDouble();
      if (value is num) return value.toDouble();
      if (value is String) {
        if (value.isEmpty) return defaultValue;
        final parsed = double.tryParse(value);
        return parsed ?? defaultValue;
      }
      return defaultValue;
    } catch (e) {
      return defaultValue;
    }
  }

  /// ULTIMATE FIX: Safely get string value
  static String safeString(dynamic value, [String defaultValue = '']) {
    if (value == null) return defaultValue;
    try {
      return value.toString();
    } catch (e) {
      return defaultValue;
    }
  }

  /// ULTIMATE FIX: Safely get int value
  static int safeInt(dynamic value, [int defaultValue = 0]) {
    if (value == null) return defaultValue;
    
    try {
      if (value is int) return value;
      if (value is double) return value.round();
      if (value is num) return value.round();
      if (value is String) {
        if (value.isEmpty) return defaultValue;
        final parsed = int.tryParse(value);
        return parsed ?? defaultValue;
      }
      return defaultValue;
    } catch (e) {
      return defaultValue;
    }
  }

  /// ULTIMATE FIX: Safely get bool value
  static bool safeBool(dynamic value, [bool defaultValue = false]) {
    if (value == null) return defaultValue;
    
    try {
      if (value is bool) return value;
      if (value is String) {
        return value.toLowerCase() == 'true' || value == '1';
      }
      if (value is int) return value != 0;
      if (value is double) return value != 0.0;
      return defaultValue;
    } catch (e) {
      return defaultValue;
    }
  }

  /// ULTIMATE FIX: Safely access nested map - ROBUST VERSION
  static dynamic safeGetNested(dynamic data, List<String> keys, [dynamic defaultValue]) {
    if (data == null || keys.isEmpty) return defaultValue;
    
    try {
      dynamic current = data;
      
      for (final key in keys) {
        if (current == null) return defaultValue;
        
        // Handle all possible Map types
        if (current is Map<String, dynamic>) {
          current = current[key];
        } else if (current is Map<dynamic, dynamic>) {
          current = current[key];
        } else if (current is Map<String, Object?>) {
          current = current[key];
        } else if (current is Map<Object?, Object?>) {
          current = current[key];
        } else if (current is Map) {
          // Generic Map fallback
          current = current[key];
        } else {
          // Not a map, can't access key
          return defaultValue;
        }
      }
      
      return current ?? defaultValue;
    } catch (e) {
      return defaultValue;
    }
  }

  /// ULTIMATE FIX: Safely get map - ROBUST VERSION
  static Map<String, dynamic> safeMap(dynamic value, [Map<String, dynamic> defaultValue = const {}]) {
    if (value == null) return defaultValue;
    
    try {
      // Direct match
      if (value is Map<String, dynamic>) return value;
      
      // Convert from different Map types
      if (value is Map<dynamic, dynamic>) {
        return _convertMapToStringDynamic(value);
      } else if (value is Map<String, Object?>) {
        return _convertMapToStringDynamic(value);
      } else if (value is Map<Object?, Object?>) {
        return _convertMapToStringDynamic(value);
      } else if (value is Map) {
        return _convertMapToStringDynamic(value);
      }
      
      return defaultValue;
    } catch (e) {
      return defaultValue;
    }
  }

  /// Helper to convert any Map to Map<String, dynamic>
  static Map<String, dynamic> _convertMapToStringDynamic(Map map) {
    final result = <String, dynamic>{};
    try {
      for (final entry in map.entries) {
        final key = entry.key?.toString() ?? '';
        final value = entry.value;
        
        // Recursively convert nested maps
        if (value is Map && value is! Map<String, dynamic>) {
          result[key] = _convertMapToStringDynamic(value);
        } else if (value is List) {
          result[key] = _convertListRecursive(value);
        } else {
          result[key] = value;
        }
      }
    } catch (e) {
      // Return empty map if conversion fails
      return <String, dynamic>{};
    }
    return result;
  }

  /// Helper to convert List recursively
  static List<dynamic> _convertListRecursive(List list) {
    return list.map((item) {
      if (item is Map && item is! Map<String, dynamic>) {
        return _convertMapToStringDynamic(item);
      } else if (item is List) {
        return _convertListRecursive(item);
      } else {
        return item;
      }
    }).toList();
  }

  /// ULTIMATE FIX: Safely get list
  static List<T> safeList<T>(dynamic value, [List<T> defaultValue = const []]) {
    if (value == null) return defaultValue;
    
    try {
      if (value is List<T>) return value;
      if (value is List) {
        return value.cast<T>();
      }
      return defaultValue;
    } catch (e) {
      return defaultValue;
    }
  }

  // ===== DATE FORMATTING =====

  /// Format date to Indonesian format (DD/MM/YYYY)
  static String formatDate(DateTime date) {
    try {
      return DateFormat('dd/MM/yyyy', _locale).format(date);
    } catch (e) {
      return '${date.day.toString().padLeft(2, '0')}/${date.month.toString().padLeft(2, '0')}/${date.year}';
    }
  }

  /// Format relative time (e.g., "2 jam lalu")
  static String formatRelativeTime(DateTime dateTime) {
    final now = DateTime.now();
    final difference = now.difference(dateTime);

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

  // ===== PERCENTAGE FORMATTING =====

  /// Format percentage with specified decimal places
  static String formatPercentage(double percentage, {int decimalPlaces = 1}) {
    return '${percentage.toStringAsFixed(decimalPlaces)}%';
  }

  // ===== TRANSACTION FORMATTING =====

  /// Format transaction amount with sign
  static String formatTransactionAmount(double amount, String type) {
    final sign = type.toLowerCase() == 'income' ? '+' : '-';
    return '$sign${formatCurrency(amount)}';
  }

  // ===== DASHBOARD SPECIFIC HELPERS - ULTIMATE FIX =====

  /// ULTIMATE FIX: Format dashboard quick stats dengan comprehensive error handling
  static Map<String, String> formatDashboardQuickStats(dynamic data) {
    final defaultResult = {
      'real_total_savings': formatCurrency(0),
      'monthly_income': formatCurrency(0),
      'needs_spending': formatCurrency(0),
      'wants_spending': formatCurrency(0),
      'savings_spending': formatCurrency(0),
    };

    if (data == null) return defaultResult;

    try {
      final quickStats = safeMap(data);
      final realTotalSavings = safeDouble(quickStats['real_total_savings']);
      final monthlyIncome = safeDouble(quickStats['monthly_income']);
      final currentSpending = safeMap(quickStats['current_month_spending']);

      return {
        'real_total_savings': formatCurrency(realTotalSavings),
        'monthly_income': formatCurrency(monthlyIncome),
        'needs_spending': formatCurrency(safeDouble(currentSpending['needs'])),
        'wants_spending': formatCurrency(safeDouble(currentSpending['wants'])),
        'savings_spending': formatCurrency(safeDouble(currentSpending['savings'])),
      };
    } catch (e) {
      return defaultResult;
    }
  }

  /// ULTIMATE FIX: Format financial summary dengan error handling
  static Map<String, String> formatFinancialSummary(dynamic data) {
    final defaultResult = {
      'monthly_income': formatCurrency(0),
      'monthly_expense': formatCurrency(0),
      'net_balance': formatCurrency(0),
      'savings_rate': formatPercentage(0),
    };

    if (data == null) return defaultResult;

    try {
      final summary = safeMap(data);
      return {
        'monthly_income': formatCurrency(safeDouble(summary['monthly_income'])),
        'monthly_expense': formatCurrency(safeDouble(summary['monthly_expense'])),
        'net_balance': formatCurrency(safeDouble(summary['net_balance'])),
        'savings_rate': formatPercentage(safeDouble(summary['savings_rate'])),
      };
    } catch (e) {
      return defaultResult;
    }
  }

  // ===== HISTORY SPECIFIC HELPERS - ULTIMATE FIX =====

  /// ULTIMATE FIX: Format transaction history item dengan comprehensive error handling
  static Map<String, dynamic> formatTransactionHistoryItem(dynamic transaction) {
    final defaultResult = {
      'id': '',
      'type': 'expense',
      'amount': 0.0,
      'formatted_amount': formatCurrency(0),
      'category': '',
      'budget_type': '',
      'description': '',
      'date': '',
      'formatted_date': '',
      'relative_date': '',
      'status': '',
    };

    if (transaction == null) return defaultResult;

    try {
      final trans = safeMap(transaction);
      final type = safeString(trans['type'], 'expense');
      final amount = safeDouble(trans['amount']);
      
      return {
        'id': safeString(trans['id']),
        'type': type,
        'amount': amount,
        'formatted_amount': formatTransactionAmount(amount, type),
        'category': safeString(trans['category']),
        'budget_type': safeString(trans['budget_type']),
        'description': safeString(trans['description']),
        'date': safeString(trans['date']),
        'formatted_date': safeString(trans['formatted_date']),
        'relative_date': safeString(trans['relative_date']),
        'status': safeString(trans['status']),
      };
    } catch (e) {
      return defaultResult;
    }
  }

  // ===== BUDGET TYPE HELPERS =====

  /// Get budget type icon
  static String getBudgetTypeIcon(String budgetType) {
    switch (budgetType.toLowerCase()) {
      case 'needs':
        return '🏠';
      case 'wants':
        return '🎯';
      case 'savings':
        return '💰';
      case 'income':
        return '💵';
      default:
        return '📊';
    }
  }

  /// Get budget type name
  static String getBudgetTypeName(String budgetType) {
    switch (budgetType.toLowerCase()) {
      case 'needs':
        return 'Kebutuhan (50%)';
      case 'wants':
        return 'Keinginan (30%)';
      case 'savings':
        return 'Tabungan (20%)';
      case 'income':
        return 'Pemasukan';
      default:
        return 'Lainnya';
    }
  }

  // ===== ANALYTICS SPECIFIC HELPERS - ENHANCED =====

  /// ULTIMATE FIX: Format analytics chart data safely dengan comprehensive type checking
  static List<Map<String, dynamic>> formatAnalyticsChartData(List<dynamic>? rawData) {
    if (rawData == null || rawData.isEmpty) {
      return [];
    }

    try {
      return rawData.map<Map<String, dynamic>>((item) {
        try {
          final itemMap = safeMap(item);
          return {
            'period': safeString(itemMap['period']),
            'income': safeDouble(itemMap['income']),
            'expense': safeDouble(itemMap['expense']),
            'net': safeDouble(itemMap['net']),
          };
        } catch (e) {
          return {
            'period': '',
            'income': 0.0,
            'expense': 0.0,
            'net': 0.0,
          };
        }
      }).toList();
    } catch (e) {
      return [];
    }
  }

  /// ULTIMATE FIX: Format categories data safely untuk pie chart
  static List<Map<String, dynamic>> formatCategoriesData(List<dynamic>? categoriesData) {
    if (categoriesData == null || categoriesData.isEmpty) {
      return [];
    }

    try {
      return categoriesData.map<Map<String, dynamic>>((item) {
        try {
          final itemMap = safeMap(item);
          final amount = safeDouble(itemMap['amount']);
          
          return {
            'category': safeString(itemMap['category']),
            'amount': amount,
            'formatted_amount': formatCurrency(amount),
            'percentage': safeDouble(itemMap['percentage']),
            'color': safeString(itemMap['color'], '#6B7280'),
          };
        } catch (e) {
          return {
            'category': '',
            'amount': 0.0,
            'formatted_amount': formatCurrency(0),
            'percentage': 0.0,
            'color': '#6B7280',
          };
        }
      }).toList();
    } catch (e) {
      return [];
    }
  }

  // ===== MISSING METHODS - RESTORED =====

  /// RESTORED: Format savings goal history item safely
  static Map<String, dynamic> formatSavingsGoalHistoryItem(dynamic goal) {
    final defaultResult = {
      'id': '',
      'item_name': '',
      'target_amount': 0.0,
      'current_amount': 0.0,
      'formatted_target': formatCurrency(0),
      'formatted_current': formatCurrency(0),
      'progress_percentage': 0.0,
      'status': '',
      'target_date': '',
      'days_remaining': 0,
      'formatted_days_remaining': 'Tidak ada target',
    };

    if (goal == null) return defaultResult;

    try {
      final goalMap = safeMap(goal);
      final targetAmount = safeDouble(goalMap['target_amount']);
      final currentAmount = safeDouble(goalMap['current_amount']);
      final daysRemaining = safeInt(goalMap['days_remaining']);
      
      return {
        'id': safeString(goalMap['id']),
        'item_name': safeString(goalMap['item_name']),
        'target_amount': targetAmount,
        'current_amount': currentAmount,
        'formatted_target': formatCurrency(targetAmount),
        'formatted_current': formatCurrency(currentAmount),
        'progress_percentage': safeDouble(goalMap['progress_percentage']),
        'status': safeString(goalMap['status']),
        'target_date': safeString(goalMap['target_date']),
        'days_remaining': daysRemaining,
        'formatted_days_remaining': formatDaysRemaining(daysRemaining),
      };
    } catch (e) {
      return defaultResult;
    }
  }

  /// RESTORED: Format days remaining for savings goal
  static String formatDaysRemaining(int days) {
    if (days < 0) {
      return 'Terlambat ${(-days)} hari';
    } else if (days == 0) {
      return 'Hari ini';
    } else if (days == 1) {
      return '1 hari lagi';
    } else if (days < 7) {
      return '$days hari lagi';
    } else if (days < 30) {
      final weeks = (days / 7).floor();
      return '$weeks minggu lagi';
    } else {
      final months = (days / 30).floor();
      return '$months bulan lagi';
    }
  }

  /// RESTORED: Format savings goal progress
  static String formatSavingsProgress(double current, double target) {
    final percentage = target > 0 ? (current / target * 100).clamp(0, 100).toDouble() : 0.0;
    return '${formatCurrency(current)} / ${formatCurrency(target)} (${formatPercentage(percentage)})';
  }

  /// RESTORED: Format date with month name (DD MMM YYYY)
  static String formatDateWithMonth(DateTime date) {
    try {
      return DateFormat('dd MMM yyyy', _locale).format(date);
    } catch (e) {
      final months = [
        'Jan', 'Feb', 'Mar', 'Apr', 'Mei', 'Jun',
        'Jul', 'Ags', 'Sep', 'Okt', 'Nov', 'Des'
      ];
      return '${date.day} ${months[date.month - 1]} ${date.year}';
    }
  }

  /// RESTORED: Format date and time (DD/MM/YYYY HH:mm)
  static String formatDateTime(DateTime dateTime) {
    try {
      return DateFormat('dd/MM/yyyy HH:mm', _locale).format(dateTime);
    } catch (e) {
      return '${formatDate(dateTime)} ${formatTime(dateTime)}';
    }
  }

  /// RESTORED: Format time only (HH:mm)
  static String formatTime(DateTime dateTime) {
    try {
      return DateFormat('HH:mm', _locale).format(dateTime);
    } catch (e) {
      return '${dateTime.hour.toString().padLeft(2, '0')}:${dateTime.minute.toString().padLeft(2, '0')}';
    }
  }

  /// RESTORED: Format month year (MMM YYYY)
  static String formatMonthYear(DateTime date) {
    try {
      return DateFormat('MMM yyyy', _locale).format(date);
    } catch (e) {
      final months = [
        'Jan', 'Feb', 'Mar', 'Apr', 'Mei', 'Jun',
        'Jul', 'Ags', 'Sep', 'Okt', 'Nov', 'Des'
      ];
      return '${months[date.month - 1]} ${date.year}';
    }
  }

  /// RESTORED: Format currency with compact notation (e.g., Rp 1.5jt)
  static String formatCompactCurrency(double amount) {
    if (amount >= 1000000000) {
      return 'Rp ${(amount / 1000000000).toStringAsFixed(1)}M';
    } else if (amount >= 1000000) {
      return 'Rp ${(amount / 1000000).toStringAsFixed(1)}jt';
    } else if (amount >= 1000) {
      return 'Rp ${(amount / 1000).toStringAsFixed(1)}rb';
    } else {
      return formatCurrency(amount);
    }
  }

  /// RESTORED: Format number to compact format (without currency)
  static String formatCompactNumber(double number) {
    if (number >= 1000000000) {
      return '${(number / 1000000000).toStringAsFixed(1)}M';
    } else if (number >= 1000000) {
      return '${(number / 1000000).toStringAsFixed(1)}jt';
    } else if (number >= 1000) {
      return '${(number / 1000).toStringAsFixed(1)}rb';
    } else {
      return number.toStringAsFixed(0);
    }
  }

  /// RESTORED: Format percentage with color indication
  static String formatPercentageWithSign(double percentage, {int decimalPlaces = 1}) {
    final sign = percentage >= 0 ? '+' : '';
    return '$sign${percentage.toStringAsFixed(decimalPlaces)}%';
  }

  /// RESTORED: Format transaction type
  static String formatTransactionType(String type) {
    switch (type.toLowerCase()) {
      case 'income':
        return '💰 Pemasukan';
      case 'expense':
        return '💸 Pengeluaran';
      default:
        return '📊 $type';
    }
  }

  /// RESTORED: Get budget type color hex
  static String getBudgetTypeColorHex(String budgetType) {
    switch (budgetType.toLowerCase()) {
      case 'needs':
        return '#22C55E'; // Green
      case 'wants':
        return '#F59E0B'; // Orange
      case 'savings':
        return '#3B82F6'; // Blue
      case 'income':
        return '#22C55E'; // Green
      default:
        return '#6B7280'; // Gray
    }
  }

  /// RESTORED: Format error message for user display
  static String formatErrorMessage(String error) {
    // Common API errors
    if (error.contains('Network') || error.contains('network')) {
      return 'Koneksi internet bermasalah. Coba lagi.';
    } else if (error.contains('Unauthorized') || error.contains('unauthorized')) {
      return 'Sesi telah berakhir. Silakan login kembali.';
    } else if (error.contains('Not Found') || error.contains('not found')) {
      return 'Data tidak ditemukan.';
    } else if (error.contains('Server Error') || error.contains('500')) {
      return 'Server sedang bermasalah. Coba lagi nanti.';
    } else if (error.contains('setup')) {
      return 'Setup keuangan diperlukan.';
    } else if (error.contains('Map<dynamic, dynamic>')) {
      return 'Format data tidak sesuai. Silakan refresh halaman.';
    } else {
      return 'Terjadi kesalahan. Silakan coba lagi.';
    }
  }

  // ===== CONSTANTS =====

  /// Default budget percentages for 50/30/20 method
  static const Map<String, double> budgetPercentages = {
    'needs': 50.0,
    'wants': 30.0,
    'savings': 20.0,
  };

  /// Student financial health thresholds
  static const Map<String, double> healthThresholds = {
    'excellent': 80.0,
    'good': 60.0,
    'fair': 40.0,
    'needs_improvement': 0.0,
  };

  /// Budget status thresholds
  static const Map<String, double> budgetThresholds = {
    'safe': 70.0,
    'caution': 90.0,
    'warning': 100.0,
  };
}