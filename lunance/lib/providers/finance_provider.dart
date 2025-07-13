import 'package:flutter/foundation.dart';
import '../services/finance_service.dart';

class FinanceProvider with ChangeNotifier {
  final FinanceService _financeService = FinanceService();

  // Loading states
  bool _isLoadingDashboard = false;
  bool _isLoadingHistory = false;
  bool _isLoadingCharts = false;
  bool _isLoadingProgress = false;
  bool _isLoadingPredictions = false;
  bool _isLoadingStats = false;

  // Data
  Map<String, dynamic>? _dashboardData;
  Map<String, dynamic>? _historyData;
  Map<String, dynamic>? _timeSeriesChartData;
  Map<String, dynamic>? _categoryChartData;
  Map<String, dynamic>? _progressData;
  Map<String, dynamic>? _predictionsData;
  Map<String, dynamic>? _statsData;
  Map<String, dynamic>? _categoriesData;

  // Error messages
  String? _dashboardError;
  String? _historyError;
  String? _chartsError;
  String? _progressError;
  String? _predictionsError;
  String? _statsError;

  // Getters for loading states
  bool get isLoadingDashboard => _isLoadingDashboard;
  bool get isLoadingHistory => _isLoadingHistory;
  bool get isLoadingCharts => _isLoadingCharts;
  bool get isLoadingProgress => _isLoadingProgress;
  bool get isLoadingPredictions => _isLoadingPredictions;
  bool get isLoadingStats => _isLoadingStats;

  // Getters for data
  Map<String, dynamic>? get dashboardData => _dashboardData;
  Map<String, dynamic>? get historyData => _historyData;
  Map<String, dynamic>? get timeSeriesChartData => _timeSeriesChartData;
  Map<String, dynamic>? get categoryChartData => _categoryChartData;
  Map<String, dynamic>? get progressData => _progressData;
  Map<String, dynamic>? get predictionsData => _predictionsData;
  Map<String, dynamic>? get statsData => _statsData;
  Map<String, dynamic>? get categoriesData => _categoriesData;

  // Getters for errors
  String? get dashboardError => _dashboardError;
  String? get historyError => _historyError;
  String? get chartsError => _chartsError;
  String? get progressError => _progressError;
  String? get predictionsError => _predictionsError;
  String? get statsError => _statsError;

  // 1. Load Dashboard Summary
  Future<void> loadDashboardSummary() async {
    if (_isLoadingDashboard) return; // Prevent multiple calls
    
    _isLoadingDashboard = true;
    _dashboardError = null;
    notifyListeners();

    try {
      final response = await _financeService.getDashboardSummary();
      
      if (response['success'] == true) {
        _dashboardData = response['data'];
        _dashboardError = null;
      } else {
        _dashboardError = response['message'];
        _dashboardData = null;
      }
    } catch (e) {
      _dashboardError = 'Terjadi kesalahan: ${e.toString()}';
      _dashboardData = null;
    } finally {
      _isLoadingDashboard = false;
      notifyListeners();
    }
  }

