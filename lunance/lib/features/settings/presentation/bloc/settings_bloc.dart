// lib/features/settings/presentation/bloc/settings_bloc.dart
import 'package:flutter_bloc/flutter_bloc.dart';
import '../../domain/entities/user_settings.dart';
import '../../domain/usecases/get_user_settings_usecase.dart';
import '../../domain/usecases/update_settings_usecase.dart';
import '../../domain/repositories/settings_repository.dart';
import 'settings_event.dart';
import 'settings_state.dart';

class SettingsBloc extends Bloc<SettingsEvent, SettingsState> {
  final GetUserSettingsUseCase getUserSettingsUseCase;
  final UpdateSettingsUseCase updateSettingsUseCase;
  final SettingsRepository settingsRepository;

  SettingsBloc({
    required this.getUserSettingsUseCase,
    required this.updateSettingsUseCase,
    required this.settingsRepository,
  }) : super(SettingsInitial()) {
    on<LoadUserSettings>(_onLoadUserSettings);
    on<UpdateUserSettings>(_onUpdateUserSettings);
    on<ToggleDarkMode>(_onToggleDarkMode);
    on<ToggleNotifications>(_onToggleNotifications);
    on<ToggleBiometricAuth>(_onToggleBiometricAuth);
    on<ToggleAutoBackup>(_onToggleAutoBackup);
    on<ChangeCurrency>(_onChangeCurrency);
    on<ChangeLanguage>(_onChangeLanguage);
    on<UpdateMonthlyBudget>(_onUpdateMonthlyBudget);
    on<ResetSettings>(_onResetSettings);
    on<ExportUserData>(_onExportUserData);
    on<DeleteAccount>(_onDeleteAccount);
  }

  Future<void> _onLoadUserSettings(
    LoadUserSettings event,
    Emitter<SettingsState> emit,
  ) async {
    emit(SettingsLoading());
    try {
      final settings = await getUserSettingsUseCase();
      emit(SettingsLoaded(settings));
    } catch (e) {
      emit(SettingsError('Failed to load settings: ${e.toString()}'));
    }
  }

  Future<void> _onUpdateUserSettings(
    UpdateUserSettings event,
    Emitter<SettingsState> emit,
  ) async {
    if (state is SettingsLoaded) {
      emit(SettingsUpdating(event.settings));
      try {
        await updateSettingsUseCase(event.settings);
        emit(SettingsUpdateSuccess(event.settings, 'Settings updated successfully'));
        emit(SettingsLoaded(event.settings));
      } catch (e) {
        emit(SettingsError('Failed to update settings: ${e.toString()}', 
            settings: (state as SettingsLoaded).settings));
      }
    }
  }

  Future<void> _onToggleDarkMode(
    ToggleDarkMode event,
    Emitter<SettingsState> emit,
  ) async {
    if (state is SettingsLoaded) {
      final currentSettings = (state as SettingsLoaded).settings;
      final updatedSettings = currentSettings.copyWith(darkMode: event.isDarkMode);
      add(UpdateUserSettings(updatedSettings));
    }
  }

  Future<void> _onToggleNotifications(
    ToggleNotifications event,
    Emitter<SettingsState> emit,
  ) async {
    if (state is SettingsLoaded) {
      final currentSettings = (state as SettingsLoaded).settings;
      final updatedSettings = currentSettings.copyWith(notifications: event.isEnabled);
      add(UpdateUserSettings(updatedSettings));
    }
  }

  Future<void> _onToggleBiometricAuth(
    ToggleBiometricAuth event,
    Emitter<SettingsState> emit,
  ) async {
    if (state is SettingsLoaded) {
      final currentSettings = (state as SettingsLoaded).settings;
      final updatedSettings = currentSettings.copyWith(biometricAuth: event.isEnabled);
      add(UpdateUserSettings(updatedSettings));
    }
  }

  Future<void> _onToggleAutoBackup(
    ToggleAutoBackup event,
    Emitter<SettingsState> emit,
  ) async {
    if (state is SettingsLoaded) {
      final currentSettings = (state as SettingsLoaded).settings;
      final updatedSettings = currentSettings.copyWith(autoBackup: event.isEnabled);
      add(UpdateUserSettings(updatedSettings));
    }
  }

  Future<void> _onChangeCurrency(
    ChangeCurrency event,
    Emitter<SettingsState> emit,
  ) async {
    if (state is SettingsLoaded) {
      final currentSettings = (state as SettingsLoaded).settings;
      final updatedSettings = currentSettings.copyWith(currency: event.currency);
      add(UpdateUserSettings(updatedSettings));
    }
  }

  Future<void> _onChangeLanguage(
    ChangeLanguage event,
    Emitter<SettingsState> emit,
  ) async {
    if (state is SettingsLoaded) {
      final currentSettings = (state as SettingsLoaded).settings;
      final updatedSettings = currentSettings.copyWith(language: event.language);
      add(UpdateUserSettings(updatedSettings));
    }
  }

  Future<void> _onUpdateMonthlyBudget(
    UpdateMonthlyBudget event,
    Emitter<SettingsState> emit,
  ) async {
    if (state is SettingsLoaded) {
      final currentSettings = (state as SettingsLoaded).settings;
      final updatedSettings = currentSettings.copyWith(monthlyBudget: event.budget);
      add(UpdateUserSettings(updatedSettings));
    }
  }

  Future<void> _onResetSettings(
    ResetSettings event,
    Emitter<SettingsState> emit,
  ) async {
    try {
      await settingsRepository.resetSettings();
      add(LoadUserSettings());
    } catch (e) {
      emit(SettingsError('Failed to reset settings: ${e.toString()}'));
    }
  }

  Future<void> _onExportUserData(
    ExportUserData event,
    Emitter<SettingsState> emit,
  ) async {
    if (state is SettingsLoaded) {
      final currentSettings = (state as SettingsLoaded).settings;
      emit(SettingsExporting(currentSettings));
      try {
        final success = await settingsRepository.exportData();
        if (success) {
          emit(SettingsExportSuccess(currentSettings));
          emit(SettingsLoaded(currentSettings));
        } else {
          emit(SettingsError('Failed to export data', settings: currentSettings));
        }
      } catch (e) {
        emit(SettingsError('Failed to export data: ${e.toString()}', settings: currentSettings));
      }
    }
  }

  Future<void> _onDeleteAccount(
    DeleteAccount event,
    Emitter<SettingsState> emit,
  ) async {
    emit(SettingsDeleting());
    try {
      await settingsRepository.deleteAccount();
      emit(SettingsDeleteSuccess());
    } catch (e) {
      emit(SettingsError('Failed to delete account: ${e.toString()}'));
    }
  }
}