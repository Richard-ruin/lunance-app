
// lib/features/settings/data/models/user_settings_model.dart
import '../../domain/entities/user_settings.dart';

class UserSettingsModel extends UserSettings {
  const UserSettingsModel({
    required super.notifications,
    required super.display,
    required super.privacy,
  });

  factory UserSettingsModel.fromJson(Map<String, dynamic> json) {
    return UserSettingsModel(
      notifications: NotificationSettingsModel.fromJson(
        json['notifications'] ?? {},
      ),
      display: DisplaySettingsModel.fromJson(
        json['display'] ?? {},
      ),
      privacy: PrivacySettingsModel.fromJson(
        json['privacy'] ?? {},
      ),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'notifications': (notifications as NotificationSettingsModel).toJson(),
      'display': (display as DisplaySettingsModel).toJson(),
      'privacy': (privacy as PrivacySettingsModel).toJson(),
    };
  }
}

class NotificationSettingsModel extends NotificationSettings {
  const NotificationSettingsModel({
    required super.budgetAlerts,
    required super.savingsReminders,
    required super.expenseSharingUpdates,
    required super.achievementNotifications,
  });

  factory NotificationSettingsModel.fromJson(Map<String, dynamic> json) {
    return NotificationSettingsModel(
      budgetAlerts: json['budget_alerts'] ?? true,
      savingsReminders: json['savings_reminders'] ?? true,
      expenseSharingUpdates: json['expense_sharing_updates'] ?? true,
      achievementNotifications: json['achievement_notifications'] ?? true,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'budget_alerts': budgetAlerts,
      'savings_reminders': savingsReminders,
      'expense_sharing_updates': expenseSharingUpdates,
      'achievement_notifications': achievementNotifications,
    };
  }
}

class DisplaySettingsModel extends DisplaySettings {
  const DisplaySettingsModel({
    required super.currency,
    required super.theme,
    required super.language,
  });

  factory DisplaySettingsModel.fromJson(Map<String, dynamic> json) {
    return DisplaySettingsModel(
      currency: json['currency'] ?? 'IDR',
      theme: json['theme'] ?? 'light',
      language: json['language'] ?? 'id',
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'currency': currency,
      'theme': theme,
      'language': language,
    };
  }
}

class PrivacySettingsModel extends PrivacySettings {
  const PrivacySettingsModel({
    required super.showInLeaderboard,
    required super.allowExpenseSharing,
  });

  factory PrivacySettingsModel.fromJson(Map<String, dynamic> json) {
    return PrivacySettingsModel(
      showInLeaderboard: json['show_in_leaderboard'] ?? true,
      allowExpenseSharing: json['allow_expense_sharing'] ?? true,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'show_in_leaderboard': showInLeaderboard,
      'allow_expense_sharing': allowExpenseSharing,
    };
  }
}