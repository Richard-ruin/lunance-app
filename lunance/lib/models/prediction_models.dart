// lib/models/prediction_models.dart
import '../utils/format_eksplore.dart';

// ===== BASE PREDICTION MODELS =====

class PredictionPoint {
  final DateTime date;
  final double predictedValue;
  final double lowerBound;
  final double upperBound;
  final String formattedDate;
  final String formattedValue;

  PredictionPoint({
    required this.date,
    required this.predictedValue,
    required this.lowerBound,
    required this.upperBound,
    required this.formattedDate,
    required this.formattedValue,
  });

  factory PredictionPoint.fromJson(Map<String, dynamic> json) {
    final date = DateTime.parse(json['ds'] ?? DateTime.now().toIso8601String());
    final predictedValue = FormatUtils.safeDouble(json['yhat']);
    
    return PredictionPoint(
      date: date,
      predictedValue: predictedValue,
      lowerBound: FormatUtils.safeDouble(json['yhat_lower']),
      upperBound: FormatUtils.safeDouble(json['yhat_upper']),
      formattedDate: json['formatted_date'] ?? FormatUtils.formatDate(date),
      formattedValue: json['formatted_value'] ?? FormatUtils.formatCurrency(predictedValue),
    );
  }
}

class ModelPerformance {
  final double mae;
  final double mape;
  final double rmse;
  final double accuracyScore;
  final double r2Score;
  final int dataPoints;

  ModelPerformance({
    required this.mae,
    required this.mape,
    required this.rmse,
    required this.accuracyScore,
    required this.r2Score,
    required this.dataPoints,
  });

  factory ModelPerformance.fromJson(Map<String, dynamic> json) {
    return ModelPerformance(
      mae: FormatUtils.safeDouble(json['mae']),
      mape: FormatUtils.safeDouble(json['mape']),
      rmse: FormatUtils.safeDouble(json['rmse']),
      accuracyScore: FormatUtils.safeDouble(json['accuracy_score']),
      r2Score: FormatUtils.safeDouble(json['r2_score']),
      dataPoints: FormatUtils.safeInt(json['data_points']),
    );
  }

  String get confidenceLevel {
    if (accuracyScore >= 85) return 'Tinggi';
    if (accuracyScore >= 70) return 'Menengah';
    return 'Rendah';
  }
}

// ===== INCOME PREDICTION MODELS =====

class IncomePredictionSummary {
  final double totalPredictedIncome;
  final double averageDailyIncome;
  final String formattedTotal;
  final String formattedDailyAvg;
  final String confidenceLevel;

  IncomePredictionSummary({
    required this.totalPredictedIncome,
    required this.averageDailyIncome,
    required this.formattedTotal,
    required this.formattedDailyAvg,
    required this.confidenceLevel,
  });

  factory IncomePredictionSummary.fromJson(Map<String, dynamic> json) {
    return IncomePredictionSummary(
      totalPredictedIncome: FormatUtils.safeDouble(json['total_predicted_income']),
      averageDailyIncome: FormatUtils.safeDouble(json['average_daily_income']),
      formattedTotal: FormatUtils.safeString(json['formatted_total']),
      formattedDailyAvg: FormatUtils.safeString(json['formatted_daily_avg']),
      confidenceLevel: FormatUtils.safeString(json['confidence_level'], 'Menengah'),
    );
  }
}

class IncomePrediction {
  final String method;
  final String predictionType;
  final String forecastPeriod;
  final String generatedAt;
  final IncomePredictionSummary summary;
  final List<PredictionPoint> dailyPredictions;
  final ModelPerformance modelPerformance;
  final List<String> aiInsights;
  final List<String> recommendations;
  final int dataPointsUsed;

  IncomePrediction({
    required this.method,
    required this.predictionType,
    required this.forecastPeriod,
    required this.generatedAt,
    required this.summary,
    required this.dailyPredictions,
    required this.modelPerformance,
    required this.aiInsights,
    required this.recommendations,
    required this.dataPointsUsed,
  });

