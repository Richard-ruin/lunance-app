import 'package:flutter/foundation.dart';
import '../models/user_model.dart';
import '../services/api_service.dart';

enum AuthState {
  initial,
  loading,
  authenticated,
  unauthenticated,
  error,
}

class AuthProvider with ChangeNotifier {
  final ApiService _apiService = ApiService();

  AuthState _state = AuthState.initial;
  User? _user;
  String? _errorMessage;
  bool _isLoading = false;

  // Additional 50/30/20 specific data
  Map<String, dynamic>? _financialOverview;
  Map<String, dynamic>? _budgetStatus;
  List<String> _studentTips = [];

  // Getters
  AuthState get state => _state;
  User? get user => _user;
  String? get errorMessage => _errorMessage;
  bool get isLoading => _isLoading;
  bool get isAuthenticated =>
      _state == AuthState.authenticated && _user != null;
  bool get needsProfileSetup => _user != null && !_user!.profileSetupCompleted;
  bool get needsFinancialSetup =>
      _user != null && !_user!.financialSetupCompleted;
  bool get isOnboardingComplete => _user != null && _user!.onboardingCompleted;

  // 50/30/20 specific getters
  Map<String, dynamic>? get financialOverview => _financialOverview;
  Map<String, dynamic>? get budgetStatus => _budgetStatus;
  List<String> get studentTips => _studentTips;
  bool get hasBudgetSetup => _user?.financialSettings != null;

  // Initialize auth state
  Future<void> initialize() async {
    _setLoading(true);

    try {
      final token = await _apiService.getAccessToken();
      if (token != null) {
        await getCurrentUser();
      } else {
        _setState(AuthState.unauthenticated);
      }
    } catch (e) {
      _setState(AuthState.unauthenticated);
    } finally {
      _setLoading(false);
    }
  }

  // Register user
  Future<bool> register({
    required String username,
    required String email,
    required String password,
    required String confirmPassword,
  }) async {
    _setLoading(true);
    _clearError();

    try {
      final response = await _apiService.register(
        username: username,
        email: email,
        password: password,
        confirmPassword: confirmPassword,
      );

      if (response['success'] == true) {
        _setLoading(false);
        return true;
      } else {
        _setError(response['message'] ?? 'Registration failed');
        return false;
      }
    } catch (e) {
      _setError('Registration failed: ${e.toString()}');
      return false;
    } finally {
      _setLoading(false);
    }
  }

  // Login user
  Future<bool> login({
    required String email,
    required String password,
  }) async {
    _setLoading(true);
    _clearError();

    try {
      final response = await _apiService.login(
        email: email,
        password: password,
      );

      if (response['success'] == true) {
        final userData = response['data']['user'];
        _user = User.fromJson(userData);

        // Load financial data if available
        if (response['data']['financial_overview'] != null) {
          _financialOverview = response['data']['financial_overview'];
        }
        if (response['data']['budget_status'] != null) {
          _budgetStatus = response['data']['budget_status'];
        }

        _setState(AuthState.authenticated);
        return true;
      } else {
        _setError(response['message'] ?? 'Login failed');
        return false;
      }
    } catch (e) {
      _setError('Login failed: ${e.toString()}');
      return false;
    } finally {
      _setLoading(false);
    }
  }

  // Get current user
  Future<void> getCurrentUser() async {
    try {
      final response = await _apiService.getCurrentUser();

      if (response['success'] == true) {
        final userData = response['data']['user'];
        _user = User.fromJson(userData);

        // Load additional data if available
        if (response['data']['financial_overview'] != null) {
          _financialOverview = response['data']['financial_overview'];
        }
        if (response['data']['budget_status'] != null) {
          _budgetStatus = response['data']['budget_status'];
        }
        if (response['data']['student_context'] != null) {
          _studentTips = List<String>.from(
              response['data']['student_context']['student_tips'] ?? []);
        }

        _setState(AuthState.authenticated);
      } else {
        await logout();
      }
    } catch (e) {
      await logout();
    }
  }

