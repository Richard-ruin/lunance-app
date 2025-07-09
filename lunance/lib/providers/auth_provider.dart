// lib/providers/auth_provider.dart
import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../models/user_model.dart';
import '../models/auth_response_model.dart';
import '../services/auth_service.dart';
import '../utils/constants.dart';
import '../utils/routes.dart';
import '../widgets/common/snackbar_helper.dart';
import '../providers/university_provider.dart';
import '../providers/category_provider.dart';
import '../providers/transaction_provider.dart';
import '../providers/university_request_provider.dart';
import 'package:provider/provider.dart';

enum AuthState { initial, loading, authenticated, unauthenticated }

class AuthProvider extends ChangeNotifier {
  AuthState _authState = AuthState.initial;
  User? _user;
  AuthTokens? _tokens;
  String _errorMessage = '';

  // Getters
  AuthState get authState => _authState;
  User? get user => _user;
  AuthTokens? get tokens => _tokens;
  String? get accessToken => _tokens?.accessToken;
  String? get refreshToken => _tokens?.refreshToken;
  String get errorMessage => _errorMessage;
  bool get isAuthenticated => _authState == AuthState.authenticated;
  bool get isLoading => _authState == AuthState.loading;

  AuthProvider() {
    _initializeAuth();
  }

  Future<void> _initializeAuth() async {
    _setAuthState(AuthState.loading);
    await _loadUserData();
    
    if (_tokens?.accessToken != null && _user != null) {
      // Skip token validation during initialization to avoid 401 issues
      // Just check if we have stored data
      debugPrint('Found stored auth data, setting authenticated state');
      debugPrint('Stored user role: ${_user?.role}');
      _setAuthState(AuthState.authenticated);
    } else {
      debugPrint('No stored auth data found');
      _setAuthState(AuthState.unauthenticated);
    }
  }

  Future<void> _loadUserData() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      
      final accessToken = prefs.getString(AppConstants.accessTokenKey);
      final refreshToken = prefs.getString(AppConstants.refreshTokenKey);
      
      if (accessToken != null && refreshToken != null) {
        _tokens = AuthTokens(
          accessToken: accessToken,
          refreshToken: refreshToken,
          tokenType: 'bearer',
          expiresIn: 3600,
          refreshExpiresIn: 2592000,
        );
      }
      
