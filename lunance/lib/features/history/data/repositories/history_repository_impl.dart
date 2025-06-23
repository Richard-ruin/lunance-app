// lib/features/history/data/repositories/history_repository_impl.dart
import '../../domain/entities/transaction_history.dart';
import '../../domain/entities/filter.dart';
import '../../domain/entities/sort_type.dart';
import '../../domain/repositories/history_repository.dart';
import '../datasources/history_remote_datasource.dart';
import '../models/filter_model.dart';

class HistoryRepositoryImpl implements HistoryRepository {
  final HistoryRemoteDataSource remoteDataSource;

  HistoryRepositoryImpl({required this.remoteDataSource});

  @override
  Future<List<TransactionHistory>> getTransactionHistory() async {
    try {
      final transactions = await remoteDataSource.getTransactionHistory();
      return transactions;
    } catch (e) {
      throw Exception('Failed to get transaction history: $e');
    }
  }

  @override
  Future<List<TransactionHistory>> searchTransactions(String query) async {
    try {
      final transactions = await remoteDataSource.searchTransactions(query);
      return transactions;
    } catch (e) {
      throw Exception('Failed to search transactions: $e');
    }
  }

  @override
  Future<List<TransactionHistory>> filterTransactions(Filter filter) async {
    try {
      final filterModel = FilterModel.fromEntity(filter);
      final transactions = await remoteDataSource.filterTransactions(filterModel);
      return transactions;
    } catch (e) {
      throw Exception('Failed to filter transactions: $e');
    }
  }

  @override
  Future<List<TransactionHistory>> sortTransactions(
      List<TransactionHistory> transactions, SortType sortType) async {
    try {
      var sortedTransactions = List<TransactionHistory>.from(transactions);
      
      switch (sortType) {
        case SortType.dateNewest:
          sortedTransactions.sort((a, b) => b.date.compareTo(a.date));
          break;
        case SortType.dateOldest:
          sortedTransactions.sort((a, b) => a.date.compareTo(b.date));
          break;
        case SortType.amountHighest:
          sortedTransactions.sort((a, b) => b.amount.compareTo(a.amount));
          break;
        case SortType.amountLowest:
          sortedTransactions.sort((a, b) => a.amount.compareTo(b.amount));
          break;
        case SortType.alphabetical:
          sortedTransactions.sort((a, b) => a.title.compareTo(b.title));
          break;
        case SortType.nameAZ:
          sortedTransactions.sort((a, b) => a.title.compareTo(b.title));
          break;
        case SortType.nameZA:
          sortedTransactions.sort((a, b) => b.title.compareTo(a.title));
          break;
      }
      
      return sortedTransactions;
    } catch (e) {
      throw Exception('Failed to sort transactions: $e');
    }
  }

  @override
  Future<TransactionHistory?> getTransactionById(String id) async {
    try {
      final transaction = await remoteDataSource.getTransactionById(id);
      return transaction;
    } catch (e) {
      throw Exception('Failed to get transaction by id: $e');
    }
  }
}