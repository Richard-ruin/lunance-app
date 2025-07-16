import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import '../services/finance_service.dart';

class FinanceProvider with ChangeNotifier {
  final FinanceService _financeService = FinanceService();

  // ===== 50/30/20 METHOD - LOADING STATES =====
  bool _isLoadingDashboard = false;
  bool _isLoadingAnalytics = false;
  bool _isLoadingHistory = false;
  bool _isLoadingBudgetStatus = false;
  bool _isLoadingCategories = false;
  bool _isLoadingStats = false;
  bool _isLoadingProgress = false;
  bool _isLoadingPredictions = false;
  bool _isLoadingFinancialOverview = false;
  bool _isLoadingTips = false;

  // ===== 50/30/20 METHOD - DATA STORAGE =====
  Map<String, dynamic>? _dashboardData;
  Map<String, dynamic>? _analyticsData;
  Map<String, dynamic>? _historyData;
  Map<String, dynamic>? _budgetStatusData;
  Map<String, dynamic>? _categoriesData;
  Map<String, dynamic>? _statsData;
  Map<String, dynamic>? _progressData;
  Map<String, dynamic>? _predictionsData;
  Map<String, dynamic>? _financialOverviewData;
  Map<String, dynamic>? _tipsData;

  // ===== 50/30/20 METHOD - ERROR HANDLING =====
  String? _dashboardError;
  String? _analyticsError;
  String? _historyError;
  String? _budgetStatusError;
  String? _categoriesError;
  String? _statsError;
  String? _progressError;
  String? _predictionsError;
  String? _financialOverviewError;
  String? _tipsError;

  // ===== GETTERS FOR LOADING STATES =====
  bool get isLoadingDashboard => _isLoadingDashboard;
  bool get isLoadingAnalytics => _isLoadingAnalytics;
  bool get isLoadingHistory => _isLoadingHistory;
  bool get isLoadingBudgetStatus => _isLoadingBudgetStatus;
  bool get isLoadingCategories => _isLoadingCategories;
  bool get isLoadingStats => _isLoadingStats;
  bool get isLoadingProgress => _isLoadingProgress;
  bool get isLoadingPredictions => _isLoadingPredictions;
  bool get isLoadingFinancialOverview => _isLoadingFinancialOverview;
  bool get isLoadingTips => _isLoadingTips;

  // ===== GETTERS FOR DATA =====
  Map<String, dynamic>? get dashboardData => _dashboardData;
  Map<String, dynamic>? get analyticsData => _analyticsData;
  Map<String, dynamic>? get historyData => _historyData;
  Map<String, dynamic>? get budgetStatusData => _budgetStatusData;
  Map<String, dynamic>? get categoriesData => _categoriesData;
  Map<String, dynamic>? get statsData => _statsData;
  Map<String, dynamic>? get progressData => _progressData;
  Map<String, dynamic>? get predictionsData => _predictionsData;
  Map<String, dynamic>? get financialOverviewData => _financialOverviewData;
  Map<String, dynamic>? get tipsData => _tipsData;

  // ===== GETTERS FOR ERRORS =====
  String? get dashboardError => _dashboardError;
  String? get analyticsError => _analyticsError;
  String? get historyError => _historyError;
  String? get budgetStatusError => _budgetStatusError;
  String? get categoriesError => _categoriesError;
  String? get statsError => _statsError;
  String? get progressError => _progressError;
  String? get predictionsError => _predictionsError;
  String? get financialOverviewError => _financialOverviewError;
  String? get tipsError => _tipsError;

  // ===== 50/30/20 METHOD - MAIN METHODS =====

