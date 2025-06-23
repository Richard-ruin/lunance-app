// lib/features/settings/domain/repositories/settings_repository.dart
import '../entities/user_settings.dart';

abstract class SettingsRepository {
  Future<UserSettings> getUserSettings();
  Future<void> updateUserSettings(UserSettings settings);
  Future<void> resetSettings();
  Future<bool> exportData();
  Future<void> deleteAccount();
}