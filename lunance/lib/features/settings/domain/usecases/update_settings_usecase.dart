// lib/features/settings/domain/usecases/update_settings_usecase.dart
import '../entities/user_settings.dart';
import '../repositories/settings_repository.dart';

class UpdateSettingsUseCase {
  final SettingsRepository repository;

  UpdateSettingsUseCase(this.repository);

  Future<void> call(UserSettings settings) async {
    await repository.updateUserSettings(settings);
  }
}