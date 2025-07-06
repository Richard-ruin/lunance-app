import '../utils/constants.dart';

class Validators {
  // ======================
  // Email Validators
  // ======================
  
  static String? validateEmail(String? value) {
    if (value == null || value.isEmpty) {
      return ErrorMessages.emailRequired;
    }
    
    if (!RegExp(ValidationPatterns.email).hasMatch(value)) {
      return ErrorMessages.emailInvalid;
    }
    
    return null;
  }

  static String? validateAcademicEmail(String? value) {
    if (value == null || value.isEmpty) {
      return ErrorMessages.emailRequired;
    }
    
    // Check basic email format first
    if (!RegExp(ValidationPatterns.email).hasMatch(value)) {
      return ErrorMessages.emailInvalid;
    }
    
    // Check if it's academic email (.ac.id)
    if (!RegExp(ValidationPatterns.academicEmail).hasMatch(value)) {
      return ErrorMessages.emailAcademicRequired;
    }
    
    return null;
  }

  // ======================
  // Password Validators
  // ======================
  
  static String? validatePassword(String? value) {
    if (value == null || value.isEmpty) {
      return ErrorMessages.passwordRequired;
    }
    
    if (value.length < 8) {
      return ErrorMessages.passwordTooShort;
    }
    
    // Check for strong password pattern
    if (!RegExp(ValidationPatterns.password).hasMatch(value)) {
      return ErrorMessages.passwordWeak;
    }
    
    return null;
  }

  static String? validatePasswordConfirmation(String? value, String? password) {
    if (value == null || value.isEmpty) {
      return ErrorMessages.passwordRequired;
    }
    
    if (value != password) {
      return ErrorMessages.passwordMismatch;
    }
    
    return null;
  }

  // ======================
  // Name Validators
  // ======================
  
  static String? validateName(String? value) {
    if (value == null || value.isEmpty) {
      return ErrorMessages.nameRequired;
    }
    
    if (value.trim().length < 2) {
      return 'Nama minimal 2 karakter';
    }
    
    if (value.trim().length > 100) {
      return 'Nama maksimal 100 karakter';
    }
    
    // Check for valid name characters (letters, spaces, some special chars)
    if (!RegExp(r'^[a-zA-Z\s\.\-\']+$').hasMatch(value)) {
      return 'Nama hanya boleh mengandung huruf, spasi, titik, strip, dan apostrof';
    }
    
    return null;
  }

  // ======================
  // NIM Validators
  // ======================
  
  static String? validateNim(String? value) {
    if (value == null || value.isEmpty) {
      return ErrorMessages.nimRequired;
    }
    
    if (!RegExp(ValidationPatterns.nim).hasMatch(value)) {
      return ErrorMessages.nimInvalid;
    }
    
    return null;
  }

  // ======================
  // Phone Number Validators
  // ======================
  
  static String? validatePhone(String? value) {
    if (value == null || value.isEmpty) {
      return null; // Phone is optional in most cases
    }
    
    if (!RegExp(ValidationPatterns.phone).hasMatch(value)) {
      return 'Format nomor telepon tidak valid';
    }
    
    return null;
  }

  static String? validateRequiredPhone(String? value) {
    if (value == null || value.isEmpty) {
      return 'Nomor telepon wajib diisi';
    }
    
    return validatePhone(value);
  }

  // ======================
  // University Related Validators
  // ======================
  
  static String? validateUniversityName(String? value) {
    if (value == null || value.isEmpty) {
      return 'Nama universitas wajib diisi';
    }
    
    if (value.trim().length < 5) {
      return 'Nama universitas minimal 5 karakter';
    }
    
    if (value.trim().length > 200) {
      return 'Nama universitas maksimal 200 karakter';
    }
    
    return null;
  }

  static String? validateUniversityCode(String? value) {
    if (value == null || value.isEmpty) {
      return 'Kode universitas wajib diisi';
    }
    
    if (!RegExp(ValidationPatterns.universityCode).hasMatch(value)) {
      return 'Kode universitas harus 2-10 huruf besar';
    }
    
    return null;
  }

  static String? validateFacultyName(String? value) {
    if (value == null || value.isEmpty) {
      return 'Nama fakultas wajib diisi';
    }
    
    if (value.trim().length < 3) {
      return 'Nama fakultas minimal 3 karakter';
    }
    
    if (value.trim().length > 150) {
      return 'Nama fakultas maksimal 150 karakter';
    }
    
    return null;
  }

  static String? validateProdiName(String? value) {
    if (value == null || value.isEmpty) {
      return 'Nama program studi wajib diisi';
    }
    
    if (value.trim().length < 3) {
      return 'Nama program studi minimal 3 karakter';
    }
    
    if (value.trim().length > 150) {
      return 'Nama program studi maksimal 150 karakter';
    }
    
    return null;
  }

  // ======================
  // Address Validators
  // ======================
  
  static String? validateAddress(String? value) {
    if (value == null || value.isEmpty) {
      return 'Alamat wajib diisi';
    }
    
    if (value.trim().length < 10) {
      return 'Alamat minimal 10 karakter';
    }
    
    if (value.trim().length > 500) {
      return 'Alamat maksimal 500 karakter';
    }
    
    return null;
  }