  // 2. Load Transaction History
  Future<void> loadTransactionHistory({
    String? type,
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
    if (_isLoadingHistory) return; // Prevent multiple calls
    
    _isLoadingHistory = true;
    _historyError = null;
    notifyListeners();

    try {
      final response = await _financeService.getTransactionHistory(
        type: type,
        category: category,
        startDate: startDate,
        endDate: endDate,
        minAmount: minAmount,
        maxAmount: maxAmount,
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
        _historyError = response['message'];
        _historyData = null;
      }
    } catch (e) {
      _historyError = 'Terjadi kesalahan: ${e.toString()}';
      _historyData = null;
    } finally {
      _isLoadingHistory = false;
      notifyListeners();
    }
  }

  // 3. Load Time Series Chart Data
  Future<void> loadTimeSeriesChartData({
    String period = 'monthly',
    DateTime? startDate,
    DateTime? endDate,
  }) async {
    if (_isLoadingCharts) return; // Prevent multiple calls
    
    _isLoadingCharts = true;
    _chartsError = null;
    notifyListeners();

    try {
      final response = await _financeService.getTimeSeriesChartData(
        period: period,
        startDate: startDate,
        endDate: endDate,
      );
      
      if (response['success'] == true) {
        _timeSeriesChartData = response['data'];
        _chartsError = null;
      } else {
        _chartsError = response['message'];
        _timeSeriesChartData = null;
      }
    } catch (e) {
      _chartsError = 'Terjadi kesalahan: ${e.toString()}';
      _timeSeriesChartData = null;
    } finally {
      _isLoadingCharts = false;
      notifyListeners();
    }
  }

  // 4. Load Category Chart Data
  Future<void> loadCategoryChartData({
    String type = 'expense',
    String period = 'monthly',
    DateTime? startDate,
    DateTime? endDate,
  }) async {
    _chartsError = null;
    notifyListeners();

    try {
      final response = await _financeService.getCategoryChartData(
        type: type,
        period: period,
        startDate: startDate,
        endDate: endDate,
      );
      
      if (response['success'] == true) {
        _categoryChartData = response['data'];
        _chartsError = null;
      } else {
        _chartsError = response['message'];
        _categoryChartData = null;
      }
    } catch (e) {
      _chartsError = 'Terjadi kesalahan: ${e.toString()}';
      _categoryChartData = null;
    } finally {
      notifyListeners();
    }
  }

  // 5. Load Progress Data
  Future<void> loadProgressData() async {
    if (_isLoadingProgress) return; // Prevent multiple calls
    
    _isLoadingProgress = true;
    _progressError = null;
    notifyListeners();

    try {
      final response = await _financeService.getProgressData();
      
      if (response['success'] == true) {
        _progressData = response['data'];
        _progressError = null;
      } else {
        _progressError = response['message'];
        _progressData = null;
      }
    } catch (e) {
      _progressError = 'Terjadi kesalahan: ${e.toString()}';
      _progressData = null;
    } finally {
      _isLoadingProgress = false;
      notifyListeners();
    }
  }

  // 6. Load Financial Predictions
  Future<void> loadFinancialPredictions({
    int daysAhead = 30,
    String type = 'both',
  }) async {
    if (_isLoadingPredictions) return; // Prevent multiple calls
    
    _isLoadingPredictions = true;
    _predictionsError = null;
    notifyListeners();

    try {
      final response = await _financeService.getFinancialPredictions(
        daysAhead: daysAhead,
        type: type,
      );
      
      if (response['success'] == true) {
        _predictionsData = response['data'];
        _predictionsError = null;
      } else {
        _predictionsError = response['message'];
        _predictionsData = null;
      }
    } catch (e) {
      _predictionsError = 'Terjadi kesalahan: ${e.toString()}';
      _predictionsData = null;
    } finally {
      _isLoadingPredictions = false;
      notifyListeners();
    }
  }

  // 7. Load Available Categories
  Future<void> loadAvailableCategories() async {
    try {
      final response = await _financeService.getAvailableCategories();
      
      if (response['success'] == true) {
        _categoriesData = response['data'];
        notifyListeners();
      }
    } catch (e) {
      debugPrint('Error loading categories: $e');
    }
  }

  // 8. Load Basic Stats
  Future<void> loadBasicStats() async {
    if (_isLoadingStats) return; // Prevent multiple calls
    
    _isLoadingStats = true;
    _statsError = null;
    notifyListeners();

    try {
      final response = await _financeService.getBasicStats();
      
      if (response['success'] == true) {
        _statsData = response['data'];
        _statsError = null;
      } else {
        _statsError = response['message'];
        _statsData = null;
      }
    } catch (e) {
      _statsError = 'Terjadi kesalahan: ${e.toString()}';
      _statsData = null;
    } finally {
      _isLoadingStats = false;
      notifyListeners();
    }
  }

  // Utility methods
  void clearErrors() {
    _dashboardError = null;
    _historyError = null;
    _chartsError = null;
    _progressError = null;
    _predictionsError = null;
    _statsError = null;
    notifyListeners();
  }

  void clearAllData() {
    _dashboardData = null;
    _historyData = null;
    _timeSeriesChartData = null;
    _categoryChartData = null;
    _progressData = null;
    _predictionsData = null;
    _statsData = null;
    _categoriesData = null;
    notifyListeners();
  }

  // Load all essential data with better error handling
  Future<void> loadAllEssentialData() async {
    // Load categories first as they're needed by other components
    await loadAvailableCategories();
    
    // Load essential data in parallel but handle errors individually
    final futures = <Future<void>>[];
    
    if (_dashboardData == null && !_isLoadingDashboard) {
      futures.add(loadDashboardSummary());
    }
    
    if (_statsData == null && !_isLoadingStats) {
      futures.add(loadBasicStats());
    }
    
    if (_progressData == null && !_isLoadingProgress) {
      futures.add(loadProgressData());
    }
    
    // Wait for all to complete, but don't throw if any fail
    await Future.wait(futures, eagerError: false);
  }

  // Force refresh all data
  Future<void> refreshAllData() async {
    clearAllData();
    await loadAllEssentialData();
  }
}