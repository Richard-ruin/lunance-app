// lib/features/settings/data/repositories/settings_repository_impl.dart
import '../../domain/entities/user_settings.dart';
import '../../domain/repositories/settings_repository.dart';
import '../datasources/settings_remote_datasource.dart';
import '../models/user_settings_model.dart';

class SettingsRepositoryImpl implements SettingsRepository {
  final SettingsRemoteDataSource remoteDataSource;

  SettingsRepositoryImpl({required this.remoteDataSource});

  @override
  Future<UserSettings> getUserSettings() async {
    try {
      final result = await remoteDataSource.getUserSettings();
      return result.toEntity();
    } catch (e) {
      throw Exception('Failed to get user settings: $e');
    }
  }

  @override
  Future<void> updateUserSettings(UserSettings settings) async {
    try {
      final model = UserSettingsModel.fromEntity(settings);
      await remoteDataSource.updateUserSettings(model);
    } catch (e) {
      throw Exception('Failed to update settings: $e');
    }
  }

  @override
  Future<void> resetSettings() async {
    try {
      await remoteDataSource.resetSettings();
    } catch (e) {
      throw Exception('Failed to reset settings: $e');
    }
  }

  @override
  Future<bool> exportData() async {
    try {
      return await remoteDataSource.exportData();
    } catch (e) {
      throw Exception('Failed to export data: $e');
    }
  }

  @override
  Future<void> deleteAccount() async {
    try {
      await remoteDataSource.deleteAccount();
    } catch (e) {
      throw Exception('Failed to delete account: $e');
    }
  }
}