// lib/features/settings/domain/entities/user_settings.dart
import 'package:equatable/equatable.dart';

class UserSettings extends Equatable {
  final NotificationSettings notifications;
  final DisplaySettings display;
  final PrivacySettings privacy;

  const UserSettings({
    required this.notifications,
    required this.display,
    required this.privacy,
  });

  UserSettings copyWith({
    NotificationSettings? notifications,
    DisplaySettings? display,
    PrivacySettings? privacy,
  }) {
    return UserSettings(
      notifications: notifications ?? this.notifications,
      display: display ?? this.display,
      privacy: privacy ?? this.privacy,
    );
  }

  @override
  List<Object> get props => [notifications, display, privacy];
}

class NotificationSettings extends Equatable {
  final bool budgetAlerts;
  final bool savingsReminders;
  final bool expenseSharingUpdates;
  final bool achievementNotifications;

  const NotificationSettings({
    required this.budgetAlerts,
    required this.savingsReminders,
    required this.expenseSharingUpdates,
    required this.achievementNotifications,
  });

  NotificationSettings copyWith({
    bool? budgetAlerts,
    bool? savingsReminders,
    bool? expenseSharingUpdates,
    bool? achievementNotifications,
  }) {
    return NotificationSettings(
      budgetAlerts: budgetAlerts ?? this.budgetAlerts,
      savingsReminders: savingsReminders ?? this.savingsReminders,
      expenseSharingUpdates: expenseSharingUpdates ?? this.expenseSharingUpdates,
      achievementNotifications: achievementNotifications ?? this.achievementNotifications,
    );
  }

  @override
  List<Object> get props => [
        budgetAlerts,
        savingsReminders,
        expenseSharingUpdates,
        achievementNotifications,
      ];
}

class DisplaySettings extends Equatable {
  final String currency;
  final String theme;
  final String language;

  const DisplaySettings({
    required this.currency,
    required this.theme,
    required this.language,
  });

  DisplaySettings copyWith({
    String? currency,
    String? theme,
    String? language,
  }) {
    return DisplaySettings(
      currency: currency ?? this.currency,
      theme: theme ?? this.theme,
      language: language ?? this.language,
    );
  }

  @override
  List<Object> get props => [currency, theme, language];
}

class PrivacySettings extends Equatable {
  final bool showInLeaderboard;
  final bool allowExpenseSharing;

  const PrivacySettings({
    required this.showInLeaderboard,
    required this.allowExpenseSharing,
  });

  PrivacySettings copyWith({
    bool? showInLeaderboard,
    bool? allowExpenseSharing,
  }) {
    return PrivacySettings(
      showInLeaderboard: showInLeaderboard ?? this.showInLeaderboard,
      allowExpenseSharing: allowExpenseSharing ?? this.allowExpenseSharing,
    );
  }

  @override
  List<Object> get props => [showInLeaderboard, allowExpenseSharing];
}
