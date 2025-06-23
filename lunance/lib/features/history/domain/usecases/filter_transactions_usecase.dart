// lib/features/history/domain/usecases/filter_transactions_usecase.dart
import '../entities/transaction_history.dart';
import '../entities/filter.dart';
import '../entities/sort_type.dart';
import '../repositories/history_repository.dart';

class FilterTransactionsUseCase {
  final HistoryRepository repository;

  FilterTransactionsUseCase({required this.repository});

  Future<List<TransactionHistory>> call({
    Filter? filter,
    SortType? sortType,
  }) async {
    try {
      List<TransactionHistory> transactions;
      
      if (filter != null) {
        transactions = await repository.filterTransactions(filter);
      } else {
        transactions = await repository.getTransactionHistory();
      }
      
      if (sortType != null) {
        transactions = await repository.sortTransactions(transactions, sortType);
      }
      
      return transactions;
    } catch (e) {
      throw Exception('Failed to filter transactions: $e');
    }
  }
}