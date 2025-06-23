// lib/features/settings/data/datasources/settings_remote_datasource.dart
import '../models/user_settings_model.dart';

abstract class SettingsRemoteDataSource {
  Future<UserSettingsModel> getUserSettings();
  Future<void> updateUserSettings(UserSettingsModel settings);
  Future<void> resetSettings();
  Future<bool> exportData();
  Future<void> deleteAccount();
}

class SettingsRemoteDataSourceImpl implements SettingsRemoteDataSource {
  // Mock implementation for now
  @override
  Future<UserSettingsModel> getUserSettings() async {
    // Simulate API call delay
    await Future.delayed(const Duration(milliseconds: 500));
    
    // Return mock data
    return const UserSettingsModel(
      userId: 'user123',
      name: 'John Doe',
      email: 'john.doe@example.com',
      profilePicture: '',
      currency: 'IDR',
      language: 'id',
      darkMode: false,
      notifications: true,
      biometricAuth: false,
      autoBackup: true,
      defaultCategory: 'Lainnya',
      monthlyBudget: 5000000.0,
    );
  }

  @override
  Future<void> updateUserSettings(UserSettingsModel settings) async {
    // Simulate API call delay
    await Future.delayed(const Duration(milliseconds: 500));
    
    // Mock API call - in real implementation, this would make HTTP request
    print('Updating settings: ${settings.toJson()}');
  }

  @override
  Future<void> resetSettings() async {
    await Future.delayed(const Duration(milliseconds: 500));
    print('Resetting settings to default');
  }

  @override
  Future<bool> exportData() async {
    await Future.delayed(const Duration(seconds: 2));
    // Mock export - in real implementation, this would generate and download file
    print('Exporting user data');
    return true;
  }

  @override
  Future<void> deleteAccount() async {
    await Future.delayed(const Duration(milliseconds: 1000));
    print('Deleting user account');
  }
}