  factory IncomePrediction.fromJson(Map<String, dynamic> json) {
    return IncomePrediction(
      method: FormatUtils.safeString(json['method']),
      predictionType: FormatUtils.safeString(json['prediction_type']),
      forecastPeriod: FormatUtils.safeString(json['forecast_period']),
      generatedAt: FormatUtils.safeString(json['generated_at']),
      summary: IncomePredictionSummary.fromJson(
        FormatUtils.safeMap(json['prediction_summary']),
      ),
      dailyPredictions: FormatUtils.safeList<dynamic>(json['daily_predictions'])
          .map((item) => PredictionPoint.fromJson(FormatUtils.safeMap(item)))
          .toList(),
      modelPerformance: ModelPerformance.fromJson(
        FormatUtils.safeMap(json['model_performance']),
      ),
      aiInsights: FormatUtils.safeList<dynamic>(json['ai_insights'])
          .map((item) => FormatUtils.safeString(item))
          .toList(),
      recommendations: FormatUtils.safeList<dynamic>(json['recommendations'])
          .map((item) => FormatUtils.safeString(item))
          .toList(),
      dataPointsUsed: FormatUtils.safeInt(
        FormatUtils.safeGetNested(json, ['historical_analysis', 'data_points_used'], 0),
      ),
    );
  }
}

// ===== EXPENSE PREDICTION MODELS =====

class ExpensePredictionSummary {
  final double totalPredictedExpense;
  final double averageDailyExpense;
  final String formattedTotal;
  final String formattedDailyAvg;

  ExpensePredictionSummary({
    required this.totalPredictedExpense,
    required this.averageDailyExpense,
    required this.formattedTotal,
    required this.formattedDailyAvg,
  });

  factory ExpensePredictionSummary.fromJson(Map<String, dynamic> json) {
    return ExpensePredictionSummary(
      totalPredictedExpense: FormatUtils.safeDouble(json['total_predicted_expense']),
      averageDailyExpense: FormatUtils.safeDouble(json['average_daily_expense']),
      formattedTotal: FormatUtils.safeString(json['formatted_total']),
      formattedDailyAvg: FormatUtils.safeString(json['formatted_daily_avg']),
    );
  }
}

class BudgetPredictionPoint extends PredictionPoint {
  final double? dailyBudget;
  final String? budgetStatus;
  final double? budgetUsagePercentage;
  final String? formattedDailyBudget;

  BudgetPredictionPoint({
    required DateTime date,
    required double predictedValue,
    required double lowerBound,
    required double upperBound,
    required String formattedDate,
    required String formattedValue,
    this.dailyBudget,
    this.budgetStatus,
    this.budgetUsagePercentage,
    this.formattedDailyBudget,
  }) : super(
          date: date,
          predictedValue: predictedValue,
          lowerBound: lowerBound,
          upperBound: upperBound,
          formattedDate: formattedDate,
          formattedValue: formattedValue,
        );

  factory BudgetPredictionPoint.fromJson(Map<String, dynamic> json) {
    final base = PredictionPoint.fromJson(json);
    
    return BudgetPredictionPoint(
      date: base.date,
      predictedValue: base.predictedValue,
      lowerBound: base.lowerBound,
      upperBound: base.upperBound,
      formattedDate: base.formattedDate,
      formattedValue: base.formattedValue,
      dailyBudget: FormatUtils.safeDouble(json['daily_budget']),
      budgetStatus: FormatUtils.safeString(json['budget_status']),
      budgetUsagePercentage: FormatUtils.safeDouble(json['budget_usage_percentage']),
      formattedDailyBudget: FormatUtils.safeString(json['formatted_daily_budget']),
    );
  }

  bool get isOverBudget => budgetStatus == 'over_budget';
  bool get isWarning => budgetUsagePercentage != null && budgetUsagePercentage! > 80;
}

class ExpensePrediction {
  final String method;
  final String predictionType;
  final String budgetType;
  final String forecastPeriod;
  final String generatedAt;
  final ExpensePredictionSummary summary;
  final List<BudgetPredictionPoint> dailyPredictions;
  final ModelPerformance modelPerformance;
  final List<String> aiInsights;
  final List<String> budgetRecommendations;
  final Map<String, dynamic> budgetAnalysis;

  ExpensePrediction({
    required this.method,
    required this.predictionType,
    required this.budgetType,
    required this.forecastPeriod,
    required this.generatedAt,
    required this.summary,
    required this.dailyPredictions,
    required this.modelPerformance,
    required this.aiInsights,
    required this.budgetRecommendations,
    required this.budgetAnalysis,
  });

