// lib/providers/prediction_provider.dart
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import '../services/prediction_service.dart';
import '../models/prediction_models.dart';
import '../utils/format_eksplore.dart';

class PredictionProvider with ChangeNotifier {
  final PredictionService _predictionService = PredictionService();

  // ===== LOADING STATES =====
  bool _isLoadingIncome = false;
  bool _isLoadingBudget = false;
  bool _isLoadingAnalytics = false;
  bool _isLoadingAll = false;

  // ===== PREDICTION DATA =====
  IncomePrediction? _incomePrediction;
  BudgetPerformancePrediction? _budgetPrediction;
  Map<String, ExpensePrediction> _expensePredictions = {};
  PredictionAnalytics? _analytics;
  Map<String, SavingsGoalPrediction> _savingsGoalPredictions = {};

  // ===== ERROR HANDLING =====
  String? _incomeError;
  String? _budgetError;
  String? _analyticsError;
  String? _generalError;

  // ===== CONFIGURATION =====
  int _forecastDays = 30;
  DateTime? _lastRefresh;

  // ===== GETTERS =====
  bool get isLoadingIncome => _isLoadingIncome;
  bool get isLoadingBudget => _isLoadingBudget;
  bool get isLoadingAnalytics => _isLoadingAnalytics;
  bool get isLoadingAll => _isLoadingAll;
  bool get hasAnyLoading => _isLoadingIncome || _isLoadingBudget || _isLoadingAnalytics || _isLoadingAll;

  IncomePrediction? get incomePrediction => _incomePrediction;
  BudgetPerformancePrediction? get budgetPrediction => _budgetPrediction;
  Map<String, ExpensePrediction> get expensePredictions => _expensePredictions;
  PredictionAnalytics? get analytics => _analytics;
  Map<String, SavingsGoalPrediction> get savingsGoalPredictions => _savingsGoalPredictions;

  String? get incomeError => _incomeError;
  String? get budgetError => _budgetError;
  String? get analyticsError => _analyticsError;
  String? get generalError => _generalError;
  bool get hasAnyError => _incomeError != null || _budgetError != null || _analyticsError != null || _generalError != null;

  int get forecastDays => _forecastDays;
  DateTime? get lastRefresh => _lastRefresh;

  // ===== DERIVED GETTERS =====
  bool get hasIncomeData => _incomePrediction != null;
  bool get hasBudgetData => _budgetPrediction != null;
  bool get hasAnalyticsData => _analytics != null;
  bool get hasExpenseData => _expensePredictions.isNotEmpty;

  double get overallHealthScore => _budgetPrediction?.budgetHealth.healthScore ?? 0.0;
  String get overallHealthLevel => _budgetPrediction?.budgetHealth.healthLevel ?? 'unknown';

  List<String> get allInsights {
    final insights = <String>[];
    if (_incomePrediction != null) insights.addAll(_incomePrediction!.aiInsights);
    if (_budgetPrediction != null) insights.addAll(_budgetPrediction!.comprehensiveInsights);
    for (final expense in _expensePredictions.values) {
      insights.addAll(expense.aiInsights);
    }
    return insights;
  }

  List<String> get allRecommendations {
    final recommendations = <String>[];
    if (_incomePrediction != null) recommendations.addAll(_incomePrediction!.recommendations);
    if (_budgetPrediction != null) recommendations.addAll(_budgetPrediction!.optimizationRecommendations);
    for (final expense in _expensePredictions.values) {
      recommendations.addAll(expense.budgetRecommendations);
    }
    return recommendations;
  }

  // ===== INCOME PREDICTION METHODS =====

  /// Load income prediction dengan error handling
  Future<void> loadIncomePrediction({int? forecastDays}) async {
    if (_isLoadingIncome) return;

    _isLoadingIncome = true;
    _incomeError = null;
    
    WidgetsBinding.instance.addPostFrameCallback((_) {
      notifyListeners();
    });

    try {
      final days = forecastDays ?? _forecastDays;
      final response = await _predictionService.predictIncome(forecastDays: days);

      if (response['success'] == true) {
        _incomePrediction = IncomePrediction.fromJson(
          FormatUtils.safeMap(response['data']),
        );
        _incomeError = null;
        debugPrint('✅ Income prediction loaded successfully');
      } else {
        _incomeError = FormatUtils.safeString(
          response['message'],
          'Gagal memuat prediksi income',
        );
        _incomePrediction = null;
        debugPrint('❌ Income prediction failed: $_incomeError');
      }
    } catch (e) {
      _incomeError = 'Terjadi kesalahan: ${e.toString()}';
      _incomePrediction = null;
      debugPrint('💥 Income prediction error: $e');
    } finally {
      _isLoadingIncome = false;
      WidgetsBinding.instance.addPostFrameCallback((_) {
        notifyListeners();
      });
    }
  }