  // Setup profile - Updated for Indonesian students
  Future<bool> setupProfile({
    required String fullName,
    String? phoneNumber,
    required String university, // Required field for university
    required String city, // Required field for city/district
    String? occupation, // Optional side job
    bool notificationsEnabled = true,
    bool voiceEnabled = true,
    bool darkMode = false,
  }) async {
    _setLoading(true);
    _clearError();

    try {
      final response = await _apiService.setupProfile(
        fullName: fullName,
        phoneNumber: phoneNumber,
        university: university,
        city: city,
        occupation: occupation,
        notificationsEnabled: notificationsEnabled,
        voiceEnabled: voiceEnabled,
        darkMode: darkMode,
      );

      if (response['success'] == true) {
        final userData = response['data']['user'];
        _user = User.fromJson(userData);
        notifyListeners();
        return true;
      } else {
        _setError(response['message'] ?? 'Profile setup failed');
        return false;
      }
    } catch (e) {
      _setError('Profile setup failed: ${e.toString()}');
      return false;
    } finally {
      _setLoading(false);
    }
  }

  // Setup financial with 50/30/20 method
  Future<bool> setupFinancial50302({
    required double currentSavings,
    required double monthlyIncome,
    required String primaryBank,
  }) async {
    _setLoading(true);
    _clearError();

    try {
      final response = await _apiService.setupFinancial50302(
        currentSavings: currentSavings,
        monthlyIncome: monthlyIncome,
        primaryBank: primaryBank,
      );

      if (response['success'] == true) {
        final userData = response['data']['user'];
        _user = User.fromJson(userData);

        // Store financial overview and budget allocation
        if (response['data']['financial_overview'] != null) {
          _financialOverview = response['data']['financial_overview'];
        }
        if (response['data']['budget_allocation'] != null) {
          _budgetStatus = response['data']['budget_allocation'];
        }

        notifyListeners();
        return true;
      } else {
        _setError(response['message'] ?? 'Financial setup failed');
        return false;
      }
    } catch (e) {
      _setError('Financial setup failed: ${e.toString()}');
      return false;
    } finally {
      _setLoading(false);
    }
  }

  // Update financial settings
  Future<bool> updateFinancialSettings({
    double? currentSavings,
    double? monthlyIncome,
    String? primaryBank,
  }) async {
    _setLoading(true);
    _clearError();

    try {
      final response = await _apiService.updateFinancialSettings(
        currentSavings: currentSavings,
        monthlyIncome: monthlyIncome,
        primaryBank: primaryBank,
      );

      if (response['success'] == true) {
        final userData = response['data']['user'];
        _user = User.fromJson(userData);

        // Update financial overview and budget allocation
        if (response['data']['financial_overview'] != null) {
          _financialOverview = response['data']['financial_overview'];
        }
        if (response['data']['budget_allocation'] != null) {
          _budgetStatus = response['data']['budget_allocation'];
        }

        notifyListeners();
        return true;
      } else {
        _setError(response['message'] ?? 'Update failed');
        return false;
      }
    } catch (e) {
      _setError('Update failed: ${e.toString()}');
      return false;
    } finally {
      _setLoading(false);
    }
  }

  // Get financial overview
  Future<void> loadFinancialOverview() async {
    try {
      final response = await _apiService.getFinancialOverview();

      if (response['success'] == true) {
        _financialOverview = response['data'];
        notifyListeners();
      }
    } catch (e) {
      debugPrint('Failed to load financial overview: $e');
    }
  }

  // Get budget status
  Future<void> loadBudgetStatus() async {
    try {
      final response = await _apiService.getBudgetStatus();

      if (response['success'] == true) {
        _budgetStatus = response['data'];
        notifyListeners();
      }
    } catch (e) {
      debugPrint('Failed to load budget status: $e');
    }
  }

  // Get student financial tips
  Future<void> loadStudentTips() async {
    try {
      final response = await _apiService.getStudentFinancialTips();

      if (response['success'] == true) {
        _studentTips = List<String>.from(response['data']['tips'] ?? []);
        notifyListeners();
      }
    } catch (e) {
      debugPrint('Failed to load student tips: $e');
    }
  }

  // Reset monthly budget
  Future<bool> resetMonthlyBudget() async {
    _setLoading(true);

    try {
      final response = await _apiService.resetMonthlyBudget();

      if (response['success'] == true) {
        // Reload budget status after reset
        await loadBudgetStatus();
        return true;
      } else {
        _setError(response['message'] ?? 'Failed to reset budget');
        return false;
      }
    } catch (e) {
      _setError('Failed to reset budget: ${e.toString()}');
      return false;
    } finally {
      _setLoading(false);
    }
  }

