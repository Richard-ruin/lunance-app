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
  final DateTime? dateOfBirth;
  final String? occupation;
  final String? city;
  final String? profilePicture;

  UserProfile({
    required this.fullName,
    this.phoneNumber,
    this.dateOfBirth,
    this.occupation,
    this.city,
    this.profilePicture,
  });

  factory UserProfile.fromJson(Map<String, dynamic> json) {
    return UserProfile(
      fullName: json['full_name'] ?? '',
      phoneNumber: json['phone_number'],
      dateOfBirth: json['date_of_birth'] != null 
          ? DateTime.parse(json['date_of_birth']) 
          : null,
      occupation: json['occupation'],
      city: json['city'],
      profilePicture: json['profile_picture'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'full_name': fullName,
      'phone_number': phoneNumber,
      'date_of_birth': dateOfBirth?.toIso8601String(),
      'occupation': occupation,
      'city': city,
      'profile_picture': profilePicture,
    };
  }
}

class UserPreferences {
  final String language;
  final String currency;
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
      language: json['language'] ?? 'id',
      currency: json['currency'] ?? 'IDR',
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
  final double monthlyIncome;
  final double? monthlyBudget;
  final double savingsGoalPercentage;
  final double? emergencyFundTarget;
  final String? primaryBank;
  final List<String> expenseCategories;
  final List<String> incomeCategories;

  FinancialSettings({
    required this.monthlyIncome,
    this.monthlyBudget,
    required this.savingsGoalPercentage,
    this.emergencyFundTarget,
    this.primaryBank,
    required this.expenseCategories,
    required this.incomeCategories,
  });

  factory FinancialSettings.fromJson(Map<String, dynamic> json) {
    return FinancialSettings(
      monthlyIncome: (json['monthly_income'] ?? 0).toDouble(),
      monthlyBudget: json['monthly_budget']?.toDouble(),
      savingsGoalPercentage: (json['savings_goal_percentage'] ?? 20.0).toDouble(),
      emergencyFundTarget: json['emergency_fund_target']?.toDouble(),
      primaryBank: json['primary_bank'],
      expenseCategories: List<String>.from(json['expense_categories'] ?? []),
      incomeCategories: List<String>.from(json['income_categories'] ?? []),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'monthly_income': monthlyIncome,
      'monthly_budget': monthlyBudget,
      'savings_goal_percentage': savingsGoalPercentage,
      'emergency_fund_target': emergencyFundTarget,
      'primary_bank': primaryBank,
      'expense_categories': expenseCategories,
      'income_categories': incomeCategories,
    };
  }
}