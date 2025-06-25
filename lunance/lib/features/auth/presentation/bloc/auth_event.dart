
// lib/features/auth/presentation/bloc/auth_event.dart
import 'package:equatable/equatable.dart';

abstract class AuthEvent extends Equatable {
  const AuthEvent();

  @override
  List<Object?> get props => [];
}

class AuthCheckStatusEvent extends AuthEvent {
  const AuthCheckStatusEvent();
}

class AuthLoginEvent extends AuthEvent {
  final String email;
  final String password;
  final bool rememberMe;

  const AuthLoginEvent({
    required this.email,
    required this.password,
    this.rememberMe = false,
  });

  @override
  List<Object> get props => [email, password, rememberMe];
}

class AuthRegisterEvent extends AuthEvent {
  final String email;
  final String password;
  final String confirmPassword;
  final String fullName;
  final String university;
  final String faculty;
  final String major;
  final String studentId;
  final int semester;
  final int graduationYear;
  final String? phoneNumber;

  const AuthRegisterEvent({
    required this.email,
    required this.password,
    required this.confirmPassword,
    required this.fullName,
    required this.university,
    required this.faculty,
    required this.major,
    required this.studentId,
    required this.semester,
    required this.graduationYear,
    this.phoneNumber,
  });

  @override
  List<Object?> get props => [
        email,
        password,
        confirmPassword,
        fullName,
        university,
        faculty,
        major,
        studentId,
        semester,
        graduationYear,
        phoneNumber,
      ];
}

class AuthLogoutEvent extends AuthEvent {
  const AuthLogoutEvent();
}

class AuthForgotPasswordEvent extends AuthEvent {
  final String email;

  const AuthForgotPasswordEvent(this.email);

  @override
  List<Object> get props => [email];
}

class AuthVerifyOtpEvent extends AuthEvent {
  final String email;
  final String code;
  final String type;

  const AuthVerifyOtpEvent({
    required this.email,
    required this.code,
    required this.type,
  });

  @override
  List<Object> get props => [email, code, type];
}

class AuthResetPasswordEvent extends AuthEvent {
  final String email;
  final String otpCode;
  final String newPassword;

  const AuthResetPasswordEvent({
    required this.email,
    required this.otpCode,
    required this.newPassword,
  });

  @override
  List<Object> get props => [email, otpCode, newPassword];
}

class AuthRequestOtpEvent extends AuthEvent {
  final String email;
  final String type;

  const AuthRequestOtpEvent({
    required this.email,
    required this.type,
  });

  @override
  List<Object> get props => [email, type];
}
