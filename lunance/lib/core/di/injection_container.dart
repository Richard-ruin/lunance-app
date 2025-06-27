
// lib/core/di/injection_container.dart
import 'package:get_it/get_it.dart';
import 'package:connectivity_plus/connectivity_plus.dart';
import 'package:http/http.dart' as http;

// Core
import '../storage/local_storage.dart';
import '../network/network_info.dart';
import '../utils/dio_client.dart';

// Auth
import '../../features/auth/data/datasources/auth_remote_datasource.dart';
import '../../features/auth/data/repositories/auth_repository_impl.dart';
import '../../features/auth/domain/repositories/auth_repository.dart';
import '../../features/auth/domain/usecases/login_usecase.dart';
import '../../features/auth/domain/usecases/register_usecase.dart';
import '../../features/auth/domain/usecases/forgot_password_usecase.dart';
import '../../features/auth/presentation/bloc/auth_bloc.dart';

// Settings
import '../../features/settings/data/datasources/settings_remote_datasource.dart';
import '../../features/settings/data/repositories/settings_repository_impl.dart';
import '../../features/settings/domain/repositories/settings_repository.dart';
import '../../features/settings/domain/usecases/get_user_settings_usecase.dart';
import '../../features/settings/domain/usecases/update_settings_usecase.dart';
import '../../features/settings/presentation/bloc/settings_bloc.dart';

final sl = GetIt.instance;

Future<void> init() async {
  // Initialize core dependencies first
  await _initCore();
  
  // Initialize features
  await _initAuth();
  await _initSettings();
  
  // Add other features here when implemented
  // await _initTransactions();
  // await _initCategories();
  // await _initDashboard();
}

Future<void> _initCore() async {
  // Storage
  final localStorage = await LocalStorage.getInstance();
  sl.registerSingleton<LocalStorage>(localStorage);
  
  // Network
  sl.registerLazySingleton<Connectivity>(() => Connectivity());
  sl.registerLazySingleton<NetworkInfo>(
    () => NetworkInfoImpl(sl<Connectivity>()),
  );
  
  // HTTP Client
  sl.registerLazySingleton<http.Client>(() => http.Client());
  sl.registerLazySingleton<DioClient>(() => DioClient(sl<LocalStorage>()));
}

Future<void> _initAuth() async {
  // Data Sources
  sl.registerLazySingleton<AuthRemoteDataSource>(
    () => AuthRemoteDataSourceImpl(
      client: sl<http.Client>(),
      localStorage: sl<LocalStorage>(),
    ),
  );
  
  // Repositories
  sl.registerLazySingleton<AuthRepository>(
    () => AuthRepositoryImpl(
      remoteDataSource: sl<AuthRemoteDataSource>(),
      localStorage: sl<LocalStorage>(),
    ),
  );
  
  // Use Cases
  sl.registerLazySingleton<LoginUseCase>(
    () => LoginUseCase(sl<AuthRepository>()),
  );
  
  sl.registerLazySingleton<RegisterUseCase>(
    () => RegisterUseCase(sl<AuthRepository>()),
  );
  
  sl.registerLazySingleton<ForgotPasswordUseCase>(
    () => ForgotPasswordUseCase(sl<AuthRepository>()),
  );
  
  // BLoC
  sl.registerFactory<AuthBloc>(
    () => AuthBloc(
      loginUseCase: sl<LoginUseCase>(),
      registerUseCase: sl<RegisterUseCase>(),
      forgotPasswordUseCase: sl<ForgotPasswordUseCase>(),
      authRepository: sl<AuthRepository>(),
    ),
  );
}

Future<void> _initSettings() async {
  // Data Sources
  sl.registerLazySingleton<SettingsRemoteDataSource>(
    () => SettingsRemoteDataSourceImpl(sl<DioClient>()),
  );

  // Repositories
  sl.registerLazySingleton<SettingsRepository>(
    () => SettingsRepositoryImpl(sl<SettingsRemoteDataSource>()),
  );

  // Use Cases
  sl.registerLazySingleton<GetUserSettingsUseCase>(
    () => GetUserSettingsUseCase(sl<SettingsRepository>()),
  );
  
  sl.registerLazySingleton<UpdateNotificationSettingsUseCase>(
    () => UpdateNotificationSettingsUseCase(sl<SettingsRepository>()),
  );
  
  sl.registerLazySingleton<UpdateDisplaySettingsUseCase>(
    () => UpdateDisplaySettingsUseCase(sl<SettingsRepository>()),
  );
  
  sl.registerLazySingleton<UpdatePrivacySettingsUseCase>(
    () => UpdatePrivacySettingsUseCase(sl<SettingsRepository>()),
  );

  // BLoC
  sl.registerFactory<SettingsBloc>(
    () => SettingsBloc(
      getUserSettingsUseCase: sl<GetUserSettingsUseCase>(),
      updateNotificationSettingsUseCase: sl<UpdateNotificationSettingsUseCase>(),
      updateDisplaySettingsUseCase: sl<UpdateDisplaySettingsUseCase>(),
      updatePrivacySettingsUseCase: sl<UpdatePrivacySettingsUseCase>(),
    ),
  );
}