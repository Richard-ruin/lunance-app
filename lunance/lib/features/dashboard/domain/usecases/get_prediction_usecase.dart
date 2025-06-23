// lib/features/dashboard/domain/usecases/get_prediction_usecase.dart
import '../entities/prediction.dart';
import '../repositories/dashboard_repository.dart';

class GetPredictionUseCase {
  final DashboardRepository repository;

  GetPredictionUseCase(this.repository);

  Future<List<Prediction>> call() async {
    return await repository.getPredictions();
  }
}

class GetMonthlyPredictionUseCase {
  final DashboardRepository repository;

  GetMonthlyPredictionUseCase(this.repository);

  Future<MonthlyPrediction> call() async {
    return await repository.getMonthlyPrediction();
  }
}