import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'app.dart';

import 'features/dashboard/data/datasources/dashboard_remote_datasource.dart';
import 'features/dashboard/data/repositories/dashboard_repository_impl.dart';
import 'features/dashboard/domain/usecases/get_financial_summary_usecase.dart';
import 'features/dashboard/domain/usecases/get_prediction_usecase.dart';
import 'features/dashboard/presentation/bloc/dashboard_bloc.dart';

import 'features/settings/data/repositories/settings_repository_impl.dart';
import 'features/settings/data/datasources/settings_remote_datasource.dart';
import 'features/settings/domain/repositories/settings_repository.dart';
import 'features/settings/domain/usecases/get_user_settings_usecase.dart';
import 'features/settings/domain/usecases/update_settings_usecase.dart';
import 'features/settings/presentation/bloc/settings_bloc.dart';

void main() {
  // Dashboard Dependencies
  final dashboardRemoteDataSource = DashboardRemoteDataSourceImpl();
  final dashboardRepository = DashboardRepositoryImpl(remoteDataSource: dashboardRemoteDataSource);
  final getFinancialSummaryUseCase = GetFinancialSummaryUseCase(dashboardRepository);
  final getPredictionUseCase = GetPredictionUseCase(dashboardRepository);
  final getMonthlyPredictionUseCase = GetMonthlyPredictionUseCase(dashboardRepository);

  // Settings Dependencies
  final settingsRemoteDataSource = SettingsRemoteDataSourceImpl();
  final settingsRepository = SettingsRepositoryImpl(remoteDataSource: settingsRemoteDataSource);
  final getUserSettingsUseCase = GetUserSettingsUseCase(settingsRepository);
  final updateSettingsUseCase = UpdateSettingsUseCase(settingsRepository);

  runApp(
    MultiBlocProvider(
      providers: [
        BlocProvider<DashboardBloc>(
          create: (context) => DashboardBloc(
            getFinancialSummaryUseCase: getFinancialSummaryUseCase,
            getPredictionUseCase: getPredictionUseCase,
            getMonthlyPredictionUseCase: getMonthlyPredictionUseCase,
          ),
        ),
        BlocProvider<SettingsBloc>(
          create: (context) => SettingsBloc(
            getUserSettingsUseCase: getUserSettingsUseCase,
            updateSettingsUseCase: updateSettingsUseCase,
            settingsRepository: settingsRepository,
          ),
        ),
      ],
      child: const MyApp(),
    ),
  );
}