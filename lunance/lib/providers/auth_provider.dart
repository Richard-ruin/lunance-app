import 'package:flutter/material.dart';
import '../models/user_model.dart';
import '../models/base_model.dart';
import '../models/auth/register_data.dart' hide RegisterStep1Data, RegisterStep2Data, RegisterStep3Data, RegisterStep4Data, RegisterStep5Data, ResendOtpRequest;
import '../models/auth/register_data.dart' as RegisterData;
import '../models/auth/auth_responses.dart';
import '../services/auth_service.dart';
import '../services/storage_service.dart';
import '../services/websocket_service.dart';

class AuthProvider extends ChangeNotifier {
  User? _user;
  bool _isLoading = false;
  bool _isAuthenticated = false;
  String? _errorMessage;

  // Getters
  User? get user => _user;
  bool get isLoading => _isLoading;
  bool get isAuthenticated => _isAuthenticated;
  String? get errorMessage => _errorMessage;
  bool get hasError => _errorMessage != null;
  bool get isAdmin => _user?.role == UserRole.admin;
  bool get isStudent => _user?.role == UserRole.student;

  // Service instances
  final AuthService _authService = AuthService();
  final WebSocketService _wsService = WebSocketService();

  // Multi-step registration data
  final Map<String, dynamic> _registrationData = {};

  // Registration step state
  int _registrationStep = 1;
  int get registrationStep => _registrationStep;

  // OTP state
  bool _isOtpSent = false;
  bool _isOtpVerified = false;
  int _otpResendCount = 0;
  DateTime? _otpSentTime;
  
  bool get isOtpSent => _isOtpSent;
  bool get isOtpVerified => _isOtpVerified;
  int get otpResendCount => _otpResendCount;
  DateTime? get otpSentTime => _otpSentTime;

  // Clear error message
  void clearError() {
    _errorMessage = null;
    notifyListeners();
  }

  // Set loading state
  void _setLoading(bool loading) {
    _isLoading = loading;
    notifyListeners();
  }

  // Set error message
  void _setError(String? error) {
    _errorMessage = error;
    notifyListeners();
  }

  // Set user and authentication state
  void _setUser(User? user) {
    _user = user;
    _isAuthenticated = user != null;
    notifyListeners();
  }

  // Check authentication status on app start
  Future<void> checkAuthStatus() async {
    _setLoading(true);

    try {
      // Check if we have a stored token
      final token = StorageService.getAuthToken();
      if (token == null) {
        _setUser(null);
        _setLoading(false);
        return;
      }

      // Check if we have stored user data
      final storedUser = StorageService.getUser();
      if (storedUser != null) {
        _setUser(storedUser);
      }

      // Verify token with server by fetching current user profile
      final response = await _authService.getProfile();
      if (response.success && response.data != null) {
        _setUser(response.data!);
        await StorageService.saveUser(response.data!);
        
        // Connect to WebSocket if authenticated
        if (_isAuthenticated) {
          _wsService.connect().catchError((e) {
            // WebSocket connection is optional, don't fail auth if it fails
            debugPrint('WebSocket connection failed: $e');
          });
        }
      } else {
        // Token is invalid, clear auth data
        await _clearAuthData();
      }
    } catch (e) {
      // If verification fails, clear auth data
      await _clearAuthData();
      _setError('Gagal memverifikasi status login');
    } finally {
      _setLoading(false);
    }
  }

  // Login user
  Future<bool> login(String email, String password) async {
    _setLoading(true);
    _setError(null);

    try {
      final loginRequest = LoginRequest(
        email: email,
        password: password,
      );

      final response = await _authService.login(loginRequest);
      
      if (response.success && response.data != null) {
        final loginResponse = response.data!;
        
        // Store auth token and user data
        await StorageService.saveAuthToken(loginResponse.accessToken);
        await StorageService.saveUser(loginResponse.user);
        
        _setUser(loginResponse.user);
        
        // Connect to WebSocket
        _wsService.connect().catchError((e) {
          debugPrint('WebSocket connection failed: $e');
        });
        
        _setLoading(false);
        return true;
      } else {
        _setError(response.message);
        _setLoading(false);
        return false;
      }
    } catch (e) {
      if (e is AuthException) {
        _setError(e.userMessage);
      } else {
        _setError('Gagal login, silakan coba lagi');
      }
      _setLoading(false);
      return false;
    }
  }