  // ===== BUDGET PREDICTION METHODS =====

  /// Load budget performance prediction
  Future<void> loadBudgetPrediction({int? forecastDays}) async {
    if (_isLoadingBudget) return;

    _isLoadingBudget = true;
    _budgetError = null;
    
    WidgetsBinding.instance.addPostFrameCallback((_) {
      notifyListeners();
    });

    try {
      final days = forecastDays ?? _forecastDays;
      final response = await _predictionService.predictBudgetPerformance(forecastDays: days);

      if (response['success'] == true) {
        _budgetPrediction = BudgetPerformancePrediction.fromJson(
          FormatUtils.safeMap(response['data']),
        );
        _budgetError = null;
        debugPrint('✅ Budget prediction loaded successfully');

        // Also load individual expense predictions
        await _loadExpensePredictions(days);
      } else {
        _budgetError = FormatUtils.safeString(
          response['message'],
          'Gagal memuat prediksi budget',
        );
        _budgetPrediction = null;
        debugPrint('❌ Budget prediction failed: $_budgetError');
      }
    } catch (e) {
      _budgetError = 'Terjadi kesalahan: ${e.toString()}';
      _budgetPrediction = null;
      debugPrint('💥 Budget prediction error: $e');
    } finally {
      _isLoadingBudget = false;
      WidgetsBinding.instance.addPostFrameCallback((_) {
        notifyListeners();
      });
    }
  }

  /// Load individual expense predictions untuk setiap budget type
  Future<void> _loadExpensePredictions(int forecastDays) async {
    final budgetTypes = ['needs', 'wants', 'savings'];
    final newExpensePredictions = <String, ExpensePrediction>{};

    for (final budgetType in budgetTypes) {
      try {
        final response = await _predictionService.predictExpenseByBudgetType(
          budgetType: budgetType,
          forecastDays: forecastDays,
        );

        if (response['success'] == true) {
          final expensePrediction = ExpensePrediction.fromJson(
            FormatUtils.safeMap(response['data']),
          );
          newExpensePredictions[budgetType] = expensePrediction;
          debugPrint('✅ $budgetType expense prediction loaded');
        } else {
          debugPrint('❌ $budgetType expense prediction failed: ${response['message']}');
        }
      } catch (e) {
        debugPrint('💥 $budgetType expense prediction error: $e');
      }
    }

    _expensePredictions = newExpensePredictions;
  }

  // ===== ANALYTICS METHODS =====

  /// Load comprehensive analytics
  Future<void> loadPredictionAnalytics() async {
    if (_isLoadingAnalytics) return;

    _isLoadingAnalytics = true;
    _analyticsError = null;
    
    WidgetsBinding.instance.addPostFrameCallback((_) {
      notifyListeners();
    });

    try {
      final response = await _predictionService.getPredictionAnalytics();

      if (response['success'] == true) {
        _analytics = PredictionAnalytics.fromJson(
          FormatUtils.safeMap(response['data']),
        );
        _analyticsError = null;
        debugPrint('✅ Analytics loaded successfully');
      } else {
        _analyticsError = FormatUtils.safeString(
          response['message'],
          'Gagal memuat analytics',
        );
        _analytics = null;
        debugPrint('❌ Analytics failed: $_analyticsError');
      }
    } catch (e) {
      _analyticsError = 'Terjadi kesalahan: ${e.toString()}';
      _analytics = null;
      debugPrint('💥 Analytics error: $e');
    } finally {
      _isLoadingAnalytics = false;
      WidgetsBinding.instance.addPostFrameCallback((_) {
        notifyListeners();
      });
    }
  }

  // ===== COMPREHENSIVE LOADING METHODS =====

