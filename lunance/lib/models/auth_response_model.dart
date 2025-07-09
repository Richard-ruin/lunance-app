// lib/models/auth_response_model.dart
import 'user_model.dart';

class AuthResponse {
  final bool success;
  final String message;
  final User? user;
  final AuthTokens? tokens;

  AuthResponse({
    required this.success,
    required this.message,
    this.user,
    this.tokens,
  });

  factory AuthResponse.fromJson(Map<String, dynamic> json) {
    return AuthResponse(
      success: json['success'] ?? false,
      message: json['message'] ?? '',
      user: json['user'] != null ? User.fromJson(json['user']) : null,
      tokens: json['tokens'] != null ? AuthTokens.fromJson(json['tokens']) : null,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'success': success,
      'message': message,
      'user': user?.toJson(),
      'tokens': tokens?.toJson(),
    };
  }
}

class AuthTokens {
  final String accessToken;
  final String refreshToken;
  final String tokenType;
  final int expiresIn;
  final int refreshExpiresIn;

  AuthTokens({
    required this.accessToken,
    required this.refreshToken,
    required this.tokenType,
    required this.expiresIn,
    required this.refreshExpiresIn,
  });

  factory AuthTokens.fromJson(Map<String, dynamic> json) {
    return AuthTokens(
      accessToken: json['access_token'] ?? '',
      refreshToken: json['refresh_token'] ?? '',
      tokenType: json['token_type'] ?? 'bearer',
      expiresIn: json['expires_in'] ?? 3600,
      refreshExpiresIn: json['refresh_expires_in'] ?? 2592000,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'access_token': accessToken,
      'refresh_token': refreshToken,
      'token_type': tokenType,
      'expires_in': expiresIn,
      'refresh_expires_in': refreshExpiresIn,
    };
  }
}

// Registration models
class RegisterRequest {
  final String email;
  final String password;
  final String confirmPassword;
  final String fullName;
  final String phoneNumber;
  final String universityId;
  final String facultyId;
  final String majorId;
  final double? initialSavings;
  final String otpCode;

  RegisterRequest({
    required this.email,
    required this.password,
    required this.confirmPassword,
    required this.fullName,
    required this.phoneNumber,
    required this.universityId,
    required this.facultyId,
    required this.majorId,
    this.initialSavings,
    required this.otpCode,
  });

  Map<String, dynamic> toJson() {
    return {
      'email': email,
      'password': password,
      'confirm_password': confirmPassword,
      'full_name': fullName,
      'phone_number': phoneNumber,
      'university_id': universityId,
      'faculty_id': facultyId,
      'major_id': majorId,
      'initial_savings': initialSavings,
      'otp_code': otpCode,
    };
  }
}

class OTPRequest {
  final String email;

  OTPRequest({required this.email});

  Map<String, dynamic> toJson() {
    return {'email': email};
  }
}

class OTPResponse {
  final bool success;
  final String message;
  final int expiresInSeconds;

  OTPResponse({
    required this.success,
    required this.message,
    required this.expiresInSeconds,
  });

  factory OTPResponse.fromJson(Map<String, dynamic> json) {
    return OTPResponse(
      success: json['success'] ?? false,
      message: json['message'] ?? '',
      expiresInSeconds: json['data']?['expires_in_seconds'] ?? 300,
    );
  }
}

class ForgotPasswordRequest {
  final String email;

  ForgotPasswordRequest({required this.email});

  Map<String, dynamic> toJson() {
    return {'email': email};
  }
}

class ResetPasswordRequest {
  final String email;
  final String otpCode;
  final String newPassword;
  final String confirmNewPassword;

  ResetPasswordRequest({
    required this.email,
    required this.otpCode,
    required this.newPassword,
    required this.confirmNewPassword,
  });

  Map<String, dynamic> toJson() {
    return {
      'email': email,
      'otp_code': otpCode,
      'new_password': newPassword,
      'confirm_new_password': confirmNewPassword,
    };
  }
}

class ChangePasswordRequest {
  final String currentPassword;
  final String newPassword;
  final String confirmNewPassword;

  ChangePasswordRequest({
    required this.currentPassword,
    required this.newPassword,
    required this.confirmNewPassword,
  });

  Map<String, dynamic> toJson() {
    return {
      'current_password': currentPassword,
      'new_password': newPassword,
      'confirm_new_password': confirmNewPassword,
    };
  }
}

class VerifyEmailRequest {
  final String email;
  final String otpCode;

  VerifyEmailRequest({
    required this.email,
    required this.otpCode,
  });

  Map<String, dynamic> toJson() {
    return {
      'email': email,
      'otp_code': otpCode,
    };
  }
}