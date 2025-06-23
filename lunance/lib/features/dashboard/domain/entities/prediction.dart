// lib/features/dashboard/domain/entities/prediction.dart
class Prediction {
  final String message;
  final PredictionType type;
  final double confidence;
  final Map<String, dynamic> data;
  final DateTime generatedAt;

  const Prediction({
    required this.message,
    required this.type,
    required this.confidence,
    required this.data,
    required this.generatedAt,
  });
}

enum PredictionType {
  saving,
  spending,
  budget,
  warning,
  achievement,
}

class MonthlyPrediction {
  final String month;
  final double predictedIncome;
  final double predictedExpense;
  final double predictedSavings;
  final List<String> recommendations;

  const MonthlyPrediction({
    required this.month,
    required this.predictedIncome,
    required this.predictedExpense,
    required this.predictedSavings,
    required this.recommendations,
  });
}