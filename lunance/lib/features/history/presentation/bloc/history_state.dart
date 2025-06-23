// lib/features/history/presentation/bloc/history_state.dart
import 'package:equatable/equatable.dart';
import '../../domain/entities/transaction_history.dart';
import '../../domain/entities/filter.dart';
import '../../domain/entities/sort_type.dart';

abstract class HistoryState extends Equatable {
  const HistoryState();

  @override
  List<Object?> get props => [];
}

class HistoryInitial extends HistoryState {
  const HistoryInitial();
}

class HistoryLoading extends HistoryState {
  const HistoryLoading();
}

class HistoryLoaded extends HistoryState {
  final List<TransactionHistory> transactions;
  final List<TransactionHistory> filteredTransactions;
  final Filter? activeFilter;
  final SortType? activeSortType;
  final String searchQuery;

  const HistoryLoaded({
    required this.transactions,
    required this.filteredTransactions,
    this.activeFilter,
    this.activeSortType,
    this.searchQuery = '',
  });

  @override
  List<Object?> get props => [
    transactions,
    filteredTransactions,
    activeFilter,
    activeSortType,
    searchQuery,
  ];

  HistoryLoaded copyWith({
    List<TransactionHistory>? transactions,
    List<TransactionHistory>? filteredTransactions,
    Filter? activeFilter,
    SortType? activeSortType,
    String? searchQuery,
    bool clearFilter = false,
    bool clearSort = false,
  }) {
    return HistoryLoaded(
      transactions: transactions ?? this.transactions,
      filteredTransactions: filteredTransactions ?? this.filteredTransactions,
      activeFilter: clearFilter ? null : (activeFilter ?? this.activeFilter),
      activeSortType: clearSort ? null : (activeSortType ?? this.activeSortType),
      searchQuery: searchQuery ?? this.searchQuery,
    );
  }
}

class HistoryError extends HistoryState {
  final String message;

  const HistoryError(this.message);

  @override
  List<Object> get props => [message];
}