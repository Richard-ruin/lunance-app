import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'app_theme.dart';

class DarkTheme {
  static ThemeData get theme => ThemeData(
    // Brightness
    brightness: Brightness.dark,
    
    // Color Scheme
    colorScheme: const ColorScheme.dark(
      brightness: Brightness.dark,
      primary: AppColors.primaryBlueDark,
      onPrimary: AppColors.darkBackground,
      primaryContainer: Color(0xFF1E3A8A),
      onPrimaryContainer: Color(0xFFDDEEFF),
      secondary: Color(0xFF818CF8),
      onSecondary: AppColors.darkBackground,
      secondaryContainer: Color(0xFF3730A3),
      onSecondaryContainer: Color(0xFFE0E7FF),
      tertiary: Color(0xFFA78BFA),
      onTertiary: AppColors.darkBackground,
      tertiaryContainer: Color(0xFF5B21B6),
      onTertiaryContainer: Color(0xFFF3E8FF),
      error: AppColors.errorLight,
      onError: AppColors.darkBackground,
      errorContainer: Color(0xFF93000A),
      onErrorContainer: Color(0xFFFFDAD6),
      background: AppColors.darkBackground,
      onBackground: AppColors.darkOnBackground,
      surface: AppColors.darkSurface,
      onSurface: AppColors.darkOnSurface,
      surfaceVariant: AppColors.darkSurfaceVariant,
      onSurfaceVariant: AppColors.darkOnSurfaceVariant,
      outline: AppColors.gray500,
      outlineVariant: AppColors.gray600,
      shadow: Colors.black,
      scrim: Colors.black,
      inverseSurface: AppColors.gray100,
      onInverseSurface: AppColors.gray800,
      inversePrimary: AppColors.primaryBlue,
      surfaceTint: AppColors.primaryBlueDark,
    ),
    
    // Text Theme
    textTheme: AppTheme.textTheme.apply(
      bodyColor: AppColors.darkOnSurface,
      displayColor: AppColors.darkOnBackground,
    ),
    
    // App Bar Theme
    appBarTheme: AppBarTheme(
      elevation: AppTheme.appBarElevation,
      scrolledUnderElevation: 1,
      backgroundColor: AppColors.darkSurface,
      foregroundColor: AppColors.darkOnSurface,
      surfaceTintColor: AppColors.primaryBlueDark,
      titleTextStyle: AppTheme.textTheme.titleLarge?.copyWith(
        color: AppColors.darkOnSurface,
        fontWeight: FontWeight.w600,
      ),
      iconTheme: const IconThemeData(
        color: AppColors.darkOnSurface,
        size: AppTheme.iconMedium,
      ),
      actionsIconTheme: const IconThemeData(
        color: AppColors.darkOnSurface,
        size: AppTheme.iconMedium,
      ),
      systemOverlayStyle: SystemUiOverlayStyle.light,
    ),
    
    // Card Theme
    cardTheme: CardTheme(
      elevation: AppTheme.cardElevation,
      shape: AppTheme.cardShape,
      color: AppColors.darkSurface,
      surfaceTintColor: AppColors.primaryBlueDark,
      shadowColor: Colors.black.withOpacity(0.3),
      margin: const EdgeInsets.all(AppTheme.spacing8),
    ),
    
    // Elevated Button Theme
    elevatedButtonTheme: ElevatedButtonThemeData(
      style: ElevatedButton.styleFrom(
        elevation: AppTheme.buttonElevation,
        shape: AppTheme.buttonShape,
        backgroundColor: AppColors.primaryBlueDark,
        foregroundColor: AppColors.darkBackground,
        disabledBackgroundColor: AppColors.gray600,
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
    
    // Outlined Button Theme
    outlinedButtonTheme: OutlinedButtonThemeData(
      style: OutlinedButton.styleFrom(
        shape: AppTheme.buttonShape,
        foregroundColor: AppColors.primaryBlueDark,
        side: const BorderSide(color: AppColors.primaryBlueDark),
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
    
    // Text Button Theme
    textButtonTheme: TextButtonThemeData(
      style: TextButton.styleFrom(
        shape: AppTheme.buttonShape,
        foregroundColor: AppColors.primaryBlueDark,
        disabledForegroundColor: AppColors.gray500,
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
        foregroundColor: AppColors.darkOnSurface,
        disabledForegroundColor: AppColors.gray500,
        iconSize: AppTheme.iconMedium,
        padding: const EdgeInsets.all(AppTheme.spacing8),
      ),
    ),
    
    // Floating Action Button Theme
    floatingActionButtonTheme: const FloatingActionButtonThemeData(
      elevation: AppTheme.fabElevation,
      backgroundColor: AppColors.primaryBlueDark,
      foregroundColor: AppColors.darkBackground,
      iconSize: AppTheme.iconMedium,
    ),
    
    // Input Decoration Theme
    inputDecorationTheme: InputDecorationTheme(
      filled: true,
      fillColor: AppColors.darkSurfaceVariant,
      border: OutlineInputBorder(
        borderRadius: BorderRadius.circular(AppTheme.radiusMedium),
        borderSide: const BorderSide(color: AppColors.gray600),
      ),
      enabledBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(AppTheme.radiusMedium),
        borderSide: const BorderSide(color: AppColors.gray600),
      ),
      focusedBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(AppTheme.radiusMedium),
        borderSide: const BorderSide(color: AppColors.primaryBlueDark, width: 2),
      ),
      errorBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(AppTheme.radiusMedium),
        borderSide: const BorderSide(color: AppColors.errorLight),
      ),
      focusedErrorBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(AppTheme.radiusMedium),
        borderSide: const BorderSide(color: AppColors.errorLight, width: 2),
      ),
      disabledBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(AppTheme.radiusMedium),
        borderSide: const BorderSide(color: AppColors.gray700),
      ),
      contentPadding: const EdgeInsets.symmetric(
        horizontal: AppTheme.spacing16,
        vertical: AppTheme.spacing12,
      ),
      hintStyle: AppTheme.textTheme.bodyMedium?.copyWith(
        color: AppColors.gray400,
      ),
      labelStyle: AppTheme.textTheme.bodyMedium?.copyWith(
        color: AppColors.gray300,
      ),
      errorStyle: AppTheme.textTheme.bodySmall?.copyWith(
        color: AppColors.errorLight,
      ),
    ),
    
