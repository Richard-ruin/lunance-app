import 'package:flutter/material.dart';
import 'app_theme.dart';

class DarkTheme {
  static final ColorScheme _colorScheme = const ColorScheme.dark(
    // Primary colors
    primary: Color(0xFF60A5FA), // Blue-400
    onPrimary: Color(0xFF1E40AF), // Blue-700
    primaryContainer: Color(0xFF1E40AF), // Blue-700
    onPrimaryContainer: Color(0xFFDBEAFE), // Blue-100
    
    // Secondary colors
    secondary: Color(0xFF818CF8), // Indigo-400
    onSecondary: Color(0xFF4338CA), // Indigo-700
    secondaryContainer: Color(0xFF4338CA), // Indigo-700
    onSecondaryContainer: Color(0xFFE0E7FF), // Indigo-100
    
    // Tertiary colors
    tertiary: Color(0xFF34D399), // Emerald-400
    onTertiary: Color(0xFF047857), // Emerald-700
    tertiaryContainer: Color(0xFF047857), // Emerald-700
    onTertiaryContainer: Color(0xFFD1FAE5), // Emerald-100
    
    // Error colors
    error: Color(0xFFF87171), // Red-400
    onError: Color(0xFFB91C1C), // Red-700
    errorContainer: Color(0xFFB91C1C), // Red-700
    onErrorContainer: Color(0xFFFEE2E2), // Red-100
    
    // Background colors
    background: Color(0xFF0F172A), // Slate-900
    onBackground: Color(0xFFF1F5F9), // Slate-100
    
    // Surface colors
    surface: Color(0xFF1E293B), // Slate-800
    onSurface: Color(0xFFF1F5F9), // Slate-100
    surfaceVariant: Color(0xFF334155), // Slate-700
    onSurfaceVariant: Color(0xFF94A3B8), // Slate-400
    
    // Outline colors
    outline: Color(0xFF475569), // Slate-600
    outlineVariant: Color(0xFF334155), // Slate-700
    
    // Other colors
    shadow: Color(0xFF000000),
    scrim: Color(0xFF000000),
    inverseSurface: Color(0xFFF1F5F9), // Slate-100
    onInverseSurface: Color(0xFF1E293B), // Slate-800
    inversePrimary: Color(0xFF3B82F6), // Blue-500
    surfaceTint: Color(0xFF60A5FA), // Blue-400
  );

  static ThemeData get theme {
    return ThemeData(
      useMaterial3: true,
      colorScheme: _colorScheme,
      fontFamily: AppTheme.fontFamily,
      
      // Component themes
      appBarTheme: AppTheme.appBarTheme(_colorScheme),
      cardTheme: AppTheme.cardTheme(_colorScheme),
      inputDecorationTheme: AppTheme.inputDecorationTheme(_colorScheme),
      bottomNavigationBarTheme: AppTheme.bottomNavigationBarTheme(_colorScheme),
      textTheme: AppTheme.textTheme(_colorScheme),
      
      // Button themes
      elevatedButtonTheme: ElevatedButtonThemeData(
        style: AppTheme.primaryButtonStyle(_colorScheme),
      ),
      outlinedButtonTheme: OutlinedButtonThemeData(
        style: AppTheme.secondaryButtonStyle(_colorScheme),
      ),
      textButtonTheme: TextButtonThemeData(
        style: TextButton.styleFrom(
          foregroundColor: _colorScheme.primary,
          padding: const EdgeInsets.symmetric(
            horizontal: AppTheme.spacingM,
            vertical: AppTheme.spacingS,
          ),
        ),
      ),
      
      // Icon theme
      iconTheme: IconThemeData(
        color: _colorScheme.onSurface,
        size: 24,
      ),
      
      // Chip theme
      chipTheme: ChipThemeData(
        backgroundColor: _colorScheme.surfaceVariant,
        labelStyle: TextStyle(
          color: _colorScheme.onSurfaceVariant,
          fontFamily: AppTheme.fontFamily,
        ),
        side: BorderSide.none,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(AppTheme.borderRadiusMedium),
        ),
      ),
      
      // Floating action button theme
      floatingActionButtonTheme: FloatingActionButtonThemeData(
        backgroundColor: _colorScheme.primary,
        foregroundColor: _colorScheme.onPrimary,
        elevation: AppTheme.elevationMedium,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(AppTheme.borderRadiusLarge),
        ),
      ),
      
      // Dialog theme
      dialogTheme: DialogTheme(
        backgroundColor: _colorScheme.surface,
        elevation: AppTheme.elevationHigh,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(AppTheme.borderRadiusLarge),
        ),
        titleTextStyle: TextStyle(
          color: _colorScheme.onSurface,
          fontSize: 20,
          fontWeight: FontWeight.w600,
          fontFamily: AppTheme.fontFamily,
        ),
        contentTextStyle: TextStyle(
          color: _colorScheme.onSurface,
          fontSize: 14,
          fontFamily: AppTheme.fontFamily,
        ),
      ),
      
      // Snack bar theme
      snackBarTheme: SnackBarThemeData(
        backgroundColor: _colorScheme.inverseSurface,
        contentTextStyle: TextStyle(
          color: _colorScheme.onInverseSurface,
          fontFamily: AppTheme.fontFamily,
        ),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(AppTheme.borderRadiusSmall),
        ),
        behavior: SnackBarBehavior.floating,
        elevation: AppTheme.elevationMedium,
      ),
      
      // Progress indicator theme
      progressIndicatorTheme: ProgressIndicatorThemeData(
        color: _colorScheme.primary,
        linearTrackColor: _colorScheme.surfaceVariant,
        circularTrackColor: _colorScheme.surfaceVariant,
      ),
      
      // Switch theme
      switchTheme: SwitchThemeData(
        thumbColor: MaterialStateProperty.resolveWith((states) {
          if (states.contains(MaterialState.selected)) {
            return _colorScheme.primary;
          }
          return _colorScheme.outline;
        }),
        trackColor: MaterialStateProperty.resolveWith((states) {
          if (states.contains(MaterialState.selected)) {
            return _colorScheme.primaryContainer;
          }
          return _colorScheme.surfaceVariant;
        }),
      ),
      
      // Checkbox theme
      checkboxTheme: CheckboxThemeData(
        fillColor: MaterialStateProperty.resolveWith((states) {
          if (states.contains(MaterialState.selected)) {
            return _colorScheme.primary;
          }
          return Colors.transparent;
        }),
        checkColor: MaterialStateProperty.all(_colorScheme.onPrimary),
        side: BorderSide(color: _colorScheme.outline),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(4),
        ),
      ),
      
      // Radio theme
      radioTheme: RadioThemeData(
        fillColor: MaterialStateProperty.resolveWith((states) {
          if (states.contains(MaterialState.selected)) {
            return _colorScheme.primary;
          }
          return _colorScheme.outline;
        }),
      ),
      
      // Divider theme
      dividerTheme: DividerThemeData(
        color: _colorScheme.outline,
        thickness: 1,
        space: 1,
      ),
      
      // List tile theme
      listTileTheme: ListTileThemeData(
        textColor: _colorScheme.onSurface,
        iconColor: _colorScheme.onSurfaceVariant,
        contentPadding: const EdgeInsets.symmetric(
          horizontal: AppTheme.spacingM,
          vertical: AppTheme.spacingS,
        ),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(AppTheme.borderRadiusSmall),
        ),
      ),
    );
  }
}