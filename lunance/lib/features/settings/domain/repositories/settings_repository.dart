// lib/features/settings/domain/repositories/settings_repository.dart
import '../entities/user_settings.dart';
import '../../../../core/network/api_result.dart';

abstract class SettingsRepository {
  Future<ApiResult<UserSettings>> getUserSettings();
  Future<ApiResult<UserSettings>> updateNotificationSettings(NotificationSettings settings);
  Future<ApiResult<UserSettings>> updateDisplaySettings(DisplaySettings settings);
  Future<ApiResult<UserSettings>> updatePrivacySettings(PrivacySettings settings);
}