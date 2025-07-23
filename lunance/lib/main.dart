import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'providers/auth_provider.dart';
import 'providers/chat_provider.dart';
import 'providers/finance_provider.dart';
import 'providers/theme_provider.dart'; // Add this import
import 'providers/prediction_provider.dart';
import 'screens/splash_screen.dart';
import 'utils/timezone_utils.dart';
import 'config/app_config.dart';

void main() async {
  // Ensure Flutter is initialized
  WidgetsFlutterBinding.ensureInitialized();
  
  // Initialize timezone and locale - FIX UNTUK LOCALE ERROR
  await IndonesiaTimeHelper.initialize();
  
  // Print app configuration in development
  if (AppConfig.isDevelopment) {
    AppConfig.printConfig();
  }
  
  runApp(const LunanceApp());
}

class LunanceApp extends StatelessWidget {
  const LunanceApp({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return MultiProvider(
      providers: [
        ChangeNotifierProvider(create: (context) => ThemeProvider()..initialize()), // Add theme provider first
        ChangeNotifierProvider(create: (context) => AuthProvider()),
        ChangeNotifierProvider(create: (context) => ChatProvider()),
        ChangeNotifierProvider(create: (context) => FinanceProvider()),
        ChangeNotifierProvider(create: (context) => PredictionProvider()),
      ],
      child: Consumer<ThemeProvider>(
        builder: (context, themeProvider, child) {
          return MaterialApp(
            title: AppConfig.appName,
            debugShowCheckedModeBanner: false,
            
            // Use theme provider for theme management
            theme: themeProvider.lightTheme,
            darkTheme: themeProvider.darkTheme,
            themeMode: themeProvider.themeMode,
            
            home: const SplashScreen(),
          );
        },
      ),
    );
  }
}