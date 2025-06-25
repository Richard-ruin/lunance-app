// lib/features/auth/presentation/bloc/auth_state.dart
import 'package:equatable/equatable.dart';
import '../../domain/entities/user.dart';

abstract class AuthState extends Equatable {
  const AuthState();

  @override
  List<Object?> get props => [];
}

class AuthInitial extends AuthState {
  const AuthInitial();
}

class AuthLoading extends AuthState {
  const AuthLoading();
}

class AuthAuthenticated extends AuthState {
  final User user;

  const AuthAuthenticated(this.user);

  @override
  List<Object> get props => [user];
}

class AuthUnauthenticated extends AuthState {
  const AuthUnauthenticated();
}

class AuthError extends AuthState {
  final String message;

  const AuthError(this.message);

  @override
  List<Object> get props => [message];
}

class AuthEmailNotVerified extends AuthState {
  final String email;
  final String message;

  const AuthEmailNotVerified({
    required this.email,
    required this.message,
  });

  @override
  List<Object> get props => [email, message];
}

class AuthRegistrationSuccess extends AuthState {
  final String email;
  final String message;

  const AuthRegistrationSuccess({
    required this.email,
    required this.message,
  });

  @override
  List<Object> get props => [email, message];
}

class AuthOtpRequested extends AuthState {
  final String email;
  final String message;

  const AuthOtpRequested({
    required this.email,
    required this.message,
  });

  @override
  List<Object> get props => [email, message];
}

class AuthOtpVerified extends AuthState {
  final String message;

  const AuthOtpVerified(this.message);

  @override
  List<Object> get props => [message];
}