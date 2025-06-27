
// lib/features/dashboard/domain/entities/prediction.dart
import 'package:equatable/equatable.dart';

class Prediction extends Equatable {
  final String predictionType;
  final bool cached;
  final DateTime generatedAt;
  final ForecastSummary forecastSummary;
  final List<Insight> insights;
  final ModelInfo? modelInfo;

  const Prediction({
    required this.predictionType,
    required this.cached,
    required this.generatedAt,
    required this.forecastSummary,
    required this.insights,
    this.modelInfo,
  });

  @override
  List<Object?> get props => [
    predictionType,
    cached,
    generatedAt,
    forecastSummary,
    insights,
    modelInfo,
  ];
}

class ForecastSummary extends Equatable {
  final PeriodForecast nextWeek;
  final PeriodForecast nextMonth;

  const ForecastSummary({
    required this.nextWeek,
    required this.nextMonth,
  });

  @override
  List<Object> get props => [nextWeek, nextMonth];
}

class PeriodForecast extends Equatable {
  final double predictedTotal;
  final String confidence;
  final double? lowerBound;
  final double? upperBound;

  const PeriodForecast({
    required this.predictedTotal,
    required this.confidence,
    this.lowerBound,
    this.upperBound,
  });

  @override
  List<Object?> get props => [predictedTotal, confidence, lowerBound, upperBound];
}

class Insight extends Equatable {
  final String type;
  final String message;
  final String importance;
  final String? suggestedAction;

  const Insight({
    required this.type,
    required this.message,
    required this.importance,
    this.suggestedAction,
  });

  bool get isHighPriority => importance == 'high';
  bool get isMediumPriority => importance == 'medium';
  bool get isLowPriority => importance == 'low';

  @override
  List<Object?> get props => [type, message, importance, suggestedAction];
}

class ModelInfo extends Equatable {
  final String method;
  final int dataPoints;
  final double dailyAverage;

  const ModelInfo({
    required this.method,
    required this.dataPoints,
    required this.dailyAverage,
  });

  @override
  List<Object> get props => [method, dataPoints, dailyAverage];
}