// lib/core/theme/lunance_colors.dart
import 'package:flutter/material.dart';

class LunanceColors {
  // Primary Colors
  static const Color primaryBlue = Color(0xFF4A90E2);
  static const Color secondaryTeal = Color(0xFF2ECC8F);
  static const Color accentOrange = Color(0xFFFF8A50);
  static const Color warningRed = Color(0xFFE74C3C);
  
  // Background Colors
  static const Color primaryBackground = Color(0xFFF8FAFC);
  static const Color cardBackground = Color(0xFFFFFFFF);
  static const Color lightGray = Color(0xFFF1F5F9);
  
  // Text Colors
  static const Color primaryText = Color(0xFF1E293B);
  static const Color secondaryText = Color(0xFF64748B);
  static const Color lightText = Color(0xFF94A3B8);
  
  // Financial Colors
  static const Color incomeGreen = Color(0xFF10B981);
  static const Color expenseRed = Color(0xFFEF4444);
  static const Color neutralYellow = Color(0xFFF59E0B);
  
  // Chatbot Colors
  static const Color botMessageBg = Color(0xFFEBF4FF);
  static const Color botAvatar = Color(0xFF6366F1);
  static const Color chatInputBorder = Color(0xFFD1D5DB);
  
  // Additional Colors for Enhanced UI
  static const Color success = Color(0xFF22C55E);
  static const Color warning = Color(0xFFF97316);
  static const Color info = Color(0xFF3B82F6);
  static const Color error = Color(0xFFDC2626);
  
  // Shadow Colors
  static const Color shadowLight = Color(0x0A000000);
  static const Color shadowMedium = Color(0x14000000);
  static const Color shadowDark = Color(0x1F000000);
  
  // Border Colors
  static const Color borderLight = Color(0xFFE2E8F0);
  static const Color borderMedium = Color(0xFFCBD5E1);
  static const Color borderDark = Color(0xFF94A3B8);
  
  // Gradient Colors
  static const List<Color> primaryGradient = [primaryBlue, secondaryTeal];
  static const List<Color> incomeGradient = [Color(0xFF10B981), Color(0xFF34D399)];
  static const List<Color> expenseGradient = [Color(0xFFEF4444), Color(0xFFF87171)];
  static const List<Color> warningGradient = [accentOrange, neutralYellow];
  
  // Category Colors (for different expense/income categories)
  static const Color categoryFood = Color(0xFFFF6B6B);
  static const Color categoryTransport = Color(0xFF4ECDC4);
  static const Color categoryEducation = Color(0xFF45B7D1);
  static const Color categoryEntertainment = Color(0xFF96CEB4);
  static const Color categoryHealth = Color(0xFFFEAC5E);
  static const Color categoryShopping = Color(0xFFDDA0DD);
  static const Color categoryBills = Color(0xFFFFD93D);
  static const Color categoryOthers = Color(0xFFB0B0B0);
  
  // Status Colors
  static const Color pending = Color(0xFFF59E0B);
  static const Color completed = Color(0xFF10B981);
  static const Color cancelled = Color(0xFFEF4444);
  static const Color draft = Color(0xFF6B7280);
  static const Color divider = borderLight;
  
  // Theme Colors for Dark Mode Support (optional)
  static const Color darkBackground = Color(0xFF0F172A);
  static const Color darkCard = Color(0xFF1E293B);
  static const Color darkText = Color(0xFFE2E8F0);
  static const Color darkSecondaryText = Color(0xFF94A3B8);
  
  // Helper method to get category color by name
  static Color getCategoryColor(String categoryName) {
    switch (categoryName.toLowerCase()) {
      case 'makanan':
      case 'food':
        return categoryFood;
      case 'transportasi':
      case 'transport':
        return categoryTransport;
      case 'pendidikan':
      case 'education':
        return categoryEducation;
      case 'hiburan':
      case 'entertainment':
        return categoryEntertainment;
      case 'kesehatan':
      case 'health':
        return categoryHealth;
      case 'belanja':
      case 'shopping':
        return categoryShopping;
      case 'tagihan':
      case 'bills':
        return categoryBills;
      default:
        return categoryOthers;
    }
  }
  
  // Helper method to get status color
  static Color getStatusColor(String status) {
    switch (status.toLowerCase()) {
      case 'pending':
        return pending;
      case 'completed':
      case 'success':
        return completed;
      case 'cancelled':
      case 'failed':
        return cancelled;
      case 'draft':
        return draft;
      default:
        return primaryBlue;
    }
  }
}