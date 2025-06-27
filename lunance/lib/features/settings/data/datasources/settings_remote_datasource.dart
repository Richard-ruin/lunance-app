// lib/features/settings/data/datasources/settings_remote_datasource.dart (Mock Implementation)
import '../models/user_settings_model.dart';
import '../../../../core/network/api_result.dart';
import '../../../../core/utils/dio_client.dart';
import '../../../../core/constants/api_endpoints.dart';

abstract class SettingsRemoteDataSource {
  Future<ApiResult<UserSettingsModel>> getUserSettings();
  Future<ApiResult<UserSettingsModel>> updateNotificationSettings(NotificationSettingsModel settings);
  Future<ApiResult<UserSettingsModel>> updateDisplaySettings(DisplaySettingsModel settings);
  Future<ApiResult<UserSettingsModel>> updatePrivacySettings(PrivacySettingsModel settings);
}

class SettingsRemoteDataSourceImpl implements SettingsRemoteDataSource {
  final DioClient dioClient;

  SettingsRemoteDataSourceImpl(this.dioClient);

  @override
  Future<ApiResult<UserSettingsModel>> getUserSettings() async {
    try {
      // Mock delay to simulate API call
      await Future.delayed(const Duration(milliseconds: 500));
      
      // Return default/mock settings instead of making actual API call
      // This prevents "method not allowed" error when backend is not ready
      final mockSettings = UserSettingsModel(
        notifications: const NotificationSettingsModel(
          budgetAlerts: true,
          savingsReminders: true,
          expenseSharingUpdates: true,
          achievementNotifications: true,
        ),
        display: const DisplaySettingsModel(
          currency: 'IDR',
          theme: 'light',
          language: 'id',
        ),
        privacy: const PrivacySettingsModel(
          showInLeaderboard: true,
          allowExpenseSharing: true,
        ),
      );
      
      return ApiResult.success(mockSettings);
      
      // Uncomment below for actual API call when backend is ready:
      /*
      final response = await dioClient.get(ApiEndpoints.userSettings);
      
      if (response.statusCode == 200) {
        Map<String, dynamic> data;
        if (response.data is Map<String, dynamic>) {
          data = response.data as Map<String, dynamic>;
        } else {
          data = {
            'notifications': {
              'budget_alerts': true,
              'savings_reminders': true,
              'expense_sharing_updates': true,
              'achievement_notifications': true,
            },
            'display': {
              'currency': 'IDR',
              'theme': 'light',
              'language': 'id',
            },
            'privacy': {
              'show_in_leaderboard': true,
              'allow_expense_sharing': true,
            },
          };
        }
        
        final settingsModel = UserSettingsModel.fromJson(data);
        return ApiResult.success(settingsModel);
      } else {
        return ApiResult.failure('Gagal memuat pengaturan: ${response.statusMessage ?? 'Unknown error'}');
      }
      */
    } catch (e) {
      // Return default settings on error
      final defaultSettings = UserSettingsModel(
        notifications: const NotificationSettingsModel(
          budgetAlerts: true,
          savingsReminders: true,
          expenseSharingUpdates: true,
          achievementNotifications: true,
        ),
        display: const DisplaySettingsModel(
          currency: 'IDR',
          theme: 'light',
          language: 'id',
        ),
        privacy: const PrivacySettingsModel(
          showInLeaderboard: true,
          allowExpenseSharing: true,
        ),
      );
      return ApiResult.success(defaultSettings);
    }
  }

  @override
  Future<ApiResult<UserSettingsModel>> updateNotificationSettings(
    NotificationSettingsModel settings,
  ) async {
    try {
      // Mock delay to simulate API call
      await Future.delayed(const Duration(milliseconds: 800));
      
      // Return updated settings with the new notification settings
      final updatedSettings = UserSettingsModel(
        notifications: settings,
        display: const DisplaySettingsModel(
          currency: 'IDR',
          theme: 'light',
          language: 'id',
        ),
        privacy: const PrivacySettingsModel(
          showInLeaderboard: true,
          allowExpenseSharing: true,
        ),
      );
      
      return ApiResult.success(updatedSettings);
      
      // Uncomment below for actual API call when backend is ready:
      /*
      final response = await dioClient.put(
        ApiEndpoints.updateNotificationSettings,
        data: {
          'notifications': settings.toJson(),
        },
      );
      
      if (response.statusCode == 200) {
        final data = response.data as Map<String, dynamic>;
        final updatedSettings = UserSettingsModel.fromJson(data);
        return ApiResult.success(updatedSettings);
      } else {
        return ApiResult.failure('Gagal memperbarui pengaturan notifikasi: ${response.statusMessage ?? 'Unknown error'}');
      }
      */
    } catch (e) {
      return ApiResult.failure('Error updating notification settings: ${e.toString()}');
    }
  }

  @override
  Future<ApiResult<UserSettingsModel>> updateDisplaySettings(
    DisplaySettingsModel settings,
  ) async {
    try {
      // Mock delay to simulate API call
      await Future.delayed(const Duration(milliseconds: 800));
      
      // Return updated settings with the new display settings
      final updatedSettings = UserSettingsModel(
        notifications: const NotificationSettingsModel(
          budgetAlerts: true,
          savingsReminders: true,
          expenseSharingUpdates: true,
          achievementNotifications: true,
        ),
        display: settings,
        privacy: const PrivacySettingsModel(
          showInLeaderboard: true,
          allowExpenseSharing: true,
        ),
      );
      
      return ApiResult.success(updatedSettings);
      
      // Uncomment below for actual API call when backend is ready:
      /*
      final response = await dioClient.put(
        ApiEndpoints.updateDisplaySettings,
        data: {
          'display': settings.toJson(),
        },
      );
      
      if (response.statusCode == 200) {
        final data = response.data as Map<String, dynamic>;
        final updatedSettings = UserSettingsModel.fromJson(data);
        return ApiResult.success(updatedSettings);
      } else {
        return ApiResult.failure('Gagal memperbarui pengaturan tampilan: ${response.statusMessage ?? 'Unknown error'}');
      }
      */
    } catch (e) {
      return ApiResult.failure('Error updating display settings: ${e.toString()}');
    }
  }

  @override
  Future<ApiResult<UserSettingsModel>> updatePrivacySettings(
    PrivacySettingsModel settings,
  ) async {
    try {
      // Mock delay to simulate API call
      await Future.delayed(const Duration(milliseconds: 800));
      
      // Return updated settings with the new privacy settings
      final updatedSettings = UserSettingsModel(
        notifications: const NotificationSettingsModel(
          budgetAlerts: true,
          savingsReminders: true,
          expenseSharingUpdates: true,
          achievementNotifications: true,
        ),
        display: const DisplaySettingsModel(
          currency: 'IDR',
          theme: 'light',
          language: 'id',
        ),
        privacy: settings,
      );
      
      return ApiResult.success(updatedSettings);
      
      // Uncomment below for actual API call when backend is ready:
      /*
      final response = await dioClient.put(
        ApiEndpoints.updatePrivacySettings,
        data: {
          'privacy': settings.toJson(),
        },
      );
      
      if (response.statusCode == 200) {
        final data = response.data as Map<String, dynamic>;
        final updatedSettings = UserSettingsModel.fromJson(data);
        return ApiResult.success(updatedSettings);
      } else {
        return ApiResult.failure('Gagal memperbarui pengaturan privasi: ${response.statusMessage ?? 'Unknown error'}');
      }
      */
    } catch (e) {
      return ApiResult.failure('Error updating privacy settings: ${e.toString()}');
    }
  }
}