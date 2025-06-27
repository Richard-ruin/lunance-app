
// lib/features/auth/domain/repositories/auth_repository.dart
import '../entities/user.dart';
import 'dart:io';

abstract class AuthRepository {
  Future<User> login({
    required String email,
    required String password,
    bool rememberMe = false,
  });

  Future<void> register({
    required String email,
    required String password,
    required String confirmPassword,
    required String fullName,
    required String university,
    required String faculty,
    required String major,
    required String studentId,
    required int semester,
    required int graduationYear,
    String? phoneNumber,
  });

  Future<void> logout();

  Future<void> forgotPassword(String email);

  Future<void> verifyOtp({
    required String email,
    required String code,
    required String type,
  });

  Future<void> resetPassword({
    required String email,
    required String otpCode,
    required String newPassword,
  });

  Future<User?> getCurrentUser();

  Future<bool> isLoggedIn();

  Future<void> requestOtp({
    required String email,
    required String type,
  });

  // NEW METHODS FOR SETTINGS
  Future<void> changePassword({
    required String currentPassword,
    required String newPassword,
  });

  Future<User> updateProfile({
    required String fullName,
    String? phoneNumber,
    required String university,
    required String faculty,
    required String major,
    required int semester,
    File? profileImage,
  });
}