  // Logout user
  Future<void> logout() async {
    _setLoading(true);

    try {
      // Call logout API
      await _authService.logout();
    } catch (e) {
      // Even if logout API fails, we still clear local data
      debugPrint('Logout API failed: $e');
    } finally {
      // Clear auth data regardless of API call result
      await _clearAuthData();
      _setLoading(false);
    }
  }

  // Multi-step registration methods
  Future<bool> registerStep1({
    required String email,
    required String namaLengkap,
    required String noTelepon,
  }) async {
    _setLoading(true);
    _setError(null);

    try {
      final data = RegisterData.RegisterStep1Data(
        email: email,
        namaLengkap: namaLengkap,
        noTelepon: noTelepon,
      );

      final response = await _authService.registerStep1(data);

      if (response.success) {
        _registrationData.addAll(data.toJson());
        _registrationStep = 2;
        _isOtpSent = true;
        _otpSentTime = DateTime.now();
        _setLoading(false);
        notifyListeners();
        return true;
      } else {
        _setError(response.message);
        _setLoading(false);
        return false;
      }
    } catch (e) {
      if (e is AuthException) {
        _setError(e.userMessage);
      } else {
        _setError('Gagal mengirim data. Silakan coba lagi.');
      }
      _setLoading(false);
      return false;
    }
  }

  Future<bool> registerStep2({
    required String universityId,
    required String fakultasId,
    required String prodiId,
  }) async {
    _setLoading(true);
    _setError(null);

    try {
      final data = RegisterData.RegisterStep2Data(
        email: _registrationData['email'],
        universityId: universityId,
        fakultasId: fakultasId,
        prodiId: prodiId,
      );

      final response = await _authService.registerStep2(data);

      if (response.success) {
        _registrationData.addAll({
          'university_id': universityId,
          'fakultas_id': fakultasId,
          'prodi_id': prodiId,
        });
        _registrationStep = 3;
        _setLoading(false);
        notifyListeners();
        return true;
      } else {
        _setError(response.message);
        _setLoading(false);
        return false;
      }
    } catch (e) {
      if (e is AuthException) {
        _setError(e.userMessage);
      } else {
        _setError('Gagal menyimpan data akademik. Silakan coba lagi.');
      }
      _setLoading(false);
      return false;
    }
  }

  Future<bool> registerStep3({required String otpCode}) async {
    _setLoading(true);
    _setError(null);

    try {
      final data = RegisterData.RegisterStep3Data(
        email: _registrationData['email'],
        otpCode: otpCode,
      );

      final response = await _authService.registerStep3(data);

      if (response.success) {
        _isOtpVerified = true;
        _registrationStep = 4;
        _setLoading(false);
        notifyListeners();
        return true;
      } else {
        _setError(response.message);
        _setLoading(false);
        return false;
      }
    } catch (e) {
      if (e is AuthException) {
        _setError(e.userMessage);
      } else {
        _setError('Kode OTP tidak valid. Silakan coba lagi.');
      }
      _setLoading(false);
      return false;
    }
  }

  Future<bool> registerStep4({required double tabunganAwal}) async {
    _setLoading(true);
    _setError(null);

    try {
      final data = RegisterData.RegisterStep4Data(
        email: _registrationData['email'],
        tabunganAwal: tabunganAwal,
      );

      final response = await _authService.registerStep4(data);

      if (response.success) {
        _registrationData['tabungan_awal'] = tabunganAwal;
        _registrationStep = 5;
        _setLoading(false);
        notifyListeners();
        return true;
      } else {
        _setError(response.message);
        _setLoading(false);
        return false;
      }
    } catch (e) {
      if (e is AuthException) {
        _setError(e.userMessage);
      } else {
        _setError('Gagal menyimpan data tabungan. Silakan coba lagi.');
      }
      _setLoading(false);
      return false;
    }
  }

