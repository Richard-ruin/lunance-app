// lib/services/auth_service.dart
import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import '../models/auth_response_model.dart';
import '../models/user_model.dart';
import '../utils/constants.dart';

class AuthService {
  static const String _baseUrl = AppConstants.authBaseUrl;
  
  static Map<String, String> _getHeaders({String? token}) {
    final headers = <String, String>{
      'Content-Type': 'application/json',
      'Accept': 'application/json',
    };
    
    if (token != null) {
      headers['Authorization'] = 'Bearer $token';
    }
    
    return headers;
  }

  // Register User
  static Future<AuthResponse> register(RegisterRequest request) async {
    try {
      debugPrint('Sending registration request to: $_baseUrl/register');
      debugPrint('Request body: ${jsonEncode(request.toJson())}');
      
      final response = await http.post(
        Uri.parse('$_baseUrl/register'),
        headers: _getHeaders(),
        body: jsonEncode(request.toJson()),
      );

      debugPrint('Registration response status: ${response.statusCode}');
      debugPrint('Registration response body: ${response.body}');
      
      final responseData = jsonDecode(response.body);
      
      if (response.statusCode == 201) {
        return AuthResponse(
          success: true,
          message: responseData['message'] ?? 'Registration successful',
          user: responseData['data']?['user'] != null 
              ? User.fromJson(responseData['data']['user']) 
              : null,
          tokens: responseData['data']?['tokens'] != null 
              ? AuthTokens.fromJson(responseData['data']['tokens']) 
              : null,
        );
      } else {
        return AuthResponse(
          success: false,
          message: responseData['message'] ?? 'Registration failed',
        );
      }
    } catch (e) {
      debugPrint('Registration error: $e');
      return AuthResponse(
        success: false,
        message: 'Network error: ${e.toString()}',
      );
    }
  }

  // Send Registration OTP
  static Future<OTPResponse> sendRegistrationOTP(String email) async {
    try {
      debugPrint('Sending registration OTP to: $email');
      
      final response = await http.post(
        Uri.parse('$_baseUrl/send-registration-otp'),
        headers: _getHeaders(),
        body: jsonEncode({'email': email}),
      );

      debugPrint('OTP response status: ${response.statusCode}');
      debugPrint('OTP response body: ${response.body}');
      
      final responseData = jsonDecode(response.body);
      
      return OTPResponse(
        success: response.statusCode == 200,
        message: responseData['message'] ?? 'OTP sent',
        expiresInSeconds: responseData['data']?['expires_in_seconds'] ?? 300,
      );
    } catch (e) {
      debugPrint('Send registration OTP error: $e');
      return OTPResponse(
        success: false,
        message: 'Network error: ${e.toString()}',
        expiresInSeconds: 0,
      );
    }
  }

  // Login User
  static Future<AuthResponse> login({
    required String email,
    required String password,
    bool rememberMe = false,
  }) async {
    try {
      debugPrint('Sending login request to: $_baseUrl/login');
      debugPrint('Request body: ${jsonEncode({
        'email': email,
        'password': password,
        'remember_me': rememberMe,
      })}');
      
      final response = await http.post(
        Uri.parse('$_baseUrl/login'),
        headers: _getHeaders(),
        body: jsonEncode({
          'email': email,
          'password': password,
          'remember_me': rememberMe,
        }),
      );

      debugPrint('Login response status: ${response.statusCode}');
      debugPrint('Login response body: ${response.body}');
      
      final responseData = jsonDecode(response.body);
      