  /// Load all prediction data sekaligus
  Future<void> loadAllPredictions({int? forecastDays}) async {
    if (_isLoadingAll) return;

    _isLoadingAll = true;
    _generalError = null;
    
    WidgetsBinding.instance.addPostFrameCallback((_) {
      notifyListeners();
    });

    try {
      final days = forecastDays ?? _forecastDays;
      if (forecastDays != null) _forecastDays = days;

      // Load predictions secara paralel untuk performance
      final futures = [
        loadIncomePrediction(forecastDays: days),
        loadBudgetPrediction(forecastDays: days),
        loadPredictionAnalytics(), // FIXED: Changed from loadAnalytics() to loadPredictionAnalytics()
      ];

      await Future.wait(futures, eagerError: false);

      _lastRefresh = DateTime.now();
      debugPrint('✅ All predictions loaded successfully at $_lastRefresh');
    } catch (e) {
      _generalError = 'Gagal memuat prediksi: ${e.toString()}';
      debugPrint('💥 Load all predictions error: $e');
    } finally {
      _isLoadingAll = false;
      WidgetsBinding.instance.addPostFrameCallback((_) {
        notifyListeners();
      });
    }
  }

  /// Refresh all data
  Future<void> refreshAllPredictions() async {
    debugPrint('🔄 Refreshing all predictions...');
    clearAllData();
    await loadAllPredictions();
  }

  // ===== SAVINGS GOAL PREDICTIONS =====

  /// Load savings goal prediction
  Future<void> loadSavingsGoalPrediction(String goalId) async {
    try {
      final response = await _predictionService.predictSavingsGoalAchievement(goalId: goalId);

      if (response['success'] == true) {
        final prediction = SavingsGoalPrediction.fromJson(
          FormatUtils.safeMap(response['data']),
        );
        _savingsGoalPredictions[goalId] = prediction;
        notifyListeners();
        debugPrint('✅ Savings goal prediction loaded for $goalId');
      } else {
        debugPrint('❌ Savings goal prediction failed: ${response['message']}');
      }
    } catch (e) {
      debugPrint('💥 Savings goal prediction error: $e');
    }
  }

  // ===== CONFIGURATION METHODS =====

  /// Update forecast period
  void updateForecastDays(int days) {
    if (days == _forecastDays) return;
    
    if (!_predictionService.isValidForecastDays(days)) {
      debugPrint('❌ Invalid forecast days: $days');
      return;
    }

    _forecastDays = days;
    notifyListeners();
    debugPrint('📅 Forecast days updated to: $days');
  }

  // ===== DATA MANAGEMENT =====

  /// Clear all prediction data
  void clearAllData() {
    _incomePrediction = null;
    _budgetPrediction = null;
    _expensePredictions.clear();
    _analytics = null;
    _savingsGoalPredictions.clear();

    _incomeError = null;
    _budgetError = null;
    _analyticsError = null;
    _generalError = null;

    _lastRefresh = null;
    
    notifyListeners();
    debugPrint('🗑️ All prediction data cleared');
  }

  /// Clear specific errors
  void clearErrors() {
    _incomeError = null;
    _budgetError = null;
    _analyticsError = null;
    _generalError = null;
    notifyListeners();
  }

  void clearIncomeError() {
    _incomeError = null;
    notifyListeners();
  }

  void clearBudgetError() {
    _budgetError = null;
    notifyListeners();
  }

  void clearAnalyticsError() {
    _analyticsError = null;
    notifyListeners();
  }

  // ===== UTILITY METHODS =====

  /// Get expense prediction by budget type
  ExpensePrediction? getExpensePrediction(String budgetType) {
    return _expensePredictions[budgetType.toLowerCase()];
  }

  /// Get savings goal prediction by ID
  SavingsGoalPrediction? getSavingsGoalPrediction(String goalId) {
    return _savingsGoalPredictions[goalId];
  }

  /// Check if predictions are stale (older than 1 hour)
  bool get isPredictionStale {
    if (_lastRefresh == null) return true;
    return DateTime.now().difference(_lastRefresh!).inHours >= 1;
  }

  /// Get prediction summary untuk dashboard
  Map<String, dynamic> getPredictionSummary() {
    return {
      'has_income_data': hasIncomeData,
      'has_budget_data': hasBudgetData,
      'has_analytics_data': hasAnalyticsData,
      'overall_health_score': overallHealthScore,
      'overall_health_level': overallHealthLevel,
      'total_insights': allInsights.length,
      'total_recommendations': allRecommendations.length,
      'is_stale': isPredictionStale,
      'last_refresh': _lastRefresh?.toIso8601String(),
      'forecast_days': _forecastDays,
    };
  }

