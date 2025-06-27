
// lib/features/settings/presentation/bloc/settings_bloc.dart
import 'package:flutter_bloc/flutter_bloc.dart';
import '../../domain/usecases/get_user_settings_usecase.dart';
import '../../domain/usecases/update_settings_usecase.dart';
import '../../../../core/network/api_result.dart';
import 'settings_event.dart';
import 'settings_state.dart';

class SettingsBloc extends Bloc<SettingsEvent, SettingsState> {
  final GetUserSettingsUseCase getUserSettingsUseCase;
  final UpdateNotificationSettingsUseCase updateNotificationSettingsUseCase;
  final UpdateDisplaySettingsUseCase updateDisplaySettingsUseCase;
  final UpdatePrivacySettingsUseCase updatePrivacySettingsUseCase;

  SettingsBloc({
    required this.getUserSettingsUseCase,
    required this.updateNotificationSettingsUseCase,
    required this.updateDisplaySettingsUseCase,
    required this.updatePrivacySettingsUseCase,
  }) : super(SettingsInitial()) {
    on<LoadUserSettings>(_onLoadUserSettings);
    on<UpdateNotificationSettings>(_onUpdateNotificationSettings);
    on<UpdateDisplaySettings>(_onUpdateDisplaySettings);
    on<UpdatePrivacySettings>(_onUpdatePrivacySettings);
  }

  Future<void> _onLoadUserSettings(
    LoadUserSettings event,
    Emitter<SettingsState> emit,
  ) async {
    emit(SettingsLoading());

    final result = await getUserSettingsUseCase();

    result.when(
      success: (settings) => emit(SettingsLoaded(settings)),
      failure: (error) => emit(SettingsError(error)),
    );
  }

  Future<void> _onUpdateNotificationSettings(
    UpdateNotificationSettings event,
    Emitter<SettingsState> emit,
  ) async {
    emit(SettingsLoading());

    final result = await updateNotificationSettingsUseCase(event.notificationSettings);

    result.when(
      success: (settings) => emit(SettingsUpdateSuccess(
        settings,
        'Pengaturan notifikasi berhasil diperbarui',
      )),
      failure: (error) => emit(SettingsError(error)),
    );
  }

  Future<void> _onUpdateDisplaySettings(
    UpdateDisplaySettings event,
    Emitter<SettingsState> emit,
  ) async {
    emit(SettingsLoading());

    final result = await updateDisplaySettingsUseCase(event.displaySettings);

    result.when(
      success: (settings) => emit(SettingsUpdateSuccess(
        settings,
        'Pengaturan tampilan berhasil diperbarui',
      )),
      failure: (error) => emit(SettingsError(error)),
    );
  }

  Future<void> _onUpdatePrivacySettings(
    UpdatePrivacySettings event,
    Emitter<SettingsState> emit,
  ) async {
    emit(SettingsLoading());

    final result = await updatePrivacySettingsUseCase(event.privacySettings);

    result.when(
      success: (settings) => emit(SettingsUpdateSuccess(
        settings,
        'Pengaturan privasi berhasil diperbarui',
      )),
      failure: (error) => emit(SettingsError(error)),
    );
  }
}