  factory ExpensePrediction.fromJson(Map<String, dynamic> json) {
    return ExpensePrediction(
      method: FormatUtils.safeString(json['method']),
      predictionType: FormatUtils.safeString(json['prediction_type']),
      budgetType: FormatUtils.safeString(json['budget_type']),
      forecastPeriod: FormatUtils.safeString(json['forecast_period']),
      generatedAt: FormatUtils.safeString(json['generated_at']),
      summary: ExpensePredictionSummary.fromJson(
        FormatUtils.safeMap(json['prediction_summary']),
      ),
      dailyPredictions: FormatUtils.safeList<dynamic>(json['daily_predictions'])
          .map((item) => BudgetPredictionPoint.fromJson(FormatUtils.safeMap(item)))
          .toList(),
      modelPerformance: ModelPerformance.fromJson(
        FormatUtils.safeMap(json['model_performance']),
      ),
      aiInsights: FormatUtils.safeList<dynamic>(json['ai_insights'])
          .map((item) => FormatUtils.safeString(item))
          .toList(),
      budgetRecommendations: FormatUtils.safeList<dynamic>(json['budget_recommendations'])
          .map((item) => FormatUtils.safeString(item))
          .toList(),
      budgetAnalysis: FormatUtils.safeMap(json['budget_analysis']),
    );
  }

  String get budgetTypeName {
    switch (budgetType.toLowerCase()) {
      case 'needs':
        return 'Kebutuhan (50%)';
      case 'wants':
        return 'Keinginan (30%)';
      case 'savings':
        return 'Tabungan (20%)';
      default:
        return budgetType;
    }
  }

  String get budgetTypeColorHex {
    switch (budgetType.toLowerCase()) {
      case 'needs':
        return '#22C55E';
      case 'wants':
        return '#F59E0B';
      case 'savings':
        return '#3B82F6';
      default:
        return '#6B7280';
    }
  }
}

// ===== BUDGET PERFORMANCE MODELS =====

class BudgetComparison {
  final double target;
  final double predicted;
  final double variance;
  final String status;

  BudgetComparison({
    required this.target,
    required this.predicted,
    required this.variance,
    required this.status,
  });

  factory BudgetComparison.fromJson(Map<String, dynamic> json) {
    return BudgetComparison(
      target: FormatUtils.safeDouble(json['target']),
      predicted: FormatUtils.safeDouble(json['predicted']),
      variance: FormatUtils.safeDouble(json['variance']),
      status: FormatUtils.safeString(json['status']),
    );
  }

  bool get isOnTrack => status == 'on_track';
  bool get isOver => status == 'over';
  bool get isUnder => status == 'under';
}

class BudgetHealth {
  final String healthLevel;
  final double healthScore;
  final double averageVariance;
  final Map<String, double> individualVariances;

  BudgetHealth({
    required this.healthLevel,
    required this.healthScore,
    required this.averageVariance,
    required this.individualVariances,
  });

  factory BudgetHealth.fromJson(Map<String, dynamic> json) {
    return BudgetHealth(
      healthLevel: FormatUtils.safeString(json['health_level']),
      healthScore: FormatUtils.safeDouble(json['health_score']),
      averageVariance: FormatUtils.safeDouble(json['average_variance']),
      individualVariances: FormatUtils.safeMap(json['individual_variances'])
          .map((key, value) => MapEntry(key, FormatUtils.safeDouble(value))),
    );
  }

  bool get isExcellent => healthLevel == 'excellent';
  bool get isGood => healthLevel == 'good';
  bool get isFair => healthLevel == 'fair';
  bool get isPoor => healthLevel == 'poor';

  String get healthEmoji {
    switch (healthLevel) {
      case 'excellent':
        return '💪';
      case 'good':
        return '👍';
      case 'fair':
        return '😐';
      case 'poor':
        return '😟';
      default:
        return '📊';
    }
  }
}

