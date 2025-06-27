
// lib/features/dashboard/domain/usecases/get_quick_stats_usecase.dart
import '../../../../core/network/api_result.dart';
import '../../../../core/usecases/usecase.dart';
import '../entities/quick_stats.dart';
import '../repositories/dashboard_repository.dart';

class GetQuickStatsUseCase implements UseCase<QuickStats, NoParams> {
  final DashboardRepository repository;

  GetQuickStatsUseCase(this.repository);

  @override
  Future<ApiResult<QuickStats>> call(NoParams params) async {
    return await repository.getQuickStats();
  }
}