  Future<bool> registerStep5({
    required String password,
    required String confirmPassword,
  }) async {
    _setLoading(true);
    _setError(null);

    try {
      final data = RegisterData.RegisterStep5Data(
        email: _registrationData['email'],
        password: password,
        confirmPassword: confirmPassword,
        namaLengkap: _registrationData['nama_lengkap'],
        noTelepon: _registrationData['no_telepon'],
        universityId: _registrationData['university_id'],
        fakultasId: _registrationData['fakultas_id'],
        prodiId: _registrationData['prodi_id'],
        tabunganAwal: _registrationData['tabungan_awal'],
      );

      final response = await _authService.registerStep5(data);

      if (response.success && response.data != null) {
        final registrationResponse = response.data!;
        
        // Store auth data
        await StorageService.saveAuthToken(registrationResponse.accessToken);
        await StorageService.saveUser(registrationResponse.user);
        
        _setUser(registrationResponse.user);
        _clearRegistrationData();
        
        // Connect to WebSocket
        _wsService.connect().catchError((e) {
          debugPrint('WebSocket connection failed: $e');
        });
        
        _setLoading(false);
        return true;
      } else {
        _setError(response.message);
        _setLoading(false);
        return false;
      }
    } catch (e) {
      if (e is AuthException) {
        _setError(e.userMessage);
      } else {
        _setError('Gagal menyelesaikan registrasi. Silakan coba lagi.');
      }
      _setLoading(false);
      return false;
    }
  }

  // Resend OTP
  Future<bool> resendOtp() async {
    if (_otpResendCount >= 3) {
      _setError('Batas pengiriman ulang OTP telah tercapai');
      return false;
    }

    _setLoading(true);
    _setError(null);

    try {
      final request = RegisterData.ResendOtpRequest(email: _registrationData['email']);
      final response = await _authService.resendOtp(request);

      if (response.success) {
        _otpResendCount++;
        _otpSentTime = DateTime.now();
        _setLoading(false);
        notifyListeners();
        return true;
      } else {
        _setError(response.message);
        _setLoading(false);
        return false;
      }
    } catch (e) {
      if (e is AuthException) {
        _setError(e.userMessage);
      } else {
        _setError('Gagal mengirim ulang OTP');
      }
      _setLoading(false);
      return false;
    }
  }

  // Forgot password
  Future<bool> forgotPassword(String email) async {
    _setLoading(true);
    _setError(null);

    try {
      final request = ForgotPasswordRequest(email: email);
      final response = await _authService.forgotPassword(request);
      
      if (response.success) {
        _setLoading(false);
        return true;
      } else {
        _setError(response.message);
        _setLoading(false);
        return false;
      }
    } catch (e) {
      if (e is AuthException) {
        _setError(e.userMessage);
      } else {
        _setError('Gagal mengirim email reset password');
      }
      _setLoading(false);
      return false;
    }
  }

  // Update user profile
  Future<bool> updateProfile(UpdateProfileRequest updateRequest) async {
    _setLoading(true);
    _setError(null);

    try {
      final response = await _authService.updateProfile(updateRequest);
      
      if (response.success && response.data != null) {
        _setUser(response.data!.user);
        await StorageService.saveUser(response.data!.user);
        _setLoading(false);
        return true;
      } else {
        _setError(response.message);
        _setLoading(false);
        return false;
      }
    } catch (e) {
      if (e is AuthException) {
        _setError(e.userMessage);
      } else {
        _setError('Gagal memperbarui profil');
      }
      _setLoading(false);
      return false;
    }
  }

