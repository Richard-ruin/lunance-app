// lib/shared/utils/validators.dart
class Validators {
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

  // University name validation
  static bool isValidUniversityName(String university) {
    if (university.isEmpty || university.length < 3) return false;
    
    // Allow Indonesian university names
    final universityRegExp = RegExp(r"^[a-zA-Z\s\.'()-]+$");
    return universityRegExp.hasMatch(university);
  }

  // Semester validation
  static bool isValidSemester(int semester) {
    return semester >= 1 && semester <= 14; // Max 14 semesters
  }

  // Graduation year validation
  static bool isValidGraduationYear(int year) {
    final currentYear = DateTime.now().year;
    return year >= currentYear && year <= currentYear + 8;
  }
}

// lib/shared/extensions/string_extensions.dart
extension StringExtensions on String {
  // Capitalize first letter of each word
  String toTitleCase() {
    if (isEmpty) return this;
    
    return split(' ')
        .map((word) => word.isEmpty 
            ? word 
            : word[0].toUpperCase() + word.substring(1).toLowerCase())
        .join(' ');
  }

  // Remove extra spaces
  String removeExtraSpaces() {
    return replaceAll(RegExp(r'\s+'), ' ').trim();
  }

  // Mask email for privacy (show first 3 chars and domain)
  String maskEmail() {
    if (!contains('@')) return this;
    
    final parts = split('@');
    if (parts[0].length <= 3) return this;
    
    final maskedLocal = parts[0].substring(0, 3) + '*' * (parts[0].length - 3);
    return '$maskedLocal@${parts[1]}';
  }

  // Mask phone number for privacy
  String maskPhone() {
    if (length <= 4) return this;
    
    final start = substring(0, 3);
    final end = substring(length - 2);
    final middle = '*' * (length - 5);
    
    return start + middle + end;
  }

  // Format Indonesian currency
  String toIDRCurrency() {
    final value = double.tryParse(replaceAll(',', '')) ?? 0;
    return 'Rp ${value.toStringAsFixed(0).replaceAllMapped(
      RegExp(r'(\d{1,3})(?=(\d{3})+(?!\d))'),
      (Match m) => '${m[1]}.',
    )}';
  }

  // Check if string is numeric
  bool get isNumeric {
    return double.tryParse(this) != null;
  }

  // Check if string is valid student email
  bool get isValidStudentEmail {
    return Validators.isValidStudentEmail(this);
  }

  // Check if string is valid Indonesian phone
  bool get isValidIndonesianPhone {
    return Validators.isValidIndonesianPhone(this);
  }
}

// lib/shared/extensions/datetime_extensions.dart
extension DateTimeExtensions on DateTime {
  // Format for Indonesian locale
  String toIndonesianDate() {
    final months = [
      'Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni',
      'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember'
    ];
    
    return '$day ${months[month - 1]} $year';
  }

  // Format for Indonesian short date
  String toIndonesianShortDate() {
    return '$day/${month.toString().padLeft(2, '0')}/$year';
  }

  // Time ago in Indonesian
  String timeAgoInIndonesian() {
    final now = DateTime.now();
    final difference = now.difference(this);
    
    if (difference.inDays > 365) {
      final years = (difference.inDays / 365).floor();
      return '$years tahun yang lalu';
    } else if (difference.inDays > 30) {
      final months = (difference.inDays / 30).floor();
      return '$months bulan yang lalu';
    } else if (difference.inDays > 0) {
      return '${difference.inDays} hari yang lalu';
    } else if (difference.inHours > 0) {
      return '${difference.inHours} jam yang lalu';
    } else if (difference.inMinutes > 0) {
      return '${difference.inMinutes} menit yang lalu';
    } else {
      return 'Baru saja';
    }
  }

  // Check if date is today
  bool get isToday {
    final now = DateTime.now();
    return year == now.year && month == now.month && day == now.day;
  }

  // Check if date is yesterday
  bool get isYesterday {
    final yesterday = DateTime.now().subtract(const Duration(days: 1));
    return year == yesterday.year && month == yesterday.month && day == yesterday.day;
  }

  // Get semester name based on month
  String getSemesterName() {
    // Assume odd semesters start in August-September
    // Even semesters start in February-March
    if (month >= 8 || month <= 1) {
      return 'Ganjil ${year + (month >= 8 ? 1 : 0)}/${year + (month >= 8 ? 2 : 1)}';
    } else {
      return 'Genap $year/${year + 1}';
    }
  }

  // Check if it's academic year end (around June-July)
  bool get isAcademicYearEnd {
    return month >= 6 && month <= 7;
  }
}
