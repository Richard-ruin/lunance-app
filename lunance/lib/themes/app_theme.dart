import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'light_theme.dart';
import 'dark_theme.dart';

class AppColors {
  // Primary Colors
  static const Color primaryBlue = Color(0xFF3B82F6);
  static const Color primaryBlueDark = Color(0xFF60A5FA);
  
  // Secondary Colors
  static const Color secondaryIndigo = Color(0xFF6366F1);
  static const Color secondaryPurple = Color(0xFF8B5CF6);
  static const Color secondaryPink = Color(0xFFEC4899);
  
  // Success Colors
  static const Color success = Color(0xFF10B981);
  static const Color successLight = Color(0xFF34D399);
  static const Color successDark = Color(0xFF059669);
  
  // Warning Colors
  static const Color warning = Color(0xFFF59E0B);
  static const Color warningLight = Color(0xFFFBBF24);
  static const Color warningDark = Color(0xFFD97706);
  
  // Error Colors
  static const Color error = Color(0xFFEF4444);
  static const Color errorLight = Color(0xFFF87171);
  static const Color errorDark = Color(0xFFDC2626);
  
  // Info Colors
  static const Color info = Color(0xFF3B82F6);
  static const Color infoLight = Color(0xFF60A5FA);
  static const Color infoDark = Color(0xFF2563EB);
  
  // Light Theme Colors
  static const Color lightBackground = Color(0xFFF8FAFC);
  static const Color lightSurface = Color(0xFFFFFFFF);
  static const Color lightSurfaceVariant = Color(0xFFF1F5F9);
  static const Color lightOnBackground = Color(0xFF0F172A);
  static const Color lightOnSurface = Color(0xFF334155);
  static const Color lightOnSurfaceVariant = Color(0xFF64748B);
  
  // Dark Theme Colors
  static const Color darkBackground = Color(0xFF0F172A);
  static const Color darkSurface = Color(0xFF1E293B);
  static const Color darkSurfaceVariant = Color(0xFF334155);
  static const Color darkOnBackground = Color(0xFFE2E8F0);
  static const Color darkOnSurface = Color(0xFFCBD5E1);
  static const Color darkOnSurfaceVariant = Color(0xFF94A3B8);
  
  // Gray Scale
  static const Color gray50 = Color(0xFFF8FAFC);
  static const Color gray100 = Color(0xFFF1F5F9);
  static const Color gray200 = Color(0xFFE2E8F0);
  static const Color gray300 = Color(0xFFCBD5E1);
  static const Color gray400 = Color(0xFF94A3B8);
  static const Color gray500 = Color(0xFF64748B);
  static const Color gray600 = Color(0xFF475569);
  static const Color gray700 = Color(0xFF334155);
  static const Color gray800 = Color(0xFF1E293B);
  static const Color gray900 = Color(0xFF0F172A);
  
  // Financial Colors
  static const Color income = Color(0xFF10B981);
  static const Color expense = Color(0xFFEF4444);
  static const Color savings = Color(0xFF3B82F6);
  static const Color investment = Color(0xFF8B5CF6);
  
  // Category Colors
  static const List<Color> categoryColors = [
    Color(0xFF3B82F6), // Blue
    Color(0xFF10B981), // Green
    Color(0xFFF59E0B), // Yellow
    Color(0xFFEF4444), // Red
    Color(0xFF8B5CF6), // Purple
    Color(0xFF6366F1), // Indigo
    Color(0xFFEC4899), // Pink
    Color(0xFF06B6D4), // Cyan
    Color(0xFF84CC16), // Lime
    Color(0xFFF97316), // Orange
  ];
}

class AppTheme {
  static ThemeData get lightTheme => LightTheme.theme;
  static ThemeData get darkTheme => DarkTheme.theme;
  