  /// Get data quality assessment
  Map<String, dynamic> getDataQuality() {
    final incomeDataPoints = _incomePrediction?.dataPointsUsed ?? 0;
    final incomeAccuracy = _incomePrediction?.modelPerformance.accuracyScore ?? 0.0;
    
    String qualityLevel;
    Color qualityColor;
    String description;
    
    if (incomeDataPoints >= 30 && incomeAccuracy >= 80) {
      qualityLevel = 'Excellent';
      qualityColor = const Color(0xFF10B981); // AppColors.success
      description = 'Data sangat cukup untuk prediksi akurat';
    } else if (incomeDataPoints >= 20 && incomeAccuracy >= 70) {
      qualityLevel = 'Good';
      qualityColor = const Color(0xFF3B82F6); // AppColors.info
      description = 'Data cukup untuk prediksi yang reliable';
    } else if (incomeDataPoints >= 10 && incomeAccuracy >= 60) {
      qualityLevel = 'Fair';
      qualityColor = const Color(0xFFF59E0B); // AppColors.warning
      description = 'Data terbatas, prediksi masih bisa digunakan';
    } else {
      qualityLevel = 'Poor';
      qualityColor = const Color(0xFFEF4444); // AppColors.error
      description = 'Data tidak cukup untuk prediksi akurat';
    }

    return {
      'data_points': incomeDataPoints,
      'model_accuracy': incomeAccuracy,
      'quality_level': qualityLevel,
      'quality_color': qualityColor,
      'description': description,
      'has_sufficient_data': incomeDataPoints >= 10,
    };
  }

  /// Get health insights dengan actionable tips
  List<Map<String, dynamic>> getHealthInsights() {
    final insights = <Map<String, dynamic>>[];

    if (_budgetPrediction != null) {
      final health = _budgetPrediction!.budgetHealth;
      
      // Overall health insight
      insights.add({
        'type': 'health_score',
        'title': 'Financial Health Score',
        'value': '${health.healthScore.toStringAsFixed(1)}/100',
        'level': health.healthLevel,
        'color': _getHealthColorFromScore(health.healthScore),
        'recommendation': _getHealthRecommendation(health.healthScore),
      });

      // Budget allocation insights
      final needsPercentage = _budgetPrediction!.needsPercentage;
      final wantsPercentage = _budgetPrediction!.wantsPercentage;
      final savingsPercentage = _budgetPrediction!.savingsPercentage;

      if ((needsPercentage - 50.0).abs() > 10.0) {
        insights.add({
          'type': 'budget_allocation',
          'title': 'Needs Budget Alert',
          'value': '${needsPercentage.toStringAsFixed(1)}%',
          'target': '50%',
          'color': const Color(0xFFF59E0B), // warning
          'recommendation': needsPercentage > 60.0 
              ? 'Pertimbangkan untuk mengurangi pengeluaran kebutuhan'
              : 'Alokasi kebutuhan terlalu rendah, pastikan kebutuhan dasar terpenuhi',
        });
      }

      if ((wantsPercentage - 30.0).abs() > 10.0) {
        insights.add({
          'type': 'budget_allocation',
          'title': 'Wants Budget Alert',
          'value': '${wantsPercentage.toStringAsFixed(1)}%',
          'target': '30%',
          'color': const Color(0xFFF59E0B), // warning
          'recommendation': wantsPercentage > 40.0 
              ? 'Kurangi pengeluaran untuk keinginan dan hiburan'
              : 'Alokasi untuk hiburan terlalu rendah, nikmati hidup sedikit',
        });
      }

      if (savingsPercentage < 15.0) {
        insights.add({
          'type': 'savings_alert',
          'title': 'Savings Alert',
          'value': '${savingsPercentage.toStringAsFixed(1)}%',
          'target': '20%',
          'color': const Color(0xFFEF4444), // error
          'recommendation': 'Tingkatkan tabungan untuk memenuhi target 20%',
        });
      }
    }

    if (_incomePrediction != null) {
      final performance = _incomePrediction!.modelPerformance;
      if (performance.accuracyScore < 70.0) {
        insights.add({
          'type': 'data_quality',
          'title': 'Data Quality Warning',
          'value': '${performance.accuracyScore.toStringAsFixed(1)}%',
          'target': '>70%',
          'color': const Color(0xFFF59E0B), // warning
          'recommendation': 'Tambahkan lebih banyak transaksi income untuk prediksi yang lebih akurat',
        });
      }
    }

    return insights;
  }

