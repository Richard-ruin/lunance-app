import 'package:flutter/material.dart';
import '../config/app_config.dart';

class Validators {
  // Email validation
  static String? validateEmail(String? value) {
    if (value == null || value.isEmpty) {
      return 'Email wajib diisi';
    }
    
    final emailRegex = RegExp(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$');
    if (!emailRegex.hasMatch(value)) {
      return 'Format email tidak valid';
    }
    
    if (!value.endsWith(AppConfig.requiredEmailDomain)) {
      return 'Email harus menggunakan domain .ac.id';
    }
    
    return null;
  }

  // Password validation
  static String? validatePassword(String? value) {
    if (value == null || value.isEmpty) {
      return 'Password wajib diisi';
    }
    
    if (value.length < AppConfig.minPasswordLength) {
      return 'Password minimal ${AppConfig.minPasswordLength} karakter';
    }
    
    if (value.length > AppConfig.maxPasswordLength) {
      return 'Password maksimal ${AppConfig.maxPasswordLength} karakter';
    }
    
    // Check for uppercase letter
    if (!RegExp(r'[A-Z]').hasMatch(value)) {
      return 'Password harus mengandung huruf besar';
    }
    
    // Check for lowercase letter
    if (!RegExp(r'[a-z]').hasMatch(value)) {
      return 'Password harus mengandung huruf kecil';
    }
    
    // Check for number
    if (!RegExp(r'[0-9]').hasMatch(value)) {
      return 'Password harus mengandung angka';
    }
    
    return null;
  }

  // Confirm password validation
  static String? validateConfirmPassword(String? value, String? password) {
    if (value == null || value.isEmpty) {
      return 'Konfirmasi password wajib diisi';
    }
    
    if (value != password) {
      return 'Konfirmasi password tidak sama dengan password';
    }
    
    return null;
  }

  // Name validation
  static String? validateName(String? value) {
    if (value == null || value.isEmpty) {
      return 'Nama lengkap wajib diisi';
    }
    
    if (value.length < AppConfig.minNameLength) {
      return 'Nama minimal ${AppConfig.minNameLength} karakter';
    }
    
    if (value.length > AppConfig.maxNameLength) {
      return 'Nama maksimal ${AppConfig.maxNameLength} karakter';
    }
    
    // Check if contains only letters and spaces
    if (!RegExp(r'^[a-zA-Z\s]+$').hasMatch(value)) {
      return 'Nama hanya boleh mengandung huruf dan spasi';
    }
    
    return null;
  }

  // Phone number validation
  static String? validatePhone(String? value) {
    if (value == null || value.isEmpty) {
      return 'Nomor telepon wajib diisi';
    }
    
    // Remove any non-digit characters for validation
    final cleanPhone = value.replaceAll(RegExp(r'[^\d]'), '');
    
    // Indonesian phone number pattern
    if (!RegExp(r'^(08|628|\+628)[0-9]{8,12}$').hasMatch(cleanPhone)) {
      return 'Format nomor telepon tidak valid';
    }
    
    return null;
  }

  // NIM validation
  static String? validateNim(String? value) {
    if (value == null || value.isEmpty) {
      return 'NIM wajib diisi';
    }
    
    if (value.length < AppConfig.minNimLength) {
      return 'NIM minimal ${AppConfig.minNimLength} digit';
    }
    
    if (value.length > AppConfig.maxNimLength) {
      return 'NIM maksimal ${AppConfig.maxNimLength} digit';
    }
    
    if (!RegExp(r'^[0-9]+$').hasMatch(value)) {
      return 'NIM hanya boleh mengandung angka';
    }
    
    return null;
  }

  // OTP validation
  static String? validateOtp(String? value) {
    if (value == null || value.isEmpty) {
      return 'Kode OTP wajib diisi';
    }
    
    if (value.length != 6) {
      return 'Kode OTP harus 6 digit';
    }
    
    if (!RegExp(r'^[0-9]+$').hasMatch(value)) {
      return 'Kode OTP hanya boleh mengandung angka';
    }
    
    return null;
  }

  // Amount validation
  static String? validateAmount(String? value, {double minAmount = 0}) {
    if (value == null || value.isEmpty) {
      return 'Nominal wajib diisi';
    }
    
    // Remove currency formatting
    final cleanValue = value.replaceAll(RegExp(r'[^\d]'), '');
    
    final amount = double.tryParse(cleanValue);
    if (amount == null) {
      return 'Format nominal tidak valid';
    }
    
    if (amount < minAmount) {
      return 'Nominal minimal ${formatCurrency(minAmount)}';
    }
    
    return null;
  }

  // Required field validation
  static String? validateRequired(String? value, String fieldName) {
    if (value == null || value.isEmpty) {
      return '$fieldName wajib diisi';
    }
    return null;
  }

  // Password strength calculation
  static PasswordStrength getPasswordStrength(String password) {
    if (password.isEmpty) return PasswordStrength.none;
    
    int score = 0;
    
    // Length
    if (password.length >= 8) score++;
    if (password.length >= 12) score++;
    
    // Character variety
    if (RegExp(r'[a-z]').hasMatch(password)) score++;
    if (RegExp(r'[A-Z]').hasMatch(password)) score++;
    if (RegExp(r'[0-9]').hasMatch(password)) score++;
    if (RegExp(r'[!@#$%^&*(),.?":{}|<>]').hasMatch(password)) score++;
    
    // No common patterns
    if (!RegExp(r'(.)\1{2,}').hasMatch(password)) score++; // No repeated chars
    if (!RegExp(r'(123|abc|qwe)', caseSensitive: false).hasMatch(password)) score++; // No sequences
    
    if (score <= 2) return PasswordStrength.weak;
    if (score <= 4) return PasswordStrength.medium;
    if (score <= 6) return PasswordStrength.strong;
    return PasswordStrength.veryStrong;
  }

  // Email availability check (would call API in real implementation)
  static Future<String?> validateEmailAvailability(String email) async {
    // This would make an API call to check if email is available
    await Future.delayed(const Duration(milliseconds: 500)); // Simulate API call
    
    // For demo purposes, return null (available)
    return null;
  }

  // Format currency for display
  static String formatCurrency(double amount) {
    return 'Rp ${amount.toStringAsFixed(0).replaceAllMapped(
      RegExp(r'(\d{1,3})(?=(\d{3})+(?!\d))'),
      (Match m) => '${m[1]}.',
    )}';
  }

  // Clean phone number for API submission
  static String cleanPhoneNumber(String phone) {
    String cleaned = phone.replaceAll(RegExp(r'[^\d]'), '');
    
    // Convert to standard format (08xxx)
    if (cleaned.startsWith('628')) {
      cleaned = '0${cleaned.substring(2)}';
    } else if (cleaned.startsWith('+628')) {
      cleaned = '0${cleaned.substring(3)}';
    }
    
    return cleaned;
  }

  // Validate university selection
  static String? validateUniversitySelection(String? value) {
    if (value == null || value.isEmpty) {
      return 'Universitas wajib dipilih';
    }
    return null;
  }

  // Validate fakultas selection
  static String? validateFakultasSelection(String? value) {
    if (value == null || value.isEmpty) {
      return 'Fakultas wajib dipilih';
    }
    return null;
  }

  // Validate prodi selection
  static String? validateProdiSelection(String? value) {
    if (value == null || value.isEmpty) {
      return 'Program studi wajib dipilih';
    }
    return null;
  }
}

enum PasswordStrength {
  none,
  weak,
  medium,
  strong,
  veryStrong,
}

extension PasswordStrengthExtension on PasswordStrength {
  String get label {
    switch (this) {
      case PasswordStrength.none:
        return '';
      case PasswordStrength.weak:
        return 'Lemah';
      case PasswordStrength.medium:
        return 'Sedang';
      case PasswordStrength.strong:
        return 'Kuat';
      case PasswordStrength.veryStrong:
        return 'Sangat Kuat';
    }
  }

  double get progress {
    switch (this) {
      case PasswordStrength.none:
        return 0.0;
      case PasswordStrength.weak:
        return 0.25;
      case PasswordStrength.medium:
        return 0.5;
      case PasswordStrength.strong:
        return 0.75;
      case PasswordStrength.veryStrong:
        return 1.0;
    }
  }

  Color get color {
    switch (this) {
      case PasswordStrength.none:
        return Colors.grey;
      case PasswordStrength.weak:
        return Colors.red;
      case PasswordStrength.medium:
        return Colors.orange;
      case PasswordStrength.strong:
        return Colors.blue;
      case PasswordStrength.veryStrong:
        return Colors.green;
    }
  }
}