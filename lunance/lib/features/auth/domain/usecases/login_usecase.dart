// lib/features/auth/domain/usecases/login_usecase.dart
import '../entities/user.dart';
import '../repositories/auth_repository.dart';

class LoginUseCase {
  final AuthRepository repository;

  LoginUseCase(this.repository);

  Future<User> call({
    required String email,
    required String password,
    bool rememberMe = false,
  }) async {
    // Validate inputs
    if (email.isEmpty) {
      throw Exception('Email tidak boleh kosong');
    }
    
    if (password.isEmpty) {
      throw Exception('Password tidak boleh kosong');
    }
    
    if (!email.contains('@')) {
      throw Exception('Format email tidak valid');
    }
    
    try {
      final user = await repository.login(
        email: email.trim().toLowerCase(),
        password: password,
        rememberMe: rememberMe,
      );
      
      // Validate user data
      if (user.id.isEmpty) {
        throw Exception('Invalid user data received');
      }
      
      return user;
    } on Exception catch (e) {
      // Re-throw Exception as is
      rethrow;
    } catch (e) {
      // Convert other errors to Exception
      throw Exception('Login gagal: ${e.toString()}');
    }
  }
}