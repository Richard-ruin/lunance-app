// lib/utils/format_eksplore.dart - FIXED untuk Finance Tab
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

  /// Format currency with compact notation (e.g., Rp 1.5jt)
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

  /// Format number to compact format (without currency)
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

  // ===== DATE FORMATTING =====

  /// Format date to Indonesian format (DD/MM/YYYY)
  static String formatDate(DateTime date) {
    try {
      return DateFormat('dd/MM/yyyy', _locale).format(date);
    } catch (e) {
      return '${date.day.toString().padLeft(2, '0')}/${date.month.toString().padLeft(2, '0')}/${date.year}';
    }
  }

  /// Format date with month name (DD MMM YYYY)
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

  /// Format date and time (DD/MM/YYYY HH:mm)
  static String formatDateTime(DateTime dateTime) {
    try {
      return DateFormat('dd/MM/yyyy HH:mm', _locale).format(dateTime);
    } catch (e) {
      return '${formatDate(dateTime)} ${formatTime(dateTime)}';
    }
  }

  /// Format time only (HH:mm)
  static String formatTime(DateTime dateTime) {
    try {
      return DateFormat('HH:mm', _locale).format(dateTime);
    } catch (e) {
      return '${dateTime.hour.toString().padLeft(2, '0')}:${dateTime.minute.toString().padLeft(2, '0')}';
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

  /// Format month year (MMM YYYY)
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

  // ===== PERCENTAGE FORMATTING =====

  /// Format percentage with specified decimal places
  static String formatPercentage(double percentage, {int decimalPlaces = 1}) {
    return '${percentage.toStringAsFixed(decimalPlaces)}%';
  }

  /// Format percentage with color indication
  static String formatPercentageWithSign(double percentage, {int decimalPlaces = 1}) {
    final sign = percentage >= 0 ? '+' : '';
    return '$sign${percentage.toStringAsFixed(decimalPlaces)}%';
  }

  // ===== 50/30/20 SPECIFIC FORMATTING =====

  /// Format budget allocation display
  static String formatBudgetAllocation(double amount, String type) {
    final typeInfo = _getBudgetTypeInfo(type);
    return '${typeInfo['emoji']} ${typeInfo['name']}: ${formatCurrency(amount)}';
  }

  /// Get budget type information
  static Map<String, String> _getBudgetTypeInfo(String type) {
    switch (type.toLowerCase()) {
      case 'needs':
        return {
          'name': 'Kebutuhan (50%)',
          'emoji': '🏠',
          'description': 'Kebutuhan pokok yang wajib',
        };
      case 'wants':
        return {
          'name': 'Keinginan (30%)',
          'emoji': '🎯',
          'description': 'Keinginan dan lifestyle',
        };
      case 'savings':
        return {
          'name': 'Tabungan (20%)',
          'emoji': '💰',
          'description': 'Tabungan masa depan',
        };
      default:
        return {
          'name': 'Lainnya',
          'emoji': '📊',
          'description': 'Kategori lainnya',
        };
    }
  }

  /// Format budget status with color indication
  static String formatBudgetStatus(double percentageUsed) {
    if (percentageUsed <= 70) {
      return 'Aman (${formatPercentage(percentageUsed)})';
    } else if (percentageUsed <= 90) {
      return 'Hati-hati (${formatPercentage(percentageUsed)})';
    } else if (percentageUsed <= 100) {
      return 'Hampir Habis (${formatPercentage(percentageUsed)})';
    } else {
      return 'Over Budget (${formatPercentage(percentageUsed)})';
    }
  }

  // ===== TRANSACTION FORMATTING =====

  /// Format transaction amount with sign
  static String formatTransactionAmount(double amount, String type) {
    final sign = type.toLowerCase() == 'income' ? '+' : '-';
    return '$sign${formatCurrency(amount)}';
  }

  /// Format transaction type
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

  // ===== SAVINGS GOALS =====

  /// Format savings goal progress
  static String formatSavingsProgress(double current, double target) {
    final percentage = target > 0 ? (current / target * 100).clamp(0, 100).toDouble() : 0.0;
    return '${formatCurrency(current)} / ${formatCurrency(target)} (${formatPercentage(percentage)})';
  }

  /// Format days remaining for savings goal
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

  // ===== VALIDATION HELPERS =====

  /// Parse currency string to double
  static double parseCurrency(String currencyString) {
    try {
      final cleanString = currencyString
          .replaceAll('Rp', '')
          .replaceAll('.', '')
          .replaceAll(',', '.')
          .trim();
      return double.tryParse(cleanString) ?? 0.0;
    } catch (e) {
      return 0.0;
    }
  }

  /// Format input currency (for text fields)
  static String formatInputCurrency(String input) {
    try {
      final number = double.tryParse(input.replaceAll(RegExp(r'[^0-9]'), '')) ?? 0;
      return formatCurrency(number);
    } catch (e) {
      return 'Rp 0';
    }
  }

  // ===== PERIOD FORMATTING =====

  /// Format period name
  static String formatPeriodName(String period) {
    switch (period.toLowerCase()) {
      case 'daily':
        return 'Harian';
      case 'weekly':
        return 'Mingguan';
      case 'monthly':
        return 'Bulanan';
      case 'yearly':
        return 'Tahunan';
      default:
        return period;
    }
  }

  /// Format date range
  static String formatDateRange(DateTime start, DateTime end) {
    return '${formatDate(start)} - ${formatDate(end)}';
  }

  // ===== ANALYTICS FORMATTING =====

  /// Format trend indicator
  static String formatTrend(double change, {bool showPercentage = true}) {
    if (change > 0) {
      return showPercentage 
          ? '📈 +${formatPercentage(change)}' 
          : '📈 +${formatCurrency(change)}';
    } else if (change < 0) {
      return showPercentage 
          ? '📉 ${formatPercentage(change)}' 
          : '📉 ${formatCurrency(change)}';
    } else {
      return '➡️ Tidak berubah';
    }
  }

  /// Format budget variance
  static String formatBudgetVariance(double actual, double budget) {
    final variance = actual - budget;
    final percentage = budget > 0 ? (variance / budget * 100) : 0.0;
    
    if (variance > 0) {
      return 'Over ${formatCurrency(variance)} (${formatPercentage(percentage)})';
    } else if (variance < 0) {
      return 'Under ${formatCurrency(-variance)} (${formatPercentage(-percentage)})';
    } else {
      return 'Sesuai Budget';
    }
  }

  // ===== SAFE DATA ACCESS HELPERS =====
  
  /// Safely get double value from dynamic data
  static double safeDouble(dynamic value, [double defaultValue = 0.0]) {
    if (value == null) return defaultValue;
    if (value is double) return value;
    if (value is int) return value.toDouble();
    if (value is String) return double.tryParse(value) ?? defaultValue;
    return defaultValue;
  }

  /// Safely get string value from dynamic data
  static String safeString(dynamic value, [String defaultValue = '']) {
    if (value == null) return defaultValue;
    return value.toString();
  }

  /// Safely get int value from dynamic data
  static int safeInt(dynamic value, [int defaultValue = 0]) {
    if (value == null) return defaultValue;
    if (value is int) return value;
    if (value is double) return value.round();
    if (value is String) return int.tryParse(value) ?? defaultValue;
    return defaultValue;
  }

  /// Safely get bool value from dynamic data
  static bool safeBool(dynamic value, [bool defaultValue = false]) {
    if (value == null) return defaultValue;
    if (value is bool) return value;
    if (value is String) {
      return value.toLowerCase() == 'true' || value == '1';
    }
    if (value is int) return value != 0;
    return defaultValue;
  }

  /// Safely access nested map data
  static dynamic safeGet(Map<String, dynamic>? map, String key, [dynamic defaultValue]) {
    if (map == null) return defaultValue;
    return map[key] ?? defaultValue;
  }

  /// Safely access nested map with multiple keys
  static dynamic safeGetNested(Map<String, dynamic>? map, List<String> keys, [dynamic defaultValue]) {
    if (map == null || keys.isEmpty) return defaultValue;
    
    dynamic current = map;
    for (String key in keys) {
      if (current is Map<String, dynamic> && current.containsKey(key)) {
        current = current[key];
      } else {
        return defaultValue;
      }
    }
    return current ?? defaultValue;
  }

  // ===== FINANCIAL HEALTH FORMATTING =====

  /// Format financial health score
  static String formatHealthScore(double score) {
    if (score >= 80) {
      return 'Excellent (${score.toStringAsFixed(0)}/100)';
    } else if (score >= 60) {
      return 'Good (${score.toStringAsFixed(0)}/100)';
    } else if (score >= 40) {
      return 'Fair (${score.toStringAsFixed(0)}/100)';
    } else {
      return 'Needs Improvement (${score.toStringAsFixed(0)}/100)';
    }
  }

  /// Format student level
  static String formatStudentLevel(String level) {
    final levels = {
      'beginner': '📚 Pemula',
      'developing': '📈 Berkembang',
      'competent': '🎯 Mahir',
      'expert': '🏆 Expert',
    };
    return levels[level.toLowerCase()] ?? '📊 $level';
  }

  // ===== CHART FORMATTING =====

  /// Format chart axis labels
  static String formatChartLabel(String label) {
    if (label.length > 10) {
      return '${label.substring(0, 8)}...';
    }
    return label;
  }

  /// Format chart tooltip
  static String formatChartTooltip(String category, double amount, String type) {
    return '$category\n${formatTransactionAmount(amount, type)}';
  }

  // ===== UTILITY METHODS =====

  /// Check if amount is significant (> 1000)
  static bool isSignificantAmount(double amount) {
    return amount.abs() >= 1000;
  }

  /// Format file size
  static String formatFileSize(int bytes) {
    if (bytes >= 1048576) {
      return '${(bytes / 1048576).toStringAsFixed(1)} MB';
    } else if (bytes >= 1024) {
      return '${(bytes / 1024).toStringAsFixed(1)} KB';
    } else {
      return '$bytes B';
    }
  }

  /// Format export filename
  static String formatExportFilename(String type, DateTime date) {
    try {
      final dateStr = DateFormat('yyyyMMdd_HHmmss').format(date);
      return 'lunance_${type}_$dateStr';
    } catch (e) {
      final dateStr = '${date.year}${date.month.toString().padLeft(2, '0')}${date.day.toString().padLeft(2, '0')}_${date.hour.toString().padLeft(2, '0')}${date.minute.toString().padLeft(2, '0')}${date.second.toString().padLeft(2, '0')}';
      return 'lunance_${type}_$dateStr';
    }
  }

  // ===== STUDENT CONTEXT FORMATTING =====

  /// Format university info
  static String formatUniversityInfo(String? university, String? city) {
    if (university != null && city != null) {
      return '$university, $city';
    } else if (university != null) {
      return university;
    } else if (city != null) {
      return city;
    } else {
      return 'Universitas tidak diketahui';
    }
  }

  /// Format academic period
  static String formatAcademicPeriod(int semester, int year) {
    return 'Semester $semester, $year';
  }

  /// Format graduation year
  static String formatGraduationYear(int year) {
    final currentYear = DateTime.now().year;
    if (year > currentYear) {
      return 'Lulus $year (${year - currentYear} tahun lagi)';
    } else if (year == currentYear) {
      return 'Lulus tahun ini';
    } else {
      return 'Lulus $year';
    }
  }

  // ===== ERROR FORMATTING =====

  /// Format error message for user display
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
    } else {
      return 'Terjadi kesalahan. Silakan coba lagi.';
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

  /// Get budget type color hex
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

  // ===== DASHBOARD SPECIFIC HELPERS =====

  /// Format dashboard quick stats safely
  static Map<String, String> formatDashboardQuickStats(Map<String, dynamic>? data) {
    if (data == null) {
      return {
        'real_total_savings': formatCurrency(0),
        'monthly_income': formatCurrency(0),
        'needs_spending': formatCurrency(0),
        'wants_spending': formatCurrency(0),
        'savings_spending': formatCurrency(0),
      };
    }

    final realTotalSavings = safeDouble(data['real_total_savings']);
    final monthlyIncome = safeDouble(data['monthly_income']);
    final currentSpending = data['current_month_spending'] as Map<String, dynamic>? ?? {};

    return {
      'real_total_savings': formatCurrency(realTotalSavings),
      'monthly_income': formatCurrency(monthlyIncome),
      'needs_spending': formatCurrency(safeDouble(currentSpending['needs'])),
      'wants_spending': formatCurrency(safeDouble(currentSpending['wants'])),
      'savings_spending': formatCurrency(safeDouble(currentSpending['savings'])),
    };
  }

  /// Format financial summary safely
  static Map<String, String> formatFinancialSummary(Map<String, dynamic>? data) {
    if (data == null) {
      return {
        'monthly_income': formatCurrency(0),
        'monthly_expense': formatCurrency(0),
        'net_balance': formatCurrency(0),
        'savings_rate': formatPercentage(0),
      };
    }

    return {
      'monthly_income': formatCurrency(safeDouble(data['monthly_income'])),
      'monthly_expense': formatCurrency(safeDouble(data['monthly_expense'])),
      'net_balance': formatCurrency(safeDouble(data['net_balance'])),
      'savings_rate': formatPercentage(safeDouble(data['savings_rate'])),
    };
  }

  // ===== ANALYTICS SPECIFIC HELPERS =====

  /// Format analytics chart data safely
  static List<Map<String, dynamic>> formatAnalyticsChartData(List<dynamic>? rawData) {
    if (rawData == null || rawData.isEmpty) {
      return [];
    }

    return rawData.map<Map<String, dynamic>>((item) {
      if (item is Map<String, dynamic>) {
        return {
          'period': safeString(item['period']),
          'income': safeDouble(item['income']),
          'expense': safeDouble(item['expense']),
          'net': safeDouble(item['net']),
        };
      }
      return {
        'period': '',
        'income': 0.0,
        'expense': 0.0,
        'net': 0.0,
      };
    }).toList();
  }

  /// Format categories data safely for pie chart
  static List<Map<String, dynamic>> formatCategoriesData(List<dynamic>? categoriesData) {
    if (categoriesData == null || categoriesData.isEmpty) {
      return [];
    }

    return categoriesData.map<Map<String, dynamic>>((item) {
      if (item is Map<String, dynamic>) {
        return {
          'category': safeString(item['category']),
          'amount': safeDouble(item['amount']),
          'formatted_amount': formatCurrency(safeDouble(item['amount'])),
          'percentage': safeDouble(item['percentage']),
          'color': safeString(item['color'], '#6B7280'),
        };
      }
      return {
        'category': '',
        'amount': 0.0,
        'formatted_amount': formatCurrency(0),
        'percentage': 0.0,
        'color': '#6B7280',
      };
    }).toList();
  }

  // ===== HISTORY SPECIFIC HELPERS =====

  /// Format transaction history item safely
  static Map<String, dynamic> formatTransactionHistoryItem(Map<String, dynamic>? transaction) {
    if (transaction == null) {
      return {};
    }

    final type = safeString(transaction['type']);
    final amount = safeDouble(transaction['amount']);
    
    return {
      'id': safeString(transaction['id']),
      'type': type,
      'amount': amount,
      'formatted_amount': formatTransactionAmount(amount, type),
      'category': safeString(transaction['category']),
      'budget_type': safeString(transaction['budget_type']),
      'description': safeString(transaction['description']),
      'date': safeString(transaction['date']),
      'formatted_date': safeString(transaction['formatted_date']),
      'relative_date': safeString(transaction['relative_date']),
      'status': safeString(transaction['status']),
    };
  }

  /// Format savings goal history item safely
  static Map<String, dynamic> formatSavingsGoalHistoryItem(Map<String, dynamic>? goal) {
    if (goal == null) {
      return {};
    }

    final targetAmount = safeDouble(goal['target_amount']);
    final currentAmount = safeDouble(goal['current_amount']);
    
    return {
      'id': safeString(goal['id']),
      'item_name': safeString(goal['item_name']),
      'target_amount': targetAmount,
      'current_amount': currentAmount,
      'formatted_target': formatCurrency(targetAmount),
      'formatted_current': formatCurrency(currentAmount),
      'progress_percentage': safeDouble(goal['progress_percentage']),
      'status': safeString(goal['status']),
      'target_date': safeString(goal['target_date']),
      'days_remaining': safeInt(goal['days_remaining']),
    };
  }
}