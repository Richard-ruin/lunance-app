// lib/features/dashboard/presentation/bloc/dashboard_event.dart
abstract class DashboardEvent {}

class LoadDashboardData extends DashboardEvent {}

class RefreshDashboardData extends DashboardEvent {}

class LoadPredictions extends DashboardEvent {}

class LoadMonthlyPrediction extends DashboardEvent {}