// lib/core/di/injection_container.dart (Updated untuk categories)
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

// Dashboard
import '../../features/dashboard/data/datasources/dashboard_remote_datasource.dart';
import '../../features/dashboard/data/repositories/dashboard_repository_impl.dart';
import '../../features/dashboard/domain/repositories/dashboard_repository.dart';
import '../../features/dashboard/domain/usecases/get_financial_summary_usecase.dart';
import '../../features/dashboard/domain/usecases/get_quick_stats_usecase.dart';
import '../../features/dashboard/domain/usecases/get_category_breakdown_usecase.dart';
import '../../features/dashboard/domain/usecases/get_recent_transactions_usecase.dart';
import '../../features/dashboard/domain/usecases/get_predictions_usecase.dart';
import '../../features/dashboard/domain/usecases/get_financial_insights_usecase.dart';
import '../../features/dashboard/presentation/bloc/dashboard_bloc.dart';

// Categories
import '../../features/categories/data/datasources/category_remote_datasource.dart';
import '../../features/categories/data/repositories/category_repository_impl.dart';
import '../../features/categories/domain/repositories/category_repository.dart';
import '../../features/categories/domain/usecases/get_categories_usecase.dart';
import '../../features/categories/domain/usecases/get_categories_with_stats_usecase.dart';
import '../../features/categories/domain/usecases/get_popular_categories_usecase.dart';
import '../../features/categories/domain/usecases/search_categories_usecase.dart';
import '../../features/categories/domain/usecases/create_category_usecase.dart';
import '../../features/categories/domain/usecases/update_category_usecase.dart';
import '../../features/categories/domain/usecases/delete_category_usecase.dart';
import '../../features/categories/domain/usecases/get_category_by_id_usecase.dart';
import '../../features/categories/presentation/bloc/category_bloc.dart';

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
  await _initDashboard();
  await _initCategories();
  await _initSettings();
  
  // Add other features here when implemented
  // await _initTransactions();
  // await _initChatbot();
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

Future<void> _initDashboard() async {
  // Data Sources
  sl.registerLazySingleton<DashboardRemoteDataSource>(
    () => DashboardRemoteDataSourceImpl(sl<DioClient>()),
  );

  // Repositories
  sl.registerLazySingleton<DashboardRepository>(
    () => DashboardRepositoryImpl(
      remoteDataSource: sl<DashboardRemoteDataSource>(),
      networkInfo: sl<NetworkInfo>(),
    ),
  );

  // Use Cases
  sl.registerLazySingleton<GetFinancialSummaryUseCase>(
    () => GetFinancialSummaryUseCase(sl<DashboardRepository>()),
  );
  
  sl.registerLazySingleton<GetQuickStatsUseCase>(
    () => GetQuickStatsUseCase(sl<DashboardRepository>()),
  );
  
  sl.registerLazySingleton<GetCategoryBreakdownUseCase>(
    () => GetCategoryBreakdownUseCase(sl<DashboardRepository>()),
  );
  
  sl.registerLazySingleton<GetRecentTransactionsUseCase>(
    () => GetRecentTransactionsUseCase(sl<DashboardRepository>()),
  );
  
  sl.registerLazySingleton<GetPredictionsUseCase>(
    () => GetPredictionsUseCase(sl<DashboardRepository>()),
  );
  
  sl.registerLazySingleton<GetFinancialInsightsUseCase>(
    () => GetFinancialInsightsUseCase(sl<DashboardRepository>()),
  );

  // BLoC
  sl.registerFactory<DashboardBloc>(
    () => DashboardBloc(
      getFinancialSummaryUseCase: sl<GetFinancialSummaryUseCase>(),
      getQuickStatsUseCase: sl<GetQuickStatsUseCase>(),
      getCategoryBreakdownUseCase: sl<GetCategoryBreakdownUseCase>(),
      getRecentTransactionsUseCase: sl<GetRecentTransactionsUseCase>(),
      getPredictionsUseCase: sl<GetPredictionsUseCase>(),
      getFinancialInsightsUseCase: sl<GetFinancialInsightsUseCase>(),
    ),
  );
}

Future<void> _initCategories() async {
  // Data Sources
  sl.registerLazySingleton<CategoryRemoteDataSource>(
    () => CategoryRemoteDataSourceImpl(sl<DioClient>()),
  );

  // Repositories
  sl.registerLazySingleton<CategoryRepository>(
    () => CategoryRepositoryImpl(
      remoteDataSource: sl<CategoryRemoteDataSource>(),
      networkInfo: sl<NetworkInfo>(),
    ),
  );

  // Use Cases
  sl.registerLazySingleton<GetCategoriesUseCase>(
    () => GetCategoriesUseCase(sl<CategoryRepository>()),
  );
  
  sl.registerLazySingleton<GetCategoriesWithStatsUseCase>(
    () => GetCategoriesWithStatsUseCase(sl<CategoryRepository>()),
  );
  
  sl.registerLazySingleton<GetPopularCategoriesUseCase>(
    () => GetPopularCategoriesUseCase(sl<CategoryRepository>()),
  );
  
  sl.registerLazySingleton<SearchCategoriesUseCase>(
    () => SearchCategoriesUseCase(sl<CategoryRepository>()),
  );
  
  sl.registerLazySingleton<CreateCategoryUseCase>(
    () => CreateCategoryUseCase(sl<CategoryRepository>()),
  );
  
  sl.registerLazySingleton<UpdateCategoryUseCase>(
    () => UpdateCategoryUseCase(sl<CategoryRepository>()),
  );
  
  sl.registerLazySingleton<DeleteCategoryUseCase>(
    () => DeleteCategoryUseCase(sl<CategoryRepository>()),
  );
  
  sl.registerLazySingleton<GetCategoryByIdUseCase>(
    () => GetCategoryByIdUseCase(sl<CategoryRepository>()),
  );

  // BLoC
  sl.registerFactory<CategoryBloc>(
    () => CategoryBloc(
      getCategoriesUseCase: sl<GetCategoriesUseCase>(),
      getCategoriesWithStatsUseCase: sl<GetCategoriesWithStatsUseCase>(),
      getPopularCategoriesUseCase: sl<GetPopularCategoriesUseCase>(),
      searchCategoriesUseCase: sl<SearchCategoriesUseCase>(),
      createCategoryUseCase: sl<CreateCategoryUseCase>(),
      updateCategoryUseCase: sl<UpdateCategoryUseCase>(),
      deleteCategoryUseCase: sl<DeleteCategoryUseCase>(),
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