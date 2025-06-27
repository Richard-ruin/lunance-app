
// lib/shared/utils/validators.dart
class Validators {
  // Basic validation methods for forms
  static String? required(String? value, String fieldName) {
    if (value == null || value.isEmpty) {
      return '$fieldName harus diisi';
    }
    return null;
  }

  static String? email(String? value) {
    if (value == null || value.isEmpty) {
      return 'Email harus diisi';
    }
    
    final emailRegex = RegExp(r'^[^@]+@[^@]+\.[^@]+$');
    if (!emailRegex.hasMatch(value)) {
      return 'Format email tidak valid';
    }
    
    return null;
  }

  static String? password(String? value, {int minLength = 8}) {
    if (value == null || value.isEmpty) {
      return 'Password harus diisi';
    }
    
    if (value.length < minLength) {
      return 'Password minimal $minLength karakter';
    }
    
    return null;
  }

  static String? confirmPassword(String? value, String? originalPassword) {
    if (value == null || value.isEmpty) {
      return 'Konfirmasi password harus diisi';
    }
    
    if (value != originalPassword) {
      return 'Password tidak cocok';
    }
    
    return null;
  }

  static String? phone(String? value) {
    if (value == null || value.isEmpty) {
      return null; // Optional field
    }
    
    final phoneRegex = RegExp(r'^(\+62|62|0)[0-9]{9,12}$');
    if (!phoneRegex.hasMatch(value)) {
      return 'Format nomor telepon tidak valid';
    }
    
    return null;
  }

  static String? name(String? value) {
    if (value == null || value.isEmpty) {
      return 'Nama harus diisi';
    }
    
    if (value.length < 2) {
      return 'Nama minimal 2 karakter';
    }
    
    final nameRegex = RegExp(r"^[a-zA-Z\s\.']+$");
    if (!nameRegex.hasMatch(value)) {
      return 'Nama hanya boleh mengandung huruf, spasi, titik, dan apostrof';
    }
    
    return null;
  }

  static String? studentId(String? value) {
    if (value == null || value.isEmpty) {
      return 'NIM harus diisi';
    }
    
    if (value.length < 8 || value.length > 15) {
      return 'NIM harus 8-15 karakter';
    }
    
    final nimRegex = RegExp(r'^[A-Za-z0-9]+$');
    if (!nimRegex.hasMatch(value)) {
      return 'NIM hanya boleh mengandung huruf dan angka';
    }
    
    return null;
  }

  static String? university(String? value) {
    if (value == null || value.isEmpty) {
      return 'Universitas harus diisi';
    }
    
    if (value.length < 3) {
      return 'Nama universitas minimal 3 karakter';
    }
    
    return null;
  }

  static String? faculty(String? value) {
    if (value == null || value.isEmpty) {
      return 'Fakultas harus diisi';
    }
    
    if (value.length < 3) {
      return 'Nama fakultas minimal 3 karakter';
    }
    
    return null;
  }

  static String? major(String? value) {
    if (value == null || value.isEmpty) {
      return 'Jurusan harus diisi';
    }
    
    if (value.length < 3) {
      return 'Nama jurusan minimal 3 karakter';
    }
    
    return null;
  }

  static String? semester(String? value) {
    if (value == null || value.isEmpty) {
      return 'Semester harus diisi';
    }
    
    final semesterInt = int.tryParse(value);
    if (semesterInt == null) {
      return 'Semester harus berupa angka';
    }
    
    if (semesterInt < 1 || semesterInt > 14) {
      return 'Semester harus antara 1-14';
    }
    
    return null;
  }

  static String? graduationYear(String? value) {
    if (value == null || value.isEmpty) {
      return 'Tahun lulus harus diisi';
    }
    
    final year = int.tryParse(value);
    if (year == null) {
      return 'Tahun lulus harus berupa angka';
    }
    
    final currentYear = DateTime.now().year;
    if (year < currentYear || year > currentYear + 8) {
      return 'Tahun lulus tidak valid';
    }
    
    return null;
  }

