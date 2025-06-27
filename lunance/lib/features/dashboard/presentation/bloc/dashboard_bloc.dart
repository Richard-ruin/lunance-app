// lib/features/dashboard/presentation/bloc/dashboard_bloc.dart
// JIKA MASIH ERROR, GUNAKAN VERSI INI DENGAN EXPLICIT CASTING

import 'package:flutter_bloc/flutter_bloc.dart';
import '../../../../core/usecases/usecase.dart';
import '../../../../core/network/api_result.dart';
import '../../domain/entities/financial_summary.dart';
import '../../domain/entities/quick_stats.dart';
import '../../domain/entities/category_breakdown.dart';
import '../../domain/entities/recent_transactions.dart';
import '../../domain/entities/prediction.dart';
import '../../domain/entities/financial_insights.dart';
import '../../domain/usecases/get_financial_summary_usecase.dart';
import '../../domain/usecases/get_quick_stats_usecase.dart';
import '../../domain/usecases/get_category_breakdown_usecase.dart';
import '../../domain/usecases/get_recent_transactions_usecase.dart';
import '../../domain/usecases/get_predictions_usecase.dart';
import '../../domain/usecases/get_financial_insights_usecase.dart';
import 'dashboard_event.dart';
import 'dashboard_state.dart';

class DashboardBloc extends Bloc<DashboardEvent, DashboardState> {
  final GetFinancialSummaryUseCase getFinancialSummaryUseCase;
  final GetQuickStatsUseCase getQuickStatsUseCase;
  final GetCategoryBreakdownUseCase getCategoryBreakdownUseCase;
  final GetRecentTransactionsUseCase getRecentTransactionsUseCase;
  final GetPredictionsUseCase getPredictionsUseCase;
  final GetFinancialInsightsUseCase getFinancialInsightsUseCase;

  DashboardBloc({
    required this.getFinancialSummaryUseCase,
    required this.getQuickStatsUseCase,
    required this.getCategoryBreakdownUseCase,
    required this.getRecentTransactionsUseCase,
    required this.getPredictionsUseCase,
    required this.getFinancialInsightsUseCase,
  }) : super(DashboardInitial()) {
    on<LoadDashboardData>(_onLoadDashboardData);
    on<RefreshDashboard>(_onRefreshDashboard);
    on<ChangePeriod>(_onChangePeriod);
    on<LoadFinancialSummary>(_onLoadFinancialSummary);
    on<LoadQuickStats>(_onLoadQuickStats);
    on<LoadCategoryBreakdown>(_onLoadCategoryBreakdown);
    on<LoadRecentTransactions>(_onLoadRecentTransactions);
    on<LoadPredictions>(_onLoadPredictions);
    on<LoadFinancialInsights>(_onLoadFinancialInsights);
  }

  Future<void> _onLoadDashboardData(
    LoadDashboardData event,
    Emitter<DashboardState> emit,
  ) async {
    if (state is! DashboardLoaded) {
      emit(DashboardLoading());
    }

    try {
      // Load all dashboard components in parallel
      final results = await Future.wait([
        getFinancialSummaryUseCase(FinancialSummaryParams(period: event.period)),
        getQuickStatsUseCase( NoParams()),
        getCategoryBreakdownUseCase(CategoryBreakdownParams(period: event.period)),
        getRecentTransactionsUseCase(const RecentTransactionsParams()),
      ]);

      final financialSummaryResult = results[0] as ApiResult<FinancialSummary>;
      final quickStatsResult = results[1] as ApiResult<QuickStats>;
      final categoryBreakdownResult = results[2] as ApiResult<CategoryBreakdown>;
      final recentTransactionsResult = results[3] as ApiResult<RecentTransactions>;

      // Check if all core components loaded successfully
      if (financialSummaryResult.isSuccess &&
          quickStatsResult.isSuccess &&
          categoryBreakdownResult.isSuccess &&
          recentTransactionsResult.isSuccess) {
        
        emit(DashboardLoaded(
          financialSummary: financialSummaryResult.data!,
          quickStats: quickStatsResult.data!,
          categoryBreakdown: categoryBreakdownResult.data!,
          recentTransactions: recentTransactionsResult.data!,
          currentPeriod: event.period,
          lastUpdated: DateTime.now(),
        ));

        // Load additional components (predictions and insights) separately
        add(const LoadPredictions());
        add( LoadFinancialInsights());
        
      } else {
        // Handle partial loading
        final failedComponents = <String>[];
        String errorMessage = 'Beberapa data gagal dimuat';

        if (financialSummaryResult.isFailure) failedComponents.add('financial_summary');
        if (quickStatsResult.isFailure) failedComponents.add('quick_stats');
        if (categoryBreakdownResult.isFailure) failedComponents.add('category_breakdown');
        if (recentTransactionsResult.isFailure) failedComponents.add('recent_transactions');

        emit(DashboardPartialError(
          errorMessage: errorMessage,
          failedComponents: failedComponents,
          financialSummary: financialSummaryResult.data,
          quickStats: quickStatsResult.data,
          categoryBreakdown: categoryBreakdownResult.data,
          recentTransactions: recentTransactionsResult.data,
          currentPeriod: event.period,
          lastUpdated: DateTime.now(),
        ));
      }
    } catch (e) {
      emit(DashboardError(
        message: 'Gagal memuat data dashboard: ${e.toString()}',
      ));
    }
  }