  // Change password
  Future<bool> changePassword(ChangePasswordRequest changeRequest) async {
    _setLoading(true);
    _setError(null);

    try {
      final response = await _authService.changePassword(changeRequest);
      
      if (response.success) {
        _setLoading(false);
        return true;
      } else {
        _setError(response.message);
        _setLoading(false);
        return false;
      }
    } catch (e) {
      if (e is AuthException) {
        _setError(e.userMessage);
      } else {
        _setError('Gagal mengubah password');
      }
      _setLoading(false);
      return false;
    }
  }

  // Refresh user profile from server
  Future<void> refreshProfile() async {
    if (!_isAuthenticated) return;

    try {
      final response = await _authService.getProfile();
      if (response.success && response.data != null) {
        _setUser(response.data!);
        await StorageService.saveUser(response.data!);
      }
    } catch (e) {
      debugPrint('Failed to refresh profile: $e');
    }
  }

  // Clear authentication data
  Future<void> _clearAuthData() async {
    await StorageService.clearAuthData();
    await _wsService.disconnect();
    _setUser(null);
  }

  // Force logout (clear data without API call)
  Future<void> forceLogout() async {
    _setLoading(true);
    await _clearAuthData();
    _setLoading(false);
  }

  // Check if token is expired and refresh if needed
  Future<bool> validateAndRefreshToken() async {
    if (!_isAuthenticated) return false;

    try {
      final response = await _authService.getProfile();
      if (response.success && response.data != null) {
        return true;
      } else {
        // Token might be expired
        await _clearAuthData();
        return false;
      }
    } catch (e) {
      if (e is AuthException && e.isUnauthorized) {
        await _clearAuthData();
        return false;
      }
      // Other errors don't necessarily mean token is invalid
      return true;
    }
  }

  // Get user display name
  String get userDisplayName {
    if (_user == null) return '';
    return _user!.namaLengkap.isNotEmpty ? _user!.namaLengkap : _user!.email;
  }

  // Get user initials for avatar
  String get userInitials {
    if (_user == null) return '';
    final name = _user!.namaLengkap.isNotEmpty ? _user!.namaLengkap : _user!.email;
    final words = name.split(' ');
    if (words.length >= 2) {
      return '${words[0][0]}${words[1][0]}'.toUpperCase();
    } else if (words.isNotEmpty) {
      return words[0][0].toUpperCase();
    }
    return '';
  }

  // Check if user has completed profile
  bool get hasCompletedProfile {
    if (_user == null) return false;
    return _user!.namaLengkap.isNotEmpty &&
           _user!.nim.isNotEmpty &&
           _user!.universityId != null &&
           _user!.fakultasId != null &&
           _user!.prodiId != null;
  }

  // Check OTP expiry
  bool get isOtpExpired {
    if (_otpSentTime == null) return true;
    return DateTime.now().difference(_otpSentTime!).inMinutes >= 5;
  }

  // Get OTP remaining time
  Duration get otpRemainingTime {
    if (_otpSentTime == null) return Duration.zero;
    final elapsed = DateTime.now().difference(_otpSentTime!);
    final remaining = const Duration(minutes: 5) - elapsed;
    return remaining.isNegative ? Duration.zero : remaining;
  }

  // Clear registration data
  void _clearRegistrationData() {
    _registrationData.clear();
    _registrationStep = 1;
    _isOtpSent = false;
    _isOtpVerified = false;
    _otpResendCount = 0;
    _otpSentTime = null;
    notifyListeners();
  }

  // Reset registration process
  void resetRegistration() {
    _clearRegistrationData();
    clearError();
  }

  // Go to previous registration step
  void goToPreviousStep() {
    if (_registrationStep > 1) {
      _registrationStep--;
      notifyListeners();
    }
  }

  // Get registration progress
  double get registrationProgress {
    return _registrationStep / 5.0;
  }

  // Get validation errors for display
  Map<String, String> getValidationErrors(AuthException exception) {
    final errors = <String, String>{};
    
    if (exception.errors != null) {
      exception.errors!.fieldErrors.forEach((field, messages) {
        if (messages.isNotEmpty) {
          errors[field] = messages.first;
        }
      });
    }
    
    return errors;
  }
}