  static String? otp(String? value) {
    if (value == null || value.isEmpty) {
      return 'Kode OTP harus diisi';
    }
    
    if (value.length != 6) {
      return 'Kode OTP harus 6 digit';
    }
    
    final otpRegex = RegExp(r'^[0-9]{6}$');
    if (!otpRegex.hasMatch(value)) {
      return 'Kode OTP hanya boleh berupa angka';
    }
    
    return null;
  }

  static String? amount(String? value) {
    if (value == null || value.isEmpty) {
      return 'Jumlah harus diisi';
    }
    
    final amount = double.tryParse(value.replaceAll(',', ''));
    if (amount == null) {
      return 'Jumlah harus berupa angka';
    }
    
    if (amount <= 0) {
      return 'Jumlah harus lebih dari 0';
    }
    
    if (amount > 999999999999) {
      return 'Jumlah terlalu besar';
    }
    
    return null;
  }

  // Email validation specifically for Indonesian academic emails
  static bool isValidStudentEmail(String email) {
    if (email.isEmpty) return false;
    
    // Check if it contains @ and .ac.id
    if (!email.contains('@') || !email.endsWith('.ac.id')) {
      return false;
    }
    
    // Basic email format validation
    final emailRegExp = RegExp(
      r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.ac\.id$',
    );
    
    return emailRegExp.hasMatch(email);
  }

  // Password validation for Indonesian students
  static Map<String, bool> validatePassword(String password) {
    return {
      'hasMinLength': password.length >= 8,
      'hasMaxLength': password.length <= 128,
      'hasUppercase': password.contains(RegExp(r'[A-Z]')),
      'hasLowercase': password.contains(RegExp(r'[a-z]')),
      'hasDigits': password.contains(RegExp(r'[0-9]')),
      'hasSpecialCharacters': password.contains(RegExp(r'[!@#$%^&*(),.?":{}|<>]')),
    };
  }

  static bool isStrongPassword(String password) {
    final validation = validatePassword(password);
    return validation['hasMinLength']! &&
           validation['hasUppercase']! &&
           validation['hasLowercase']! &&
           validation['hasDigits']!;
  }

  // Indonesian phone number validation
  static bool isValidIndonesianPhone(String phone) {
    if (phone.isEmpty) return false;
    
    // Remove all non-digit characters
    final cleanPhone = phone.replaceAll(RegExp(r'[^0-9]'), '');
    
    // Indonesian phone number patterns
    // Mobile: 08xx-xxxx-xxxx (10-13 digits total)
    // International: +62xxx or 62xxx
    if (cleanPhone.startsWith('08') && cleanPhone.length >= 10 && cleanPhone.length <= 13) {
      return true;
    }
    
    if (cleanPhone.startsWith('628') && cleanPhone.length >= 11 && cleanPhone.length <= 14) {
      return true;
    }
    
    return false;
  }

  // Indonesian NIM (Student ID) validation
  static bool isValidNIM(String nim) {
    if (nim.isEmpty) return false;
    
    // Most Indonesian universities use 8-15 digit NIM
    // Can contain letters and numbers
    final nimRegExp = RegExp(r'^[A-Za-z0-9]{8,15}$');
    return nimRegExp.hasMatch(nim);
  }

  // OTP validation
  static bool isValidOTP(String otp) {
    if (otp.isEmpty) return false;
    
    // 6 digit OTP
    final otpRegExp = RegExp(r'^[0-9]{6}$');
    return otpRegExp.hasMatch(otp);
  }

  // Name validation for Indonesian names
  static bool isValidIndonesianName(String name) {
    if (name.isEmpty || name.length < 2) return false;
    
    // Allow Indonesian characters, spaces, dots, and apostrophes
    // Common in Indonesian names like "Siti Nur'aini" or "Dr. Ahmad"
    final nameRegExp = RegExp(r"^[a-zA-Z\s\.']+$");
    return nameRegExp.hasMatch(name);
  }

  // Amount validation for financial transactions
  static bool isValidAmount(String amount) {
    if (amount.isEmpty) return false;
    
    try {
      final value = double.parse(amount.replaceAll(',', ''));
      return value > 0 && value <= 999999999999; // Max 999 billion
    } catch (e) {
      return false;
    }
  }
}