
// lib/features/auth/presentation/bloc/auth_bloc.dart
import 'package:flutter_bloc/flutter_bloc.dart';
import '../../domain/usecases/login_usecase.dart';
import '../../domain/usecases/register_usecase.dart';
import '../../domain/usecases/forgot_password_usecase.dart';
import '../../domain/repositories/auth_repository.dart';
import 'auth_event.dart';
import 'auth_state.dart';

class AuthBloc extends Bloc<AuthEvent, AuthState> {
  final LoginUseCase loginUseCase;
  final RegisterUseCase registerUseCase;
  final ForgotPasswordUseCase forgotPasswordUseCase;
  final AuthRepository authRepository;

  AuthBloc({
    required this.loginUseCase,
    required this.registerUseCase,
    required this.forgotPasswordUseCase,
    required this.authRepository,
  }) : super(const AuthInitial()) {
    on<AuthCheckStatusEvent>(_onCheckStatus);
    on<AuthLoginEvent>(_onLogin);
    on<AuthRegisterEvent>(_onRegister);
    on<AuthLogoutEvent>(_onLogout);
    on<AuthForgotPasswordEvent>(_onForgotPassword);
    on<AuthVerifyOtpEvent>(_onVerifyOtp);
    on<AuthResetPasswordEvent>(_onResetPassword);
    on<AuthRequestOtpEvent>(_onRequestOtp);
    
    // NEW HANDLERS FOR SETTINGS
    on<AuthGetUserEvent>(_onGetUser);
    on<AuthChangePasswordEvent>(_onChangePassword);
    on<AuthUpdateProfileEvent>(_onUpdateProfile);
  }

  Future<void> _onCheckStatus(
    AuthCheckStatusEvent event,
    Emitter<AuthState> emit,
  ) async {
    try {
      emit(const AuthLoading());
      
      final isLoggedIn = await authRepository.isLoggedIn();
      if (isLoggedIn) {
        final user = await authRepository.getCurrentUser();
        if (user != null) {
          emit(AuthAuthenticated(user));
        } else {
          emit(const AuthUnauthenticated());
        }
      } else {
        emit(const AuthUnauthenticated());
      }
    } catch (e) {
      emit(const AuthUnauthenticated());
    }
  }

  Future<void> _onLogin(
    AuthLoginEvent event,
    Emitter<AuthState> emit,
  ) async {
    try {
      emit(const AuthLoading());
      
      final user = await loginUseCase(
        email: event.email,
        password: event.password,
        rememberMe: event.rememberMe,
      );
      
      emit(AuthAuthenticated(user));
    } catch (e) {
      // Handle specific error types untuk email verification
      String errorMessage = e.toString();
      
      if (errorMessage.contains('not verified') || 
          errorMessage.contains('belum diverifikasi') ||
          errorMessage.contains('email_verified') ||
          errorMessage.contains('AccountNotVerifiedException')) {
        emit(AuthEmailNotVerified(
          email: event.email,
          message: 'Email Anda belum diverifikasi. Silakan verifikasi email terlebih dahulu untuk melanjutkan login.',
        ));
      } else {
        // Parse error message untuk menghilangkan "Login gagal: Exception: "
        String cleanMessage = errorMessage
            .replaceAll('Login gagal: ', '')
            .replaceAll('Exception: ', '')
            .replaceAll('type \'Null\' is not a subtype of type \'String\'', 'Terjadi kesalahan sistem. Silakan coba lagi.')
            .trim();
        
        emit(AuthError(cleanMessage));
      }
    }
  }

  Future<void> _onRegister(
    AuthRegisterEvent event,
    Emitter<AuthState> emit,
  ) async {
    try {
      emit(const AuthLoading());
      
      await registerUseCase(
        email: event.email,
        password: event.password,
        confirmPassword: event.confirmPassword,
        fullName: event.fullName,
        university: event.university,
        faculty: event.faculty,
        major: event.major,
        studentId: event.studentId,
        semester: event.semester,
        graduationYear: event.graduationYear,
        phoneNumber: event.phoneNumber,
      );
      
      emit(AuthRegistrationSuccess(
        email: event.email,
        message: 'Pendaftaran berhasil! Silakan periksa email untuk verifikasi.',
      ));
    } catch (e) {
      String errorMessage = e.toString()
          .replaceAll('Pendaftaran gagal: ', '')
          .replaceAll('Exception: ', '')
          .trim();
      emit(AuthError('Pendaftaran gagal: $errorMessage'));
    }
  }