    // Bottom Navigation Bar Theme
    bottomNavigationBarTheme: const BottomNavigationBarThemeData(
      backgroundColor: AppColors.darkSurface,
      selectedItemColor: AppColors.primaryBlueDark,
      unselectedItemColor: AppColors.gray400,
      type: BottomNavigationBarType.fixed,
      elevation: 8,
    ),
    
    // Navigation Bar Theme
    navigationBarTheme: NavigationBarThemeData(
      backgroundColor: AppColors.darkSurface,
      indicatorColor: AppColors.primaryBlueDark.withOpacity(0.2),
      elevation: 8,
      labelTextStyle: MaterialStateProperty.resolveWith((states) {
        if (states.contains(MaterialState.selected)) {
          return AppTheme.textTheme.labelSmall?.copyWith(
            color: AppColors.primaryBlueDark,
            fontWeight: FontWeight.w600,
          );
        }
        return AppTheme.textTheme.labelSmall?.copyWith(
          color: AppColors.gray400,
        );
      }),
      iconTheme: MaterialStateProperty.resolveWith((states) {
        if (states.contains(MaterialState.selected)) {
          return const IconThemeData(
            color: AppColors.primaryBlueDark,
            size: AppTheme.iconMedium,
          );
        }
        return const IconThemeData(
          color: AppColors.gray400,
          size: AppTheme.iconMedium,
        );
      }),
    ),
    
    // Switch Theme
    switchTheme: SwitchThemeData(
      thumbColor: MaterialStateProperty.resolveWith((states) {
        if (states.contains(MaterialState.selected)) {
          return AppColors.primaryBlueDark;
        }
        return AppColors.gray500;
      }),
      trackColor: MaterialStateProperty.resolveWith((states) {
        if (states.contains(MaterialState.selected)) {
          return AppColors.primaryBlueDark.withOpacity(0.5);
        }
        return AppColors.gray600;
      }),
    ),
    
    // Checkbox Theme
    checkboxTheme: CheckboxThemeData(
      fillColor: MaterialStateProperty.resolveWith((states) {
        if (states.contains(MaterialState.selected)) {
          return AppColors.primaryBlueDark;
        }
        return Colors.transparent;
      }),
      checkColor: MaterialStateProperty.all(AppColors.darkBackground),
      side: const BorderSide(color: AppColors.gray500),
    ),
    
