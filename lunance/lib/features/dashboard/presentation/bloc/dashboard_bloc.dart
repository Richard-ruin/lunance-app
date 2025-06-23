// lib/features/dashboard/presentation/bloc/dashboard_bloc.dart
import 'package:flutter_bloc/flutter_bloc.dart';
import '../../domain/usecases/get_financial_summary_usecase.dart';
import '../../domain/usecases/get_prediction_usecase.dart';
import 'dashboard_event.dart';
import 'dashboard_state.dart';

class DashboardBloc extends Bloc<DashboardEvent, DashboardState> {
  final GetFinancialSummaryUseCase getFinancialSummaryUseCase;
  final GetPredictionUseCase getPredictionUseCase;
  final GetMonthlyPredictionUseCase getMonthlyPredictionUseCase;

  DashboardBloc({
    required this.getFinancialSummaryUseCase,
    required this.getPredictionUseCase,
    required this.getMonthlyPredictionUseCase,
  }) : super(DashboardInitial()) {
    on<LoadDashboardData>(_onLoadDashboardData);
    on<RefreshDashboardData>(_onRefreshDashboardData);
    on<LoadPredictions>(_onLoadPredictions);
    on<LoadMonthlyPrediction>(_onLoadMonthlyPrediction);
  }

  Future<void> _onLoadDashboardData(
    LoadDashboardData event,
    Emitter<DashboardState> emit,
  ) async {
    emit(DashboardLoading());
    
    try {
      final financialSummary = await getFinancialSummaryUseCase();
      final predictions = await getPredictionUseCase();
      final monthlyPrediction = await getMonthlyPredictionUseCase();
      
      emit(DashboardLoaded(
        financialSummary: financialSummary,
        predictions: predictions,
        monthlyPrediction: monthlyPrediction,
      ));
    } catch (e) {
      emit(DashboardError(e.toString()));
    }
  }

  Future<void> _onRefreshDashboardData(
    RefreshDashboardData event,
    Emitter<DashboardState> emit,
  ) async {
    if (state is DashboardLoaded) {
      final currentState = state as DashboardLoaded;
      emit(DashboardRefreshing(
        financialSummary: currentState.financialSummary,
        predictions: currentState.predictions,
        monthlyPrediction: currentState.monthlyPrediction,
      ));
    }
    
    try {
      final financialSummary = await getFinancialSummaryUseCase();
      final predictions = await getPredictionUseCase();
      final monthlyPrediction = await getMonthlyPredictionUseCase();
      
      emit(DashboardLoaded(
        financialSummary: financialSummary,
        predictions: predictions,
        monthlyPrediction: monthlyPrediction,
      ));
    } catch (e) {
      emit(DashboardError(e.toString()));
    }
  }

  Future<void> _onLoadPredictions(
    LoadPredictions event,
    Emitter<DashboardState> emit,
  ) async {
    if (state is DashboardLoaded) {
      final currentState = state as DashboardLoaded;
      try {
        final predictions = await getPredictionUseCase();
        emit(currentState.copyWith(predictions: predictions));
      } catch (e) {
        // Keep current state if predictions fail to load
      }
    }
  }

  Future<void> _onLoadMonthlyPrediction(
    LoadMonthlyPrediction event,
    Emitter<DashboardState> emit,
  ) async {
    if (state is DashboardLoaded) {
      final currentState = state as DashboardLoaded;
      try {
        final monthlyPrediction = await getMonthlyPredictionUseCase();
        emit(currentState.copyWith(monthlyPrediction: monthlyPrediction));
      } catch (e) {
        // Keep current state if monthly prediction fails to load
      }
    }
  }
}