// lib/features/settings/presentation/bloc/settings_state.dart
import 'package:equatable/equatable.dart';
import '../../domain/entities/user_settings.dart';

abstract class SettingsState extends Equatable {
  const SettingsState();

  @override
  List<Object?> get props => [];
}

class SettingsInitial extends SettingsState {}

class SettingsLoading extends SettingsState {}

class SettingsLoaded extends SettingsState {
  final UserSettings settings;

  const SettingsLoaded(this.settings);

  @override
  List<Object?> get props => [settings];
}

class SettingsUpdating extends SettingsState {
  final UserSettings settings;

  const SettingsUpdating(this.settings);

  @override
  List<Object?> get props => [settings];
}

class SettingsUpdateSuccess extends SettingsState {
  final UserSettings settings;
  final String message;

  const SettingsUpdateSuccess(this.settings, this.message);

  @override
  List<Object?> get props => [settings, message];
}

class SettingsError extends SettingsState {
  final String message;
  final UserSettings? settings;

  const SettingsError(this.message, {this.settings});

  @override
  List<Object?> get props => [message, settings];
}

class SettingsExporting extends SettingsState {
  final UserSettings settings;

  const SettingsExporting(this.settings);

  @override
  List<Object?> get props => [settings];
}

class SettingsExportSuccess extends SettingsState {
  final UserSettings settings;

  const SettingsExportSuccess(this.settings);

  @override
  List<Object?> get props => [settings];
}

class SettingsDeleting extends SettingsState {}

class SettingsDeleteSuccess extends SettingsState {}