    // Radio Theme
    radioTheme: RadioThemeData(
      fillColor: MaterialStateProperty.resolveWith((states) {
        if (states.contains(MaterialState.selected)) {
          return AppColors.primaryBlueDark;
        }
        return AppColors.gray500;
      }),
    ),
    
    // Chip Theme
    chipTheme: ChipThemeData(
      backgroundColor: AppColors.gray700,
      disabledColor: AppColors.gray800,
      selectedColor: AppColors.primaryBlueDark.withOpacity(0.2),
      secondarySelectedColor: AppColors.secondaryIndigo.withOpacity(0.2),
      labelStyle: AppTheme.textTheme.labelMedium?.copyWith(
        color: AppColors.darkOnSurface,
      ),
      secondaryLabelStyle: AppTheme.textTheme.labelMedium?.copyWith(
        color: AppColors.primaryBlueDark,
      ),
      brightness: Brightness.dark,
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
      backgroundColor: AppColors.darkSurface,
      elevation: 8,
      shape: AppTheme.dialogShape,
      titleTextStyle: AppTheme.textTheme.headlineSmall?.copyWith(
        color: AppColors.darkOnSurface,
      ),
      contentTextStyle: AppTheme.textTheme.bodyMedium?.copyWith(
        color: AppColors.darkOnSurface,
      ),
    ),
    
    // Bottom Sheet Theme
    bottomSheetTheme: const BottomSheetThemeData(
      backgroundColor: AppColors.darkSurface,
      elevation: 8,
      shape: AppTheme.bottomSheetShape,
    ),
    
    // Snack Bar Theme
    snackBarThemeData: SnackBarThemeData(
      backgroundColor: AppColors.gray200,
      contentTextStyle: AppTheme.textTheme.bodyMedium?.copyWith(
        color: AppColors.darkBackground,
      ),
      actionTextColor: AppColors.primaryBlue,
      behavior: SnackBarBehavior.floating,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(AppTheme.radiusMedium),
      ),
    ),
    
    // Divider Theme
    dividerTheme: const DividerThemeData(
      color: AppColors.gray600,
      thickness: 1,
      space: 1,
    ),
    
    // List Tile Theme
    listTileTheme: ListTileThemeData(
      contentPadding: const EdgeInsets.symmetric(
        horizontal: AppTheme.spacing16,
        vertical: AppTheme.spacing4,
      ),
      iconColor: AppColors.gray300,
      textColor: AppColors.darkOnSurface,
      titleTextStyle: AppTheme.textTheme.bodyLarge?.copyWith(
        color: AppColors.darkOnSurface,
      ),
      subtitleTextStyle: AppTheme.textTheme.bodyMedium?.copyWith(
        color: AppColors.gray300,
      ),
    ),
    
    // Expansion Tile Theme
    expansionTileTheme: const ExpansionTileThemeData(
      backgroundColor: AppColors.darkSurface,
      collapsedBackgroundColor: AppColors.darkSurface,
      iconColor: AppColors.gray300,
      collapsedIconColor: AppColors.gray300,
      textColor: AppColors.darkOnSurface,
      collapsedTextColor: AppColors.darkOnSurface,
    ),
    
    // Tab Bar Theme
    tabBarTheme: TabBarTheme(
      labelColor: AppColors.primaryBlueDark,
      unselectedLabelColor: AppColors.gray400,
      labelStyle: AppTheme.textTheme.labelLarge?.copyWith(
        fontWeight: FontWeight.w600,
      ),
      unselectedLabelStyle: AppTheme.textTheme.labelLarge,
      indicator: const UnderlineTabIndicator(
        borderSide: BorderSide(
          color: AppColors.primaryBlueDark,
          width: 2,
        ),
      ),
    ),
    
    // Progress Indicator Theme
    progressIndicatorTheme: const ProgressIndicatorThemeData(
      color: AppColors.primaryBlueDark,
      linearTrackColor: AppColors.gray600,
      circularTrackColor: AppColors.gray600,
    ),
    
    // Slider Theme
    sliderTheme: SliderThemeData(
      activeTrackColor: AppColors.primaryBlueDark,
      inactiveTrackColor: AppColors.gray600,
      thumbColor: AppColors.primaryBlueDark,
      overlayColor: AppColors.primaryBlueDark.withOpacity(0.2),
      valueIndicatorColor: AppColors.primaryBlueDark,
    ),
  );
}