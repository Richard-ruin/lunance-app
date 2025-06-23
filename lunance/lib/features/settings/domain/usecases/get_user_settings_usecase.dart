// lib/features/settings/domain/usecases/get_user_settings_usecase.dart
import '../entities/user_settings.dart';
import '../repositories/settings_repository.dart';

class GetUserSettingsUseCase {
  final SettingsRepository repository;

  GetUserSettingsUseCase(this.repository);

  Future<UserSettings> call() async {
    return await repository.getUserSettings();
  }
}