  // 1. Load Dashboard 50/30/20
  Future<void> loadDashboard() async {
    if (_isLoadingDashboard) return;
    
    _isLoadingDashboard = true;
    _dashboardError = null;
    
    // FIX: Use addPostFrameCallback to avoid setState during build
    WidgetsBinding.instance.addPostFrameCallback((_) {
      notifyListeners();
    });

    try {
      final response = await _financeService.getStudentDashboard();
      
      if (response['success'] == true) {
        _dashboardData = response['data'];
        _dashboardError = null;
      } else {
        _dashboardError = response['message'] ?? 'Gagal memuat dashboard';
        _dashboardData = null;
      }
    } catch (e) {
      _dashboardError = 'Terjadi kesalahan: ${e.toString()}';
      _dashboardData = null;
    } finally {
      _isLoadingDashboard = false;
      WidgetsBinding.instance.addPostFrameCallback((_) {
        notifyListeners();
      });
    }
  }

  // 2. Load Analytics dengan Budget Analysis
  Future<void> loadAnalytics({
    String period = 'monthly',
    DateTime? startDate,
    DateTime? endDate,
  }) async {
    if (_isLoadingAnalytics) return;
    
    _isLoadingAnalytics = true;
    _analyticsError = null;
    
    WidgetsBinding.instance.addPostFrameCallback((_) {
      notifyListeners();
    });

    try {
      final response = await _financeService.getAnalytics(
        period: period,
        startDate: startDate,
        endDate: endDate,
      );
      
      if (response['success'] == true) {
        _analyticsData = response['data'];
        _analyticsError = null;
      } else {
        _analyticsError = response['message'] ?? 'Gagal memuat analytics';
        _analyticsData = null;
      }
    } catch (e) {
      _analyticsError = 'Terjadi kesalahan: ${e.toString()}';
      _analyticsData = null;
    } finally {
      _isLoadingAnalytics = false;
      WidgetsBinding.instance.addPostFrameCallback((_) {
        notifyListeners();
      });
    }
  }

  // 3. Load History dengan Budget Type Filter
  Future<void> loadHistory({
    String? type,
    String? budgetType,
    String? category,
    DateTime? startDate,
    DateTime? endDate,
    String? search,
    int page = 1,
    int limit = 20,
    String sortBy = 'date',
    String sortOrder = 'desc',
  }) async {
    if (_isLoadingHistory) return;
    
    _isLoadingHistory = true;
    _historyError = null;
    
    WidgetsBinding.instance.addPostFrameCallback((_) {
      notifyListeners();
    });

    try {
      final response = await _financeService.getHistory(
        type: type,
        budgetType: budgetType,
        category: category,
        startDate: startDate,
        endDate: endDate,
        search: search,
        page: page,
        limit: limit,
        sortBy: sortBy,
        sortOrder: sortOrder,
      );
      
      if (response['success'] == true) {
        _historyData = response['data'];
        _historyError = null;
      } else {
        _historyError = response['message'] ?? 'Gagal memuat history';
        _historyData = null;
      }
    } catch (e) {
      _historyError = 'Terjadi kesalahan: ${e.toString()}';
      _historyData = null;
    } finally {
      _isLoadingHistory = false;
      WidgetsBinding.instance.addPostFrameCallback((_) {
        notifyListeners();
      });
    }
  }

  // 4. Load Budget Status 50/30/20
  Future<void> loadBudgetStatus() async {
    if (_isLoadingBudgetStatus) return;
    
    _isLoadingBudgetStatus = true;
    _budgetStatusError = null;
    
    WidgetsBinding.instance.addPostFrameCallback((_) {
      notifyListeners();
    });

    try {
      final response = await _financeService.getBudgetStatus();
      
      if (response['success'] == true) {
        _budgetStatusData = response['data'];
        _budgetStatusError = null;
      } else {
        _budgetStatusError = response['message'] ?? 'Gagal memuat status budget';
        _budgetStatusData = null;
      }
    } catch (e) {
      _budgetStatusError = 'Terjadi kesalahan: ${e.toString()}';
      _budgetStatusData = null;
    } finally {
      _isLoadingBudgetStatus = false;
      WidgetsBinding.instance.addPostFrameCallback((_) {
        notifyListeners();
      });
    }
  }

