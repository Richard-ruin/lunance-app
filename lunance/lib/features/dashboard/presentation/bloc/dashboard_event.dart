// lib/features/dashboard/presentation/bloc/dashboard_event.dart
import 'package:equatable/equatable.dart';

abstract class DashboardEvent extends Equatable {
  const DashboardEvent();

  @override
  List<Object> get props => [];
}

class LoadDashboardData extends DashboardEvent {
  final String period;

  const LoadDashboardData({
    this.period = 'monthly',
  });

  @override
  List<Object> get props => [period];
}

class RefreshDashboard extends DashboardEvent {
  final String period;

  const RefreshDashboard({
    this.period = 'monthly',
  });

  @override
  List<Object> get props => [period];
}

class ChangePeriod extends DashboardEvent {
  final String period;

  const ChangePeriod(this.period);

  @override
  List<Object> get props => [period];
}

class LoadFinancialSummary extends DashboardEvent {
  final String period;

  const LoadFinancialSummary({
    this.period = 'monthly',
  });

  @override
  List<Object> get props => [period];
}

class LoadQuickStats extends DashboardEvent {}

class LoadCategoryBreakdown extends DashboardEvent {
  final String period;
  final int limit;

  const LoadCategoryBreakdown({
    this.period = 'monthly',
    this.limit = 5,
  });

  @override
  List<Object> get props => [period, limit];
}

class LoadRecentTransactions extends DashboardEvent {
  final int limit;

  const LoadRecentTransactions({
    this.limit = 5,
  });

  @override
  List<Object> get props => [limit];
}

class LoadPredictions extends DashboardEvent {
  final String predictionType;
  final int daysAhead;

  const LoadPredictions({
    this.predictionType = 'expense',
    this.daysAhead = 30,
  });

  @override
  List<Object> get props => [predictionType, daysAhead];
}

class LoadFinancialInsights extends DashboardEvent {}