  Color _getHealthColorFromScore(double score) {
    if (score >= 80) return const Color(0xFF10B981); // success
    if (score >= 60) return const Color(0xFF3B82F6); // info
    if (score >= 40) return const Color(0xFFF59E0B); // warning
    return const Color(0xFFEF4444); // error
  }

  String _getHealthRecommendation(double score) {
    if (score >= 80) {
      return 'Keuangan Anda sangat sehat! Pertahankan pola ini.';
    } else if (score >= 60) {
      return 'Keuangan cukup sehat, ada ruang untuk perbaikan kecil.';
    } else if (score >= 40) {
      return 'Perlu perbaikan dalam manajemen budget dan tabungan.';
    } else {
      return 'Keuangan membutuhkan perhatian serius. Konsultasi dengan ahli keuangan.';
    }
  }

  /// Get predictions performance summary
  Map<String, dynamic> getPerformanceSummary() {
    final summary = <String, dynamic>{};

    if (_incomePrediction != null) {
      final performance = _incomePrediction!.modelPerformance;
      summary['income'] = {
        'accuracy': performance.accuracyScore,
        'confidence': performance.confidenceLevel,
        'data_points': performance.dataPoints,
        'mae': performance.mae,
        'mape': performance.mape,
      };
    }

    if (_expensePredictions.isNotEmpty) {
      summary['expenses'] = {};
      for (final entry in _expensePredictions.entries) {
        final performance = entry.value.modelPerformance;
        summary['expenses'][entry.key] = {
          'accuracy': performance.accuracyScore,
          'confidence': performance.confidenceLevel,
          'data_points': performance.dataPoints,
        };
      }
    }

    return summary;
  }

  /// Format untuk display di UI
  String formatLastRefresh() {
    if (_lastRefresh == null) return 'Belum pernah dimuat';
    
    final now = DateTime.now();
    final difference = now.difference(_lastRefresh!);
    
    if (difference.inMinutes < 1) {
      return 'Baru saja';
    } else if (difference.inMinutes < 60) {
      return '${difference.inMinutes} menit lalu';
    } else if (difference.inHours < 24) {
      return '${difference.inHours} jam lalu';
    } else {
      return '${difference.inDays} hari lalu';
    }
  }

  /// Check if specific prediction type is available
  bool isPredictionAvailable(String type) {
    switch (type.toLowerCase()) {
      case 'income':
        return _incomePrediction != null;
      case 'budget':
        return _budgetPrediction != null;
      case 'analytics':
        return _analytics != null;
      case 'needs':
      case 'wants':
      case 'savings':
        return _expensePredictions.containsKey(type);
      default:
        return false;
    }
  }

  /// Get prediction confidence for specific type
  String getPredictionConfidence(String type) {
    switch (type.toLowerCase()) {
      case 'income':
        return _incomePrediction?.modelPerformance.confidenceLevel ?? 'Unknown';
      case 'needs':
      case 'wants':
      case 'savings':
        return _expensePredictions[type]?.modelPerformance.confidenceLevel ?? 'Unknown';
      default:
        return 'Unknown';
    }
  }

  /// Get formatted prediction value for display
  String getFormattedPredictionValue(String type, String valueType) {
    switch (type.toLowerCase()) {
      case 'income':
        if (_incomePrediction == null) return 'N/A';
        switch (valueType) {
          case 'total':
            return _incomePrediction!.summary.formattedTotal;
          case 'daily_avg':
            return _incomePrediction!.summary.formattedDailyAvg;
          default:
            return 'N/A';
        }
      case 'needs':
      case 'wants':
      case 'savings':
        final expense = _expensePredictions[type];
        if (expense == null) return 'N/A';
        switch (valueType) {
          case 'total':
            return expense.summary.formattedTotal;
          case 'daily_avg':
            return expense.summary.formattedDailyAvg;
          default:
            return 'N/A';
        }
      default:
        return 'N/A';
    }
  }

  // ===== BATCH OPERATIONS =====

  /// Load multiple predictions with priority
  Future<void> loadPredictionsWithPriority({
    bool loadIncome = true,
    bool loadBudget = true,
    bool loadAnalytics = false,
    int? forecastDays,
  }) async {
    final futures = <Future<void>>[];
    
    if (loadIncome) {
      futures.add(loadIncomePrediction(forecastDays: forecastDays));
    }
    
    if (loadBudget) {
      futures.add(loadBudgetPrediction(forecastDays: forecastDays));
    }
    
    if (loadAnalytics) {
      futures.add(loadPredictionAnalytics()); // FIXED: Changed from loadAnalytics()
    }

    await Future.wait(futures, eagerError: false);
    
    if (forecastDays != null) {
      _forecastDays = forecastDays;
    }
    
    _lastRefresh = DateTime.now();
    notifyListeners();
  }

