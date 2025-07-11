import 'package:flutter/material.dart';

class AppColors {
  // Primary Colors (Changed from blue to gray)
  static const Color primary = Color(0xFF6B7280); // Gray 500
  static const Color primaryLight = Color(0xFF9CA3AF); // Gray 400
  static const Color primaryDark = Color(0xFF374151); // Gray 700
  
  // Neutral Colors
  static const Color white = Color(0xFFFFFFFF);
  static const Color background = Color(0xFFFAFAFA);
  static const Color surface = Color(0xFFFFFFFF);
  
  // Gray Scale
  static const Color gray50 = Color(0xFFF9FAFB);
  static const Color gray100 = Color(0xFFF3F4F6);
  static const Color gray200 = Color(0xFFE5E7EB);
  static const Color gray300 = Color(0xFFD1D5DB);
  static const Color gray400 = Color(0xFF9CA3AF);
  static const Color gray500 = Color(0xFF6B7280);
  static const Color gray600 = Color(0xFF4B5563);
  static const Color gray700 = Color(0xFF374151);
  static const Color gray800 = Color(0xFF1F2937);
  static const Color gray900 = Color(0xFF111827);
  
  // Text Colors
  static const Color textPrimary = gray900;
  static const Color textSecondary = gray600;
  static const Color textTertiary = gray400;
  
  // Status Colors
  static const Color success = Color(0xFF10B981);
  static const Color warning = Color(0xFFF59E0B);
  static const Color error = Color(0xFFEF4444);
  static const Color info = Color(0xFF3B82F6);
  
  // Functional Colors
  static const Color border = gray200;
  static const Color divider = gray100;
  static const Color shadow = Color(0x1A000000);
  
  // Income & Expense
  static const Color income = Color(0xFF10B981);
  static const Color expense = Color(0xFFEF4444);
  
  // Chat Colors
  static const Color chatUser = primary;
  static const Color chatBot = gray100;
  
  // Overlay Colors
  static const Color overlay = Color(0x80000000);
  static const Color overlayLight = Color(0x40000000);
}

class AppGradients {
  static const LinearGradient primaryGradient = LinearGradient(
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
    colors: [
      AppColors.primary,
      AppColors.primaryDark,
    ],
  );
  
  static const LinearGradient backgroundGradient = LinearGradient(
    begin: Alignment.topCenter,
    end: Alignment.bottomCenter,
    colors: [
      AppColors.white,
      AppColors.background,
    ],
  );
  
  static const LinearGradient shimmerGradient = LinearGradient(
    begin: Alignment(-1.0, -0.3),
    end: Alignment(1.0, 0.3),
    colors: [
      Color(0xFFE0E0E0),
      Color(0xFFF5F5F5),
      Color(0xFFE0E0E0),
    ],
    stops: [0.0, 0.5, 1.0],
  );
}