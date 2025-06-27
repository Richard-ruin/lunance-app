
// lib/features/dashboard/domain/usecases/get_recent_transactions_usecase.dart
import '../../../../core/network/api_result.dart';
import '../../../../core/usecases/usecase.dart';
import '../entities/recent_transactions.dart';
import '../repositories/dashboard_repository.dart';

class GetRecentTransactionsUseCase implements UseCase<RecentTransactions, RecentTransactionsParams> {
  final DashboardRepository repository;

  GetRecentTransactionsUseCase(this.repository);

  @override
  Future<ApiResult<RecentTransactions>> call(RecentTransactionsParams params) async {
    return await repository.getRecentTransactions(limit: params.limit);
  }
}

class RecentTransactionsParams {
  final int limit;

  const RecentTransactionsParams({
    this.limit = 5,
  });
}
