import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import '../services/finance_service.dart';

class FinanceProvider with ChangeNotifier {
  final FinanceService _financeService = FinanceService();

  // ===== LOADING STATES =====
  bool _isLoadingDashboard = false;
  bool _isLoadingAnalytics = false;
  bool _isLoadingHistory = false;

  // ===== DATA STORAGE - TYPE SAFE =====
  Map<String, dynamic>? _dashboardData;
  Map<String, dynamic>? _analyticsData;
  Map<String, dynamic>? _historyData;

  // ===== ERROR HANDLING =====
  String? _dashboardError;
  String? _analyticsError;
  String? _historyError;

  // ===== GETTERS =====
  bool get isLoadingDashboard => _isLoadingDashboard;
  bool get isLoadingAnalytics => _isLoadingAnalytics;
  bool get isLoadingHistory => _isLoadingHistory;

  Map<String, dynamic>? get dashboardData => _dashboardData;
  Map<String, dynamic>? get analyticsData => _analyticsData;
  Map<String, dynamic>? get historyData => _historyData;

  String? get dashboardError => _dashboardError;
  String? get analyticsError => _analyticsError;
  String? get historyError => _historyError;

  // ===== MAIN METHODS WITH TYPE SAFETY =====

  // 1. Load Dashboard - TYPE SAFE
  Future<void> loadDashboard() async {
    if (_isLoadingDashboard) return;
    
    _isLoadingDashboard = true;
    _dashboardError = null;
    
    // Use addPostFrameCallback to avoid setState during build
    WidgetsBinding.instance.addPostFrameCallback((_) {
      notifyListeners();
    });

    try {
      final response = await _financeService.getStudentDashboard();
      
      if (response['success'] == true) {
        // FIXED: Type-safe data handling
        final data = response['data'];
        _dashboardData = _convertToTypeSafeMap(data);
        _dashboardError = null;
        
        debugPrint('Dashboard loaded successfully');
      } else {
        _dashboardError = response['message']?.toString() ?? 'Gagal memuat dashboard';
        _dashboardData = null;
        debugPrint('Dashboard loading failed: $_dashboardError');
      }
    } catch (e) {
      _dashboardError = 'Terjadi kesalahan: ${e.toString()}';
      _dashboardData = null;
      debugPrint('Dashboard loading error: $e');
    } finally {
      _isLoadingDashboard = false;
      WidgetsBinding.instance.addPostFrameCallback((_) {
        notifyListeners();
      });
    }
  }

  // 2. Load Analytics - TYPE SAFE
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
        // FIXED: Type-safe data handling
        final data = response['data'];
        _analyticsData = _convertToTypeSafeMap(data);
        _analyticsError = null;
        
