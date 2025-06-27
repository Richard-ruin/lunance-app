
// lib/features/dashboard/presentation/bloc/dashboard_state.dart
import 'package:equatable/equatable.dart';
import '../../domain/entities/financial_summary.dart';
import '../../domain/entities/quick_stats.dart';
import '../../domain/entities/category_breakdown.dart';
import '../../domain/entities/recent_transactions.dart';
import '../../domain/entities/prediction.dart';
import '../../domain/entities/financial_insights.dart';

abstract class DashboardState extends Equatable {
  const DashboardState();

  @override
  List<Object?> get props => [];
}

class DashboardInitial extends DashboardState {}

class DashboardLoading extends DashboardState {}

class DashboardLoaded extends DashboardState {
  final FinancialSummary? financialSummary;
  final QuickStats? quickStats;
  final CategoryBreakdown? categoryBreakdown;
  final RecentTransactions? recentTransactions;
  final Prediction? predictions;
  final FinancialInsights? insights;
  final String currentPeriod;
  final DateTime lastUpdated;

  const DashboardLoaded({
    this.financialSummary,
    this.quickStats,
    this.categoryBreakdown,
    this.recentTransactions,
    this.predictions,
    this.insights,
    this.currentPeriod = 'monthly',
    required this.lastUpdated,
  });

  DashboardLoaded copyWith({
    FinancialSummary? financialSummary,
    QuickStats? quickStats,
    CategoryBreakdown? categoryBreakdown,
    RecentTransactions? recentTransactions,
    Prediction? predictions,
    FinancialInsights? insights,
    String? currentPeriod,
    DateTime? lastUpdated,
  }) {
    return DashboardLoaded(
      financialSummary: financialSummary ?? this.financialSummary,
      quickStats: quickStats ?? this.quickStats,
      categoryBreakdown: categoryBreakdown ?? this.categoryBreakdown,
      recentTransactions: recentTransactions ?? this.recentTransactions,
      predictions: predictions ?? this.predictions,
      insights: insights ?? this.insights,
      currentPeriod: currentPeriod ?? this.currentPeriod,
      lastUpdated: lastUpdated ?? this.lastUpdated,
    );
  }

  bool get hasData =>
      financialSummary != null ||
      quickStats != null ||
      categoryBreakdown != null ||
      recentTransactions != null;

  bool get isFullyLoaded =>
      financialSummary != null &&
      quickStats != null &&
      categoryBreakdown != null &&
      recentTransactions != null;

  @override
  List<Object?> get props => [
        financialSummary,
        quickStats,
        categoryBreakdown,
        recentTransactions,
        predictions,
        insights,
        currentPeriod,
        lastUpdated,
      ];
}

class DashboardError extends DashboardState {
  final String message;
  final String? errorCode;

  const DashboardError({
    required this.message,
    this.errorCode,
  });

  @override
  List<Object?> get props => [message, errorCode];
}

class DashboardPartialError extends DashboardLoaded {
  final String errorMessage;
  final List<String> failedComponents;

  const DashboardPartialError({
    required this.errorMessage,
    required this.failedComponents,
    super.financialSummary,
    super.quickStats,
    super.categoryBreakdown,
    super.recentTransactions,
    super.predictions,
    super.insights,
    super.currentPeriod,
    required super.lastUpdated,
  });

  @override
  List<Object?> get props => [
        ...super.props,
        errorMessage,
        failedComponents,
      ];
}

// Component-specific states for individual loading
class DashboardComponentLoading extends DashboardLoaded {
  final List<String> loadingComponents;

  const DashboardComponentLoading({
    required this.loadingComponents,
    super.financialSummary,
    super.quickStats,
    super.categoryBreakdown,
    super.recentTransactions,
    super.predictions,
    super.insights,
    super.currentPeriod,
    required super.lastUpdated,
  });

  @override
  List<Object?> get props => [
        ...super.props,
        loadingComponents,
      ];
}