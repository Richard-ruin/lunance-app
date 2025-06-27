// lib/app.dart
import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';

import 'core/theme/app_theme.dart';
import 'core/utils/app_router.dart';
import 'core/di/injection_container.dart' as di;
import 'features/auth/presentation/bloc/auth_bloc.dart';
import 'features/auth/presentation/bloc/auth_event.dart';
import 'features/dashboard/presentation/bloc/dashboard_bloc.dart';
import 'features/settings/presentation/bloc/settings_bloc.dart';

class LunanceApp extends StatelessWidget {
  const LunanceApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MultiBlocProvider(
      providers: [
        BlocProvider(
          create: (_) => di.sl<AuthBloc>()..add(const AuthCheckStatusEvent()),
        ),
        BlocProvider(
          create: (_) => di.sl<DashboardBloc>(),
        ),
        BlocProvider(
          create: (_) => di.sl<SettingsBloc>(),
        ),
      ],
      child: MaterialApp.router(
        title: 'Lunance - Kelola Keuangan Mahasiswa',
        theme: AppTheme.lightTheme,
        darkTheme: AppTheme.darkTheme,
        themeMode: ThemeMode.system,
        routerConfig: AppRouter.router,
        debugShowCheckedModeBanner: false,
      ),
    );
  }
}