  // ===== DEBUG & MONITORING =====

  /// Get debug information untuk troubleshooting
  Map<String, dynamic> getDebugInfo() {
    return {
      'loading_states': {
        'income': _isLoadingIncome,
        'budget': _isLoadingBudget,
        'analytics': _isLoadingAnalytics,
        'all': _isLoadingAll,
      },
      'data_availability': {
        'income': _incomePrediction != null,
        'budget': _budgetPrediction != null,
        'analytics': _analytics != null,
        'expenses': _expensePredictions.keys.toList(),
        'savings_goals': _savingsGoalPredictions.keys.toList(),
      },
      'errors': {
        'income': _incomeError,
        'budget': _budgetError,
        'analytics': _analyticsError,
        'general': _generalError,
      },
      'configuration': {
        'forecast_days': _forecastDays,
        'last_refresh': _lastRefresh?.toIso8601String(),
        'is_stale': isPredictionStale,
      },
      'performance': getPerformanceSummary(),
    };
  }

  /// Print debug info to console
  void printDebugInfo() {
    final info = getDebugInfo();
    debugPrint('=== PREDICTION PROVIDER DEBUG INFO ===');
    debugPrint('Loading States: ${info['loading_states']}');
    debugPrint('Data Availability: ${info['data_availability']}');
    debugPrint('Errors: ${info['errors']}');
    debugPrint('Configuration: ${info['configuration']}');
    debugPrint('=========================================');
  }

  // ===== VALIDATION & HEALTH CHECKS =====

  /// Validate current prediction data
  List<String> validatePredictions() {
    final issues = <String>[];

    // Check data freshness
    if (isPredictionStale) {
      issues.add('Prediction data is stale (older than 1 hour)');
    }

    // Check income prediction
    if (_incomePrediction != null) {
      if (_incomePrediction!.modelPerformance.accuracyScore < 60.0) {
        issues.add('Income prediction accuracy is low (${_incomePrediction!.modelPerformance.accuracyScore.toStringAsFixed(1)}%)');
      }
      if (_incomePrediction!.dataPointsUsed < 10) {
        issues.add('Insufficient data points for income prediction (${_incomePrediction!.dataPointsUsed})');
      }
    }

    // Check budget prediction
    if (_budgetPrediction != null) {
      if (_budgetPrediction!.budgetHealth.healthScore < 40.0) {
        issues.add('Poor budget health score (${_budgetPrediction!.budgetHealth.healthScore.toStringAsFixed(1)})');
      }
    }

    // Check for missing expense predictions
    final expectedBudgetTypes = ['needs', 'wants', 'savings'];
    for (final type in expectedBudgetTypes) {
      if (!_expensePredictions.containsKey(type)) {
        issues.add('Missing $type expense prediction');
      }
    }

    return issues;
  }

  /// Get system health status
  Map<String, dynamic> getSystemHealth() {
    final issues = validatePredictions();
    final hasErrors = hasAnyError;
    final hasLoading = hasAnyLoading;
    
    String status;
    Color statusColor;
    
    if (hasErrors || issues.isNotEmpty) {
      status = 'Warning';
      statusColor = const Color(0xFFF59E0B); // warning
    } else if (hasLoading) {
      status = 'Loading';
      statusColor = const Color(0xFF3B82F6); // info
    } else if (hasIncomeData && hasBudgetData) {
      status = 'Healthy';
      statusColor = const Color(0xFF10B981); // success
    } else {
      status = 'Incomplete';
      statusColor = const Color(0xFF6B7280); // gray
    }

    return {
      'status': status,
      'status_color': statusColor,
      'has_errors': hasErrors,
      'has_loading': hasLoading,
      'issues': issues,
      'data_completeness': {
        'income': hasIncomeData,
        'budget': hasBudgetData,
        'analytics': hasAnalyticsData,
        'expenses': hasExpenseData,
      },
      'last_check': DateTime.now().toIso8601String(),
    };
  }

  // ===== DISPOSAL =====

  @override
  void dispose() {
    clearAllData();
    super.dispose();
  }
}