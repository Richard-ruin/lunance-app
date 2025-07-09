import 'package:flutter/material.dart';

class AppThemes {
  // Light Theme
  static ThemeData lightTheme = ThemeData(
    useMaterial3: true,
    brightness: Brightness.light,
    fontFamily: 'Inter',
    
    // Color Scheme
    colorScheme: const ColorScheme.light(
      primary: Color(0xFF3B82F6),
      onPrimary: Color(0xFFFFFFFF),
      primaryContainer: Color(0xFFEBF4FF),
      onPrimaryContainer: Color(0xFF1E40AF),
      
      secondary: Color(0xFFE2E8F0),
      onSecondary: Color(0xFF1E293B),
      secondaryContainer: Color(0xFFF1F5F9),
      onSecondaryContainer: Color(0xFF0F172A),
      
      surface: Color(0xFFFFFFFF),
      onSurface: Color(0xFF1E293B),
      surfaceVariant: Color(0xFFF8FAFC),
      onSurfaceVariant: Color(0xFF475569),
      
      background: Color(0xFFF8FAFC),
      onBackground: Color(0xFF0F172A),
      
      error: Color(0xFFEF4444),
      onError: Color(0xFFFFFFFF),
      errorContainer: Color(0xFFFEE2E2),
      onErrorContainer: Color(0xFF7F1D1D),
      
      outline: Color(0xFF94A3B8),
      outlineVariant: Color(0xFFCBD5E1),
    ),
    
    // App Bar
    appBarTheme: const AppBarTheme(
      backgroundColor: Color(0xFF3B82F6),
      foregroundColor: Color(0xFFFFFFFF),
      elevation: 0,
      centerTitle: true,
    ),
    
    // Bottom Navigation Bar
    bottomNavigationBarTheme: const BottomNavigationBarThemeData(
  selectedItemColor: Color(0xFF3B82F6),
  unselectedItemColor: Color(0xFF94A3B8),
  elevation: 8,
),

  );

  // Dark Theme
  static ThemeData darkTheme = ThemeData(
    useMaterial3: true,
    brightness: Brightness.dark,
    fontFamily: 'Inter',
    
    // Color Scheme
    colorScheme: const ColorScheme.dark(
      primary: Color(0xFF60A5FA),
      onPrimary: Color(0xFF0F172A),
      primaryContainer: Color(0xFF1E3A8A),
      onPrimaryContainer: Color(0xFF93C5FD),
      
      secondary: Color(0xFF475569),
      onSecondary: Color(0xFFE2E8F0),
      secondaryContainer: Color(0xFF374151),
      onSecondaryContainer: Color(0xFFF1F5F9),
      
      surface: Color(0xFF1E293B),
      onSurface: Color(0xFFE2E8F0),
      surfaceVariant: Color(0xFF334155),
      onSurfaceVariant: Color(0xFF94A3B8),
      
      background: Color(0xFF0F172A),
      onBackground: Color(0xFFF8FAFC),
      
      error: Color(0xFFF87171),
      onError: Color(0xFF0F172A),
      errorContainer: Color(0xFF7F1D1D),
      onErrorContainer: Color(0xFFFEE2E2),
      
      outline: Color(0xFF64748B),
      outlineVariant: Color(0xFF475569),
    ),
    
    // App Bar
    appBarTheme: const AppBarTheme(
      backgroundColor: Color(0xFF1E293B),
      foregroundColor: Color(0xFFE2E8F0),
      elevation: 0,
      centerTitle: true,
    ),
    
    // Bottom Navigation Bar
    bottomNavigationBarTheme: const BottomNavigationBarThemeData(
  selectedItemColor: Color(0xFF60A5FA),
  unselectedItemColor: Color(0xFF64748B),
  elevation: 8,
),
  );
}