        debugPrint('Analytics loaded successfully');
      } else {
        _analyticsError = response['message']?.toString() ?? 'Gagal memuat analytics';
        _analyticsData = null;
        debugPrint('Analytics loading failed: $_analyticsError');
      }
    } catch (e) {
      _analyticsError = 'Terjadi kesalahan: ${e.toString()}';
      _analyticsData = null;
      debugPrint('Analytics loading error: $e');
    } finally {
      _isLoadingAnalytics = false;
      WidgetsBinding.instance.addPostFrameCallback((_) {
        notifyListeners();
      });
    }
  }

  // 3. Load History - TYPE SAFE
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
        // FIXED: Type-safe data handling
        final data = response['data'];
        _historyData = _convertToTypeSafeMap(data);
        _historyError = null;
        
        debugPrint('History loaded successfully');
      } else {
        _historyError = response['message']?.toString() ?? 'Gagal memuat history';
        _historyData = null;
        debugPrint('History loading failed: $_historyError');
      }
    } catch (e) {
      _historyError = 'Terjadi kesalahan: ${e.toString()}';
      _historyData = null;
      debugPrint('History loading error: $e');
    } finally {
      _isLoadingHistory = false;
      WidgetsBinding.instance.addPostFrameCallback((_) {
        notifyListeners();
      });
    }
  }

  // ===== TYPE SAFETY HELPER METHODS =====

  /// FIXED: Convert dynamic data to type-safe Map<String, dynamic>
  Map<String, dynamic>? _convertToTypeSafeMap(dynamic data) {
    if (data == null) return null;
    
    try {
      if (data is Map<String, dynamic>) {
        // Already correct type
        return _deepConvertMap(data);
      } else if (data is Map<dynamic, dynamic>) {
        // Convert Map<dynamic, dynamic> to Map<String, dynamic>
        return _deepConvertMap(data.map((key, value) => MapEntry(key.toString(), value)));
      } else if (data is Map) {
        // Convert other Map types
        return _deepConvertMap(data.map((key, value) => MapEntry(key.toString(), value)));
      } else {
        debugPrint('Unexpected data type: ${data.runtimeType}');
        return null;
      }
    } catch (e) {
      debugPrint('Error converting data to type-safe map: $e');
      return null;
    }
  }

  /// FIXED: Deep convert map to ensure all nested maps are type-safe
  Map<String, dynamic> _deepConvertMap(Map map) {
    final result = <String, dynamic>{};
    
    for (final entry in map.entries) {
      final key = entry.key.toString();
      final value = entry.value;
      
      if (value is Map<dynamic, dynamic>) {
        result[key] = _deepConvertMap(value);
      } else if (value is Map) {
        result[key] = _deepConvertMap(value);
      } else if (value is List) {
        result[key] = _deepConvertList(value);
      } else {
        result[key] = value;
      }
    }
    
    return result;
  }

  /// FIXED: Deep convert list to ensure all nested maps are type-safe
  List<dynamic> _deepConvertList(List list) {
    return list.map((item) {
      if (item is Map<dynamic, dynamic>) {
        return _deepConvertMap(item);
      } else if (item is Map) {
        return _deepConvertMap(item);
      } else if (item is List) {
        return _deepConvertList(item);
      } else {
        return item;
      }
    }).toList();
  }

  // ===== HELPER METHODS =====

  /// Load Categories (untuk History Tab dropdown)
  Future<void> loadCategories() async {
    try {
      final response = await _financeService.getCategories();
      debugPrint('Categories loaded: ${response['success']}');
    } catch (e) {
      debugPrint('Error loading categories: $e');
    }
  }

  /// Load Stats (untuk Dashboard Tab)
  Future<void> loadStats() async {
    try {
      final response = await _financeService.getStats();
      debugPrint('Stats loaded: ${response['success']}');
    } catch (e) {
      debugPrint('Error loading stats: $e');
    }
  }

  /// Load Essential Data (untuk initialization)
  Future<void> loadAllEssentialData() async {
    try {
      final futures = <Future<void>>[];
      
      if (_dashboardData == null && !_isLoadingDashboard) {
        futures.add(loadDashboard());
      }
      
      // Wait for all to complete
      await Future.wait(futures, eagerError: false);
      debugPrint('All essential data loaded');
    } catch (e) {
      debugPrint('Error loading essential data: $e');
    }
  }

  /// Refresh All Data
  Future<void> refreshAllData() async {
    debugPrint('Refreshing all finance data...');
    clearAllData();
    await loadAllEssentialData();
  }

  /// Clear All Data
  void clearAllData() {
    _dashboardData = null;
    _analyticsData = null;
    _historyData = null;
    
    _dashboardError = null;
    _analyticsError = null;
    _historyError = null;
    
    WidgetsBinding.instance.addPostFrameCallback((_) {
      notifyListeners();
    });
  }

  // ===== UTILITY METHODS =====

  /// Get Budget Health Color
  Color getBudgetHealthColor(String? health) {
    switch (health) {
      case 'excellent':
        return const Color(0xFF10B981);
      case 'good':
        return const Color(0xFF3B82F6);
      case 'warning':
        return const Color(0xFFF59E0B);
      case 'over_budget':
        return const Color(0xFFEF4444);
      default:
        return const Color(0xFF6B7280);
    }
  }

  /// Get Budget Type Color
  Color getBudgetTypeColor(String? budgetType) {
    switch (budgetType) {
      case 'needs':
        return const Color(0xFF22C55E);
      case 'wants':
        return const Color(0xFFF59E0B);
      case 'savings':
        return const Color(0xFF3B82F6);
      default:
        return const Color(0xFF6B7280);
    }
  }

  /// Get Budget Type Icon
  String getBudgetTypeIcon(String? budgetType) {
    switch (budgetType) {
      case 'needs':
        return '🏠';
      case 'wants':
        return '🎯';
      case 'savings':
        return '💰';
      default:
        return '📊';
    }
  }

  /// Get Budget Type Name
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

  // ===== LEGACY SUPPORT FOR ANALYTICS TAB =====
  Map<String, dynamic>? get timeSeriesChartData => _analyticsData;
  Map<String, dynamic>? get categoryChartData => _analyticsData;
  bool get isLoadingCharts => _isLoadingAnalytics;
  String? get chartsError => _analyticsError;

  Future<void> loadTimeSeriesChartData({String period = 'monthly'}) async {
    await loadAnalytics(period: period);
  }

  Future<void> loadCategoryChartData({String type = 'expense', String period = 'monthly'}) async {
    await loadAnalytics(period: period);
  }

  // ===== SAFE DATA ACCESS METHODS =====

  /// Safely get nested data from dashboard
  T? getSafeDashboardData<T>(List<String> keys, [T? defaultValue]) {
    try {
      if (_dashboardData == null) return defaultValue;
      
      dynamic current = _dashboardData;
      for (final key in keys) {
        if (current is Map<String, dynamic> && current.containsKey(key)) {
          current = current[key];
        } else {
          return defaultValue;
        }
      }
      return current as T? ?? defaultValue;
    } catch (e) {
      debugPrint('Error getting dashboard data for keys $keys: $e');
      return defaultValue;
    }
  }

  /// Safely get nested data from analytics
  T? getSafeAnalyticsData<T>(List<String> keys, [T? defaultValue]) {
    try {
      if (_analyticsData == null) return defaultValue;
      
      dynamic current = _analyticsData;
      for (final key in keys) {
        if (current is Map<String, dynamic> && current.containsKey(key)) {
          current = current[key];
        } else {
          return defaultValue;
        }
      }
      return current as T? ?? defaultValue;
    } catch (e) {
      debugPrint('Error getting analytics data for keys $keys: $e');
      return defaultValue;
    }
  }

  /// Safely get nested data from history
  T? getSafeHistoryData<T>(List<String> keys, [T? defaultValue]) {
    try {
      if (_historyData == null) return defaultValue;
      
      dynamic current = _historyData;
      for (final key in keys) {
        if (current is Map<String, dynamic> && current.containsKey(key)) {
          current = current[key];
        } else {
          return defaultValue;
        }
      }
      return current as T? ?? defaultValue;
    } catch (e) {
      debugPrint('Error getting history data for keys $keys: $e');
      return defaultValue;
    }
  }

  /// Safe double conversion
  double safeDouble(dynamic value, [double defaultValue = 0.0]) {
    if (value == null) return defaultValue;
    if (value is double) return value;
    if (value is int) return value.toDouble();
    if (value is String) return double.tryParse(value) ?? defaultValue;
    return defaultValue;
  }

  /// Safe string conversion
  String safeString(dynamic value, [String defaultValue = '']) {
    if (value == null) return defaultValue;
    return value.toString();
  }

  /// Safe integer conversion
  int safeInt(dynamic value, [int defaultValue = 0]) {
    if (value == null) return defaultValue;
    if (value is int) return value;
    if (value is double) return value.round();
    if (value is String) return int.tryParse(value) ?? defaultValue;
    return defaultValue;
  }

  /// Safe boolean conversion
  bool safeBool(dynamic value, [bool defaultValue = false]) {
    if (value == null) return defaultValue;
    if (value is bool) return value;
    if (value is String) {
      return value.toLowerCase() == 'true' || value == '1';
    }
    if (value is int) return value != 0;
    return defaultValue;
  }

  /// Safe list conversion
  List<T> safeList<T>(dynamic value, [List<T> defaultValue = const []]) {
    if (value == null) return defaultValue;
    if (value is List<T>) return value;
    if (value is List) {
      try {
        return value.cast<T>();
      } catch (e) {
        debugPrint('Error casting list to List<$T>: $e');
        return defaultValue;
      }
    }
    return defaultValue;
  }

  /// Safe map conversion
  Map<String, dynamic> safeMap(dynamic value, [Map<String, dynamic> defaultValue = const {}]) {
    if (value == null) return defaultValue;
    if (value is Map<String, dynamic>) return value;
    if (value is Map) {
      try {
        return value.cast<String, dynamic>();
      } catch (e) {
        debugPrint('Error casting map to Map<String, dynamic>: $e');
        return defaultValue;
      }
    }
    return defaultValue;
  }
}