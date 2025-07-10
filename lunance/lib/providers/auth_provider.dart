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

  // Getters
  AuthState get state => _state;
  User? get user => _user;
  String? get errorMessage => _errorMessage;
  bool get isLoading => _isLoading;
  bool get isAuthenticated => _state == AuthState.authenticated && _user != null;
  bool get needsProfileSetup => _user != null && !_user!.profileSetupCompleted;
  bool get needsFinancialSetup => _user != null && !_user!.financialSetupCompleted;
  bool get isOnboardingComplete => _user != null && _user!.onboardingCompleted;

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
        _setState(AuthState.authenticated);
      } else {
        await logout();
      }
    } catch (e) {
      await logout();
    }
  }

  // Setup profile
  Future<bool> setupProfile({
    required String fullName,
    String? phoneNumber,
    DateTime? dateOfBirth,
    String? occupation,
    String? city,
    String language = 'id',
    String currency = 'IDR',
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
        dateOfBirth: dateOfBirth,
        occupation: occupation,
        city: city,
        language: language,
        currency: currency,
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

  // Setup financial
  Future<bool> setupFinancial({
    required double monthlyIncome,
    double? monthlyBudget,
    double savingsGoalPercentage = 20.0,
    double? emergencyFundTarget,
    String? primaryBank,
  }) async {
    _setLoading(true);
    _clearError();

    try {
      final response = await _apiService.setupFinancial(
        monthlyIncome: monthlyIncome,
        monthlyBudget: monthlyBudget,
        savingsGoalPercentage: savingsGoalPercentage,
        emergencyFundTarget: emergencyFundTarget,
        primaryBank: primaryBank,
      );

      if (response['success'] == true) {
        final userData = response['data']['user'];
        _user = User.fromJson(userData);
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
    _setState(AuthState.unauthenticated);
    _setLoading(false);
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