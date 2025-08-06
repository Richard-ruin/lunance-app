// lib/services/finance_service.dart - COMPLETE FIXED VERSION

import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:flutter/foundation.dart';

class FinanceService {
  static const String baseUrl = 'http://192.168.101.23:8000/api/v1';
  static const _storage = FlutterSecureStorage();

  Future<Map<String, String>> get _authHeaders async {
    final token = await _storage.read(key: 'access_token');
    return {
      'Content-Type': 'application/json',
      'Authorization': 'Bearer $token',
    };
  }

  // ===== MAIN FINANCE ENDPOINTS FOR 4 TABS =====

  /// 1. Dashboard dengan 50/30/20 Method (Dashboard Tab)
  Future<Map<String, dynamic>> getStudentDashboard() async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/finance/dashboard'),
        headers: await _authHeaders,
      );

      final result = _handleResponse(response);

      // Add fallback mechanism untuk backward compatibility
      if (result['success'] == true && result['data'] != null) {
        final data = result['data'] as Map<String, dynamic>;

        // Ensure all required fields exist with safe defaults
        _ensureRequiredFields(data);

        return result;
      }

      return result;
    } catch (e) {
      debugPrint('❌ FinanceService: Dashboard error - $e');
      return {
        'success': false,
        'message': 'Gagal mengambil dashboard: ${e.toString()}',
      };
    }
  }

  /// 2. Analytics dengan Budget Type Analysis (Analytics Tab) - ENHANCED
  Future<Map<String, dynamic>> getAnalytics({
    String period = 'monthly',
    String chartType = 'expense', // NEW: income, expense, comparison
    DateTime? startDate,
    DateTime? endDate,
  }) async {
    try {
      final queryParams = <String, String>{
        'period': period,
        'chart_type': chartType, // NEW parameter
      };

      if (startDate != null) {
        queryParams['start_date'] = startDate.toIso8601String();
      }
      if (endDate != null) {
        queryParams['end_date'] = endDate.toIso8601String();
      }

      final uri = Uri.parse('$baseUrl/finance/analytics')
          .replace(queryParameters: queryParams);

      final response = await http.get(
        uri,
        headers: await _authHeaders,
      );

      final result = _handleResponse(response);
      
      // Enhanced logging for analytics
      if (result['success'] == true) {
        debugPrint('✅ FinanceService: Analytics loaded - Period: $period, Chart: $chartType');
        final data = result['data'] as Map<String, dynamic>?;
        if (data != null) {
          final rawData = data['raw_data'] as List?;
          debugPrint('📊 Analytics raw data points: ${rawData?.length ?? 0}');
        }
      } else {
        debugPrint('❌ FinanceService: Analytics failed - ${result['message']}');
      }

      return result;
    } catch (e) {
      debugPrint('❌ FinanceService: Analytics error - $e');
      return {
        'success': false,
        'message': 'Gagal mengambil analytics: ${e.toString()}',
      };
    }
  }

  /// 3. History dengan Budget Type Filter (History Tab)
  Future<Map<String, dynamic>> getHistory({
    String? type,
    String? budgetType, // needs/wants/savings
    String? category,
    DateTime? startDate,
    DateTime? endDate,
    String? search,
    int page = 1,
    int limit = 20,
    String sortBy = 'date',
    String sortOrder = 'desc',
  }) async {
    try {
      final queryParams = <String, String>{
        'page': page.toString(),
        'limit': limit.toString(),
        'sort_by': sortBy,
        'sort_order': sortOrder,
      };

      if (type != null) queryParams['type'] = type;
      if (budgetType != null) queryParams['budget_type'] = budgetType;
      if (category != null) queryParams['category'] = category;
      if (startDate != null) {
        queryParams['start_date'] = startDate.toIso8601String();
      }
      if (endDate != null) {
        queryParams['end_date'] = endDate.toIso8601String();
      }
      if (search != null) queryParams['search'] = search;

      final uri = Uri.parse('$baseUrl/finance/history')
          .replace(queryParameters: queryParams);

      final response = await http.get(
        uri,
        headers: await _authHeaders,
      );

      final result = _handleResponse(response);
      
      if (result['success'] == true) {
        debugPrint('✅ FinanceService: History loaded - Type: $type, Budget: $budgetType');
      }

      return result;
    } catch (e) {
      debugPrint('❌ FinanceService: History error - $e');
      return {
        'success': false,
        'message': 'Gagal mengambil history: ${e.toString()}',
      };
    }
  }

  /// 4. Export Financial Data (Reports Tab)
  Future<Map<String, dynamic>> exportFinancialData({
    String format = 'csv', // csv, json, excel
    String? type, // income, expense, goals, all
    DateTime? startDate,
    DateTime? endDate,
    bool includeSummary = true,
  }) async {
    try {
      final queryParams = <String, String>{
        'format': format,
        'include_summary': includeSummary.toString(),
      };

      if (type != null) queryParams['type'] = type;
      if (startDate != null) {
        queryParams['start_date'] = startDate.toIso8601String();
      }
      if (endDate != null) {
        queryParams['end_date'] = endDate.toIso8601String();
      }

      final uri = Uri.parse('$baseUrl/finance/export')
          .replace(queryParameters: queryParams);

      final response = await http.get(
        uri,
        headers: await _authHeaders,
      );

      final result = _handleResponse(response);
      
      if (result['success'] == true) {
        debugPrint('✅ FinanceService: Export prepared - Format: $format, Type: $type');
      }

      return result;
    } catch (e) {
      debugPrint('❌ FinanceService: Export error - $e');
      return {
        'success': false,
        'message': 'Gagal export data: ${e.toString()}',
      };
    }
  }

  /// 5. Generate Summary Report (Reports Tab)
  Future<Map<String, dynamic>> generateSummaryReport({
    String period = 'monthly', // weekly, monthly, quarterly, yearly
    DateTime? startDate,
    DateTime? endDate,
  }) async {
    try {
      final queryParams = <String, String>{
        'period': period,
      };

      if (startDate != null) {
        queryParams['start_date'] = startDate.toIso8601String();
      }
      if (endDate != null) {
        queryParams['end_date'] = endDate.toIso8601String();
      }

      final uri = Uri.parse('$baseUrl/finance/reports/summary')
          .replace(queryParameters: queryParams);

      final response = await http.get(
        uri,
        headers: await _authHeaders,
      );

      final result = _handleResponse(response);
      
      if (result['success'] == true) {
        debugPrint('✅ FinanceService: Summary report generated - Period: $period');
      }

      return result;
    } catch (e) {
      debugPrint('❌ FinanceService: Summary report error - $e');
      return {
        'success': false,
        'message': 'Gagal generate summary report: ${e.toString()}',
      };
    }
  }

  // ===== HELPER ENDPOINTS =====

  /// 6. Categories (untuk dropdown di History Tab)
  Future<Map<String, dynamic>> getCategories() async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/finance/categories'),
        headers: await _authHeaders,
      );

      final result = _handleResponse(response);
      
      if (result['success'] == true) {
        debugPrint('✅ FinanceService: Categories loaded');
      }

      return result;
    } catch (e) {
      debugPrint('❌ FinanceService: Categories error - $e');
      return {
        'success': false,
        'message': 'Gagal mengambil kategori: ${e.toString()}',
      };
    }
  }

  /// 7. Basic Stats (untuk Dashboard Tab)
  Future<Map<String, dynamic>> getStats() async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/finance/stats'),
        headers: await _authHeaders,
      );

      final result = _handleResponse(response);
      
      if (result['success'] == true) {
        debugPrint('✅ FinanceService: Stats loaded');
      }

      return result;
    } catch (e) {
      debugPrint('❌ FinanceService: Stats error - $e');
      return {
        'success': false,
        'message': 'Gagal mengambil statistik: ${e.toString()}',
      };
    }
  }

  // ===== TRANSACTION MANAGEMENT =====

  /// Create new transaction
  Future<Map<String, dynamic>> createTransaction({
    required String type, // income atau expense
    required double amount,
    required String category,
    required String description,
    DateTime? date,
    List<String>? tags,
    String? notes,
  }) async {
    try {
      final body = {
        'type': type,
        'amount': amount,
        'category': category,
        'description': description,
        'date': (date ?? DateTime.now()).toIso8601String(),
        'tags': tags ?? [],
        'notes': notes,
      };

      final response = await http.post(
        Uri.parse('$baseUrl/finance/transactions'),
        headers: await _authHeaders,
        body: jsonEncode(body),
      );

      final result = _handleResponse(response);
      
      if (result['success'] == true) {
        debugPrint('✅ FinanceService: Transaction created - $type: ${_formatCurrency(amount)}');
      }

      return result;
    } catch (e) {
      debugPrint('❌ FinanceService: Create transaction error - $e');
      return {
        'success': false,
        'message': 'Gagal membuat transaksi: ${e.toString()}',
      };
    }
  }

  /// Update existing transaction
  Future<Map<String, dynamic>> updateTransaction({
    required String transactionId,
    String? type,
    double? amount,
    String? category,
    String? description,
    DateTime? date,
    List<String>? tags,
    String? notes,
  }) async {
    try {
      final body = <String, dynamic>{};

      if (type != null) body['type'] = type;
      if (amount != null) body['amount'] = amount;
      if (category != null) body['category'] = category;
      if (description != null) body['description'] = description;
      if (date != null) body['date'] = date.toIso8601String();
      if (tags != null) body['tags'] = tags;
      if (notes != null) body['notes'] = notes;

      final response = await http.put(
        Uri.parse('$baseUrl/finance/transactions/$transactionId'),
        headers: await _authHeaders,
        body: jsonEncode(body),
      );

      final result = _handleResponse(response);
      
      if (result['success'] == true) {
        debugPrint('✅ FinanceService: Transaction updated - $transactionId');
      }

      return result;
    } catch (e) {
      debugPrint('❌ FinanceService: Update transaction error - $e');
      return {
        'success': false,
        'message': 'Gagal update transaksi: ${e.toString()}',
      };
    }
  }

  /// Delete transaction
  Future<Map<String, dynamic>> deleteTransaction(String transactionId) async {
    try {
      final response = await http.delete(
        Uri.parse('$baseUrl/finance/transactions/$transactionId'),
        headers: await _authHeaders,
      );

      final result = _handleResponse(response);
      
      if (result['success'] == true) {
        debugPrint('✅ FinanceService: Transaction deleted - $transactionId');
      }

      return result;
    } catch (e) {
      debugPrint('❌ FinanceService: Delete transaction error - $e');
      return {
        'success': false,
        'message': 'Gagal hapus transaksi: ${e.toString()}',
      };
    }
  }

  // ===== SAVINGS GOALS MANAGEMENT =====

  /// Create new savings goal
  Future<Map<String, dynamic>> createSavingsGoal({
    required String itemName,
    required double targetAmount,
    String? description,
    DateTime? targetDate,
    double? monthlyTarget,
  }) async {
    try {
      final body = {
        'item_name': itemName,
        'target_amount': targetAmount,
        'description': description,
        'target_date': targetDate?.toIso8601String(),
        'monthly_target': monthlyTarget,
      };

      final response = await http.post(
        Uri.parse('$baseUrl/finance/savings-goals'),
        headers: await _authHeaders,
        body: jsonEncode(body),
      );

      final result = _handleResponse(response);
      
      if (result['success'] == true) {
        debugPrint('✅ FinanceService: Savings goal created - $itemName: ${_formatCurrency(targetAmount)}');
      }

      return result;
    } catch (e) {
      debugPrint('❌ FinanceService: Create savings goal error - $e');
      return {
        'success': false,
        'message': 'Gagal membuat target tabungan: ${e.toString()}',
      };
    }
  }

  /// Update savings goal
  Future<Map<String, dynamic>> updateSavingsGoal({
    required String goalId,
    String? itemName,
    double? targetAmount,
    String? description,
    DateTime? targetDate,
    double? monthlyTarget,
    String? status,
  }) async {
    try {
      final body = <String, dynamic>{};

      if (itemName != null) body['item_name'] = itemName;
      if (targetAmount != null) body['target_amount'] = targetAmount;
      if (description != null) body['description'] = description;
      if (targetDate != null) body['target_date'] = targetDate.toIso8601String();
      if (monthlyTarget != null) body['monthly_target'] = monthlyTarget;
      if (status != null) body['status'] = status;

      final response = await http.put(
        Uri.parse('$baseUrl/finance/savings-goals/$goalId'),
        headers: await _authHeaders,
        body: jsonEncode(body),
      );

      final result = _handleResponse(response);
      
      if (result['success'] == true) {
        debugPrint('✅ FinanceService: Savings goal updated - $goalId');
      }

      return result;
    } catch (e) {
      debugPrint('❌ FinanceService: Update savings goal error - $e');
      return {
        'success': false,
        'message': 'Gagal update target tabungan: ${e.toString()}',
      };
    }
  }

  /// Add savings to goal
  Future<Map<String, dynamic>> addSavingsToGoal({
    required String goalId,
    required double amount,
    String? note,
  }) async {
    try {
      final body = {
        'amount': amount,
        'note': note,
      };

      final response = await http.post(
        Uri.parse('$baseUrl/finance/savings-goals/$goalId/add-savings'),
        headers: await _authHeaders,
        body: jsonEncode(body),
      );

      final result = _handleResponse(response);
      
      if (result['success'] == true) {
        debugPrint('✅ FinanceService: Savings added to goal - ${_formatCurrency(amount)} to $goalId');
      }

      return result;
    } catch (e) {
      debugPrint('❌ FinanceService: Add savings error - $e');
      return {
        'success': false,
        'message': 'Gagal menambah tabungan: ${e.toString()}',
      };
    }
  }

  /// Delete savings goal
  Future<Map<String, dynamic>> deleteSavingsGoal(String goalId) async {
    try {
      final response = await http.delete(
        Uri.parse('$baseUrl/finance/savings-goals/$goalId'),
        headers: await _authHeaders,
      );

      final result = _handleResponse(response);
      
      if (result['success'] == true) {
        debugPrint('✅ FinanceService: Savings goal deleted - $goalId');
      }

      return result;
    } catch (e) {
      debugPrint('❌ FinanceService: Delete savings goal error - $e');
      return {
        'success': false,
        'message': 'Gagal hapus target tabungan: ${e.toString()}',
      };
    }
  }

  // ===== BUDGET MANAGEMENT =====

  /// Reset monthly budget
  Future<Map<String, dynamic>> resetMonthlyBudget({
    bool force = false,
    String? reason,
  }) async {
    try {
      final body = {
        'force': force,
        'reason': reason,
      };

      final response = await http.post(
        Uri.parse('$baseUrl/finance/budget/reset'),
        headers: await _authHeaders,
        body: jsonEncode(body),
      );

      final result = _handleResponse(response);
      
      if (result['success'] == true) {
        debugPrint('✅ FinanceService: Budget reset successfully');
      }

      return result;
    } catch (e) {
      debugPrint('❌ FinanceService: Budget reset error - $e');
      return {
        'success': false,
        'message': 'Gagal reset budget: ${e.toString()}',
      };
    }
  }

  /// Get budget status
  Future<Map<String, dynamic>> getBudgetStatus() async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/finance/budget/status'),
        headers: await _authHeaders,
      );

      final result = _handleResponse(response);
      
      if (result['success'] == true) {
        debugPrint('✅ FinanceService: Budget status loaded');
      }

      return result;
    } catch (e) {
      debugPrint('❌ FinanceService: Budget status error - $e');
      return {
        'success': false,
        'message': 'Gagal mengambil status budget: ${e.toString()}',
      };
    }
  }

  // ===== VALIDATION HELPERS =====

  /// Validate export format
  bool isValidExportFormat(String format) {
    return ['csv', 'json', 'excel'].contains(format.toLowerCase());
  }

  /// Validate export type
  bool isValidExportType(String type) {
    return ['income', 'expense', 'goals', 'all'].contains(type.toLowerCase());
  }

  /// Validate report period
  bool isValidReportPeriod(String period) {
    return ['weekly', 'monthly', 'quarterly', 'yearly']
        .contains(period.toLowerCase());
  }

  /// Validate transaction type
  bool isValidTransactionType(String type) {
    return ['income', 'expense'].contains(type.toLowerCase());
  }

  /// Validate chart type
  bool isValidChartType(String chartType) {
    return ['income', 'expense', 'comparison'].contains(chartType.toLowerCase());
  }

  /// Validate amount
  bool isValidAmount(double amount) {
    return amount > 0 && amount <= 1000000000; // Max 1 billion
  }

  // ===== DISPLAY NAME HELPERS =====

  /// Get export format display name
  String getExportFormatName(String format) {
    switch (format.toLowerCase()) {
      case 'csv':
        return 'CSV (Comma-Separated Values)';
      case 'json':
        return 'JSON (JavaScript Object Notation)';
      case 'excel':
        return 'Excel (Microsoft Excel)';
      default:
        return 'Unknown Format';
    }
  }

  /// Get export type display name
  String getExportTypeName(String type) {
    switch (type.toLowerCase()) {
      case 'income':
        return 'Data Pemasukan';
      case 'expense':
        return 'Data Pengeluaran';
      case 'goals':
        return 'Target Tabungan';
      case 'all':
        return 'Semua Data';
      default:
        return 'Data Keuangan';
    }
  }

  /// Get report period display name
  String getReportPeriodName(String period) {
    switch (period.toLowerCase()) {
      case 'weekly':
        return 'Laporan Mingguan';
      case 'monthly':
        return 'Laporan Bulanan';
      case 'quarterly':
        return 'Laporan Kuartalan';
      case 'yearly':
        return 'Laporan Tahunan';
      default:
        return 'Laporan Keuangan';
    }
  }

  /// Get budget type display name
  String getBudgetTypeName(String budgetType) {
    switch (budgetType.toLowerCase()) {
      case 'needs':
        return 'Kebutuhan (50%)';
      case 'wants':
        return 'Keinginan (30%)';
      case 'savings':
        return 'Tabungan (20%)';
      default:
        return 'Lainnya';
    }
  }

  /// Get transaction type display name
  String getTransactionTypeName(String type) {
    switch (type.toLowerCase()) {
      case 'income':
        return 'Pemasukan';
      case 'expense':
        return 'Pengeluaran';
      default:
        return 'Transaksi';
    }
  }

  /// Get chart type display name
  String getChartTypeName(String chartType) {
    switch (chartType.toLowerCase()) {
      case 'income':
        return 'Chart Pemasukan';
      case 'expense':
        return 'Chart Pengeluaran';
      case 'comparison':
        return 'Chart Perbandingan';
      default:
        return 'Chart Keuangan';
    }
  }

  // ===== UTILITY METHODS =====

  /// Format currency amount
  String _formatCurrency(double amount) {
    return 'Rp ${amount.toStringAsFixed(0).replaceAllMapped(RegExp(r'(\d{1,3})(?=(\d{3})+(?!\d))'), (Match m) => '${m[1]}.')}';
  }

  /// Parse currency string to double
  double parseCurrency(String currencyString) {
    try {
      // Remove "Rp", spaces, and dots
      String cleanString = currencyString
          .replaceAll('Rp', '')
          .replaceAll(' ', '')
          .replaceAll('.', '')
          .trim();

      return double.parse(cleanString);
    } catch (e) {
      debugPrint('❌ FinanceService: Error parsing currency $currencyString: $e');
      return 0.0;
    }
  }

  /// Get current user balance (mock implementation)
  Future<double> getCurrentBalance() async {
    try {
      // This would typically call an endpoint to get current balance
      // For now, return a calculated balance from recent transactions
      final dashboardData = await getStudentDashboard();
      if (dashboardData['success'] == true) {
        final data = dashboardData['data'] as Map<String, dynamic>?;
        if (data != null) {
          final quickStats = data['quick_stats'] as Map<String, dynamic>?;
          if (quickStats != null) {
            return _safeDouble(quickStats['real_total_savings']);
          }
        }
      }
      return 0.0;
    } catch (e) {
      debugPrint('❌ FinanceService: Error getting current balance: $e');
      return 0.0;
    }
  }

  /// Calculate budget utilization percentage
  double calculateBudgetUtilization(double monthlyIncome, Map<String, dynamic> spending) {
    try {
      final totalSpending = _safeDouble(spending['needs']) +
          _safeDouble(spending['wants']) +
          _safeDouble(spending['savings']);
      
      return monthlyIncome > 0 ? (totalSpending / monthlyIncome) * 100 : 0.0;
    } catch (e) {
      debugPrint('❌ FinanceService: Error calculating budget utilization: $e');
      return 0.0;
    }
  }

  /// FIXED: Add missing _ensureRequiredFields method
  void _ensureRequiredFields(Map<String, dynamic> data) {
    try {
      // Ensure quick_stats exists
      if (!data.containsKey('quick_stats')) {
        data['quick_stats'] = <String, dynamic>{};
      }

      final quickStats = data['quick_stats'] as Map<String, dynamic>;
      
      // Ensure required quick_stats fields exist
      quickStats['real_total_savings'] ??= 0.0;
      quickStats['monthly_income'] ??= 0.0;
      quickStats['current_month_spending'] ??= <String, dynamic>{
        'needs': 0.0,
        'wants': 0.0,
        'savings': 0.0,
      };

      // Ensure financial_summary exists
      if (!data.containsKey('financial_summary')) {
        data['financial_summary'] = <String, dynamic>{};
      }

      // Ensure budget_overview exists
      if (!data.containsKey('budget_overview')) {
        final monthlyIncome = _safeDouble(quickStats['monthly_income']);
        final spending = quickStats['current_month_spending'] as Map<String, dynamic>? ?? {};
        
        data['budget_overview'] = {
          'monthly_income': monthlyIncome,
          'formatted_monthly_income': _formatCurrency(monthlyIncome),
          'allocation': {
            'needs': {
              'budget': monthlyIncome * 0.5,
              'spent': _safeDouble(spending['needs']),
              'remaining': (monthlyIncome * 0.5) - _safeDouble(spending['needs']),
              'percentage_used': monthlyIncome > 0
                  ? (_safeDouble(spending['needs']) / (monthlyIncome * 0.5) * 100)
                  : 0,
            },
            'wants': {
              'budget': monthlyIncome * 0.3,
              'spent': _safeDouble(spending['wants']),
              'remaining': (monthlyIncome * 0.3) - _safeDouble(spending['wants']),
              'percentage_used': monthlyIncome > 0
                  ? (_safeDouble(spending['wants']) / (monthlyIncome * 0.3) * 100)
                  : 0,
            },
            'savings': {
              'budget': monthlyIncome * 0.2,
              'spent': _safeDouble(spending['savings']),
              'remaining': (monthlyIncome * 0.2) - _safeDouble(spending['savings']),
              'percentage_used': monthlyIncome > 0
                  ? (_safeDouble(spending['savings']) / (monthlyIncome * 0.2) * 100)
                  : 0,
            },
          },
        };
      }

      debugPrint('✅ FinanceService: Required fields ensured in dashboard data');
    } catch (e) {
      debugPrint('❌ FinanceService: Error ensuring required fields: $e');
    }
  }

  double _safeDouble(dynamic value) {
    if (value == null) return 0.0;
    if (value is double) return value;
    if (value is int) return value.toDouble();
    if (value is String) return double.tryParse(value) ?? 0.0;
    return 0.0;
  }

  // Enhanced error handling with more specific messages
  Map<String, dynamic> _handleResponse(http.Response response) {
    try {
      final Map<String, dynamic> data = jsonDecode(response.body);

      if (response.statusCode >= 200 && response.statusCode < 300) {
        return data;
      } else {
        String errorMessage = data['message'] ?? 'Terjadi kesalahan';

        if (response.statusCode == 400) {
          errorMessage = data['message'] ?? 'Data yang dikirim tidak valid';
          if (errorMessage.contains('setup')) {
            errorMessage = 'Setup keuangan belum dilakukan. Silakan setup terlebih dahulu.';
          }
        } else if (response.statusCode == 401) {
          errorMessage = 'Tidak memiliki akses. Silakan login kembali';
        } else if (response.statusCode == 404) {
          errorMessage = 'Endpoint tidak ditemukan';
        } else if (response.statusCode >= 500) {
          errorMessage = 'Terjadi kesalahan pada server';
        }

        // Add more context for finance-specific errors
        if (errorMessage.contains('export')) {
          errorMessage = 'Gagal export data. Pastikan Anda memiliki data transaksi.';
        } else if (errorMessage.contains('report')) {
          errorMessage = 'Gagal generate laporan. Coba lagi dalam beberapa saat.';
        } else if (errorMessage.contains('dashboard')) {
          errorMessage = 'Gagal memuat dashboard. Periksa koneksi internet Anda.';
        } else if (errorMessage.contains('transaction')) {
          errorMessage = 'Gagal memproses transaksi. Periksa data yang dimasukkan.';
        } else if (errorMessage.contains('goal')) {
          errorMessage = 'Gagal memproses target tabungan. Periksa data yang dimasukkan.';
        } else if (errorMessage.contains('analytics')) {
          errorMessage = 'Gagal memuat analytics. Coba ubah periode atau chart type.';
        }

        debugPrint('❌ FinanceService HTTP Error: ${response.statusCode} - $errorMessage');

        return {
          'success': false,
          'message': errorMessage,
          'status_code': response.statusCode,
        };
      }
    } catch (e) {
      String errorMessage = 'Gagal memproses response: ${e.toString()}';
      
      // Handle specific parsing errors
      if (e.toString().contains('FormatException')) {
        errorMessage = 'Format response dari server tidak valid';
      } else if (e.toString().contains('SocketException')) {
        errorMessage = 'Tidak ada koneksi internet';
      } else if (e.toString().contains('TimeoutException')) {
        errorMessage = 'Koneksi timeout. Coba lagi nanti.';
      }

      debugPrint('❌ FinanceService Response Error: $errorMessage');

      return {
        'success': false,
        'message': errorMessage,
        'status_code': 0,
      };
    }
  }

  /// Get service connection status
  Future<bool> isConnected() async {
    try {
      final response = await getStats().timeout(const Duration(seconds: 5));
      return response['success'] == true;
    } catch (e) {
      debugPrint('❌ FinanceService: Connection test failed: $e');
      return false;
    }
  }

  /// Get service health status  
  Map<String, dynamic> getServiceHealth() {
    return {
      'service_name': 'FinanceService',
      'base_url': baseUrl,
      'version': '1.0.0',
      'endpoints_available': [
        'dashboard',
        'analytics', 
        'history',
        'export',
        'categories',
        'stats',
        'transactions',
        'savings-goals',
        'budget'
      ],
      'features': [
        '50/30/20 Budget Method',
        'Real-time Analytics',
        'Transaction Management', 
        'Savings Goals',
        'Export & Reports',
        'Budget Tracking'
      ]
    };
  }
}