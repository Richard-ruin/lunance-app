// lib/features/history/domain/usecases/search_transactions_usecase.dart
import '../entities/transaction_history.dart';
import '../repositories/history_repository.dart';

class SearchTransactionsUseCase {
  final HistoryRepository repository;

  SearchTransactionsUseCase({required this.repository});

  Future<List<TransactionHistory>> call(String query) async {
    try {
      if (query.trim().isEmpty) {
        return await repository.getTransactionHistory();
      }
      return await repository.searchTransactions(query.trim());
    } catch (e) {
      throw Exception('Failed to search transactions: $e');
    }
  }
}