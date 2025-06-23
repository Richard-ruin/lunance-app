// lib/features/history/domain/usecases/get_transaction_history_usecase.dart
import '../entities/transaction_history.dart';
import '../repositories/history_repository.dart';

class GetTransactionHistoryUseCase {
  final HistoryRepository repository;

  GetTransactionHistoryUseCase({required this.repository});

  Future<List<TransactionHistory>> call() async {
    try {
      return await repository.getTransactionHistory();
    } catch (e) {
      throw Exception('Failed to get transaction history: $e');
    }
  }
}