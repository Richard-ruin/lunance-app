// lib/features/dashboard/data/models/prediction_model.dart
import '../../domain/entities/prediction.dart';

class PredictionModel extends Prediction {
  const PredictionModel({
    required super.predictionType,
    required super.cached,
    required super.generatedAt,
    required super.forecastSummary,
    required super.insights,
    super.modelInfo,
  });

  factory PredictionModel.fromJson(Map<String, dynamic> json) {
    return PredictionModel(
      predictionType: json['prediction_type'] ?? 'expense',
      cached: json['cached'] ?? false,
      generatedAt: DateTime.parse(json['generated_at'] ?? DateTime.now().toIso8601String()),
      forecastSummary: ForecastSummaryModel.fromJson(json['forecast_summary'] ?? {}),
      insights: (json['insights'] as List<dynamic>?)
          ?.map((item) => InsightModel.fromJson(item))
          .toList() ?? [],
      modelInfo: json['model_info'] != null
          ? ModelInfoModel.fromJson(json['model_info'])
          : null,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'prediction_type': predictionType,
      'cached': cached,
      'generated_at': generatedAt.toIso8601String(),
      'forecast_summary': (forecastSummary as ForecastSummaryModel).toJson(),
      'insights': insights.map((item) => (item as InsightModel).toJson()).toList(),
      'model_info': modelInfo != null
          ? (modelInfo as ModelInfoModel).toJson()
          : null,
    };
  }
}

class ForecastSummaryModel extends ForecastSummary {
  const ForecastSummaryModel({
    required super.nextWeek,
    required super.nextMonth,
  });

  factory ForecastSummaryModel.fromJson(Map<String, dynamic> json) {
    return ForecastSummaryModel(
      nextWeek: PeriodForecastModel.fromJson(json['next_week'] ?? {}),
      nextMonth: PeriodForecastModel.fromJson(json['next_month'] ?? {}),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'next_week': (nextWeek as PeriodForecastModel).toJson(),
      'next_month': (nextMonth as PeriodForecastModel).toJson(),
    };
  }
}

class PeriodForecastModel extends PeriodForecast {
  const PeriodForecastModel({
    required super.predictedTotal,
    required super.confidence,
    super.lowerBound,
    super.upperBound,
  });

  factory PeriodForecastModel.fromJson(Map<String, dynamic> json) {
    return PeriodForecastModel(
      predictedTotal: (json['predicted_total'] ?? 0).toDouble(),
      confidence: json['confidence'] ?? 'medium',
      lowerBound: json['lower_bound']?.toDouble(),
      upperBound: json['upper_bound']?.toDouble(),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'predicted_total': predictedTotal,
      'confidence': confidence,
      'lower_bound': lowerBound,
      'upper_bound': upperBound,
    };
  }
}

class InsightModel extends Insight {
  const InsightModel({
    required super.type,
    required super.message,
    required super.importance,
    super.suggestedAction,
  });

  factory InsightModel.fromJson(Map<String, dynamic> json) {
    return InsightModel(
      type: json['type'] ?? '',
      message: json['message'] ?? '',
      importance: json['importance'] ?? 'medium',
      suggestedAction: json['suggested_action'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'type': type,
      'message': message,
      'importance': importance,
      'suggested_action': suggestedAction,
    };
  }
}

class ModelInfoModel extends ModelInfo {
  const ModelInfoModel({
    required super.method,
    required super.dataPoints,
    required super.dailyAverage,
  });

  factory ModelInfoModel.fromJson(Map<String, dynamic> json) {
    return ModelInfoModel(
      method: json['method'] ?? 'historical_average',
      dataPoints: json['data_points'] ?? 0,
      dailyAverage: (json['daily_average'] ?? 0).toDouble(),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'method': method,
      'data_points': dataPoints,
      'daily_average': dailyAverage,
    };
  }
}
