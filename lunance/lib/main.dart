import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:provider/provider.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:hive_flutter/hive_flutter.dart';

import 'config/app_config.dart';
import 'themes/app_theme.dart';
import 'providers/auth_provider.dart';
import 'providers/university_provider.dart';
import 'providers/theme_provider.dart';
import 'services/storage_service.dart';
import 'services/api_service.dart';
import 'services/websocket_service.dart';
import 'screens/auth/login_screen.dart';
import 'screens/student/student_main_screen.dart';
import 'screens/admin/admin_main_screen.dart';
import 'utils/constants.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  
  // Initialize Hive
  await Hive.initFlutter();
  
  // Initialize SharedPreferences
  final prefs = await SharedPreferences.getInstance();
  
  // Initialize Storage Service
  final storageService = StorageService();
  await storageService.init();
  
  // Set preferred orientations
  await SystemChrome.setPreferredOrientations([
    DeviceOrientation.portraitUp,
    DeviceOrientation.portraitDown,
  ]);
  
  // Set system UI overlay style
  SystemChrome.setSystemUIOverlayStyle(
    const SystemUiOverlayStyle(
      statusBarColor: Colors.transparent,
      statusBarIconBrightness: Brightness.dark,
    ),
  );
  
  runApp(
    MultiProvider(
      providers: [
        // Core Providers
        Provider<StorageService>.value(value: storageService),
        Provider<ApiService>(
          create: (_) => ApiService(storageService),
        ),
        Provider<WebSocketService>(
          create: (context) => WebSocketService(
            Provider.of<StorageService>(context, listen: false),
          ),
        ),
        
        // State Providers
        ChangeNotifierProvider<ThemeProvider>(
          create: (_) => ThemeProvider(storageService),
        ),
        ChangeNotifierProvider<AuthProvider>(
          create: (context) => AuthProvider(
            Provider.of<ApiService>(context, listen: false),
            Provider.of<StorageService>(context, listen: false),
          ),
        ),
        ChangeNotifierProvider<UniversityProvider>(
          create: (context) => UniversityProvider(
            Provider.of<ApiService>(context, listen: false),
          ),
        ),
      ],
      child: const LunanceApp(),
    ),
  );
}

class LunanceApp extends StatelessWidget {
  const LunanceApp({super.key});

  @override
  Widget build(BuildContext context) {
    return Consumer2<ThemeProvider, AuthProvider>(
      builder: (context, themeProvider, authProvider, child) {
        return MaterialApp(
          title: AppConfig.appName,
          debugShowCheckedModeBanner: false,
          
          // Theme Configuration
          theme: AppTheme.lightTheme,
          darkTheme: AppTheme.darkTheme,
          themeMode: themeProvider.themeMode,
          
          // Home Screen Based on Auth State
          home: _buildHomeScreen(authProvider),
          
          // Routes
          routes: {
            Routes.login: (context) => const LoginScreen(),
            Routes.studentMain: (context) => const StudentMainScreen(),
            Routes.adminMain: (context) => const AdminMainScreen(),
          },
          
          // Locale Configuration
          locale: const Locale('id', 'ID'),
          
          // Builder for Global Configurations
          builder: (context, child) {
            return MediaQuery(
              data: MediaQuery.of(context).copyWith(
                textScaler: const TextScaler.linear(1.0),
              ),
              child: child!,
            );
          },
        );
      },
    );
  }

  Widget _buildHomeScreen(AuthProvider authProvider) {
    return FutureBuilder<void>(
      future: authProvider.checkAuthStatus(),
      builder: (context, snapshot) {
        if (snapshot.connectionState == ConnectionState.waiting) {
          return const SplashScreen();
        }
        
        if (authProvider.isAuthenticated && authProvider.currentUser != null) {
          // Route based on user role
          switch (authProvider.currentUser!.role) {
            case UserRole.student:
              return const StudentMainScreen();
            case UserRole.admin:
              return const AdminMainScreen();
            default:
              return const LoginScreen();
          }
        }
        
        return const LoginScreen();
      },
    );
  }
}

class SplashScreen extends StatelessWidget {
  const SplashScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Theme.of(context).colorScheme.primary,
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            // Logo
            Container(
              width: 120,
              height: 120,
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(24),
                boxShadow: [
                  BoxShadow(
                    color: Colors.black.withOpacity(0.1),
                    blurRadius: 20,
                    offset: const Offset(0, 10),
                  ),
                ],
              ),
              child: const Icon(
                Icons.account_balance_wallet,
                size: 60,
                color: AppColors.primaryBlue,
              ),
            ),
            
            const SizedBox(height: 24),
            
            // App Name
            Text(
              AppConfig.appName,
              style: Theme.of(context).textTheme.headlineMedium?.copyWith(
                color: Colors.white,
                fontWeight: FontWeight.bold,
              ),
            ),
            
            const SizedBox(height: 8),
            
            // Tagline
            Text(
              'Manajemen Keuangan Mahasiswa',
              style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                color: Colors.white.withOpacity(0.8),
              ),
            ),
            
            const SizedBox(height: 40),
            
            // Loading Indicator
            const CircularProgressIndicator(
              valueColor: AlwaysStoppedAnimation<Color>(Colors.white),
            ),
          ],
        ),
      ),
    );
  }
}