  // 5. Load Categories dengan Budget Type
  Future<void> loadCategories() async {
    if (_isLoadingCategories) return;
    
    _isLoadingCategories = true;
    _categoriesError = null;
    
    WidgetsBinding.instance.addPostFrameCallback((_) {
      notifyListeners();
    });

    try {
      final response = await _financeService.getCategories();
      
      if (response['success'] == true) {
        _categoriesData = response['data'];
        _categoriesError = null;
      } else {
        _categoriesError = response['message'] ?? 'Gagal memuat kategori';
        _categoriesData = null;
      }
    } catch (e) {
      _categoriesError = 'Terjadi kesalahan: ${e.toString()}';
      _categoriesData = null;
    } finally {
      _isLoadingCategories = false;
      WidgetsBinding.instance.addPostFrameCallback((_) {
        notifyListeners();
      });
    }
  }

  // 6. Load Stats dengan Budget Breakdown
  Future<void> loadStats() async {
    if (_isLoadingStats) return;
    
    _isLoadingStats = true;
    _statsError = null;
    
    WidgetsBinding.instance.addPostFrameCallback((_) {
      notifyListeners();
    });

    try {
      final response = await _financeService.getStats();
      
      if (response['success'] == true) {
        _statsData = response['data'];
        _statsError = null;
      } else {
        _statsError = response['message'] ?? 'Gagal memuat statistik';
        _statsData = null;
      }
    } catch (e) {
      _statsError = 'Terjadi kesalahan: ${e.toString()}';
      _statsData = null;
    } finally {
      _isLoadingStats = false;
      WidgetsBinding.instance.addPostFrameCallback((_) {
        notifyListeners();
      });
    }
  }

  // 7. Load Progress dengan Savings Goals
  Future<void> loadProgress() async {
    if (_isLoadingProgress) return;
    
    _isLoadingProgress = true;
    _progressError = null;
    
    WidgetsBinding.instance.addPostFrameCallback((_) {
      notifyListeners();
    });

    try {
      final response = await _financeService.getProgress();
      
      if (response['success'] == true) {
        _progressData = response['data'];
        _progressError = null;
      } else {
        _progressError = response['message'] ?? 'Gagal memuat progress';
        _progressData = null;
      }
    } catch (e) {
      _progressError = 'Terjadi kesalahan: ${e.toString()}';
      _progressData = null;
    } finally {
      _isLoadingProgress = false;
      WidgetsBinding.instance.addPostFrameCallback((_) {
        notifyListeners();
      });
    }
  }

  // 8. Load Predictions
  Future<void> loadPredictions({
    int daysAhead = 30,
    String type = 'both',
  }) async {
    if (_isLoadingPredictions) return;
    
    _isLoadingPredictions = true;
    _predictionsError = null;
    
    WidgetsBinding.instance.addPostFrameCallback((_) {
      notifyListeners();
    });

    try {
      final response = await _financeService.getPredictions(
        daysAhead: daysAhead,
        type: type,
      );
      
      if (response['success'] == true) {
        _predictionsData = response['data'];
        _predictionsError = null;
      } else {
        _predictionsError = response['message'] ?? 'Gagal memuat prediksi';
        _predictionsData = null;
      }
    } catch (e) {
      _predictionsError = 'Terjadi kesalahan: ${e.toString()}';
      _predictionsData = null;
    } finally {
      _isLoadingPredictions = false;
      WidgetsBinding.instance.addPostFrameCallback((_) {
        notifyListeners();
      });
    }
  }

  // 9. Load Financial Overview
  Future<void> loadFinancialOverview() async {
    if (_isLoadingFinancialOverview) return;
    
    _isLoadingFinancialOverview = true;
    _financialOverviewError = null;
    
    WidgetsBinding.instance.addPostFrameCallback((_) {
      notifyListeners();
    });

    try {
      final response = await _financeService.getFinancialOverview();
      
      if (response['success'] == true) {
        _financialOverviewData = response['data'];
        _financialOverviewError = null;
      } else {
        _financialOverviewError = response['message'] ?? 'Gagal memuat overview';
        _financialOverviewData = null;
      }
    } catch (e) {
      _financialOverviewError = 'Terjadi kesalahan: ${e.toString()}';
      _financialOverviewData = null;
    } finally {
      _isLoadingFinancialOverview = false;
      WidgetsBinding.instance.addPostFrameCallback((_) {
        notifyListeners();
      });
    }
  }

