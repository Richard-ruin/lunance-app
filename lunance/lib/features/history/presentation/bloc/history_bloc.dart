
// lib/features/history/presentation/bloc/history_bloc.dart
import 'package:flutter_bloc/flutter_bloc.dart';
import '../../domain/usecases/get_transaction_history_usecase.dart';
import '../../domain/usecases/search_transactions_usecase.dart';
import '../../domain/usecases/filter_transactions_usecase.dart';
import 'history_event.dart';
import 'history_state.dart';

class HistoryBloc extends Bloc<HistoryEvent, HistoryState> {
  final GetTransactionHistoryUseCase getTransactionHistoryUseCase;
  final SearchTransactionsUseCase searchTransactionsUseCase;
  final FilterTransactionsUseCase filterTransactionsUseCase;

  HistoryBloc({
    required this.getTransactionHistoryUseCase,
    required this.searchTransactionsUseCase,
    required this.filterTransactionsUseCase,
  }) : super(const HistoryInitial()) {
    on<LoadTransactionHistory>(_onLoadTransactionHistory);
    on<SearchTransactions>(_onSearchTransactions);
    on<FilterTransactions>(_onFilterTransactions);
    on<SortTransactions>(_onSortTransactions);
    on<ApplyFilterAndSort>(_onApplyFilterAndSort);
    on<ClearFilters>(_onClearFilters);
    on<RefreshHistory>(_onRefreshHistory);
  }

  Future<void> _onLoadTransactionHistory(
    LoadTransactionHistory event,
    Emitter<HistoryState> emit,
  ) async {
    emit(const HistoryLoading());
    
    try {
      final transactions = await getTransactionHistoryUseCase();
      emit(HistoryLoaded(
        transactions: transactions,
        filteredTransactions: transactions,
      ));
    } catch (e) {
      emit(HistoryError(e.toString()));
    }
  }

  Future<void> _onSearchTransactions(
    SearchTransactions event,
    Emitter<HistoryState> emit,
  ) async {
    if (state is! HistoryLoaded) return;
    
    final currentState = state as HistoryLoaded;
    
    try {
      final transactions = await searchTransactionsUseCase(event.query);
      
      emit(currentState.copyWith(
        filteredTransactions: transactions,
        searchQuery: event.query,
      ));
    } catch (e) {
      emit(HistoryError(e.toString()));
    }
  }

  Future<void> _onFilterTransactions(
    FilterTransactions event,
    Emitter<HistoryState> emit,
  ) async {
    if (state is! HistoryLoaded) return;
    
    final currentState = state as HistoryLoaded;
    
    try {
      final transactions = await filterTransactionsUseCase(
        filter: event.filter,
        sortType: currentState.activeSortType,
      );
      
      emit(currentState.copyWith(
        filteredTransactions: transactions,
        activeFilter: event.filter,
      ));
    } catch (e) {
      emit(HistoryError(e.toString()));
    }
  }

  Future<void> _onSortTransactions(
    SortTransactions event,
    Emitter<HistoryState> emit,
  ) async {
    if (state is! HistoryLoaded) return;
    
    final currentState = state as HistoryLoaded;
    
    try {
      final transactions = await filterTransactionsUseCase(
        filter: currentState.activeFilter,
        sortType: event.sortType,
      );
      
      emit(currentState.copyWith(
        filteredTransactions: transactions,
        activeSortType: event.sortType,
      ));
    } catch (e) {
      emit(HistoryError(e.toString()));
    }
  }

  Future<void> _onApplyFilterAndSort(
    ApplyFilterAndSort event,
    Emitter<HistoryState> emit,
  ) async {
    if (state is! HistoryLoaded) return;
    
    final currentState = state as HistoryLoaded;
    
    try {
      final transactions = await filterTransactionsUseCase(
        filter: event.filter,
        sortType: event.sortType,
      );
      
      emit(currentState.copyWith(
        filteredTransactions: transactions,
        activeFilter: event.filter,
        activeSortType: event.sortType,
      ));
    } catch (e) {
      emit(HistoryError(e.toString()));
    }
  }

  Future<void> _onClearFilters(
    ClearFilters event,
    Emitter<HistoryState> emit,
  ) async {
    if (state is! HistoryLoaded) return;
    
    final currentState = state as HistoryLoaded;
    
    emit(currentState.copyWith(
      filteredTransactions: currentState.transactions,
      clearFilter: true,
      clearSort: true,
      searchQuery: '',
    ));
  }

  Future<void> _onRefreshHistory(
    RefreshHistory event,
    Emitter<HistoryState> emit,
  ) async {
    try {
      final transactions = await getTransactionHistoryUseCase();
      
      if (state is HistoryLoaded) {
        final currentState = state as HistoryLoaded;
        emit(currentState.copyWith(
          transactions: transactions,
          filteredTransactions: transactions,
        ));
      } else {
        emit(HistoryLoaded(
          transactions: transactions,
          filteredTransactions: transactions,
        ));
      }
    } catch (e) {
      emit(HistoryError(e.toString()));
    }
  }
}