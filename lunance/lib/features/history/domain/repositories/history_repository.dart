// lib/features/history/domain/repositories/history_repository.dart
import '../entities/transaction_history.dart';
import '../entities/filter.dart';
import '../entities/sort_type.dart';

abstract class HistoryRepository {
  Future<List<TransactionHistory>> getTransactionHistory();
  Future<List<TransactionHistory>> searchTransactions(String query);
  Future<List<TransactionHistory>> filterTransactions(Filter filter);
  Future<List<TransactionHistory>> sortTransactions(List<TransactionHistory> transactions, SortType sortType);
  Future<TransactionHistory?> getTransactionById(String id);
}