      if (response.statusCode == 200) {
        return AuthResponse(
          success: true,
          message: responseData['message'] ?? 'Login successful',
          user: responseData['user'] != null 
              ? User.fromJson(responseData['user']) 
              : null,
          tokens: responseData['tokens'] != null 
              ? AuthTokens.fromJson(responseData['tokens']) 
              : null,
        );
      } else {
        return AuthResponse(
          success: false,
          message: responseData['message'] ?? 'Login failed',
        );
      }
    } catch (e) {
      debugPrint('Login error: $e');
      return AuthResponse(
        success: false,
        message: 'Network error: ${e.toString()}',
      );
    }
  }

  // Refresh Token
  static Future<AuthResponse> refreshToken(String refreshToken) async {
    try {
      debugPrint('Refreshing token...');
      
      final response = await http.post(
        Uri.parse('$_baseUrl/refresh-token'),
        headers: _getHeaders(),
        body: jsonEncode({'refresh_token': refreshToken}),
      );

      debugPrint('Refresh token response status: ${response.statusCode}');
      debugPrint('Refresh token response body: ${response.body}');
      
      final responseData = jsonDecode(response.body);
      
      if (response.statusCode == 200) {
        return AuthResponse(
          success: true,
          message: 'Token refreshed successfully',
          tokens: AuthTokens.fromJson(responseData),
        );
      } else {
        return AuthResponse(
          success: false,
          message: responseData['message'] ?? 'Token refresh failed',
        );
      }
    } catch (e) {
      debugPrint('Refresh token error: $e');
      return AuthResponse(
        success: false,
        message: 'Network error: ${e.toString()}',
      );
    }
  }

  // Logout User
  static Future<AuthResponse> logout({
    required String accessToken,
    required String refreshToken,
  }) async {
    try {
      debugPrint('Logging out user...');
      
      final response = await http.post(
        Uri.parse('$_baseUrl/logout'),
        headers: _getHeaders(token: accessToken),
        body: jsonEncode({'refresh_token': refreshToken}),
      );

      debugPrint('Logout response status: ${response.statusCode}');
      debugPrint('Logout response body: ${response.body}');
      
      final responseData = jsonDecode(response.body);
      
      if (response.statusCode == 200) {
        return AuthResponse(
          success: true,
          message: responseData['message'] ?? 'Logged out successfully',
        );
      } else {
        return AuthResponse(
          success: false,
          message: responseData['message'] ?? 'Logout failed',
        );
      }
    } catch (e) {
      debugPrint('Logout error: $e');
      return AuthResponse(
        success: false,
        message: 'Network error: ${e.toString()}',
      );
    }
  }

  // Forgot Password
  static Future<OTPResponse> forgotPassword(String email) async {
    try {
      debugPrint('Sending forgot password OTP to: $email');
      
      final response = await http.post(
        Uri.parse('$_baseUrl/forgot-password'),
        headers: _getHeaders(),
        body: jsonEncode({'email': email}),
      );

      debugPrint('Forgot password response status: ${response.statusCode}');
      debugPrint('Forgot password response body: ${response.body}');
      
      final responseData = jsonDecode(response.body);
      
      return OTPResponse(
        success: response.statusCode == 200,
        message: responseData['message'] ?? 'Reset code sent',
        expiresInSeconds: responseData['data']?['expires_in_seconds'] ?? 300,
      );
    } catch (e) {
      debugPrint('Forgot password error: $e');
      return OTPResponse(
        success: false,
        message: 'Network error: ${e.toString()}',
        expiresInSeconds: 0,
      );
    }
  }

  // Reset Password
  static Future<AuthResponse> resetPassword(ResetPasswordRequest request) async {
    try {
      debugPrint('Resetting password...');
      
      final response = await http.post(
        Uri.parse('$_baseUrl/reset-password'),
        headers: _getHeaders(),
        body: jsonEncode(request.toJson()),
      );

      debugPrint('Reset password response status: ${response.statusCode}');
      debugPrint('Reset password response body: ${response.body}');
      
      final responseData = jsonDecode(response.body);
      
      return AuthResponse(
        success: response.statusCode == 200,
        message: responseData['message'] ?? 'Password reset',
      );
    } catch (e) {
      debugPrint('Reset password error: $e');
      return AuthResponse(
        success: false,
        message: 'Network error: ${e.toString()}',
      );
    }
  }

  // Change Password
  static Future<AuthResponse> changePassword(
    String accessToken,
    ChangePasswordRequest request,
  ) async {
    try {
      debugPrint('Changing password...');
      
      final response = await http.post(
        Uri.parse('$_baseUrl/change-password'),
        headers: _getHeaders(token: accessToken),
        body: jsonEncode(request.toJson()),
      );

      debugPrint('Change password response status: ${response.statusCode}');
      debugPrint('Change password response body: ${response.body}');
      
      final responseData = jsonDecode(response.body);
      
      return AuthResponse(
        success: response.statusCode == 200,
        message: responseData['message'] ?? 'Password changed',
      );
    } catch (e) {
      debugPrint('Change password error: $e');
      return AuthResponse(
        success: false,
        message: 'Network error: ${e.toString()}',
      );
    }
  }

  // Send Email Verification
  static Future<OTPResponse> sendEmailVerification(String accessToken) async {
    try {
      debugPrint('Sending email verification...');
      
      final response = await http.post(
        Uri.parse('$_baseUrl/send-email-verification'),
        headers: _getHeaders(token: accessToken),
      );

      debugPrint('Send email verification response status: ${response.statusCode}');
      debugPrint('Send email verification response body: ${response.body}');
      
      final responseData = jsonDecode(response.body);
      
      return OTPResponse(
        success: response.statusCode == 200,
        message: responseData['message'] ?? 'Verification code sent',
        expiresInSeconds: responseData['data']?['expires_in_seconds'] ?? 300,
      );
    } catch (e) {
      debugPrint('Send email verification error: $e');
      return OTPResponse(
        success: false,
        message: 'Network error: ${e.toString()}',
        expiresInSeconds: 0,
      );
    }
  }

  // Verify Email
  static Future<AuthResponse> verifyEmail(
    String accessToken,
    VerifyEmailRequest request,
  ) async {
    try {
      debugPrint('Verifying email...');
      
      final response = await http.post(
        Uri.parse('$_baseUrl/verify-email'),
        headers: _getHeaders(token: accessToken),
        body: jsonEncode(request.toJson()),
      );

      debugPrint('Verify email response status: ${response.statusCode}');
      debugPrint('Verify email response body: ${response.body}');
      
      final responseData = jsonDecode(response.body);
      
      return AuthResponse(
        success: response.statusCode == 200,
        message: responseData['message'] ?? 'Email verified',
      );
    } catch (e) {
      debugPrint('Verify email error: $e');
      return AuthResponse(
        success: false,
        message: 'Network error: ${e.toString()}',
      );
    }
  }

  // Get Current User
  static Future<AuthResponse> getCurrentUser(String accessToken) async {
    try {
      debugPrint('Getting current user...');
      
      final response = await http.get(
        Uri.parse('$_baseUrl/me'),
        headers: _getHeaders(token: accessToken),
      );

      debugPrint('Get current user response status: ${response.statusCode}');
      debugPrint('Get current user response body: ${response.body}');
      
      final responseData = jsonDecode(response.body);
      
      if (response.statusCode == 200) {
        return AuthResponse(
          success: true,
          message: 'User data retrieved',
          user: User.fromJson(responseData),
        );
      } else {
        return AuthResponse(
          success: false,
          message: responseData['message'] ?? 'Failed to get user data',
        );
      }
    } catch (e) {
      debugPrint('Get current user error: $e');
      return AuthResponse(
        success: false,
        message: 'Network error: ${e.toString()}',
      );
    }
  }

  // Validate Token
  static Future<AuthResponse> validateToken(String accessToken) async {
    try {
      debugPrint('Validating token...');
      
      final response = await http.post(
        Uri.parse('$_baseUrl/validate-token'),
        headers: _getHeaders(token: accessToken),
      );

      debugPrint('Validate token response status: ${response.statusCode}');
      debugPrint('Validate token response body: ${response.body}');
      
      final responseData = jsonDecode(response.body);
      
      return AuthResponse(
        success: response.statusCode == 200,
        message: responseData['message'] ?? 'Token validated',
      );
    } catch (e) {
      debugPrint('Validate token error: $e');
      return AuthResponse(
        success: false,
        message: 'Network error: ${e.toString()}',
      );
    }
  }
}