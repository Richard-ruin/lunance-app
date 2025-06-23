// lib/features/dashboard/presentation/bloc/dashboard_state.dart
import '../../domain/entities/financial_summary.dart';
import '../../domain/entities/prediction.dart';

abstract class DashboardState {}

class DashboardInitial extends DashboardState {}

class DashboardLoading extends DashboardState {}

class DashboardLoaded extends DashboardState {
  final FinancialSummary financialSummary;
  final List<Prediction> predictions;
  final MonthlyPrediction? monthlyPrediction;

  DashboardLoaded({
    required this.financialSummary,
    this.predictions = const [],
    this.monthlyPrediction,
  });

  DashboardLoaded copyWith({
    FinancialSummary? financialSummary,
    List<Prediction>? predictions,
    MonthlyPrediction? monthlyPrediction,
  }) {
    return DashboardLoaded(
      financialSummary: financialSummary ?? this.financialSummary,
      predictions: predictions ?? this.predictions,
      monthlyPrediction: monthlyPrediction ?? this.monthlyPrediction,
    );
  }
}

class DashboardError extends DashboardState {
  final String message;

  DashboardError(this.message);
}

class DashboardRefreshing extends DashboardState {
  final FinancialSummary financialSummary;
  final List<Prediction> predictions;
  final MonthlyPrediction? monthlyPrediction;

  DashboardRefreshing({
    required this.financialSummary,
    this.predictions = const [],
    this.monthlyPrediction,
  });
}