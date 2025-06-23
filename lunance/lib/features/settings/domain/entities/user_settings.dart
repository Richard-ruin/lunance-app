// lib/features/settings/domain/entities/user_settings.dart
class UserSettings {
  final String userId;
  final String name;
  final String email;
  final String profilePicture;
  final String currency;
  final String language;
  final bool darkMode;
  final bool notifications;
  final bool biometricAuth;
  final bool autoBackup;
  final String defaultCategory;
  final double monthlyBudget;

  const UserSettings({
    required this.userId,
    required this.name,
    required this.email,
    this.profilePicture = '',
    this.currency = 'IDR',
    this.language = 'id',
    this.darkMode = false,
    this.notifications = true,
    this.biometricAuth = false,
    this.autoBackup = true,
    this.defaultCategory = 'Lainnya',
    this.monthlyBudget = 0.0,
  });

  UserSettings copyWith({
    String? userId,
    String? name,
    String? email,
    String? profilePicture,
    String? currency,
    String? language,
    bool? darkMode,
    bool? notifications,
    bool? biometricAuth,
    bool? autoBackup,
    String? defaultCategory,
    double? monthlyBudget,
  }) {
    return UserSettings(
      userId: userId ?? this.userId,
      name: name ?? this.name,
      email: email ?? this.email,
      profilePicture: profilePicture ?? this.profilePicture,
      currency: currency ?? this.currency,
      language: language ?? this.language,
      darkMode: darkMode ?? this.darkMode,
      notifications: notifications ?? this.notifications,
      biometricAuth: biometricAuth ?? this.biometricAuth,
      autoBackup: autoBackup ?? this.autoBackup,
      defaultCategory: defaultCategory ?? this.defaultCategory,
      monthlyBudget: monthlyBudget ?? this.monthlyBudget,
    );
  }
}