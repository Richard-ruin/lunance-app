// lib/features/auth/domain/usecases/register_usecase.dart
import '../repositories/auth_repository.dart';

class RegisterUseCase {
  final AuthRepository repository;

  RegisterUseCase(this.repository);

  Future<void> call({
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
  }) async {
    return await repository.register(
      email: email,
      password: password,
      confirmPassword: confirmPassword,
      fullName: fullName,
      university: university,
      faculty: faculty,
      major: major,
      studentId: studentId,
      semester: semester,
      graduationYear: graduationYear,
      phoneNumber: phoneNumber,
    );
  }
}