  // ======================
  // URL Validators
  // ======================
  
  static String? validateUrl(String? value) {
    if (value == null || value.isEmpty) {
      return null; // URL is usually optional
    }
    
    try {
      final uri = Uri.parse(value);
      if (!uri.hasScheme || (!uri.scheme.startsWith('http'))) {
        return 'URL harus dimulai dengan http:// atau https://';
      }
      return null;
    } catch (e) {
      return 'Format URL tidak valid';
    }
  }

  static String? validateRequiredUrl(String? value) {
    if (value == null || value.isEmpty) {
      return 'URL wajib diisi';
    }
    
    return validateUrl(value);
  }

  // ======================
  // Dropdown/Selection Validators
  // ======================
  
  static String? validateRequired(String? value, String fieldName) {
    if (value == null || value.isEmpty) {
      return '$fieldName wajib dipilih';
    }
    return null;
  }

  static String? validateUniversity(String? value) {
    return validateRequired(value, 'Universitas');
  }

  static String? validateFaculty(String? value) {
    return validateRequired(value, 'Fakultas');
  }

  static String? validateProdi(String? value) {
    return validateRequired(value, 'Program Studi');
  }

  static String? validateDegreeType(String? value) {
    return validateRequired(value, 'Jenjang Pendidikan');
  }

  // ======================
  // Financial Validators (Future Implementation)
  // ======================
  
  static String? validateAmount(String? value) {
    if (value == null || value.isEmpty) {
      return 'Jumlah wajib diisi';
    }
    
    // Remove currency formatting
    final cleanValue = value.replaceAll(RegExp(r'[Rp\s\.]'), '').replaceAll(',', '.');
    
    final amount = double.tryParse(cleanValue);
    if (amount == null) {
      return 'Format jumlah tidak valid';
    }
    
    if (amount <= 0) {
      return 'Jumlah harus lebih dari 0';
    }
    
    if (amount > 999999999999) {
      return 'Jumlah terlalu besar';
    }
    
    return null;
  }

  static String? validateBudgetAmount(String? value) {
    final amountValidation = validateAmount(value);
    if (amountValidation != null) return amountValidation;
    
    // Additional budget-specific validation
    final cleanValue = value!.replaceAll(RegExp(r'[Rp\s\.]'), '').replaceAll(',', '.');
    final amount = double.parse(cleanValue);
    
    if (amount < 1000) {
      return 'Anggaran minimal Rp 1.000';
    }
    
    return null;
  }

  // ======================
  // Date Validators
  // ======================
  
  static String? validateDate(DateTime? value) {
    if (value == null) {
      return 'Tanggal wajib dipilih';
    }
    
    return null;
  }

  static String? validateBirthDate(DateTime? value) {
    if (value == null) {
      return 'Tanggal lahir wajib dipilih';
    }
    
    final now = DateTime.now();
    final age = now.year - value.year;
    
    if (age < 16) {
      return 'Umur minimal 16 tahun';
    }
    
    if (age > 100) {
      return 'Umur tidak valid';
    }
    
    return null;
  }

  static String? validateFutureDate(DateTime? value) {
    if (value == null) {
      return 'Tanggal wajib dipilih';
    }
    
    final now = DateTime.now();
    if (value.isBefore(now)) {
      return 'Tanggal harus di masa depan';
    }
    
    return null;
  }

  static String? validatePastDate(DateTime? value) {
    if (value == null) {
      return 'Tanggal wajib dipilih';
    }
    
    final now = DateTime.now();
    if (value.isAfter(now)) {
      return 'Tanggal harus di masa lalu';
    }
    
    return null;
  }

  // ======================
  // File Validators
  // ======================
  
  static String? validateImageFile(String? filePath) {
    if (filePath == null || filePath.isEmpty) {
      return 'File gambar wajib dipilih';
    }
    
    final extension = filePath.split('.').last.toLowerCase();
    if (!['jpg', 'jpeg', 'png', 'webp'].contains(extension)) {
      return 'Format file harus JPG, PNG, atau WebP';
    }
    
    return null;
  }

  static String? validateDocumentFile(String? filePath) {
    if (filePath == null || filePath.isEmpty) {
      return 'File dokumen wajib dipilih';
    }
    
    final extension = filePath.split('.').last.toLowerCase();
    if (!['pdf', 'doc', 'docx'].contains(extension)) {
      return 'Format file harus PDF, DOC, atau DOCX';
    }
    
    return null;
  }

  // ======================
  // Text Validators
  // ======================
  
  static String? validateDescription(String? value) {
    if (value == null || value.isEmpty) {
      return null; // Description is usually optional
    }
    
    if (value.trim().length > 1000) {
      return 'Deskripsi maksimal 1000 karakter';
    }
    
    return null;
  }

  static String? validateRequiredDescription(String? value) {
    if (value == null || value.isEmpty) {
      return 'Deskripsi wajib diisi';
    }
    
    if (value.trim().length < 10) {
      return 'Deskripsi minimal 10 karakter';
    }
    
    return validateDescription(value);
  }