  // 10. Load Student Tips
  Future<void> loadStudentTips() async {
    if (_isLoadingTips) return;
    
    _isLoadingTips = true;
    _tipsError = null;
    
    WidgetsBinding.instance.addPostFrameCallback((_) {
      notifyListeners();
    });

    try {
      final response = await _financeService.getStudentFinancialTips();
      
      if (response['success'] == true) {
        _tipsData = response['data'];
        _tipsError = null;
      } else {
        _tipsError = response['message'] ?? 'Gagal memuat tips';
        _tipsData = null;
      }
    } catch (e) {
      _tipsError = 'Terjadi kesalahan: ${e.toString()}';
      _tipsData = null;
    } finally {
      _isLoadingTips = false;
      WidgetsBinding.instance.addPostFrameCallback((_) {
        notifyListeners();
      });
    }
  }

  // ===== 50/30/20 METHOD - UTILITY METHODS =====

  // Update Financial Settings
  Future<bool> updateFinancialSettings({
    double? currentSavings,
    double? monthlyIncome,
    String? primaryBank,
  }) async {
    try {
      final response = await _financeService.updateFinancialSettings(
        currentSavings: currentSavings,
        monthlyIncome: monthlyIncome,
        primaryBank: primaryBank,
      );
      
      if (response['success'] == true) {
        // Refresh related data
        await loadDashboard();
        await loadBudgetStatus();
        return true;
      } else {
        return false;
      }
    } catch (e) {
      return false;
    }
  }

  // Reset Monthly Budget
  Future<bool> resetMonthlyBudget() async {
    try {
      final response = await _financeService.resetMonthlyBudget();
      
      if (response['success'] == true) {
        // Refresh budget-related data
        await loadBudgetStatus();
        await loadDashboard();
        return true;
      } else {
        return false;
      }
    } catch (e) {
      return false;
    }
  }

  // Load All Essential Data (50/30/20)
  Future<void> loadAllEssentialData() async {
    try {
      // Load categories first as they're needed by other components
      await loadCategories();
      
      // Load essential data in parallel
      final futures = <Future<void>>[];
      
      if (_dashboardData == null && !_isLoadingDashboard) {
        futures.add(loadDashboard());
      }
      
      if (_budgetStatusData == null && !_isLoadingBudgetStatus) {
        futures.add(loadBudgetStatus());
      }
      
      if (_statsData == null && !_isLoadingStats) {
        futures.add(loadStats());
      }
      
      if (_progressData == null && !_isLoadingProgress) {
        futures.add(loadProgress());
      }
      
      // Wait for all to complete
      await Future.wait(futures, eagerError: false);
    } catch (e) {
      debugPrint('Error loading essential data: $e');
    }
  }

  // Refresh All Data
  Future<void> refreshAllData() async {
    clearAllData();
    await loadAllEssentialData();
  }

  // Clear All Data
  void clearAllData() {
    _dashboardData = null;
    _analyticsData = null;
    _historyData = null;
    _budgetStatusData = null;
    _categoriesData = null;
    _statsData = null;
    _progressData = null;
    _predictionsData = null;
    _financialOverviewData = null;
    _tipsData = null;
    
    clearAllErrors();
    
    WidgetsBinding.instance.addPostFrameCallback((_) {
      notifyListeners();
    });
  }

  // Clear All Errors
  void clearAllErrors() {
    _dashboardError = null;
    _analyticsError = null;
    _historyError = null;
    _budgetStatusError = null;
    _categoriesError = null;
    _statsError = null;
    _progressError = null;
    _predictionsError = null;
    _financialOverviewError = null;
    _tipsError = null;
  }

  // Export Data
  Future<Map<String, dynamic>?> exportData({
    String format = 'csv',
    String? type,
    DateTime? startDate,
    DateTime? endDate,
  }) async {
    try {
      final response = await _financeService.exportData(
        format: format,
        type: type,
        startDate: startDate,
        endDate: endDate,
      );
      
      if (response['success'] == true) {
        return response['data'];
      } else {
        return null;
      }
    } catch (e) {
      return null;
    }
  }

