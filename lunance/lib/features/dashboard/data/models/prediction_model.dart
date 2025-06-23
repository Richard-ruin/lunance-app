// lib/features/dashboard/data/models/prediction_model.dart
import '../../domain/entities/prediction.dart';

class PredictionModel extends Prediction {
  const PredictionModel({
    required super.message,
    required super.type,
    required super.confidence,
    required super.data,
    required super.generatedAt,
  });

  factory PredictionModel.fromJson(Map<String, dynamic> json) {
    return PredictionModel(
      message: json['message'] as String,
      type: PredictionType.values.byName(json['type'] as String),
      confidence: (json['confidence'] as num).toDouble(),
      data: json['data'] as Map<String, dynamic>,
      generatedAt: DateTime.parse(json['generatedAt'] as String),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'message': message,
      'type': type.name,
      'confidence': confidence,
      'data': data,
      'generatedAt': generatedAt.toIso8601String(),
    };
  }
}

class MonthlyPredictionModel extends MonthlyPrediction {
  const MonthlyPredictionModel({
    required super.month,
    required super.predictedIncome,
    required super.predictedExpense,
    required super.predictedSavings,
    required super.recommendations,
  });

  factory MonthlyPredictionModel.fromJson(Map<String, dynamic> json) {
    return MonthlyPredictionModel(
      month: json['month'] as String,
      predictedIncome: (json['predictedIncome'] as num).toDouble(),
      predictedExpense: (json['predictedExpense'] as num).toDouble(),
      predictedSavings: (json['predictedSavings'] as num).toDouble(),
      recommendations: List<String>.from(json['recommendations'] as List),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'month': month,
      'predictedIncome': predictedIncome,
      'predictedExpense': predictedExpense,
      'predictedSavings': predictedSavings,
      'recommendations': recommendations,
    };
  }
}