  Future<void> _onLogout(
    AuthLogoutEvent event,
    Emitter<AuthState> emit,
  ) async {
    try {
      await authRepository.logout();
      emit(const AuthUnauthenticated());
    } catch (e) {
      // Even if logout fails on server, clear local state
      emit(const AuthUnauthenticated());
    }
  }

  Future<void> _onForgotPassword(
    AuthForgotPasswordEvent event,
    Emitter<AuthState> emit,
  ) async {
    try {
      emit(const AuthLoading());
      
      await forgotPasswordUseCase(event.email);
      
      emit(AuthOtpRequested(
        email: event.email,
        message: 'Kode OTP telah dikirim ke email Anda.',
      ));
    } catch (e) {
      String errorMessage = e.toString()
          .replaceAll('Exception: ', '')
          .trim();
      emit(AuthError('Gagal mengirim kode OTP: $errorMessage'));
    }
  }

  Future<void> _onVerifyOtp(
    AuthVerifyOtpEvent event,
    Emitter<AuthState> emit,
  ) async {
    try {
      emit(const AuthLoading());
      
      await authRepository.verifyOtp(
        email: event.email,
        code: event.code,
        type: event.type,
      );
      
      emit(const AuthOtpVerified('Kode OTP berhasil diverifikasi.'));
    } catch (e) {
      String errorMessage = e.toString()
          .replaceAll('Exception: ', '')
          .trim();
      emit(AuthError('Verifikasi OTP gagal: $errorMessage'));
    }
  }

  Future<void> _onResetPassword(
    AuthResetPasswordEvent event,
    Emitter<AuthState> emit,
  ) async {
    try {
      emit(const AuthLoading());
      
      await authRepository.resetPassword(
        email: event.email,
        otpCode: event.otpCode,
        newPassword: event.newPassword,
      );
      
      emit(const AuthOtpVerified('Password berhasil diubah. Silakan login dengan password baru.'));
    } catch (e) {
      String errorMessage = e.toString()
          .replaceAll('Exception: ', '')
          .trim();
      emit(AuthError('Reset password gagal: $errorMessage'));
    }
  }

  Future<void> _onRequestOtp(
    AuthRequestOtpEvent event,
    Emitter<AuthState> emit,
  ) async {
    try {
      emit(const AuthLoading());
      
      await authRepository.requestOtp(
        email: event.email,
        type: event.type,
      );
      
      emit(AuthOtpRequested(
        email: event.email,
        message: 'Kode OTP telah dikirim ke email Anda.',
      ));
    } catch (e) {
      String errorMessage = e.toString()
          .replaceAll('Exception: ', '')
          .trim();
      emit(AuthError('Gagal mengirim kode OTP: $errorMessage'));
    }
  }

  // NEW HANDLERS FOR SETTINGS
  Future<void> _onGetUser(
    AuthGetUserEvent event,
    Emitter<AuthState> emit,
  ) async {
    emit(const AuthLoading());
    
    try {
      final user = await authRepository.getCurrentUser();
      if (user != null) {
        emit(AuthAuthenticated(user));
      } else {
        emit(const AuthError('Gagal memuat data pengguna'));
      }
    } catch (e) {
      emit(AuthError('Gagal memuat data pengguna: ${e.toString()}'));
    }
  }

  Future<void> _onChangePassword(
    AuthChangePasswordEvent event,
    Emitter<AuthState> emit,
  ) async {
    emit(const AuthLoading());
    
    try {
      await authRepository.changePassword(
        currentPassword: event.currentPassword,
        newPassword: event.newPassword,
      );
      emit(const AuthChangePasswordSuccess());
    } catch (e) {
      String errorMessage = e.toString()
          .replaceAll('Exception: ', '')
          .replaceAll('Change password failed: ', '')
          .trim();
      emit(AuthError('Gagal mengubah password: $errorMessage'));
    }
  }

  Future<void> _onUpdateProfile(
    AuthUpdateProfileEvent event,
    Emitter<AuthState> emit,
  ) async {
    emit(const AuthLoading());
    
    try {
      final user = await authRepository.updateProfile(
        fullName: event.fullName,
        phoneNumber: event.phoneNumber,
        university: event.university,
        faculty: event.faculty,
        major: event.major,
        semester: event.semester,
        profileImage: event.profileImage,
      );
      
      emit(const AuthUpdateProfileSuccess('Profil berhasil diperbarui'));
      emit(AuthAuthenticated(user));
    } catch (e) {
      String errorMessage = e.toString()
          .replaceAll('Exception: ', '')
          .replaceAll('Update profile failed: ', '')
          .trim();
      emit(AuthError('Gagal memperbarui profil: $errorMessage'));
    }
  }
}