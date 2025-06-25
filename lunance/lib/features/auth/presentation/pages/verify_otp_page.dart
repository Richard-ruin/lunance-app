
// lib/features/auth/presentation/pages/verify_otp_page.dart
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:go_router/go_router.dart';
import 'dart:async';

import '../../../../core/theme/lunance_colors.dart';
import '../../../../shared/widgets/custom_button.dart';
import '../../../../shared/widgets/loading_widget.dart';
import '../bloc/auth_bloc.dart';
import '../bloc/auth_event.dart';
import '../bloc/auth_state.dart';

class VerifyOtpPage extends StatefulWidget {
  final String email;
  final String type; // 'registration', 'forgot_password', 'email_verification'

  const VerifyOtpPage({
    super.key,
    required this.email,
    required this.type,
  });

  @override
  State<VerifyOtpPage> createState() => _VerifyOtpPageState();
}

class _VerifyOtpPageState extends State<VerifyOtpPage> {
  final List<TextEditingController> _controllers = 
      List.generate(6, (index) => TextEditingController());
  final List<FocusNode> _focusNodes = 
      List.generate(6, (index) => FocusNode());
  
  Timer? _timer;
  int _remainingTime = 600; // 10 minutes
  bool _canResend = false;

  @override
  void initState() {
    super.initState();
    _startTimer();
  }

  @override
  void dispose() {
    _timer?.cancel();
    for (var controller in _controllers) {
      controller.dispose();
    }
    for (var focusNode in _focusNodes) {
      focusNode.dispose();
    }
    super.dispose();
  }

  void _startTimer() {
    _timer = Timer.periodic(const Duration(seconds: 1), (timer) {
      setState(() {
        if (_remainingTime > 0) {
          _remainingTime--;
        } else {
          _canResend = true;
          timer.cancel();
        }
      });
    });
  }

