// lib/features/settings/data/repositories/settings_repository_impl.dart
import '../../domain/entities/user_settings.dart';
import '../../domain/repositories/settings_repository.dart';
import '../datasources/settings_remote_datasource.dart';
import '../models/user_settings_model.dart';
import '../../../../core/network/api_result.dart';

class SettingsRepositoryImpl implements SettingsRepository {
  final SettingsRemoteDataSource remoteDataSource;

  SettingsRepositoryImpl(this.remoteDataSource);

  @override
  Future<ApiResult<UserSettings>> getUserSettings() async {
    try {
      final result = await remoteDataSource.getUserSettings();
      return result.when(
        success: (data) {
          // Convert UserSettingsModel to UserSettings
          final settings = _convertToUserSettings(data);
          return ApiResult.success(settings);
        },
        failure: (error) => ApiResult.failure(error),
      );
    } catch (e) {
      return ApiResult.failure('Gagal memuat pengaturan: ${e.toString()}');
    }
  }

  @override
  Future<ApiResult<UserSettings>> updateNotificationSettings(
    NotificationSettings settings,
  ) async {
    try {
      final settingsModel = _ensureNotificationSettingsModel(settings);
      final result = await remoteDataSource.updateNotificationSettings(settingsModel);
      
      return result.when(
        success: (data) {
          final updatedSettings = _convertToUserSettings(data);
          return ApiResult.success(updatedSettings);
        },
        failure: (error) => ApiResult.failure(error),
      );
    } catch (e) {
      return ApiResult.failure('Gagal memperbarui pengaturan notifikasi: ${e.toString()}');
    }
  }

  @override
  Future<ApiResult<UserSettings>> updateDisplaySettings(
    DisplaySettings settings,
  ) async {
    try {
      final settingsModel = _ensureDisplaySettingsModel(settings);
      final result = await remoteDataSource.updateDisplaySettings(settingsModel);
      
      return result.when(
        success: (data) {
          final updatedSettings = _convertToUserSettings(data);
          return ApiResult.success(updatedSettings);
        },
        failure: (error) => ApiResult.failure(error),
      );
    } catch (e) {
      return ApiResult.failure('Gagal memperbarui pengaturan tampilan: ${e.toString()}');
    }
  }

  @override
  Future<ApiResult<UserSettings>> updatePrivacySettings(
    PrivacySettings settings,
  ) async {
    try {
      final settingsModel = _ensurePrivacySettingsModel(settings);
      final result = await remoteDataSource.updatePrivacySettings(settingsModel);
      
      return result.when(
        success: (data) {
          final updatedSettings = _convertToUserSettings(data);
          return ApiResult.success(updatedSettings);
        },
        failure: (error) => ApiResult.failure(error),
      );
    } catch (e) {
      return ApiResult.failure('Gagal memperbarui pengaturan privasi: ${e.toString()}');
    }
  }

  // Helper methods
  UserSettings _convertToUserSettings(UserSettingsModel model) {
    return UserSettings(
      notifications: NotificationSettings(
        budgetAlerts: model.notifications.budgetAlerts,
        savingsReminders: model.notifications.savingsReminders,
        expenseSharingUpdates: model.notifications.expenseSharingUpdates,
        achievementNotifications: model.notifications.achievementNotifications,
      ),
      display: DisplaySettings(
        currency: model.display.currency,
        theme: model.display.theme,
        language: model.display.language,
      ),
      privacy: PrivacySettings(
        showInLeaderboard: model.privacy.showInLeaderboard,
        allowExpenseSharing: model.privacy.allowExpenseSharing,
      ),
    );
  }

  NotificationSettingsModel _ensureNotificationSettingsModel(NotificationSettings settings) {
    if (settings is NotificationSettingsModel) {
      return settings;
    }
    return NotificationSettingsModel(
      budgetAlerts: settings.budgetAlerts,
      savingsReminders: settings.savingsReminders,
      expenseSharingUpdates: settings.expenseSharingUpdates,
      achievementNotifications: settings.achievementNotifications,
    );
  }

  DisplaySettingsModel _ensureDisplaySettingsModel(DisplaySettings settings) {
    if (settings is DisplaySettingsModel) {
      return settings;
    }
    return DisplaySettingsModel(
      currency: settings.currency,
      theme: settings.theme,
      language: settings.language,
    );
  }

  PrivacySettingsModel _ensurePrivacySettingsModel(PrivacySettings settings) {
    if (settings is PrivacySettingsModel) {
      return settings;
    }
    return PrivacySettingsModel(
      showInLeaderboard: settings.showInLeaderboard,
      allowExpenseSharing: settings.allowExpenseSharing,
    );
  }
}