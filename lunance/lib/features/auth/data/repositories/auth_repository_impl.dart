// lib/features/auth/data/repositories/auth_repository_impl.dart
import '../../domain/entities/user.dart';
import '../../domain/repositories/auth_repository.dart';
import '../datasources/auth_remote_datasource.dart';
import '../models/login_request_model.dart';
import '../models/register_request_model.dart';
import '../models/user_model.dart';
import '../../../../core/storage/local_storage.dart';

class AuthRepositoryImpl implements AuthRepository {
  final AuthRemoteDataSource remoteDataSource;
  final LocalStorage localStorage;

  AuthRepositoryImpl({
    required this.remoteDataSource,
    required this.localStorage,
  });

  @override
  Future<User> login({
    required String email,
    required String password,
    bool rememberMe = false,
  }) async {
    try {
      final request = LoginRequestModel(
        email: email,
        password: password,
        rememberMe: rememberMe,
      );

      print('🚀 REPOSITORY: Starting login process');
      final result = await remoteDataSource.login(request);
      
      print('📥 REPOSITORY: Got response from datasource');
      print('📋 REPOSITORY: Response keys: ${result.keys.toList()}');
      
      // Validate response structure
      if (result['user'] == null) {
        print('❌ REPOSITORY: Missing user data in response');
        print('📋 REPOSITORY: Available keys: ${result.keys.toList()}');
        throw Exception('Server response missing user data');
      }
      
      final userData = result['user'];
      print('📋 REPOSITORY: User data type: ${userData.runtimeType}');
      print('📋 REPOSITORY: User data: $userData');
      
      if (userData is! Map<String, dynamic>) {
        print('❌ REPOSITORY: User data is not a Map<String, dynamic>');
        throw Exception('Invalid user data format in server response');
      }
      
      // Create UserModel with comprehensive error handling
      UserModel userModel;
      try {
        print('🔄 REPOSITORY: Creating UserModel from data...');
        userModel = UserModel.fromJson(userData);
        print('✅ REPOSITORY: UserModel created successfully');
      } catch (userError) {
        print('❌ REPOSITORY: Failed to create UserModel: $userError');
        print('📋 REPOSITORY: UserData was: $userData');
        throw Exception('Failed to parse user information: $userError');
      }
      
      // Additional validation for critical fields
      if (userModel.id.isEmpty) {
        throw Exception('User ID is missing or empty');
      }
      
      if (userModel.email.isEmpty) {
        throw Exception('User email is missing or empty');
      }
      
      // Convert to User entity
      final user = User(
        id: userModel.id,
        email: userModel.email,
        fullName: userModel.fullName,
        university: userModel.university,
        faculty: userModel.faculty,
        major: userModel.major,
        semester: userModel.semester,
        phoneNumber: userModel.phoneNumber,
        profilePictureUrl: userModel.profilePictureUrl,
        isEmailVerified: userModel.isEmailVerified,
        createdAt: userModel.createdAt,
      );
      
      print('✅ REPOSITORY: Login successful for user: ${user.email}');
      return user;
      
    } catch (e, stackTrace) {
      print('❌ REPOSITORY: Login failed with error: $e');
      print('📚 REPOSITORY: Stack trace: $stackTrace');
      
      // Provide user-friendly error messages based on error type
      if (e.toString().contains('Failed to parse user')) {
        throw Exception('Terjadi kesalahan saat memproses data pengguna. Silakan coba lagi.');
      } else if (e.toString().contains('missing user data')) {
        throw Exception('Respons server tidak lengkap. Silakan coba lagi.');
      } else if (e.toString().contains('Invalid user data format')) {
        throw Exception('Format data pengguna tidak valid. Silakan coba lagi.');
      } else if (e.toString().contains('Network error')) {
        throw Exception('Gagal terhubung ke server. Periksa koneksi internet Anda.');
      } else if (e is Exception) {
        // Re-throw Exception as is for specific errors like email not verified
        rethrow;
      } else {
        throw Exception('Login gagal: ${e.toString()}');
      }
    }
  }

  @override
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
  }) async {
    try {
      final request = RegisterRequestModel(
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

      await remoteDataSource.register(request);
    } catch (e) {
      if (e is Exception) {
        rethrow;
      }
      throw Exception('Registration failed: ${e.toString()}');
    }
  }

  @override
  Future<void> logout() async {
    try {
      await remoteDataSource.logout();
    } catch (e) {
      // Don't throw error on logout failure, just log it
      print('Logout error: $e');
    }
  }

  @override
  Future<void> forgotPassword(String email) async {
    try {
      await remoteDataSource.forgotPassword(email);
    } catch (e) {
      if (e is Exception) {
        rethrow;
      }
      throw Exception('Forgot password failed: ${e.toString()}');
    }
  }

  @override
  Future<void> verifyOtp({
    required String email,
    required String code,
    required String type,
  }) async {
    try {
      await remoteDataSource.verifyOtp(
        email: email,
        code: code,
        type: type,
      );
    } catch (e) {
      if (e is Exception) {
        rethrow;
      }
      throw Exception('OTP verification failed: ${e.toString()}');
    }
  }

  @override
  Future<void> resetPassword({
    required String email,
    required String otpCode,
    required String newPassword,
  }) async {
    try {
      await remoteDataSource.resetPassword(
        email: email,
        otpCode: otpCode,
        newPassword: newPassword,
      );
    } catch (e) {
      if (e is Exception) {
        rethrow;
      }
      throw Exception('Password reset failed: ${e.toString()}');
    }
  }

  @override
  Future<User?> getCurrentUser() async {
    try {
      final userModel = await remoteDataSource.getCurrentUser();
      if (userModel == null) return null;
      
      // Convert UserModel to User entity
      return User(
        id: userModel.id,
        email: userModel.email,
        fullName: userModel.fullName,
        university: userModel.university,
        faculty: userModel.faculty,
        major: userModel.major,
        semester: userModel.semester,
        phoneNumber: userModel.phoneNumber,
        profilePictureUrl: userModel.profilePictureUrl,
        isEmailVerified: userModel.isEmailVerified,
        createdAt: userModel.createdAt,
      );
    } catch (e) {
      print('Get current user error: $e');
      return null;
    }
  }

  @override
  Future<bool> isLoggedIn() async {
    try {
      final token = localStorage.getString('access_token');
      return token != null && token.isNotEmpty;
    } catch (e) {
      return false;
    }
  }

  @override
  Future<void> requestOtp({
    required String email,
    required String type,
  }) async {
    try {
      await remoteDataSource.requestOtp(
        email: email,
        type: type,
      );
    } catch (e) {
      if (e is Exception) {
        rethrow;
      }
      throw Exception('Request OTP failed: ${e.toString()}');
    }
  }
}