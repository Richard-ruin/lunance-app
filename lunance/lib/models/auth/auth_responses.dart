// lib/models/auth/auth_responses.dart
import '../base_model.dart';
import '../user_model.dart';

// Generic register step response
class RegisterStepResponse extends BaseModel {
  final String email;
  final String message;
  final String? otpCode; // Only in development
  final Map<String, dynamic>? additionalData;

  const RegisterStepResponse({
    required this.email,
    required this.message,
    this.otpCode,
    this.additionalData,
  });

  factory RegisterStepResponse.fromJson(Map<String, dynamic> json) {
    return RegisterStepResponse(
      email: json['email'] ?? '',
      message: json['message'] ?? '',
      otpCode: json['otp_code'],
      additionalData: json['additional_data'],
    );
  }

  @override
  Map<String, dynamic> toJson() {
    return {
      'email': email,
      'message': message,
      if (otpCode != null) 'otp_code': otpCode,
      if (additionalData != null) 'additional_data': additionalData,
    };
  }

  @override
  List<Object?> get props => [email, message, otpCode, additionalData];
}

// Login response
class LoginResponse extends BaseModel {
  final String accessToken;
  final String refreshToken;
  final String tokenType;
  final int expiresIn;
  final User user;

  const LoginResponse({
    required this.accessToken,
    required this.refreshToken,
    required this.tokenType,
    required this.expiresIn,
    required this.user,
  });

  factory LoginResponse.fromJson(Map<String, dynamic> json) {
    return LoginResponse(
      accessToken: json['access_token'] ?? '',
      refreshToken: json['refresh_token'] ?? '',
      tokenType: json['token_type'] ?? 'Bearer',
      expiresIn: json['expires_in'] ?? 3600,
      user: User.fromJson(json['user'] ?? {}),
    );
  }

  @override
  Map<String, dynamic> toJson() {
    return {
      'access_token': accessToken,
      'refresh_token': refreshToken,
      'token_type': tokenType,
      'expires_in': expiresIn,
      'user': user.toJson(),
    };
  }

  @override
  List<Object?> get props => [accessToken, refreshToken, tokenType, expiresIn, user];
}

// Refresh token response
class RefreshTokenResponse extends BaseModel {
  final String accessToken;
  final String tokenType;
  final int expiresIn;

  const RefreshTokenResponse({
    required this.accessToken,
    required this.tokenType,
    required this.expiresIn,
  });

  factory RefreshTokenResponse.fromJson(Map<String, dynamic> json) {
    return RefreshTokenResponse(
      accessToken: json['access_token'] ?? '',
      tokenType: json['token_type'] ?? 'Bearer',
      expiresIn: json['expires_in'] ?? 3600,
    );
  }

  @override
  Map<String, dynamic> toJson() {
    return {
      'access_token': accessToken,
      'token_type': tokenType,
      'expires_in': expiresIn,
    };
  }

  @override
  List<Object?> get props => [accessToken, tokenType, expiresIn];
}

// OTP response
class OtpResponse extends BaseModel {
  final String email;
  final String message;
  final String? otpCode; // Only in development
  final int expiresIn; // in minutes
  final int remainingAttempts;

  const OtpResponse({
    required this.email,
    required this.message,
    this.otpCode,
    required this.expiresIn,
    required this.remainingAttempts,
  });

  factory OtpResponse.fromJson(Map<String, dynamic> json) {
    return OtpResponse(
      email: json['email'] ?? '',
      message: json['message'] ?? '',
      otpCode: json['otp_code'],
      expiresIn: json['expires_in'] ?? 5,
      remainingAttempts: json['remaining_attempts'] ?? 3,
    );
  }

  @override
  Map<String, dynamic> toJson() {
    return {
      'email': email,
      'message': message,
      if (otpCode != null) 'otp_code': otpCode,
      'expires_in': expiresIn,
      'remaining_attempts': remainingAttempts,
    };
  }

  @override
  List<Object?> get props => [email, message, otpCode, expiresIn, remainingAttempts];
}

// Email check response
class EmailCheckResponse extends BaseModel {
  final String email;
  final bool isAvailable;
  final String message;

  const EmailCheckResponse({
    required this.email,
    required this.isAvailable,
    required this.message,
  });

  factory EmailCheckResponse.fromJson(Map<String, dynamic> json) {
    return EmailCheckResponse(
      email: json['email'] ?? '',
      isAvailable: json['is_available'] ?? false,
      message: json['message'] ?? '',
    );
  }

  @override
  Map<String, dynamic> toJson() {
    return {
      'email': email,
      'is_available': isAvailable,
      'message': message,
    };
  }

  @override
  List<Object?> get props => [email, isAvailable, message];
}

// Password reset response
class PasswordResetResponse extends BaseModel {
  final String email;
  final String message;
  final bool success;