  Future<void> _onRefreshDashboard(
    RefreshDashboard event,
    Emitter<DashboardState> emit,
  ) async {
    add(LoadDashboardData(period: event.period));
  }

  Future<void> _onChangePeriod(
    ChangePeriod event,
    Emitter<DashboardState> emit,
  ) async {
    if (state is DashboardLoaded) {
      final currentState = state as DashboardLoaded;
      emit(DashboardComponentLoading(
        loadingComponents: const ['financial_summary', 'category_breakdown'],
        financialSummary: currentState.financialSummary,
        quickStats: currentState.quickStats,
        categoryBreakdown: currentState.categoryBreakdown,
        recentTransactions: currentState.recentTransactions,
        predictions: currentState.predictions,
        insights: currentState.insights,
        currentPeriod: event.period,
        lastUpdated: currentState.lastUpdated,
      ));
    }

    add(LoadFinancialSummary(period: event.period));
    add(LoadCategoryBreakdown(period: event.period));
  }

  Future<void> _onLoadFinancialSummary(
    LoadFinancialSummary event,
    Emitter<DashboardState> emit,
  ) async {
    final result = await getFinancialSummaryUseCase(
      FinancialSummaryParams(period: event.period),
    );

    if (result.isSuccess) {
      if (state is DashboardLoaded) {
        emit((state as DashboardLoaded).copyWith(
          financialSummary: result.data!,
          currentPeriod: event.period,
          lastUpdated: DateTime.now(),
        ));
      }
    } else {
      if (state is DashboardLoaded) {
        // Keep existing state but show error for this component
        emit(DashboardPartialError(
          errorMessage: 'Gagal memuat ringkasan keuangan',
          failedComponents: const ['financial_summary'],
          financialSummary: (state as DashboardLoaded).financialSummary,
          quickStats: (state as DashboardLoaded).quickStats,
          categoryBreakdown: (state as DashboardLoaded).categoryBreakdown,
          recentTransactions: (state as DashboardLoaded).recentTransactions,
          predictions: (state as DashboardLoaded).predictions,
          insights: (state as DashboardLoaded).insights,
          currentPeriod: event.period,
          lastUpdated: DateTime.now(),
        ));
      }
    }
  }

  Future<void> _onLoadQuickStats(
    LoadQuickStats event,
    Emitter<DashboardState> emit,
  ) async {
    final result = await getQuickStatsUseCase( NoParams());

    if (result.isSuccess) {
      if (state is DashboardLoaded) {
        emit((state as DashboardLoaded).copyWith(
          quickStats: result.data!,
          lastUpdated: DateTime.now(),
        ));
      }
    }
    // Handle error silently for optional components
  }

  Future<void> _onLoadCategoryBreakdown(
    LoadCategoryBreakdown event,
    Emitter<DashboardState> emit,
  ) async {
    final result = await getCategoryBreakdownUseCase(
      CategoryBreakdownParams(period: event.period, limit: event.limit),
    );

    if (result.isSuccess) {
      if (state is DashboardLoaded) {
        emit((state as DashboardLoaded).copyWith(
          categoryBreakdown: result.data!,
          lastUpdated: DateTime.now(),
        ));
      }
    }
    // Handle error silently for optional components
  }

  Future<void> _onLoadRecentTransactions(
    LoadRecentTransactions event,
    Emitter<DashboardState> emit,
  ) async {
    final result = await getRecentTransactionsUseCase(
      RecentTransactionsParams(limit: event.limit),
    );

    if (result.isSuccess) {
      if (state is DashboardLoaded) {
        emit((state as DashboardLoaded).copyWith(
          recentTransactions: result.data!,
          lastUpdated: DateTime.now(),
        ));
      }
    }
    // Handle error silently for optional components
  }

  Future<void> _onLoadPredictions(
    LoadPredictions event,
    Emitter<DashboardState> emit,
  ) async {
    final result = await getPredictionsUseCase(
      PredictionsParams(
        predictionType: event.predictionType,
        daysAhead: event.daysAhead,
      ),
    );

    if (result.isSuccess) {
      if (state is DashboardLoaded) {
        emit((state as DashboardLoaded).copyWith(
          predictions: result.data!,
          lastUpdated: DateTime.now(),
        ));
      }
    }
    // Predictions are optional, don't show error
  }

  Future<void> _onLoadFinancialInsights(
    LoadFinancialInsights event,
    Emitter<DashboardState> emit,
  ) async {
    final result = await getFinancialInsightsUseCase( NoParams());

    if (result.isSuccess) {
      if (state is DashboardLoaded) {
        emit((state as DashboardLoaded).copyWith(
          insights: result.data!,
          lastUpdated: DateTime.now(),
        ));
      }
    }
    // Insights are optional, don't show error
  }
}