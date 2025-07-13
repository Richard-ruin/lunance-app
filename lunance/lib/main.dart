import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'providers/auth_provider.dart';
import 'providers/chat_provider.dart';
import 'providers/finance_provider.dart'; // Add this import
import 'screens/splash_screen.dart';
import 'utils/app_colors.dart';
import 'utils/app_text_styles.dart';
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
        ChangeNotifierProvider(create: (context) => AuthProvider()),
        ChangeNotifierProvider(create: (context) => ChatProvider()),
        ChangeNotifierProvider(create: (context) => FinanceProvider()), // Add this line
      ],
      child: MaterialApp(
        title: AppConfig.appName,
        debugShowCheckedModeBanner: false,
        theme: ThemeData(
          // Color scheme
          colorScheme: ColorScheme.fromSeed(
            seedColor: AppColors.primary,
            brightness: Brightness.light,
          ),
          
          // Primary colors
          primarySwatch: Colors.blue,
          primaryColor: AppColors.primary,
          
          // Background colors
          scaffoldBackgroundColor: AppColors.background,
          canvasColor: AppColors.white,
          
          // Text theme
          textTheme: TextTheme(
            displayLarge: AppTextStyles.h1,
            displayMedium: AppTextStyles.h2,
            displaySmall: AppTextStyles.h3,
            headlineLarge: AppTextStyles.h4,
            headlineMedium: AppTextStyles.h5,
            headlineSmall: AppTextStyles.h6,
            bodyLarge: AppTextStyles.bodyLarge,
            bodyMedium: AppTextStyles.bodyMedium,
            bodySmall: AppTextStyles.bodySmall,
            labelLarge: AppTextStyles.labelLarge,
            labelMedium: AppTextStyles.labelMedium,
            labelSmall: AppTextStyles.labelSmall,
          ),
          
          // App bar theme
          appBarTheme: const AppBarTheme(
            backgroundColor: AppColors.white,
            foregroundColor: AppColors.textPrimary,
            elevation: 0,
            scrolledUnderElevation: 0,
            centerTitle: true,
            titleTextStyle: AppTextStyles.h6,
          ),
          
          // Button themes
          elevatedButtonTheme: ElevatedButtonThemeData(
            style: ElevatedButton.styleFrom(
              backgroundColor: AppColors.primary,
              foregroundColor: AppColors.white,
              elevation: 2,
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(12),
              ),
              textStyle: AppTextStyles.buttonMedium,
            ),
          ),
          
          textButtonTheme: TextButtonThemeData(
            style: TextButton.styleFrom(
              foregroundColor: AppColors.primary,
              textStyle: AppTextStyles.labelMedium,
            ),
          ),
          
          outlinedButtonTheme: OutlinedButtonThemeData(
            style: OutlinedButton.styleFrom(
              foregroundColor: AppColors.primary,
              side: const BorderSide(color: AppColors.primary),
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(12),
              ),
              textStyle: AppTextStyles.buttonMedium,
            ),
          ),
          
          // Input decoration theme
          inputDecorationTheme: InputDecorationTheme(
            filled: true,
            fillColor: AppColors.gray50,
            border: OutlineInputBorder(
              borderRadius: BorderRadius.circular(12),
              borderSide: const BorderSide(color: AppColors.border),
            ),
            enabledBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(12),
              borderSide: const BorderSide(color: AppColors.border),
            ),
            focusedBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(12),
              borderSide: const BorderSide(color: AppColors.primary, width: 2),
            ),
            errorBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(12),
              borderSide: const BorderSide(color: AppColors.error),
            ),
            contentPadding: const EdgeInsets.symmetric(
              horizontal: 16,
              vertical: 16,
            ),
            hintStyle: AppTextStyles.bodyMedium.copyWith(
              color: AppColors.textTertiary,
            ),
          ),
          
          // Card theme
          cardTheme: CardTheme(
            color: AppColors.white,
            elevation: 2,
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(12),
            ),
          ),
          
          // Dialog theme
          dialogTheme: DialogTheme(
            backgroundColor: AppColors.white,
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(16),
            ),
            titleTextStyle: AppTextStyles.h6,
            contentTextStyle: AppTextStyles.bodyMedium,
          ),
          
          // Snackbar theme
          snackBarTheme: SnackBarThemeData(
            backgroundColor: AppColors.gray800,
            contentTextStyle: AppTextStyles.bodyMedium.copyWith(
              color: AppColors.white,
            ),
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(8),
            ),
            behavior: SnackBarBehavior.floating,
          ),
          
          // Progress indicator theme
          progressIndicatorTheme: const ProgressIndicatorThemeData(
            color: AppColors.primary,
            linearTrackColor: AppColors.gray200,
          ),
          
          // Switch theme
          switchTheme: SwitchThemeData(
            thumbColor: MaterialStateProperty.resolveWith((states) {
              if (states.contains(MaterialState.selected)) {
                return AppColors.primary;
              }
              return AppColors.gray400;
            }),
            trackColor: MaterialStateProperty.resolveWith((states) {
              if (states.contains(MaterialState.selected)) {
                return AppColors.primary.withOpacity(0.3);
              }
              return AppColors.gray200;
            }),
          ),
          
          // Slider theme
          sliderTheme: SliderThemeData(
            activeTrackColor: AppColors.primary,
            inactiveTrackColor: AppColors.gray200,
            thumbColor: AppColors.primary,
            overlayColor: AppColors.primary.withOpacity(0.2),
            valueIndicatorColor: AppColors.primary,
            valueIndicatorTextStyle: AppTextStyles.labelSmall.copyWith(
              color: AppColors.white,
            ),
          ),
          
          // Divider theme
          dividerTheme: const DividerThemeData(
            color: AppColors.divider,
            thickness: 1,
          ),
          
          // Font family
          fontFamily: AppTextStyles.fontFamily,
          
          // Use Material 3
          useMaterial3: true,
        ),
        home: const SplashScreen(),
      ),
    );
  }
}