class BudgetPerformancePrediction {
  final String method;
  final String predictionType;
  final String forecastPeriod;
  final String generatedAt;
  final Map<String, double> predictedTotals;
  final Map<String, String> formattedTotals;
  final Map<String, double> predictedPercentages;
  final Map<String, BudgetComparison> budgetComparison;
  final BudgetHealth budgetHealth;
  final List<String> comprehensiveInsights;
  final List<String> optimizationRecommendations;

  BudgetPerformancePrediction({
    required this.method,
    required this.predictionType,
    required this.forecastPeriod,
    required this.generatedAt,
    required this.predictedTotals,
    required this.formattedTotals,
    required this.predictedPercentages,
    required this.budgetComparison,
    required this.budgetHealth,
    required this.comprehensiveInsights,
    required this.optimizationRecommendations,
  });

  factory BudgetPerformancePrediction.fromJson(Map<String, dynamic> json) {
    final budgetComparisonData = FormatUtils.safeGetNested(
      json,
      ['budget_analysis_50_30_20', 'variance_analysis'],
      <String, dynamic>{},
    );

    return BudgetPerformancePrediction(
      method: FormatUtils.safeString(json['method']),
      predictionType: FormatUtils.safeString(json['prediction_type']),
      forecastPeriod: FormatUtils.safeString(json['forecast_period']),
      generatedAt: FormatUtils.safeString(json['generated_at']),
      predictedTotals: FormatUtils.safeMap(
        FormatUtils.safeGetNested(json, ['prediction_summary', 'predicted_totals'], {}),
      ).map((key, value) => MapEntry(key, FormatUtils.safeDouble(value))),
      formattedTotals: FormatUtils.safeMap(
        FormatUtils.safeGetNested(json, ['prediction_summary', 'formatted_totals'], {}),
      ).map((key, value) => MapEntry(key, FormatUtils.safeString(value))),
      predictedPercentages: FormatUtils.safeMap(
        FormatUtils.safeGetNested(json, ['prediction_summary', 'predicted_percentages'], {}),
      ).map((key, value) => MapEntry(key, FormatUtils.safeDouble(value))),
      budgetComparison: FormatUtils.safeMap(budgetComparisonData).map(
        (key, value) => MapEntry(key, BudgetComparison.fromJson(FormatUtils.safeMap(value))),
      ),
      budgetHealth: BudgetHealth.fromJson(
        FormatUtils.safeMap(
          FormatUtils.safeGetNested(json, ['prediction_summary', 'budget_health'], {}),
        ),
      ),
      comprehensiveInsights: FormatUtils.safeList<dynamic>(
        FormatUtils.safeGetNested(json, ['ai_analysis', 'comprehensive_insights'], []),
      ).map((item) => FormatUtils.safeString(item)).toList(),
      optimizationRecommendations: FormatUtils.safeList<dynamic>(
        FormatUtils.safeGetNested(json, ['ai_analysis', 'optimization_recommendations'], []),
      ).map((item) => FormatUtils.safeString(item)).toList(),
    );
  }

  double get needsPercentage => predictedPercentages['needs'] ?? 0.0;
  double get wantsPercentage => predictedPercentages['wants'] ?? 0.0;
  double get savingsPercentage => predictedPercentages['savings'] ?? 0.0;

  bool get isHealthy => budgetHealth.isExcellent || budgetHealth.isGood;
}

// ===== SAVINGS GOAL MODELS =====

class SavingsScenario {
  final double monthlyRate;
  final double monthsNeeded;
  final String achievementDate;
  final String formattedRate;
  final double? additionalRequired;
  final String? formattedAdditional;

  SavingsScenario({
    required this.monthlyRate,
    required this.monthsNeeded,
    required this.achievementDate,
    required this.formattedRate,
    this.additionalRequired,
    this.formattedAdditional,
  });

  factory SavingsScenario.fromJson(Map<String, dynamic> json) {
    return SavingsScenario(
      monthlyRate: FormatUtils.safeDouble(json['monthly_rate']),
      monthsNeeded: FormatUtils.safeDouble(json['months_needed']),
      achievementDate: FormatUtils.safeString(json['achievement_date']),
      formattedRate: FormatUtils.safeString(json['formatted_rate']),
      additionalRequired: FormatUtils.safeDouble(json['additional_required']),
      formattedAdditional: FormatUtils.safeString(json['formatted_additional']),
    );
  }
}