  void _verifyOtp() {
    String otp = _controllers.map((controller) => controller.text).join();
    if (otp.length == 6) {
      context.read<AuthBloc>().add(
            AuthVerifyOtpEvent(
              email: widget.email,
              code: otp,
              type: widget.type,
            ),
          );
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Silakan masukkan kode OTP lengkap'),
          backgroundColor: LunanceColors.warning,
        ),
      );
    }
  }

  void _resendOtp() {
    if (_canResend) {
      context.read<AuthBloc>().add(
            AuthRequestOtpEvent(
              email: widget.email,
              type: widget.type,
            ),
          );
      setState(() {
        _remainingTime = 600;
        _canResend = false;
      });
      _startTimer();
      
      // Clear OTP fields
      for (var controller in _controllers) {
        controller.clear();
      }
      _focusNodes[0].requestFocus();
    }
  }

  String get _formattedTime {
    int minutes = _remainingTime ~/ 60;
    int seconds = _remainingTime % 60;
    return '${minutes.toString().padLeft(2, '0')}:${seconds.toString().padLeft(2, '0')}';
  }

  String get _getTitle {
    switch (widget.type) {
      case 'registration':
        return 'Verifikasi Pendaftaran';
      case 'forgot_password':
        return 'Verifikasi Reset Password';
      case 'email_verification':
        return 'Verifikasi Email';
      default:
        return 'Verifikasi OTP';
    }
  }

  String get _getSubtitle {
    switch (widget.type) {
      case 'registration':
        return 'Masukkan kode OTP yang telah dikirim ke email Anda untuk menyelesaikan pendaftaran.';
      case 'forgot_password':
        return 'Masukkan kode OTP yang telah dikirim ke email Anda untuk reset password.';
      case 'email_verification':
        return 'Masukkan kode OTP yang telah dikirim ke email Anda untuk verifikasi.';
      default:
        return 'Masukkan kode OTP yang telah dikirim ke email Anda.';
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(_getTitle),
      ),
      body: SafeArea(
        child: BlocConsumer<AuthBloc, AuthState>(
          listener: (context, state) {
            if (state is AuthError) {
              ScaffoldMessenger.of(context).showSnackBar(
                SnackBar(
                  content: Text(state.message),
                  backgroundColor: LunanceColors.error,
                ),
              );
            } else if (state is AuthOtpVerified) {
              ScaffoldMessenger.of(context).showSnackBar(
                SnackBar(
                  content: Text(state.message),
                  backgroundColor: LunanceColors.success,
                ),
              );
              
              if (widget.type == 'forgot_password') {
                context.push('/reset-password', extra: {
                  'email': widget.email,
                });
              } else {
                context.go('/login');
              }
            } else if (state is AuthOtpRequested) {
              ScaffoldMessenger.of(context).showSnackBar(
                SnackBar(
                  content: Text(state.message),
                  backgroundColor: LunanceColors.success,
                ),
              );
            }
          },
          builder: (context, state) {
            return SingleChildScrollView(
              padding: const EdgeInsets.all(24.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  const SizedBox(height: 32),
                  
                  // Illustration
                  Center(
                    child: Container(
                      width: 120,
                      height: 120,
                      decoration: BoxDecoration(
                        color: LunanceColors.primary.withOpacity(0.1),
                        borderRadius: BorderRadius.circular(60),
                      ),
                      child: const Icon(
                        Icons.verified_user,
                        size: 60,
                        color: LunanceColors.primary,
                      ),
                    ),
                  ),
                  
                  const SizedBox(height: 32),
                  
                  Text(
                    _getTitle,
                    style: const TextStyle(
                      fontSize: 28,
                      fontWeight: FontWeight.bold,
                      color: LunanceColors.textPrimary,
                    ),
                    textAlign: TextAlign.center,
                  ),
                  
                  const SizedBox(height: 16),
                  
                  Text(
                    _getSubtitle,
                    style: const TextStyle(
                      fontSize: 16,
                      color: LunanceColors.textSecondary,
                      height: 1.5,
                    ),
                    textAlign: TextAlign.center,
                  ),
                  
                  const SizedBox(height: 8),
                  
                  Text(
                    widget.email,
                    style: const TextStyle(
                      fontSize: 16,
                      color: LunanceColors.primary,
                      fontWeight: FontWeight.w600,
                    ),
                    textAlign: TextAlign.center,
                  ),
                  
                  const SizedBox(height: 48),
                  
                  // OTP Input Fields
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                    children: List.generate(6, (index) {
                      return SizedBox(
                        width: 45,
                        height: 60,
                        child: TextFormField(
                          controller: _controllers[index],
                          focusNode: _focusNodes[index],
                          keyboardType: TextInputType.number,
                          textAlign: TextAlign.center,
                          maxLength: 1,
                          style: const TextStyle(
                            fontSize: 24,
                            fontWeight: FontWeight.bold,
                          ),
                          decoration: InputDecoration(
                            counterText: '',
                            filled: true,
                            fillColor: LunanceColors.surfaceVariant,
                            border: OutlineInputBorder(
                              borderRadius: BorderRadius.circular(12),
                              borderSide: BorderSide.none,
                            ),
                            focusedBorder: OutlineInputBorder(
                              borderRadius: BorderRadius.circular(12),
                              borderSide: const BorderSide(
                                color: LunanceColors.primary,
                                width: 2,
                              ),
                            ),
                          ),
                          inputFormatters: [
                            FilteringTextInputFormatter.digitsOnly,
                          ],
                          onChanged: (value) {
                            if (value.isNotEmpty && index < 5) {
                              _focusNodes[index + 1].requestFocus();
                            } else if (value.isEmpty && index > 0) {
                              _focusNodes[index - 1].requestFocus();
                            }
                            
                            // Auto verify when all fields are filled
                            if (index == 5 && value.isNotEmpty) {
                              String otp = _controllers.map((c) => c.text).join();
                              if (otp.length == 6) {
                                _verifyOtp();
                              }
                            }
                          },
                        ),
                      );
                    }),
                  ),
                  
                  const SizedBox(height: 32),
                  
                  // Timer
                  if (!_canResend)
                    Text(
                      'Kirim ulang kode dalam $_formattedTime',
                      style: const TextStyle(
                        color: LunanceColors.textSecondary,
                        fontSize: 14,
                      ),
                      textAlign: TextAlign.center,
                    ),
                  
                  const SizedBox(height: 24),
                  
                  // Verify Button
                  if (state is AuthLoading)
                    const LoadingWidget(message: 'Memverifikasi kode OTP...')
                  else
                    CustomButton(
                      text: 'Verifikasi',
                      onPressed: _verifyOtp,
                      icon: Icons.check,
                    ),
                  
                  const SizedBox(height: 16),
                  
                  // Resend Button
                  CustomButton(
                    text: _canResend ? 'Kirim Ulang Kode' : 'Kirim Ulang ($_formattedTime)',
                    onPressed: _canResend ? _resendOtp : null,
                    isOutlined: true,
                    icon: Icons.refresh,
                  ),
                  
                  const SizedBox(height: 32),
                  
                  // Back Button
                  TextButton(
                    onPressed: () {
                      context.pop();
                    },
                    child: const Text(
                      'Kembali',
                      style: TextStyle(
                        color: LunanceColors.textSecondary,
                      ),
                    ),
                  ),
                ],
              ),
            );
          },
        ),
      ),
    );
  }
}