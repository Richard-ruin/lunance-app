
// lib/features/settings/domain/usecases/update_settings_usecase.dart
import '../entities/user_settings.dart';
import '../repositories/settings_repository.dart';
import '../../../../core/network/api_result.dart';

class UpdateNotificationSettingsUseCase {
  final SettingsRepository repository;

  UpdateNotificationSettingsUseCase(this.repository);

  Future<ApiResult<UserSettings>> call(NotificationSettings settings) async {
    return await repository.updateNotificationSettings(settings);
  }
}

class UpdateDisplaySettingsUseCase {
  final SettingsRepository repository;

  UpdateDisplaySettingsUseCase(this.repository);

  Future<ApiResult<UserSettings>> call(DisplaySettings settings) async {
    return await repository.updateDisplaySettings(settings);
  }
}

class UpdatePrivacySettingsUseCase {
  final SettingsRepository repository;

  UpdatePrivacySettingsUseCase(this.repository);

  Future<ApiResult<UserSettings>> call(PrivacySettings settings) async {
    return await repository.updatePrivacySettings(settings);
  }
}