  const PasswordResetResponse({
    required this.email,
    required this.message,
    required this.success,
  });

  factory PasswordResetResponse.fromJson(Map<String, dynamic> json) {
    return PasswordResetResponse(
      email: json['email'] ?? '',
      message: json['message'] ?? '',
      success: json['success'] ?? false,
    );
  }

  @override
  Map<String, dynamic> toJson() {
    return {
      'email': email,
      'message': message,
      'success': success,
    };
  }

  @override
  List<Object?> get props => [email, message, success];
}

// Profile update response
class ProfileUpdateResponse extends BaseModel {
  final User user;
  final String message;

  const ProfileUpdateResponse({
    required this.user,
    required this.message,
  });

  factory ProfileUpdateResponse.fromJson(Map<String, dynamic> json) {
    return ProfileUpdateResponse(
      user: User.fromJson(json['user'] ?? {}),
      message: json['message'] ?? '',
    );
  }

  @override
  Map<String, dynamic> toJson() {
    return {
      'user': user.toJson(),
      'message': message,
    };
  }

  @override
  List<Object?> get props => [user, message];
}

// Logout response
class LogoutResponse extends BaseModel {
  final String message;
  final bool success;

  const LogoutResponse({
    required this.message,
    required this.success,
  });

  factory LogoutResponse.fromJson(Map<String, dynamic> json) {
    return LogoutResponse(
      message: json['message'] ?? '',
      success: json['success'] ?? false,
    );
  }

  @override
  Map<String, dynamic> toJson() {
    return {
      'message': message,
      'success': success,
    };
  }

  @override
  List<Object?> get props => [message, success];
}

// Registration complete response
class RegistrationCompleteResponse extends BaseModel {
  final String accessToken;
  final String refreshToken;
  final String tokenType;
  final int expiresIn;
  final User user;
  final String message;

  const RegistrationCompleteResponse({
    required this.accessToken,
    required this.refreshToken,
    required this.tokenType,
    required this.expiresIn,
    required this.user,
    required this.message,
  });

  factory RegistrationCompleteResponse.fromJson(Map<String, dynamic> json) {
    return RegistrationCompleteResponse(
      accessToken: json['access_token'] ?? '',
      refreshToken: json['refresh_token'] ?? '',
      tokenType: json['token_type'] ?? 'Bearer',
      expiresIn: json['expires_in'] ?? 3600,
      user: User.fromJson(json['user'] ?? {}),
      message: json['message'] ?? '',
    );
  }

  @override
  Map<String, dynamic> toJson() {
    return {
      'access_token': accessToken,
      'refresh_token': refreshToken,
      'token_type': tokenType,
      'expires_in': expiresIn,
      'user': user.toJson(),
      'message': message,
    };
  }

  @override
  List<Object?> get props => [
        accessToken,
        refreshToken,
        tokenType,
        expiresIn,
        user,
        message,
      ];
}

// Verification status response
class VerificationStatusResponse extends BaseModel {
  final String email;
  final bool isVerified;
  final String status; // 'pending', 'verified', 'expired'
  final String message;

  const VerificationStatusResponse({
    required this.email,
    required this.isVerified,
    required this.status,
    required this.message,
  });

  factory VerificationStatusResponse.fromJson(Map<String, dynamic> json) {
    return VerificationStatusResponse(
      email: json['email'] ?? '',
      isVerified: json['is_verified'] ?? false,
      status: json['status'] ?? 'pending',
      message: json['message'] ?? '',
    );
  }

  @override
  Map<String, dynamic> toJson() {
    return {
      'email': email,
      'is_verified': isVerified,
      'status': status,
      'message': message,
    };
  }

  @override
  List<Object?> get props => [email, isVerified, status, message];
}

// Token validation response
class TokenValidationResponse extends BaseModel {
  final bool isValid;
  final String? userId;
  final String? email;
  final String? role;
  final DateTime? expiresAt;

  const TokenValidationResponse({
    required this.isValid,
    this.userId,
    this.email,
    this.role,
    this.expiresAt,
  });

  factory TokenValidationResponse.fromJson(Map<String, dynamic> json) {
    return TokenValidationResponse(
      isValid: json['is_valid'] ?? false,
      userId: json['user_id'],
      email: json['email'],
      role: json['role'],
      expiresAt: json['expires_at'] != null 
          ? DateTime.parse(json['expires_at']) 
          : null,
    );
  }

  @override
  Map<String, dynamic> toJson() {
    return {
      'is_valid': isValid,
      if (userId != null) 'user_id': userId,
      if (email != null) 'email': email,
      if (role != null) 'role': role,
      if (expiresAt != null) 'expires_at': expiresAt!.toIso8601String(),
    };
  }

  @override
  List<Object?> get props => [isValid, userId, email, role, expiresAt];
}