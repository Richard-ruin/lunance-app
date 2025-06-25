// lib/features/auth/domain/usecases/forgot_password_usecase.dart
import '../repositories/auth_repository.dart';

class ForgotPasswordUseCase {
  final AuthRepository repository;

  ForgotPasswordUseCase(this.repository);

  Future<void> call(String email) async {
    return await repository.forgotPassword(email);
  }
}