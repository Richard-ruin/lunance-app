// lib/features/settings/presentation/bloc/settings_event.dart
import 'package:equatable/equatable.dart';
import '../../domain/entities/user_settings.dart';

abstract class SettingsEvent extends Equatable {
  const SettingsEvent();

  @override
  List<Object> get props => [];
}

class LoadUserSettings extends SettingsEvent {
  const LoadUserSettings();
}

class UpdateNotificationSettings extends SettingsEvent {
  final NotificationSettings notificationSettings;

  const UpdateNotificationSettings(this.notificationSettings);

  @override
  List<Object> get props => [notificationSettings];
}

class UpdateDisplaySettings extends SettingsEvent {
  final DisplaySettings displaySettings;

  const UpdateDisplaySettings(this.displaySettings);

  @override
  List<Object> get props => [displaySettings];
}

class UpdatePrivacySettings extends SettingsEvent {
  final PrivacySettings privacySettings;

  const UpdatePrivacySettings(this.privacySettings);

  @override
  List<Object> get props => [privacySettings];
}