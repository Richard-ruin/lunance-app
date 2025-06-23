// lib/features/history/presentation/bloc/history_event.dart
import 'package:equatable/equatable.dart';
import '../../domain/entities/filter.dart';
import '../../domain/entities/sort_type.dart';

abstract class HistoryEvent extends Equatable {
  const HistoryEvent();

  @override
  List<Object?> get props => [];
}

class LoadTransactionHistory extends HistoryEvent {
  const LoadTransactionHistory();
}

class SearchTransactions extends HistoryEvent {
  final String query;

  const SearchTransactions(this.query);

  @override
  List<Object> get props => [query];
}

class FilterTransactions extends HistoryEvent {
  final Filter filter;

  const FilterTransactions(this.filter);

  @override
  List<Object> get props => [filter];
}

class SortTransactions extends HistoryEvent {
  final SortType sortType;

  const SortTransactions(this.sortType);

  @override
  List<Object> get props => [sortType];
}

class ApplyFilterAndSort extends HistoryEvent {
  final Filter? filter;
  final SortType? sortType;

  const ApplyFilterAndSort({this.filter, this.sortType});

  @override
  List<Object?> get props => [filter, sortType];
}

class ClearFilters extends HistoryEvent {
  const ClearFilters();
}

class RefreshHistory extends HistoryEvent {
  const RefreshHistory();
}