  // Get budget categories
  Future<Map<String, dynamic>?> getBudgetCategories() async {
    try {
      final response = await _apiService.getBudgetCategories();

      if (response['success'] == true) {
        return response['data'];
      }
      return null;
    } catch (e) {
      debugPrint('Failed to get budget categories: $e');
      return null;
    }
  }

  // Get onboarding status
  Future<Map<String, dynamic>?> getOnboardingStatus() async {
    try {
      final response = await _apiService.getOnboardingStatus();

      if (response['success'] == true) {
        return response['data'];
      }
      return null;
    } catch (e) {
      debugPrint('Failed to get onboarding status: $e');
      return null;
    }
  }

  // Update profile
  Future<bool> updateProfile({
    String? fullName,
    String? phoneNumber,
    String? university,
    String? city,
    String? occupation,
    bool? notificationsEnabled,
    bool? voiceEnabled,
    bool? darkMode,
    bool? autoCategorization,
  }) async {
    _setLoading(true);
    _clearError();

    try {
      final response = await _apiService.updateProfile(
        fullName: fullName,
        phoneNumber: phoneNumber,
        university: university,
        city: city,
        occupation: occupation,
        notificationsEnabled: notificationsEnabled,
        voiceEnabled: voiceEnabled,
        darkMode: darkMode,
        autoCategorization: autoCategorization,
      );

      if (response['success'] == true) {
        final userData = response['data']['user'];
        _user = User.fromJson(userData);
        notifyListeners();
        return true;
      } else {
        _setError(response['message'] ?? 'Update profile failed');
        return false;
      }
    } catch (e) {
      _setError('Update profile failed: ${e.toString()}');
      return false;
    } finally {
      _setLoading(false);
    }
  }

  // Change password
  Future<bool> changePassword({
    required String currentPassword,
    required String newPassword,
    required String confirmPassword,
  }) async {
    _setLoading(true);
    _clearError();

    try {
      final response = await _apiService.changePassword(
        currentPassword: currentPassword,
        newPassword: newPassword,
        confirmPassword: confirmPassword,
      );

      if (response['success'] == true) {
        // User will be logged out from all devices after password change
        await logout();
        return true;
      } else {
        _setError(response['message'] ?? 'Change password failed');
        return false;
      }
    } catch (e) {
      _setError('Change password failed: ${e.toString()}');
      return false;
    } finally {
      _setLoading(false);
    }
  }

  // Logout user
  Future<void> logout() async {
    _setLoading(true);

    try {
      await _apiService.logout();
    } catch (e) {
      // Even if logout API fails, clear local data
      debugPrint('Logout API failed: $e');
    }

    await _apiService.clearTokens();
    _user = null;
    _financialOverview = null;
    _budgetStatus = null;
    _studentTips.clear();
    _setState(AuthState.unauthenticated);
    _setLoading(false);
  }

  // Get budget allocation for current user
  Map<String, dynamic>? getBudgetAllocation() {
    if (_user?.financialSettings == null) return null;

    final monthlyIncome = _user!.financialSettings!.monthlyIncome;
    return {
      'monthly_income': monthlyIncome!,
      'needs_budget': monthlyIncome * 0.5,
      'wants_budget': monthlyIncome * 0.3,
      'savings_budget': monthlyIncome * 0.2,
      'method': '50/30/20 Elizabeth Warren',
    };
  }

  // Check if user has healthy budget
  bool hasHealthyBudget() {
    if (_budgetStatus == null) return false;

    final budgetHealth = _budgetStatus!['budget_health'];
    return budgetHealth == 'excellent' || budgetHealth == 'good';
  }

  // Get financial health level
  String getFinancialHealthLevel() {
    if (_budgetStatus == null) return 'unknown';
    return _budgetStatus!['budget_health'] ?? 'unknown';
  }

  // Refresh all financial data
  Future<void> refreshFinancialData() async {
    await loadFinancialOverview();
    await loadBudgetStatus();
    await loadStudentTips();
  }

  // Private helper methods
  void _setState(AuthState state) {
    _state = state;
    notifyListeners();
  }

  void _setLoading(bool loading) {
    _isLoading = loading;
    notifyListeners();
  }

  void _setError(String message) {
    _errorMessage = message;
    _setState(AuthState.error);
  }

  void _clearError() {
    _errorMessage = null;
  }

  // Clear error
  void clearError() {
    _clearError();
    notifyListeners();
  }
}
