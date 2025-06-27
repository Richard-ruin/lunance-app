
// lib/features/dashboard/domain/usecases/get_predictions_usecase.dart
import '../../../../core/network/api_result.dart';
import '../../../../core/usecases/usecase.dart';
import '../entities/prediction.dart';
import '../repositories/dashboard_repository.dart';

class GetPredictionsUseCase implements UseCase<Prediction, PredictionsParams> {
  final DashboardRepository repository;

  GetPredictionsUseCase(this.repository);

  @override
  Future<ApiResult<Prediction>> call(PredictionsParams params) async {
    return await repository.getPredictions(
      predictionType: params.predictionType,
      daysAhead: params.daysAhead,
    );
  }
}

class PredictionsParams {
  final String predictionType;
  final int daysAhead;

  const PredictionsParams({
    this.predictionType = 'expense',
    this.daysAhead = 30,
  });
}