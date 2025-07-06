import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'app_theme.dart';

class LightTheme {
  static ThemeData get theme => ThemeData(
    // Brightness
    brightness: Brightness.light,
    
    // Color Scheme
    colorScheme: const ColorScheme.light(
      brightness: Brightness.light,
      primary: AppColors.primaryBlue,
      onPrimary: Colors.white,
      primaryContainer: Color(0xFFDDEEFF),
      onPrimaryContainer: Color(0xFF001B3E),
      secondary: AppColors.secondaryIndigo,
      onSecondary: Colors.white,
      secondaryContainer: Color(0xFFE0E7FF),
      onSecondaryContainer: Color(0xFF1E1B3A),
      tertiary: AppColors.secondaryPurple,
      onTertiary: Colors.white,
      tertiaryContainer: Color(0xFFF3E8FF),
      onTertiaryContainer: Color(0xFF2D1B69),
      error: AppColors.error,
      onError: Colors.white,
      errorContainer: Color(0xFFFFDAD6),
      onErrorContainer: Color(0xFF410002),
      background: AppColors.lightBackground,
      onBackground: AppColors.lightOnBackground,
      surface: AppColors.lightSurface,
      onSurface: AppColors.lightOnSurface,
      surfaceVariant: AppColors.lightSurfaceVariant,
      onSurfaceVariant: AppColors.lightOnSurfaceVariant,
      outline: AppColors.gray400,
      outlineVariant: AppColors.gray200,
      shadow: Colors.black,
      scrim: Colors.black,
      inverseSurface: AppColors.gray800,
      onInverseSurface: AppColors.gray100,
      inversePrimary: AppColors.primaryBlueDark,
      surfaceTint: AppColors.primaryBlue,
    ),
    
    // Text Theme
    textTheme: AppTheme.textTheme.apply(
      bodyColor: AppColors.lightOnSurface,
      displayColor: AppColors.lightOnBackground,
    ),
    
    // App Bar Theme
    appBarTheme: AppBarTheme(
      elevation: AppTheme.appBarElevation,
      scrolledUnderElevation: 1,
      backgroundColor: AppColors.lightSurface,
      foregroundColor: AppColors.lightOnSurface,
      surfaceTintColor: AppColors.primaryBlue,
      titleTextStyle: AppTheme.textTheme.titleLarge?.copyWith(
        color: AppColors.lightOnSurface,
        fontWeight: FontWeight.w600,
      ),
      iconTheme: const IconThemeData(
        color: AppColors.lightOnSurface,
        size: AppTheme.iconMedium,
      ),
      actionsIconTheme: const IconThemeData(
        color: AppColors.lightOnSurface,
        size: AppTheme.iconMedium,
      ),
      systemOverlayStyle: SystemUiOverlayStyle.dark,
    ),
    
    // Card Theme
    cardTheme: CardTheme(
      elevation: AppTheme.cardElevation,
      shape: AppTheme.cardShape,
      color: AppColors.lightSurface,
      surfaceTintColor: AppColors.primaryBlue,
      shadowColor: Colors.black.withOpacity(0.1),
      margin: const EdgeInsets.all(AppTheme.spacing8),
    ),
    
    // Elevated Button Theme
    elevatedButtonTheme: ElevatedButtonThemeData(
      style: ElevatedButton.styleFrom(
        elevation: AppTheme.buttonElevation,
        shape: AppTheme.buttonShape,
        backgroundColor: AppColors.primaryBlue,
        foregroundColor: Colors.white,
        disabledBackgroundColor: AppColors.gray300,
        disabledForegroundColor: AppColors.gray500,
        padding: const EdgeInsets.symmetric(
          horizontal: AppTheme.spacing24,
          vertical: AppTheme.spacing12,
        ),
        textStyle: AppTheme.textTheme.labelLarge?.copyWith(
          fontWeight: FontWeight.w600,
        ),
      ),
    ),
    
    // Outlined Button Theme
    outlinedButtonTheme: OutlinedButtonThemeData(
      style: OutlinedButton.styleFrom(
        shape: AppTheme.buttonShape,
        foregroundColor: AppColors.primaryBlue,
        side: const BorderSide(color: AppColors.primaryBlue),
        disabledForegroundColor: AppColors.gray400,
        padding: const EdgeInsets.symmetric(
          horizontal: AppTheme.spacing24,
          vertical: AppTheme.spacing12,
        ),
        textStyle: AppTheme.textTheme.labelLarge?.copyWith(
          fontWeight: FontWeight.w600,
        ),
      ),
    ),
    
    // Text Button Theme
    textButtonTheme: TextButtonThemeData(
      style: TextButton.styleFrom(
        shape: AppTheme.buttonShape,
        foregroundColor: AppColors.primaryBlue,
        disabledForegroundColor: AppColors.gray400,
        padding: const EdgeInsets.symmetric(
          horizontal: AppTheme.spacing16,
          vertical: AppTheme.spacing8,
        ),
        textStyle: AppTheme.textTheme.labelLarge?.copyWith(
          fontWeight: FontWeight.w600,
        ),
      ),
    ),
    
    // Icon Button Theme
    iconButtonTheme: IconButtonThemeData(
      style: IconButton.styleFrom(
        foregroundColor: AppColors.lightOnSurface,
        disabledForegroundColor: AppColors.gray400,
        iconSize: AppTheme.iconMedium,
        padding: const EdgeInsets.all(AppTheme.spacing8),
      ),
    ),
    
    // Floating Action Button Theme
    floatingActionButtonTheme: const FloatingActionButtonThemeData(
      elevation: AppTheme.fabElevation,
      backgroundColor: AppColors.primaryBlue,
      foregroundColor: Colors.white,
      iconSize: AppTheme.iconMedium,
    ),
    
    // Input Decoration Theme
    inputDecorationTheme: InputDecorationTheme(
      filled: true,
      fillColor: AppColors.lightSurface,
      border: OutlineInputBorder(
        borderRadius: BorderRadius.circular(AppTheme.radiusMedium),
        borderSide: const BorderSide(color: AppColors.gray300),
      ),
      enabledBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(AppTheme.radiusMedium),
        borderSide: const BorderSide(color: AppColors.gray300),
      ),
      focusedBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(AppTheme.radiusMedium),
        borderSide: const BorderSide(color: AppColors.primaryBlue, width: 2),
      ),
      errorBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(AppTheme.radiusMedium),
        borderSide: const BorderSide(color: AppColors.error),
      ),
      focusedErrorBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(AppTheme.radiusMedium),
        borderSide: const BorderSide(color: AppColors.error, width: 2),
      ),
      disabledBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(AppTheme.radiusMedium),
        borderSide: const BorderSide(color: AppColors.gray200),
      ),
      contentPadding: const EdgeInsets.symmetric(
        horizontal: AppTheme.spacing16,
        vertical: AppTheme.spacing12,
      ),
      hintStyle: AppTheme.textTheme.bodyMedium?.copyWith(
        color: AppColors.gray500,
      ),
      labelStyle: AppTheme.textTheme.bodyMedium?.copyWith(
        color: AppColors.gray600,
      ),
      errorStyle: AppTheme.textTheme.bodySmall?.copyWith(
        color: AppColors.error,
      ),
    ),
    
    // Bottom Navigation Bar Theme
    bottomNavigationBarTheme: const BottomNavigationBarThemeData(
      backgroundColor: AppColors.lightSurface,
      selectedItemColor: AppColors.primaryBlue,
      unselectedItemColor: AppColors.gray500,
      type: BottomNavigationBarType.fixed,
      elevation: 8,
    ),
    
    // Navigation Bar Theme
    navigationBarTheme: NavigationBarThemeData(
      backgroundColor: AppColors.lightSurface,
      indicatorColor: AppColors.primaryBlue.withOpacity(0.1),
      elevation: 8,
      labelTextStyle: MaterialStateProperty.resolveWith((states) {
        if (states.contains(MaterialState.selected)) {
          return AppTheme.textTheme.labelSmall?.copyWith(
            color: AppColors.primaryBlue,
            fontWeight: FontWeight.w600,
          );
        }
        return AppTheme.textTheme.labelSmall?.copyWith(
          color: AppColors.gray500,
        );
      }),
      iconTheme: MaterialStateProperty.resolveWith((states) {
        if (states.contains(MaterialState.selected)) {
          return const IconThemeData(
            color: AppColors.primaryBlue,
            size: AppTheme.iconMedium,
          );
        }
        return const IconThemeData(
          color: AppColors.gray500,
          size: AppTheme.iconMedium,
        );
      }),
    ),
    
    // Switch Theme
    switchTheme: SwitchThemeData(
      thumbColor: MaterialStateProperty.resolveWith((states) {
        if (states.contains(MaterialState.selected)) {
          return AppColors.primaryBlue;
        }
        return AppColors.gray400;
      }),
      trackColor: MaterialStateProperty.resolveWith((states) {
        if (states.contains(MaterialState.selected)) {
          return AppColors.primaryBlue.withOpacity(0.5);
        }
        return AppColors.gray300;
      }),
    ),
    
    // Checkbox Theme
    checkboxTheme: CheckboxThemeData(
      fillColor: MaterialStateProperty.resolveWith((states) {
        if (states.contains(MaterialState.selected)) {
          return AppColors.primaryBlue;
        }
        return Colors.transparent;
      }),
      checkColor: MaterialStateProperty.all(Colors.white),
      side: const BorderSide(color: AppColors.gray400),
    ),
    
    // Radio Theme
    radioTheme: RadioThemeData(
      fillColor: MaterialStateProperty.resolveWith((states) {
        if (states.contains(MaterialState.selected)) {
          return AppColors.primaryBlue;
        }
        return AppColors.gray400;
      }),
    ),
    
    // Chip Theme
    chipTheme: ChipThemeData(
      backgroundColor: AppColors.gray100,
      disabledColor: AppColors.gray200,
      selectedColor: AppColors.primaryBlue.withOpacity(0.1),
      secondarySelectedColor: AppColors.secondaryIndigo.withOpacity(0.1),
      labelStyle: AppTheme.textTheme.labelMedium?.copyWith(
        color: AppColors.lightOnSurface,
      ),
      secondaryLabelStyle: AppTheme.textTheme.labelMedium?.copyWith(
        color: AppColors.primaryBlue,
      ),
      brightness: Brightness.light,
      padding: const EdgeInsets.symmetric(
        horizontal: AppTheme.spacing12,
        vertical: AppTheme.spacing4,
      ),
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(AppTheme.radiusLarge),
      ),
    ),
    
    // Dialog Theme
    dialogTheme: DialogTheme(
      backgroundColor: AppColors.lightSurface,
      elevation: 8,
      shape: AppTheme.dialogShape,
      titleTextStyle: AppTheme.textTheme.headlineSmall?.copyWith(
        color: AppColors.lightOnSurface,
      ),
      contentTextStyle: AppTheme.textTheme.bodyMedium?.copyWith(
        color: AppColors.lightOnSurface,
      ),
    ),
    
    // Bottom Sheet Theme
    bottomSheetTheme: const BottomSheetThemeData(
      backgroundColor: AppColors.lightSurface,
      elevation: 8,
      shape: AppTheme.bottomSheetShape,
    ),
    
    // Snack Bar Theme
    snackBarTheme: SnackBarThemeData(
      backgroundColor: AppColors.gray800,
      contentTextStyle: AppTheme.textTheme.bodyMedium?.copyWith(
        color: Colors.white,
      ),
      actionTextColor: AppColors.primaryBlueDark,
      behavior: SnackBarBehavior.floating,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(AppTheme.radiusMedium),
      ),
    ),
    
    // Divider Theme
    dividerTheme: const DividerThemeData(
      color: AppColors.gray200,
      thickness: 1,
      space: 1,
    ),
    
    // List Tile Theme
    listTileTheme: ListTileThemeData(
      contentPadding: const EdgeInsets.symmetric(
        horizontal: AppTheme.spacing16,
        vertical: AppTheme.spacing4,
      ),
      iconColor: AppColors.gray600,
      textColor: AppColors.lightOnSurface,
      titleTextStyle: AppTheme.textTheme.bodyLarge?.copyWith(
        color: AppColors.lightOnSurface,
      ),
      subtitleTextStyle: AppTheme.textTheme.bodyMedium?.copyWith(
        color: AppColors.gray600,
      ),
    ),
    
    // Expansion Tile Theme
    expansionTileTheme: const ExpansionTileThemeData(
      backgroundColor: AppColors.lightSurface,
      collapsedBackgroundColor: AppColors.lightSurface,
      iconColor: AppColors.gray600,
      collapsedIconColor: AppColors.gray600,
      textColor: AppColors.lightOnSurface,
      collapsedTextColor: AppColors.lightOnSurface,
    ),
    
    // Tab Bar Theme
    tabBarTheme: TabBarTheme(
      labelColor: AppColors.primaryBlue,
      unselectedLabelColor: AppColors.gray500,
      labelStyle: AppTheme.textTheme.labelLarge?.copyWith(
        fontWeight: FontWeight.w600,
      ),
      unselectedLabelStyle: AppTheme.textTheme.labelLarge,
      indicator: const UnderlineTabIndicator(
        borderSide: BorderSide(
          color: AppColors.primaryBlue,
          width: 2,
        ),
      ),
    ),
    
    // Progress Indicator Theme
    progressIndicatorTheme: const ProgressIndicatorThemeData(
      color: AppColors.primaryBlue,
      linearTrackColor: AppColors.gray200,
      circularTrackColor: AppColors.gray200,
    ),
    
    // Slider Theme
    sliderTheme: const SliderThemeData(
      activeTrackColor: AppColors.primaryBlue,
      inactiveTrackColor: AppColors.gray300,
      thumbColor: AppColors.primaryBlue,
      overlayColor: Color(0x1F3B82F6),
      valueIndicatorColor: AppColors.primaryBlue,
    ),
  );
}