class SavingsGoalPrediction {
  final String method;
  final String predictionType;
  final String generatedAt;
  final String achievementStatus;
  final Map<String, dynamic> goalInfo;
  final Map<String, String> formattedAmounts;
  final Map<String, dynamic> achievementPrediction;
  final Map<String, SavingsScenario> achievementScenarios;
  final List<String> accelerationTips;

  SavingsGoalPrediction({
    required this.method,
    required this.predictionType,
    required this.generatedAt,
    required this.achievementStatus,
    required this.goalInfo,
    required this.formattedAmounts,
    required this.achievementPrediction,
    required this.achievementScenarios,
    required this.accelerationTips,
  });

  factory SavingsGoalPrediction.fromJson(Map<String, dynamic> json) {
    final scenariosData = FormatUtils.safeMap(json['achievement_scenarios']);
    
    return SavingsGoalPrediction(
      method: FormatUtils.safeString(json['method']),
      predictionType: FormatUtils.safeString(json['prediction_type']),
      generatedAt: FormatUtils.safeString(json['generated_at']),
      achievementStatus: FormatUtils.safeString(json['achievement_status']),
      goalInfo: FormatUtils.safeMap(json['goal_info']),
      formattedAmounts: FormatUtils.safeMap(json['formatted_amounts'])
          .map((key, value) => MapEntry(key, FormatUtils.safeString(value))),
      achievementPrediction: FormatUtils.safeMap(json['achievement_prediction']),
      achievementScenarios: scenariosData.map(
        (key, value) => MapEntry(key, SavingsScenario.fromJson(FormatUtils.safeMap(value))),
      ),
      accelerationTips: FormatUtils.safeList<dynamic>(
        FormatUtils.safeGetNested(json, ['acceleration_strategies', 'tips'], []),
      ).map((item) => FormatUtils.safeString(item)).toList(),
    );
  }

  String get itemName => FormatUtils.safeString(goalInfo['item_name']);
  double get targetAmount => FormatUtils.safeDouble(goalInfo['target_amount']);
  double get currentAmount => FormatUtils.safeDouble(goalInfo['current_amount']);
  double get progressPercentage => FormatUtils.safeDouble(goalInfo['progress_percentage']);
  
  bool get isCompleted => achievementStatus == 'completed';
  bool get isInProgress => achievementStatus == 'in_progress';
}

// ===== ANALYTICS MODELS =====

class PredictionAnalytics {
  final String method;
  final String analyticsType;
  final String generatedAt;
  final Map<String, dynamic> userInfo;
  final Map<String, dynamic> predictionSummary;
  final Map<String, dynamic>? incomeAnalytics;
  final Map<String, dynamic>? budgetAnalytics;
  final List<String> aiRecommendations;

  PredictionAnalytics({
    required this.method,
    required this.analyticsType,
    required this.generatedAt,
    required this.userInfo,
    required this.predictionSummary,
    this.incomeAnalytics,
    this.budgetAnalytics,
    required this.aiRecommendations,
  });

  factory PredictionAnalytics.fromJson(Map<String, dynamic> json) {
    final recommendations = <String>[];
    final aiRec = FormatUtils.safeMap(json['ai_recommendations']);
    
    // Combine all recommendation types
    for (final recList in aiRec.values) {
      if (recList is List) {
        recommendations.addAll(
          recList.map((item) => FormatUtils.safeString(item)),
        );
      }
    }

    return PredictionAnalytics(
      method: FormatUtils.safeString(json['method']),
      analyticsType: FormatUtils.safeString(json['analytics_type']),
      generatedAt: FormatUtils.safeString(json['generated_at']),
      userInfo: FormatUtils.safeMap(json['user_info']),
      predictionSummary: FormatUtils.safeMap(json['prediction_summary']),
      incomeAnalytics: FormatUtils.safeMap(json['income_analytics']),
      budgetAnalytics: FormatUtils.safeMap(json['budget_analytics']),
      aiRecommendations: recommendations,
    );
  }

  bool get hasIncomeData => incomeAnalytics != null;
  bool get hasBudgetData => budgetAnalytics != null;
  String get dataQuality => FormatUtils.safeString(predictionSummary['data_quality'], 'unknown');
}