  // Common Text Theme
  static TextTheme get textTheme => GoogleFonts.interTextTheme().copyWith(
    // Display Styles
    displayLarge: GoogleFonts.inter(
      fontSize: 57,
      fontWeight: FontWeight.w400,
      letterSpacing: -0.25,
      height: 1.12,
    ),
    displayMedium: GoogleFonts.inter(
      fontSize: 45,
      fontWeight: FontWeight.w400,
      letterSpacing: 0,
      height: 1.16,
    ),
    displaySmall: GoogleFonts.inter(
      fontSize: 36,
      fontWeight: FontWeight.w400,
      letterSpacing: 0,
      height: 1.22,
    ),
    
    // Headline Styles
    headlineLarge: GoogleFonts.inter(
      fontSize: 32,
      fontWeight: FontWeight.w600,
      letterSpacing: 0,
      height: 1.25,
    ),
    headlineMedium: GoogleFonts.inter(
      fontSize: 28,
      fontWeight: FontWeight.w600,
      letterSpacing: 0,
      height: 1.29,
    ),
    headlineSmall: GoogleFonts.inter(
      fontSize: 24,
      fontWeight: FontWeight.w600,
      letterSpacing: 0,
      height: 1.33,
    ),
    
    // Title Styles
    titleLarge: GoogleFonts.inter(
      fontSize: 22,
      fontWeight: FontWeight.w600,
      letterSpacing: 0,
      height: 1.27,
    ),
    titleMedium: GoogleFonts.inter(
      fontSize: 16,
      fontWeight: FontWeight.w600,
      letterSpacing: 0.15,
      height: 1.50,
    ),
    titleSmall: GoogleFonts.inter(
      fontSize: 14,
      fontWeight: FontWeight.w600,
      letterSpacing: 0.10,
      height: 1.43,
    ),
    
    // Label Styles
    labelLarge: GoogleFonts.inter(
      fontSize: 14,
      fontWeight: FontWeight.w500,
      letterSpacing: 0.10,
      height: 1.43,
    ),
    labelMedium: GoogleFonts.inter(
      fontSize: 12,
      fontWeight: FontWeight.w500,
      letterSpacing: 0.50,
      height: 1.33,
    ),
    labelSmall: GoogleFonts.inter(
      fontSize: 11,
      fontWeight: FontWeight.w500,
      letterSpacing: 0.50,
      height: 1.45,
    ),
    
    // Body Styles
    bodyLarge: GoogleFonts.inter(
      fontSize: 16,
      fontWeight: FontWeight.w400,
      letterSpacing: 0.15,
      height: 1.50,
    ),
    bodyMedium: GoogleFonts.inter(
      fontSize: 14,
      fontWeight: FontWeight.w400,
      letterSpacing: 0.25,
      height: 1.43,
    ),
    bodySmall: GoogleFonts.inter(
      fontSize: 12,
      fontWeight: FontWeight.w400,
      letterSpacing: 0.40,
      height: 1.33,
    ),
  );
  
  // Common Shape Theme
  static ShapeBorder get cardShape => RoundedRectangleBorder(
    borderRadius: BorderRadius.circular(12),
  );
  
  static ShapeBorder get buttonShape => RoundedRectangleBorder(
    borderRadius: BorderRadius.circular(8),
  );
  
  static ShapeBorder get inputShape => RoundedRectangleBorder(
    borderRadius: BorderRadius.circular(8),
  );
  
  static ShapeBorder get bottomSheetShape => const RoundedRectangleBorder(
    borderRadius: BorderRadius.vertical(
      top: Radius.circular(16),
    ),
  );
  
  static ShapeBorder get dialogShape => RoundedRectangleBorder(
    borderRadius: BorderRadius.circular(16),
  );
  
  // Common Elevation
  static const double cardElevation = 2;
  static const double buttonElevation = 1;
  static const double fabElevation = 6;
  static const double appBarElevation = 0;
  
  // Common Durations
  static const Duration shortAnimation = Duration(milliseconds: 200);
  static const Duration mediumAnimation = Duration(milliseconds: 300);
  static const Duration longAnimation = Duration(milliseconds: 500);
  
  // Common Curves
  static const Curve defaultCurve = Curves.easeInOut;
  static const Curve fastCurve = Curves.easeOut;
  static const Curve slowCurve = Curves.easeIn;
  
  // Spacing
  static const double spacing4 = 4.0;
  static const double spacing8 = 8.0;
  static const double spacing12 = 12.0;
  static const double spacing16 = 16.0;
  static const double spacing20 = 20.0;
  static const double spacing24 = 24.0;
  static const double spacing32 = 32.0;
  static const double spacing40 = 40.0;
  static const double spacing48 = 48.0;
  
  // Border Radius
  static const double radiusSmall = 4.0;
  static const double radiusMedium = 8.0;
  static const double radiusLarge = 12.0;
  static const double radiusXLarge = 16.0;
  static const double radiusXXLarge = 24.0;
  
  // Icon Sizes
  static const double iconSmall = 16.0;
  static const double iconMedium = 24.0;
  static const double iconLarge = 32.0;
  static const double iconXLarge = 48.0;
  
  // Helper Methods
  static Color getFinancialColor(String type) {
    switch (type.toLowerCase()) {
      case 'income':
      case 'pemasukan':
        return AppColors.income;
      case 'expense':
      case 'pengeluaran':
        return AppColors.expense;
      case 'savings':
      case 'tabungan':
        return AppColors.savings;
      case 'investment':
      case 'investasi':
        return AppColors.investment;
      default:
        return AppColors.gray500;
    }
  }
  
  static Color getCategoryColor(int index) {
    return AppColors.categoryColors[index % AppColors.categoryColors.length];
  }
  
  static TextStyle getFinancialTextStyle(
    BuildContext context, {
    required double amount,
    TextStyle? baseStyle,
  }) {
    final color = amount >= 0 ? AppColors.income : AppColors.expense;
    return (baseStyle ?? Theme.of(context).textTheme.bodyMedium!).copyWith(
      color: color,
      fontWeight: FontWeight.w600,
    );
  }
}