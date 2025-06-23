// lib/features/settings/presentation/bloc/settings_event.dart
import 'package:equatable/equatable.dart';
import '../../domain/entities/user_settings.dart';

abstract class SettingsEvent extends Equatable {
  const SettingsEvent();

  @override
  List<Object?> get props => [];
}

class LoadUserSettings extends SettingsEvent {}

class UpdateUserSettings extends SettingsEvent {
  final UserSettings settings;

  const UpdateUserSettings(this.settings);

  @override
  List<Object?> get props => [settings];
}

class ToggleDarkMode extends SettingsEvent {
  final bool isDarkMode;

  const ToggleDarkMode(this.isDarkMode);

  @override
  List<Object?> get props => [isDarkMode];
}

class ToggleNotifications extends SettingsEvent {
  final bool isEnabled;

  const ToggleNotifications(this.isEnabled);

  @override
  List<Object?> get props => [isEnabled];
}

class ToggleBiometricAuth extends SettingsEvent {
  final bool isEnabled;

  const ToggleBiometricAuth(this.isEnabled);

  @override
  List<Object?> get props => [isEnabled];
}

class ToggleAutoBackup extends SettingsEvent {
  final bool isEnabled;

  const ToggleAutoBackup(this.isEnabled);

  @override
  List<Object?> get props => [isEnabled];
}

class ChangeCurrency extends SettingsEvent {
  final String currency;

  const ChangeCurrency(this.currency);

  @override
  List<Object?> get props => [currency];
}

class ChangeLanguage extends SettingsEvent {
  final String language;

  const ChangeLanguage(this.language);

  @override
  List<Object?> get props => [language];
}

class UpdateMonthlyBudget extends SettingsEvent {
  final double budget;

  const UpdateMonthlyBudget(this.budget);

  @override
  List<Object?> get props => [budget];
}

class ResetSettings extends SettingsEvent {}

class ExportUserData extends SettingsEvent {}

class DeleteAccount extends SettingsEvent {}