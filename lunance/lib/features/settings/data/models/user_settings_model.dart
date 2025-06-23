// lib/features/settings/data/models/user_settings_model.dart
import '../../domain/entities/user_settings.dart';

class UserSettingsModel extends UserSettings {
  const UserSettingsModel({
    required super.userId,
    required super.name,
    required super.email,
    super.profilePicture,
    super.currency,
    super.language,
    super.darkMode,
    super.notifications,
    super.biometricAuth,
    super.autoBackup,
    super.defaultCategory,
    super.monthlyBudget,
  });

  factory UserSettingsModel.fromJson(Map<String, dynamic> json) {
    return UserSettingsModel(
      userId: json['userId'] ?? '',
      name: json['name'] ?? '',
      email: json['email'] ?? '',
      profilePicture: json['profilePicture'] ?? '',
      currency: json['currency'] ?? 'IDR',
      language: json['language'] ?? 'id',
      darkMode: json['darkMode'] ?? false,
      notifications: json['notifications'] ?? true,
      biometricAuth: json['biometricAuth'] ?? false,
      autoBackup: json['autoBackup'] ?? true,
      defaultCategory: json['defaultCategory'] ?? 'Lainnya',
      monthlyBudget: (json['monthlyBudget'] ?? 0.0).toDouble(),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'userId': userId,
      'name': name,
      'email': email,
      'profilePicture': profilePicture,
      'currency': currency,
      'language': language,
      'darkMode': darkMode,
      'notifications': notifications,
      'biometricAuth': biometricAuth,
      'autoBackup': autoBackup,
      'defaultCategory': defaultCategory,
      'monthlyBudget': monthlyBudget,
    };
  }

  factory UserSettingsModel.fromEntity(UserSettings settings) {
    return UserSettingsModel(
      userId: settings.userId,
      name: settings.name,
      email: settings.email,
      profilePicture: settings.profilePicture,
      currency: settings.currency,
      language: settings.language,
      darkMode: settings.darkMode,
      notifications: settings.notifications,
      biometricAuth: settings.biometricAuth,
      autoBackup: settings.autoBackup,
      defaultCategory: settings.defaultCategory,
      monthlyBudget: settings.monthlyBudget,
    );
  }

  UserSettings toEntity() {
    return UserSettings(
      userId: userId,
      name: name,
      email: email,
      profilePicture: profilePicture,
      currency: currency,
      language: language,
      darkMode: darkMode,
      notifications: notifications,
      biometricAuth: biometricAuth,
      autoBackup: autoBackup,
      defaultCategory: defaultCategory,
      monthlyBudget: monthlyBudget,
    );
  }
}