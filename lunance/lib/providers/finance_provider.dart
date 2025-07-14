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
  bool _isLoadingInsights = false;
  bool _isLoadingRecommendations = false;

  // Data
  Map<String, dynamic>? _dashboardData;
  Map<String, dynamic>? _historyData;
  Map<String, dynamic>? _timeSeriesChartData;
  Map<String, dynamic>? _categoryChartData;
  Map<String, dynamic>? _progressData;
  Map<String, dynamic>? _predictionsData;
  Map<String, dynamic>? _statsData;
  Map<String, dynamic>? _categoriesData;
  Map<String, dynamic>? _insightsData;
  Map<String, dynamic>? _recommendationsData;

  // Error messages
  String? _dashboardError;
  String? _historyError;
  String? _chartsError;
  String? _progressError;
  String? _predictionsError;
  String? _statsError;
  String? _insightsError;
  String? _recommendationsError;

  // Getters for loading states
  bool get isLoadingDashboard => _isLoadingDashboard;
  bool get isLoadingHistory => _isLoadingHistory;
  bool get isLoadingCharts => _isLoadingCharts;
  bool get isLoadingProgress => _isLoadingProgress;
  bool get isLoadingPredictions => _isLoadingPredictions;
  bool get isLoadingStats => _isLoadingStats;
  bool get isLoadingInsights => _isLoadingInsights;
  bool get isLoadingRecommendations => _isLoadingRecommendations;

  // Getters for data
  Map<String, dynamic>? get dashboardData => _dashboardData;
  Map<String, dynamic>? get historyData => _historyData;
  Map<String, dynamic>? get timeSeriesChartData => _timeSeriesChartData;
  Map<String, dynamic>? get categoryChartData => _categoryChartData;
  Map<String, dynamic>? get progressData => _progressData;
  Map<String, dynamic>? get predictionsData => _predictionsData;
  Map<String, dynamic>? get statsData => _statsData;
  Map<String, dynamic>? get categoriesData => _categoriesData;
  Map<String, dynamic>? get insightsData => _insightsData;
  Map<String, dynamic>? get recommendationsData => _recommendationsData;

  // Getters for errors
  String? get dashboardError => _dashboardError;
  String? get historyError => _historyError;
  String? get chartsError => _chartsError;
  String? get progressError => _progressError;
  String? get predictionsError => _predictionsError;
  String? get statsError => _statsError;
  String? get insightsError => _insightsError;
  String? get recommendationsError => _recommendationsError;

  // 1. Load Student Dashboard Summary (UPDATED)
  Future<void> loadStudentDashboardSummary() async {
    if (_isLoadingDashboard) return; // Prevent multiple calls
    
    _isLoadingDashboard = true;
    _dashboardError = null;
    notifyListeners();

    try {
      final response = await _financeService.getStudentDashboardSummary();
      
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

  // 2. Load Student Categories (NEW)
  Future<void> loadStudentCategories() async {
    try {
      final response = await _financeService.getStudentCategories();
      
      if (response['success'] == true) {
        _categoriesData = response['data'];
        notifyListeners();
      }
    } catch (e) {
      debugPrint('Error loading student categories: $e');
    }
  }

  // 3. Load Student Transaction History (UPDATED)
  Future<void> loadStudentTransactionHistory({
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
      final response = await _financeService.getStudentTransactionHistory(
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

  // 4. Load Student Financial Insights (NEW)
  Future<void> loadStudentInsights({
    String period = 'monthly',
  }) async {
    if (_isLoadingInsights) return; // Prevent multiple calls
    
    _isLoadingInsights = true;
    _insightsError = null;
    notifyListeners();

    try {
      final response = await _financeService.getStudentInsights(period: period);
      
      if (response['success'] == true) {
        _insightsData = response['data'];
        _insightsError = null;
      } else {
        _insightsError = response['message'];
        _insightsData = null;
      }
    } catch (e) {
      _insightsError = 'Terjadi kesalahan: ${e.toString()}';
      _insightsData = null;
    } finally {
      _isLoadingInsights = false;
      notifyListeners();
    }
  }

  // 5. Load Student Recommendations (NEW)
  Future<void> loadStudentRecommendations() async {
    if (_isLoadingRecommendations) return; // Prevent multiple calls
    
    _isLoadingRecommendations = true;
    _recommendationsError = null;
    notifyListeners();

    try {
      final response = await _financeService.getStudentRecommendations();
      
      if (response['success'] == true) {
        _recommendationsData = response['data'];
        _recommendationsError = null;
      } else {
        _recommendationsError = response['message'];
        _recommendationsData = null;
      }
    } catch (e) {
      _recommendationsError = 'Terjadi kesalahan: ${e.toString()}';
      _recommendationsData = null;
    } finally {
      _isLoadingRecommendations = false;
      notifyListeners();
    }
  }

  // 6. Load Time Series Chart Data (UNCHANGED)
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

  // 7. Load Category Chart Data (UNCHANGED)
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

  // 8. Load Progress Data (UNCHANGED)
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

  // 9. Load Financial Predictions (UNCHANGED)
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

  // 10. Load Basic Stats (UNCHANGED)
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

  // LEGACY METHODS (for backward compatibility)
  
  @Deprecated('Use loadStudentDashboardSummary() instead')
  Future<void> loadDashboardSummary() async {
    await loadStudentDashboardSummary();
  }

  @Deprecated('Use loadStudentCategories() instead')
  Future<void> loadAvailableCategories() async {
    await loadStudentCategories();
  }

  @Deprecated('Use loadStudentTransactionHistory() instead')
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
    await loadStudentTransactionHistory(
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
  }

  // Utility methods
  void clearErrors() {
    _dashboardError = null;
    _historyError = null;
    _chartsError = null;
    _progressError = null;
    _predictionsError = null;
    _statsError = null;
    _insightsError = null;
    _recommendationsError = null;
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
    _insightsData = null;
    _recommendationsData = null;
    notifyListeners();
  }

  // Load all essential data for student dashboard
  Future<void> loadAllStudentEssentialData() async {
    // Load student categories first as they're needed by other components
    await loadStudentCategories();
    
    // Load essential data in parallel but handle errors individually
    final futures = <Future<void>>[];
    
    if (_dashboardData == null && !_isLoadingDashboard) {
      futures.add(loadStudentDashboardSummary());
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

  // For backward compatibility
  @Deprecated('Use loadAllStudentEssentialData() instead')
  Future<void> loadAllEssentialData() async {
    await loadAllStudentEssentialData();
  }

  // Force refresh all student data
  Future<void> refreshAllStudentData() async {
    clearAllData();
    await loadAllStudentEssentialData();
  }

  // Export financial data (NEW)
  Future<Map<String, dynamic>?> exportFinancialData({
    String format = 'csv',
    DateTime? startDate,
    DateTime? endDate,
  }) async {
    try {
      final response = await _financeService.exportFinancialData(
        format: format,
        startDate: startDate,
        endDate: endDate,
      );
      
      if (response['success'] == true) {
        return response['data'];
      } else {
        debugPrint('Export failed: ${response['message']}');
        return null;
      }
    } catch (e) {
      debugPrint('Export error: $e');
      return null;
    }
  }
}