  // ===== HELPER METHODS =====

  // Safe double conversion
  double _safeDouble(dynamic value) {
    if (value == null) return 0.0;
    if (value is double) return value;
    if (value is int) return value.toDouble();
    if (value is String) return double.tryParse(value) ?? 0.0;
    return 0.0;
  }

  // Get Budget Health Color
  Color getBudgetHealthColor(String? health) {
    switch (health) {
      case 'excellent':
        return const Color(0xFF10B981); // Success green
      case 'good':
        return const Color(0xFF3B82F6); // Primary blue
      case 'warning':
        return const Color(0xFFF59E0B); // Warning yellow
      case 'over_budget':
        return const Color(0xFFEF4444); // Error red
      default:
        return const Color(0xFF6B7280); // Gray
    }
  }

  // Get Budget Type Color
  Color getBudgetTypeColor(String? budgetType) {
    switch (budgetType) {
      case 'needs':
        return const Color(0xFF22C55E); // Green
      case 'wants':
        return const Color(0xFFF59E0B); // Orange
      case 'savings':
        return const Color(0xFF3B82F6); // Blue
      default:
        return const Color(0xFF6B7280); // Gray
    }
  }

  // Get Budget Type Icon
  String getBudgetTypeIcon(String? budgetType) {
    switch (budgetType) {
      case 'needs':
        return '🏠'; // House
      case 'wants':
        return '🎯'; // Target
      case 'savings':
        return '💰'; // Money bag
      default:
        return '📊'; // Chart
    }
  }

  // Get Budget Type Name
  String getBudgetTypeName(String? budgetType) {
    switch (budgetType) {
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

  // ===== LEGACY SUPPORT =====

  // Legacy methods for backward compatibility
  @Deprecated('Use loadDashboard() instead')
  Future<void> loadDashboardSummary() async {
    await loadDashboard();
  }

  @Deprecated('Use loadCategories() instead')
  Future<void> loadAvailableCategories() async {
    await loadCategories();
  }

  @Deprecated('Use loadHistory() instead')
  Future<void> loadTransactionHistory({
    String? type,
    String? category,
    DateTime? startDate,
    DateTime? endDate,
    String? search,
    int page = 1,
    int limit = 20,
  }) async {
    await loadHistory(
      type: type,
      category: category,
      startDate: startDate,
      endDate: endDate,
      search: search,
      page: page,
      limit: limit,
    );
  }

  // NEW: Add the missing method for history tab
  Future<void> loadStudentTransactionHistory({
    String? type,
    String? budgetType,
    String? category,
    DateTime? startDate,
    DateTime? endDate,
    double? minAmount,
    double? maxAmount,
    String? search,
    int page = 1,
    int limit = 20,
    String sortBy = 'date',
    String sortOrder = 'desc',
  }) async {
    await loadHistory(
      type: type,
      budgetType: budgetType,
      category: category,
      startDate: startDate,
      endDate: endDate,
      search: search,
      page: page,
      limit: limit,
      sortBy: sortBy,
      sortOrder: sortOrder,
    );
  }

  // Legacy chart methods
  Map<String, dynamic>? get timeSeriesChartData => _analyticsData;
  Map<String, dynamic>? get categoryChartData => _analyticsData;
  bool get isLoadingCharts => _isLoadingAnalytics;
  String? get chartsError => _analyticsError;

  // Legacy methods
  Future<void> loadTimeSeriesChartData({String period = 'monthly'}) async {
    await loadAnalytics(period: period);
  }

  Future<void> loadCategoryChartData({String type = 'expense', String period = 'monthly'}) async {
    await loadAnalytics(period: period);
  }

  Future<void> loadFinancialPredictions({int daysAhead = 30, String type = 'both'}) async {
    await loadPredictions(daysAhead: daysAhead, type: type);
  }

  Future<void> loadBasicStats() async {
    await loadStats();
  }

  Future<void> loadProgressData() async {
    await loadProgress();
  }
}