      final userDataString = prefs.getString(AppConstants.userDataKey);
      if (userDataString != null) {
        final userData = jsonDecode(userDataString);
        _user = User.fromJson(userData);
        debugPrint('Loaded user data: ${_user?.toJson()}');
      }
    } catch (e) {
      debugPrint('Error loading user data: $e');
    }
  }

  Future<bool> _validateStoredToken() async {
    if (_tokens?.accessToken == null) return false;
    
    try {
      final response = await AuthService.validateToken(_tokens!.accessToken);
      return response.success;
    } catch (e) {
      debugPrint('Error validating token: $e');
      return false;
    }
  }

  Future<void> _saveAuthData({
    required User user,
    required AuthTokens tokens,
  }) async {
    try {
      final prefs = await SharedPreferences.getInstance();
      
      await prefs.setString(AppConstants.accessTokenKey, tokens.accessToken);
      await prefs.setString(AppConstants.refreshTokenKey, tokens.refreshToken);
      await prefs.setString(AppConstants.userDataKey, jsonEncode(user.toJson()));
      
      _user = user;
      _tokens = tokens;
      
      debugPrint('Saved auth data for user: ${user.fullName}, role: ${user.role}');
    } catch (e) {
      debugPrint('Error saving auth data: $e');
    }
  }

  Future<void> _clearAuthData() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      
      await prefs.remove(AppConstants.accessTokenKey);
      await prefs.remove(AppConstants.refreshTokenKey);
      await prefs.remove(AppConstants.userDataKey);
      
      _user = null;
      _tokens = null;
      
      debugPrint('Cleared auth data');
    } catch (e) {
      debugPrint('Error clearing auth data: $e');
    }
  }

  void _setAuthState(AuthState state) {
    _authState = state;
    notifyListeners();
  }

  void _setError(String message) {
    _errorMessage = message;
    notifyListeners();
  }

  void clearError() {
    _errorMessage = '';
    notifyListeners();
  }

  // Helper method to normalize role for comparison
  String _normalizeRole(String role) {
    return role.toLowerCase().trim();
  }

  // Helper method to check if user is admin
  bool get isAdmin {
    if (_user?.role == null) return false;
    return _normalizeRole(_user!.role) == 'admin';
  }

  // Helper method to check if user is student
  bool get isStudent {
    if (_user?.role == null) return false;
    return _normalizeRole(_user!.role) == 'student';
  }

  Future<bool> login({
    required String email,
    required String password,
    bool rememberMe = false,
  }) async {
    _setAuthState(AuthState.loading);
    clearError();
    
    try {
      final response = await AuthService.login(
        email: email,
        password: password,
        rememberMe: rememberMe,
      );
      
      debugPrint('Login response: ${response.toJson()}');
      debugPrint('Response success: ${response.success}');
      debugPrint('Response user: ${response.user?.toJson()}');
      debugPrint('Response tokens: ${response.tokens?.toJson()}');
      
      if (response.success && response.user != null && response.tokens != null) {
        await _saveAuthData(
          user: response.user!,
          tokens: response.tokens!,
        );
        
        _setAuthState(AuthState.authenticated);
        
        debugPrint('User role after login: ${response.user!.role}');
        debugPrint('Normalized role: ${_normalizeRole(response.user!.role)}');
        debugPrint('Is admin: ${isAdmin}');
        debugPrint('Is student: ${isStudent}');
        
        return true;
      } else {
        debugPrint('Login failed: ${response.message}');
        _setError(response.message);
        _setAuthState(AuthState.unauthenticated);
        return false;
      }
    } catch (e) {
      debugPrint('Login error: $e');
      _setError('Login gagal: ${e.toString()}');
      _setAuthState(AuthState.unauthenticated);
      return false;
    }
  }

  Future<bool> register({
    required String email,
    required String password,
    required String confirmPassword,
    required String fullName,
    required String phoneNumber,
    required String universityId,
    required String facultyId,
    required String majorId,
    double? initialSavings,
    required String otpCode,
  }) async {
    _setAuthState(AuthState.loading);
    clearError();
    
    try {
      final registerRequest = RegisterRequest(
        email: email,
        password: password,
        confirmPassword: confirmPassword,
        fullName: fullName,
        phoneNumber: phoneNumber,
        universityId: universityId,
        facultyId: facultyId,
        majorId: majorId,
        initialSavings: initialSavings,
        otpCode: otpCode,
      );
      
      final response = await AuthService.register(registerRequest);
      
      if (response.success && response.user != null && response.tokens != null) {
        await _saveAuthData(
          user: response.user!,
          tokens: response.tokens!,
        );
        
        _setAuthState(AuthState.authenticated);
        return true;
      } else {
        _setError(response.message);
        _setAuthState(AuthState.unauthenticated);
        return false;
      }
    } catch (e) {
      debugPrint('Registration error: $e');
      _setError('Registrasi gagal: ${e.toString()}');
      _setAuthState(AuthState.unauthenticated);
      return false;
    }
  }

  Future<bool> sendRegistrationOTP(String email) async {
    clearError();
    
    try {
      final response = await AuthService.sendRegistrationOTP(email);
      
      if (!response.success) {
        _setError(response.message);
      }
      
      return response.success;
    } catch (e) {
      debugPrint('Send registration OTP error: $e');
      _setError('Gagal mengirim OTP: ${e.toString()}');
      return false;
    }
  }

  Future<bool> sendForgotPasswordOTP(String email) async {
    clearError();
    
    try {
      final response = await AuthService.forgotPassword(email);
      
      if (!response.success) {
        _setError(response.message);
      }
      
      return response.success;
    } catch (e) {
      debugPrint('Send forgot password OTP error: $e');
      _setError('Gagal mengirim OTP: ${e.toString()}');
      return false;
    }
  }

  Future<bool> resetPassword({
    required String email,
    required String otpCode,
    required String newPassword,
    required String confirmNewPassword,
  }) async {
    clearError();
    
    try {
      final resetRequest = ResetPasswordRequest(
        email: email,
        otpCode: otpCode,
        newPassword: newPassword,
        confirmNewPassword: confirmNewPassword,
      );
      
      final response = await AuthService.resetPassword(resetRequest);
      
      if (!response.success) {
        _setError(response.message);
      }
      
      return response.success;
    } catch (e) {
      debugPrint('Reset password error: $e');
      _setError('Gagal reset password: ${e.toString()}');
      return false;
    }
  }

  Future<bool> changePassword({
    required String currentPassword,
    required String newPassword,
    required String confirmNewPassword,
  }) async {
    if (_tokens?.accessToken == null) {
      _setError('Sesi telah berakhir');
      return false;
    }
    
    clearError();
    
    try {
      final changeRequest = ChangePasswordRequest(
        currentPassword: currentPassword,
        newPassword: newPassword,
        confirmNewPassword: confirmNewPassword,
      );
      
      final response = await AuthService.changePassword(
        _tokens!.accessToken,
        changeRequest,
      );
      
      if (!response.success) {
        _setError(response.message);
      }
      
      return response.success;
    } catch (e) {
      debugPrint('Change password error: $e');
      _setError('Gagal mengubah password: ${e.toString()}');
      return false;
    }
  }

  Future<bool> sendEmailVerification() async {
    if (_tokens?.accessToken == null) {
      _setError('Sesi telah berakhir');
      return false;
    }
    
    clearError();
    
    try {
      final response = await AuthService.sendEmailVerification(_tokens!.accessToken);
      
      if (!response.success) {
        _setError(response.message);
      }
      
      return response.success;
    } catch (e) {
      debugPrint('Send email verification error: $e');
      _setError('Gagal mengirim verifikasi email: ${e.toString()}');
      return false;
    }
  }

  Future<bool> verifyEmail({
    required String email,
    required String otpCode,
  }) async {
    if (_tokens?.accessToken == null) {
      _setError('Sesi telah berakhir');
      return false;
    }
    
    clearError();
    
    try {
      final verifyRequest = VerifyEmailRequest(
        email: email,
        otpCode: otpCode,
      );
      
      final response = await AuthService.verifyEmail(
        _tokens!.accessToken,
        verifyRequest,
      );
      
      if (response.success) {
        // Update user verification status
        if (_user != null) {
          _user = _user!.copyWith(isVerified: true);
          await _saveAuthData(user: _user!, tokens: _tokens!);
        }
      } else {
        _setError(response.message);
      }
      
      return response.success;
    } catch (e) {
      debugPrint('Verify email error: $e');
      _setError('Gagal verifikasi email: ${e.toString()}');
      return false;
    }
  }

  Future<void> getCurrentUser() async {
    if (_tokens?.accessToken == null) return;
    
    try {
      final response = await AuthService.getCurrentUser(_tokens!.accessToken);
      
      if (response.success && response.user != null) {
        _user = response.user;
        
        // Update stored user data
        final prefs = await SharedPreferences.getInstance();
        await prefs.setString(AppConstants.userDataKey, jsonEncode(_user!.toJson()));
        
        notifyListeners();
      }
    } catch (e) {
      debugPrint('Get current user error: $e');
    }
  }

  
