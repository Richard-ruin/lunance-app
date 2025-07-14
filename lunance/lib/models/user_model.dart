class User {
  final String id;
  final String username;
  final String email;
  final UserProfile? profile;
  final UserPreferences preferences;
  final FinancialSettings? financialSettings;
  final bool isActive;
  final bool isVerified;
  final bool isPremium;
  final bool profileSetupCompleted;
  final bool financialSetupCompleted;
  final bool onboardingCompleted;
  final DateTime createdAt;
  final DateTime? lastLogin;

  User({
    required this.id,
    required this.username,
    required this.email,
    this.profile,
    required this.preferences,
    this.financialSettings,
    required this.isActive,
    required this.isVerified,
    required this.isPremium,
    required this.profileSetupCompleted,
    required this.financialSetupCompleted,
    required this.onboardingCompleted,
    required this.createdAt,
    this.lastLogin,
  });

  factory User.fromJson(Map<String, dynamic> json) {
    return User(
      id: json['id'] ?? '',
      username: json['username'] ?? '',
      email: json['email'] ?? '',
      profile: json['profile'] != null ? UserProfile.fromJson(json['profile']) : null,
      preferences: UserPreferences.fromJson(json['preferences'] ?? {}),
      financialSettings: json['financial_settings'] != null 
          ? FinancialSettings.fromJson(json['financial_settings']) 
          : null,
      isActive: json['is_active'] ?? false,
      isVerified: json['is_verified'] ?? false,
      isPremium: json['is_premium'] ?? false,
      profileSetupCompleted: json['profile_setup_completed'] ?? false,
      financialSetupCompleted: json['financial_setup_completed'] ?? false,
      onboardingCompleted: json['onboarding_completed'] ?? false,
      createdAt: DateTime.parse(json['created_at'] ?? DateTime.now().toIso8601String()),
      lastLogin: json['last_login'] != null ? DateTime.parse(json['last_login']) : null,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'username': username,
      'email': email,
      'profile': profile?.toJson(),
      'preferences': preferences.toJson(),
      'financial_settings': financialSettings?.toJson(),
      'is_active': isActive,
      'is_verified': isVerified,
      'is_premium': isPremium,
      'profile_setup_completed': profileSetupCompleted,
      'financial_setup_completed': financialSetupCompleted,
      'onboarding_completed': onboardingCompleted,
      'created_at': createdAt.toIso8601String(),
      'last_login': lastLogin?.toIso8601String(),
    };
  }
}

class UserProfile {
  final String fullName;
  final String? phoneNumber;
  final String? university;  // Field baru untuk universitas
  final String? city;  // Kota/kecamatan tempat tinggal
  final String? occupation;  // Pekerjaan sampingan (opsional)
  final String? profilePicture;

  UserProfile({
    required this.fullName,
    this.phoneNumber,
    this.university,
    this.city,
    this.occupation,
    this.profilePicture,
  });

  factory UserProfile.fromJson(Map<String, dynamic> json) {
    return UserProfile(
      fullName: json['full_name'] ?? '',
      phoneNumber: json['phone_number'],
      university: json['university'],  // Field universitas
      city: json['city'],
      occupation: json['occupation'],
      profilePicture: json['profile_picture'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'full_name': fullName,
      'phone_number': phoneNumber,
      'university': university,  // Field universitas
      'city': city,
      'occupation': occupation,
      'profile_picture': profilePicture,
    };
  }
}

class UserPreferences {
  final String language;  // Fixed ke "id" untuk Bahasa Indonesia
  final String currency;  // Fixed ke "IDR" untuk Rupiah
  final String dateFormat;
  final String timeFormat;
  final bool notificationsEnabled;
  final bool voiceEnabled;
  final bool darkMode;
  final bool autoCategorization;

  UserPreferences({
    required this.language,
    required this.currency,
    required this.dateFormat,
    required this.timeFormat,
    required this.notificationsEnabled,
    required this.voiceEnabled,
    required this.darkMode,
    required this.autoCategorization,
  });

  factory UserPreferences.fromJson(Map<String, dynamic> json) {
    return UserPreferences(
      language: json['language'] ?? 'id',  // Default Bahasa Indonesia
      currency: json['currency'] ?? 'IDR',  // Default Rupiah
      dateFormat: json['date_format'] ?? 'DD/MM/YYYY',
      timeFormat: json['time_format'] ?? '24h',
      notificationsEnabled: json['notifications_enabled'] ?? true,
      voiceEnabled: json['voice_enabled'] ?? true,
      darkMode: json['dark_mode'] ?? false,
      autoCategorization: json['auto_categorization'] ?? true,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'language': language,
      'currency': currency,
      'date_format': dateFormat,
      'time_format': timeFormat,
      'notifications_enabled': notificationsEnabled,
      'voice_enabled': voiceEnabled,
      'dark_mode': darkMode,
      'auto_categorization': autoCategorization,
    };
  }
}
class FinancialSettings {
  final double currentSavings;  // Total tabungan saat ini
  final double monthlySavingsTarget;  // Target tabungan bulanan
  final double emergencyFund;  // Dana darurat saat ini
  final String primaryBank;  // Bank atau e-wallet utama
  final List<String> expenseCategories;
  final List<String> incomeCategories;

  FinancialSettings({
    required this.currentSavings,
    required this.monthlySavingsTarget,
    required this.emergencyFund,
    required this.primaryBank,
    required this.expenseCategories,
    required this.incomeCategories,
  });

  factory FinancialSettings.fromJson(Map<String, dynamic> json) {
    return FinancialSettings(
      currentSavings: (json['current_savings'] ?? 0).toDouble(),
      monthlySavingsTarget: (json['monthly_savings_target'] ?? 0).toDouble(),
      emergencyFund: (json['emergency_fund'] ?? 0).toDouble(),
      primaryBank: json['primary_bank'] ?? '',
      expenseCategories: List<String>.from(json['expense_categories'] ?? [
        "Makanan & Minuman",
        "Transportasi", 
        "Buku & Alat Tulis",
        "Hiburan",
        "Kesehatan",
        "Kos/Tempat Tinggal",
        "Internet & Pulsa",
        "Lainnya"
      ]),
      incomeCategories: List<String>.from(json['income_categories'] ?? [
        "Uang Saku/Kiriman Ortu",
        "Part-time Job",
        "Freelance",
        "Beasiswa",
        "Lainnya"
      ]),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'current_savings': currentSavings,
      'monthly_savings_target': monthlySavingsTarget,
      'emergency_fund': emergencyFund,
      'primary_bank': primaryBank,
      'expense_categories': expenseCategories,
      'income_categories': incomeCategories,
    };
  }
}