  static String? validateNotes(String? value) {
    if (value == null || value.isEmpty) {
      return null; // Notes are optional
    }
    
    if (value.trim().length > 500) {
      return 'Catatan maksimal 500 karakter';
    }
    
    return null;
  }

  // ======================
  // Numeric Validators
  // ======================
  
  static String? validateInteger(String? value, {int? min, int? max}) {
    if (value == null || value.isEmpty) {
      return 'Angka wajib diisi';
    }
    
    final number = int.tryParse(value);
    if (number == null) {
      return 'Format angka tidak valid';
    }
    
    if (min != null && number < min) {
      return 'Angka minimal $min';
    }
    
    if (max != null && number > max) {
      return 'Angka maksimal $max';
    }
    
    return null;
  }

  static String? validateDouble(String? value, {double? min, double? max}) {
    if (value == null || value.isEmpty) {
      return 'Angka wajib diisi';
    }
    
    final number = double.tryParse(value);
    if (number == null) {
      return 'Format angka tidak valid';
    }
    
    if (min != null && number < min) {
      return 'Angka minimal $min';
    }
    
    if (max != null && number > max) {
      return 'Angka maksimal $max';
    }
    
    return null;
  }

  // ======================
  // Combined Validators
  // ======================
  
  static String? validateEmailOrPhone(String? value) {
    if (value == null || value.isEmpty) {
      return 'Email atau nomor telepon wajib diisi';
    }
    
    // Check if it's email format
    if (value.contains('@')) {
      return validateEmail(value);
    } else {
      return validatePhone(value);
    }
  }

  // ======================
  // Custom Business Logic Validators
  // ======================
  
  static String? validateUniversityRequest(Map<String, dynamic> data) {
    final errors = <String>[];
    
    if (validateUniversityName(data['university_name']) != null) {
      errors.add('Nama universitas tidak valid');
    }
    
    if (validateUniversityCode(data['university_code']) != null) {
      errors.add('Kode universitas tidak valid');
    }
    
    if (validateAddress(data['university_address']) != null) {
      errors.add('Alamat universitas tidak valid');
    }
    
    if (validateName(data['requester_name']) != null) {
      errors.add('Nama pemohon tidak valid');
    }
    
    if (validateAcademicEmail(data['email']) != null) {
      errors.add('Email akademik tidak valid');
    }
    
    if (validateNim(data['nim']) != null) {
      errors.add('NIM tidak valid');
    }
    
    if (errors.isNotEmpty) {
      return errors.join(', ');
    }
    
    return null;
  }

  // ======================
  // Utility Methods
  // ======================
  
  static bool isValidEmail(String email) {
    return validateEmail(email) == null;
  }
  
  static bool isValidAcademicEmail(String email) {
    return validateAcademicEmail(email) == null;
  }
  
  static bool isValidPassword(String password) {
    return validatePassword(password) == null;
  }
  
  static bool isValidNim(String nim) {
    return validateNim(nim) == null;
  }
  
  static bool isValidPhone(String phone) {
    return validatePhone(phone) == null;
  }
  
  static bool isValidUrl(String url) {
    return validateUrl(url) == null;
  }

  // ======================
  // Form Validation Helpers
  // ======================
  
  static Map<String, String?> validateLoginForm({
    required String email,
    required String password,
  }) {
    return {
      'email': validateAcademicEmail(email),
      'password': validatePassword(password),
    };
  }

  static Map<String, String?> validateRegisterForm({
    required String name,
    required String email,
    required String nim,
    required String password,
    required String confirmPassword,
    required String university,
    required String faculty,
    required String prodi,
  }) {
    return {
      'name': validateName(name),
      'email': validateAcademicEmail(email),
      'nim': validateNim(nim),
      'password': validatePassword(password),
      'confirm_password': validatePasswordConfirmation(confirmPassword, password),
      'university': validateUniversity(university),
      'faculty': validateFaculty(faculty),
      'prodi': validateProdi(prodi),
    };
  }

  static Map<String, String?> validateUniversityRequestForm({
    required String universityName,
    required String universityCode,
    required String universityAddress,
    String? universityWebsite,
    required String requesterName,
    required String email,
    required String nim,
  }) {
    return {
      'university_name': validateUniversityName(universityName),
      'university_code': validateUniversityCode(universityCode),
      'university_address': validateAddress(universityAddress),
      'university_website': universityWebsite?.isNotEmpty == true 
          ? validateUrl(universityWebsite) : null,
      'requester_name': validateName(requesterName),
      'email': validateAcademicEmail(email),
      'nim': validateNim(nim),
    };
  }

  // ======================
  // Real-time Validation Helpers
  // ======================
  
  static bool hasFormErrors(Map<String, String?> validationResults) {
    return validationResults.values.any((error) => error != null);
  }
  
  static List<String> getFormErrors(Map<String, String?> validationResults) {
    return validationResults.values
        .where((error) => error != null)
        .cast<String>()
        .toList();
  }
  
  static String? getFirstFormError(Map<String, String?> validationResults) {
    for (final error in validationResults.values) {
      if (error != null) return error;
    }
    return null;
  }
}