Future<bool> logout({BuildContext? context}) async {
  try {
    // Optional: Call logout endpoint if tokens exist
    if (_tokens?.accessToken != null && _tokens?.refreshToken != null) {
      try {
        await AuthService.logout(
          accessToken: _tokens!.accessToken,
          refreshToken: _tokens!.refreshToken,
        );
      } catch (e) {
        debugPrint('Error during logout API call: $e');
        // Continue with local logout even if API call fails
      }
    }

    // Clear other providers if context is provided
    if (context != null) {
      try {
        // Clear category provider
        final categoryProvider = Provider.of<CategoryProvider>(context, listen: false);
        categoryProvider.clearAllData();
        
        // Clear university provider
        final universityProvider = Provider.of<UniversityProvider>(context, listen: false);
        universityProvider.clearAllData();
        
        // Clear transaction provider
        final transactionProvider = Provider.of<TransactionProvider>(context, listen: false);
        transactionProvider.clearAllData();
        
        // Clear university request provider
        final universityRequestProvider = Provider.of<UniversityRequestProvider>(context, listen: false);
        universityRequestProvider.clearAllData();
      } catch (e) {
        debugPrint('Error clearing other providers: $e');
      }
    }
  } catch (e) {
    debugPrint('Error during logout: $e');
  }
  
  await _clearAuthData();
  _setAuthState(AuthState.unauthenticated);
  return true;
}

  Future<bool> refreshAccessToken() async {
    if (_tokens?.refreshToken == null) return false;
    
    try {
      final response = await AuthService.refreshToken(_tokens!.refreshToken);
      
      if (response.success && response.tokens != null) {
        _tokens = response.tokens!;
        
        final prefs = await SharedPreferences.getInstance();
        await prefs.setString(AppConstants.accessTokenKey, _tokens!.accessToken);
        await prefs.setString(AppConstants.refreshTokenKey, _tokens!.refreshToken);
        
        notifyListeners();
        return true;
      } else {
        await logout();
        return false;
      }
    } catch (e) {
      debugPrint('Error refreshing token: $e');
      await logout();
      return false;
    }
  }
}