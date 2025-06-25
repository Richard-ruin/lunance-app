// lib/features/auth/presentation/pages/register_page.dart
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:go_router/go_router.dart';

import '../../../../core/theme/lunance_colors.dart';
import '../../../../shared/widgets/custom_button.dart';
import '../../../../shared/widgets/loading_widget.dart';
import '../bloc/auth_bloc.dart';
import '../bloc/auth_event.dart';
import '../bloc/auth_state.dart';
import '../widgets/auth_text_field.dart';

// Custom TextInputFormatter untuk nomor telepon Indonesia
class IndonesianPhoneFormatter extends TextInputFormatter {
  @override
  TextEditingValue formatEditUpdate(
    TextEditingValue oldValue,
    TextEditingValue newValue,
  ) {
    // Pastikan selalu dimulai dengan +62
    String newText = newValue.text;
    
    if (!newText.startsWith('+62')) {
      // Jika user mencoba menghapus +62, kembalikan ke +62
      if (newText.isEmpty || newText.length < 3) {
        return const TextEditingValue(
          text: '+62',
          selection: TextSelection.collapsed(offset: 3),
        );
      }
      // Jika user mengetik tanpa +62, tambahkan +62
      newText = '+62$newText';
    }
    
    // Hapus karakter non-digit setelah +62
    String digitsOnly = newText.substring(3).replaceAll(RegExp(r'[^\d]'), '');
    
    // Batasi maksimal 10-12 digit setelah +62
    if (digitsOnly.length > 12) {
      digitsOnly = digitsOnly.substring(0, 12);
    }
    
    String formattedText = '+62$digitsOnly';
    
    return TextEditingValue(
      text: formattedText,
      selection: TextSelection.collapsed(offset: formattedText.length),
    );
  }
}

class RegisterPage extends StatefulWidget {
  const RegisterPage({super.key});

  @override
  State<RegisterPage> createState() => _RegisterPageState();
}

class _RegisterPageState extends State<RegisterPage> {
  final _formKey = GlobalKey<FormState>();
  final _pageController = PageController();
  
  // Controllers untuk Step 1 (Data Akun)
  final _emailController = TextEditingController();
  final _passwordController = TextEditingController();
  final _confirmPasswordController = TextEditingController();
  final _fullNameController = TextEditingController();
  
  // Controllers untuk Step 2 (Data Akademik)
  final _universityController = TextEditingController();
  final _facultyController = TextEditingController();
  final _majorController = TextEditingController();
  final _studentIdController = TextEditingController();
  final _phoneController = TextEditingController(text: '+62'); // Set default value
  
  // State variables
  int _currentStep = 0;
  int _semester = 1;
  int _graduationYear = DateTime.now().year + 4;
  bool _obscurePassword = true;
  bool _obscureConfirmPassword = true;
  bool _agreeToTerms = false;

  final List<String> _indonesianUniversities = [
    'Universitas Logistik dan Bisnis Internasional',
    'Universitas Indonesia',
    'Institut Teknologi Bandung',
    'Universitas Gadjah Mada',
    'Institut Teknologi Sepuluh Nopember',
    'Universitas Brawijaya',
    'Universitas Diponegoro',
    'Universitas Padjadjaran',
    'Universitas Airlangga',
    'Universitas Sebelas Maret',
    'Universitas Negeri Yogyakarta',
    'Universitas Hasanuddin',
    'Universitas Lampung',
    'Universitas Riau',
    'Universitas Sumatera Utara',
    'Universitas Andalas',
  ];

  @override
  void dispose() {
    _emailController.dispose();
    _passwordController.dispose();
    _confirmPasswordController.dispose();
    _fullNameController.dispose();
    _universityController.dispose();
    _facultyController.dispose();
    _majorController.dispose();
    _studentIdController.dispose();
    _phoneController.dispose();
    _pageController.dispose();
    super.dispose();
  }

  void _nextStep() {
    if (_currentStep == 0 && _validateStep1()) {
      setState(() {
        _currentStep = 1;
      });
      _pageController.nextPage(
        duration: const Duration(milliseconds: 300),
        curve: Curves.easeInOut,
      );
    } else if (_currentStep == 1 && _validateStep2()) {
      _register();
    }
  }

  void _previousStep() {
    if (_currentStep > 0) {
      setState(() {
        _currentStep--;
      });
      _pageController.previousPage(
        duration: const Duration(milliseconds: 300),
        curve: Curves.easeInOut,
      );
    }
  }

  bool _validateStep1() {
    return _emailController.text.isNotEmpty &&
           _passwordController.text.isNotEmpty &&
           _confirmPasswordController.text.isNotEmpty &&
           _fullNameController.text.isNotEmpty &&
           _passwordController.text == _confirmPasswordController.text;
  }

  bool _validateStep2() {
    return _universityController.text.isNotEmpty &&
           _facultyController.text.isNotEmpty &&
           _majorController.text.isNotEmpty &&
           _studentIdController.text.isNotEmpty &&
           _agreeToTerms;
  }

  String? _getPhoneNumber() {
    String phone = _phoneController.text.trim();
    if (phone.isEmpty || phone == '+62') {
      return null; // Phone is optional
    }
    return phone;
  }

  void _register() {
    if (_formKey.currentState?.validate() ?? false) {
      context.read<AuthBloc>().add(
            AuthRegisterEvent(
              email: _emailController.text.trim(),
              password: _passwordController.text,
              confirmPassword: _confirmPasswordController.text,
              fullName: _fullNameController.text.trim(),
              university: _universityController.text.trim(),
              faculty: _facultyController.text.trim(),
              major: _majorController.text.trim(),
              studentId: _studentIdController.text.trim(),
              semester: _semester,
              graduationYear: _graduationYear,
              phoneNumber: _getPhoneNumber(),
            ),
          );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Daftar Akun Baru'),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          onPressed: () {
            if (_currentStep > 0) {
              _previousStep();
            } else {
              context.pop();
            }
          },
        ),
      ),
      body: BlocConsumer<AuthBloc, AuthState>(
        listener: (context, state) {
          if (state is AuthError) {
            ScaffoldMessenger.of(context).showSnackBar(
              SnackBar(
                content: Text(state.message),
                backgroundColor: LunanceColors.error,
                behavior: SnackBarBehavior.floating,
                margin: const EdgeInsets.all(16),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(8),
                ),
              ),
            );
          } else if (state is AuthRegistrationSuccess) {
            ScaffoldMessenger.of(context).showSnackBar(
              SnackBar(
                content: Text(state.message),
                backgroundColor: LunanceColors.success,
                behavior: SnackBarBehavior.floating,
                margin: const EdgeInsets.all(16),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(8),
                ),
              ),
            );
            // Navigate to OTP verification
            context.push('/verify-otp', extra: {
              'email': state.email,
              'type': 'registration',
            });
          }
        },
        builder: (context, state) {
          if (state is AuthLoading) {
            return const Center(child: LoadingWidget());
          }

          return Column(
            children: [
              // Progress Indicator
              Container(
                padding: const EdgeInsets.all(16),
                child: Row(
                  children: [
                    Expanded(
                      child: LinearProgressIndicator(
                        value: (_currentStep + 1) / 2,
                        backgroundColor: Colors.grey[300],
                        valueColor: const AlwaysStoppedAnimation<Color>(
                          LunanceColors.primary,
                        ),
                      ),
                    ),
                    const SizedBox(width: 16),
                    Text(
                      'Langkah ${_currentStep + 1} dari 2',
                      style: const TextStyle(
                        color: LunanceColors.textSecondary,
                        fontSize: 12,
                      ),
                    ),
                  ],
                ),
              ),
              
              // Form Content
              Expanded(
                child: Form(
                  key: _formKey,
                  child: PageView(
                    controller: _pageController,
                    physics: const NeverScrollableScrollPhysics(),
                    children: [
                      _buildStep1(),
                      _buildStep2(),
                    ],
                  ),
                ),
              ),
              
              // Navigation Buttons
              Container(
                padding: const EdgeInsets.all(16),
                child: Row(
                  children: [
                    if (_currentStep > 0)
                      Expanded(
                        child: OutlinedButton(
                          onPressed: _previousStep,
                          child: const Text('Kembali'),
                        ),
                      ),
                    if (_currentStep > 0) const SizedBox(width: 16),
                    Expanded(
                      child: CustomButton(
                        text: _currentStep == 0 ? 'Lanjutkan' : 'Daftar',
                        onPressed: _nextStep,
                        isLoading: state is AuthLoading,
                      ),
                    ),
                  ],
                ),
              ),
            ],
          );
        },
      ),
    );
  }

  Widget _buildStep1() {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(24.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          const Text(
            'Data Akun',
            style: TextStyle(
              fontSize: 24,
              fontWeight: FontWeight.bold,
              color: LunanceColors.textPrimary,
            ),
          ),
          const SizedBox(height: 8),
          const Text(
            'Silakan isi data akun Anda',
            style: TextStyle(
              fontSize: 14,
              color: LunanceColors.textSecondary,
            ),
          ),
          
          const SizedBox(height: 32),
          
          // Nama Lengkap
          AuthTextField(
            controller: _fullNameController,
            labelText: 'Nama Lengkap',
            hintText: 'Masukkan nama lengkap Anda',
            prefixIcon: Icons.person,
            validator: (value) {
              if (value == null || value.isEmpty) {
                return 'Nama lengkap tidak boleh kosong';
              }
              return null;
            },
          ),
          
          const SizedBox(height: 16),
          
          // Email
          AuthTextField(
            controller: _emailController,
            labelText: 'Email Mahasiswa',
            hintText: 'contoh@mahasiswa.ac.id',
            keyboardType: TextInputType.emailAddress,
            prefixIcon: Icons.email,
            validator: (value) {
              if (value == null || value.isEmpty) {
                return 'Email tidak boleh kosong';
              }
              if (!value.contains('@') || !value.contains('.ac.id')) {
                return 'Gunakan email mahasiswa (.ac.id)';
              }
              return null;
            },
          ),
          
          const SizedBox(height: 16),
          
          // Password
          AuthTextField(
            controller: _passwordController,
            labelText: 'Password',
            hintText: 'Minimal 8 karakter',
            obscureText: _obscurePassword,
            prefixIcon: Icons.lock,
            suffixIcon: IconButton(
              icon: Icon(
                _obscurePassword ? Icons.visibility_off : Icons.visibility,
              ),
              onPressed: () {
                setState(() {
                  _obscurePassword = !_obscurePassword;
                });
              },
            ),
            validator: (value) {
              if (value == null || value.isEmpty) {
                return 'Password tidak boleh kosong';
              }
              if (value.length < 8) {
                return 'Password minimal 8 karakter';
              }
              return null;
            },
          ),
          
          const SizedBox(height: 16),
          
          // Confirm Password
          AuthTextField(
            controller: _confirmPasswordController,
            labelText: 'Konfirmasi Password',
            hintText: 'Ulangi password Anda',
            obscureText: _obscureConfirmPassword,
            prefixIcon: Icons.lock_outline,
            suffixIcon: IconButton(
              icon: Icon(
                _obscureConfirmPassword ? Icons.visibility_off : Icons.visibility,
              ),
              onPressed: () {
                setState(() {
                  _obscureConfirmPassword = !_obscureConfirmPassword;
                });
              },
            ),
            validator: (value) {
              if (value == null || value.isEmpty) {
                return 'Konfirmasi password tidak boleh kosong';
              }
              if (value != _passwordController.text) {
                return 'Password tidak sama';
              }
              return null;
            },
          ),
        ],
      ),
    );
  }

  Widget _buildStep2() {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(24.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          const Text(
            'Data Akademik',
            style: TextStyle(
              fontSize: 24,
              fontWeight: FontWeight.bold,
              color: LunanceColors.textPrimary,
            ),
          ),
          const SizedBox(height: 8),
          const Text(
            'Isi data universitas dan program studi Anda',
            style: TextStyle(
              fontSize: 14,
              color: LunanceColors.textSecondary,
            ),
          ),
          
          const SizedBox(height: 32),
          
          // Universitas
          AuthTextField(
            controller: _universityController,
            labelText: 'Universitas',
            hintText: 'Pilih universitas Anda',
            prefixIcon: Icons.school,
            readOnly: true,
            onTap: () => _showUniversityPicker(),
            validator: (value) {
              if (value == null || value.isEmpty) {
                return 'Universitas tidak boleh kosong';
              }
              return null;
            },
          ),
          
          const SizedBox(height: 16),
          
          // Fakultas
          AuthTextField(
            controller: _facultyController,
            labelText: 'Fakultas',
            hintText: 'Masukkan fakultas Anda',
            prefixIcon: Icons.account_balance,
            validator: (value) {
              if (value == null || value.isEmpty) {
                return 'Fakultas tidak boleh kosong';
              }
              return null;
            },
          ),
          
          const SizedBox(height: 16),
          
          // Program Studi
          AuthTextField(
            controller: _majorController,
            labelText: 'Program Studi',
            hintText: 'Masukkan program studi Anda',
            prefixIcon: Icons.menu_book,
            validator: (value) {
              if (value == null || value.isEmpty) {
                return 'Program studi tidak boleh kosong';
              }
              return null;
            },
          ),
          
          const SizedBox(height: 16),
          
          // NIM
          AuthTextField(
            controller: _studentIdController,
            labelText: 'NIM (Nomor Induk Mahasiswa)',
            hintText: 'Masukkan NIM Anda',
            prefixIcon: Icons.badge,
            keyboardType: TextInputType.text,
            validator: (value) {
              if (value == null || value.isEmpty) {
                return 'NIM tidak boleh kosong';
              }
              return null;
            },
          ),
          
          const SizedBox(height: 16),
          
          // Semester dan Tahun Lulus
          Row(
            children: [
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text(
                      'Semester',
                      style: TextStyle(
                        fontSize: 14,
                        fontWeight: FontWeight.w500,
                        color: LunanceColors.textPrimary,
                      ),
                    ),
                    const SizedBox(height: 8),
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 16),
                      decoration: BoxDecoration(
                        color: LunanceColors.surfaceVariant,
                        borderRadius: BorderRadius.circular(12),
                      ),
                      child: DropdownButtonHideUnderline(
                        child: DropdownButton<int>(
                          value: _semester,
                          isExpanded: true,
                          items: List.generate(14, (index) => index + 1)
                              .map((semester) => DropdownMenuItem(
                                    value: semester,
                                    child: Text('Semester $semester'),
                                  ))
                              .toList(),
                          onChanged: (value) {
                            setState(() {
                              _semester = value ?? 1;
                            });
                          },
                        ),
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(width: 16),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text(
                      'Tahun Lulus',
                      style: TextStyle(
                        fontSize: 14,
                        fontWeight: FontWeight.w500,
                        color: LunanceColors.textPrimary,
                      ),
                    ),
                    const SizedBox(height: 8),
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 16),
                      decoration: BoxDecoration(
                        color: LunanceColors.surfaceVariant,
                        borderRadius: BorderRadius.circular(12),
                      ),
                      child: DropdownButtonHideUnderline(
                        child: DropdownButton<int>(
                          value: _graduationYear,
                          isExpanded: true,
                          items: List.generate(8, (index) => DateTime.now().year + index)
                              .map((year) => DropdownMenuItem(
                                    value: year,
                                    child: Text(year.toString()),
                                  ))
                              .toList(),
                          onChanged: (value) {
                            setState(() {
                              _graduationYear = value ?? DateTime.now().year + 4;
                            });
                          },
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
          
          const SizedBox(height: 16),
          
          // Nomor HP dengan Prefix +62
          Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text(
                'Nomor HP (Opsional)',
                style: TextStyle(
                  fontSize: 14,
                  fontWeight: FontWeight.w500,
                  color: LunanceColors.textPrimary,
                ),
              ),
              const SizedBox(height: 8),
              Container(
                decoration: BoxDecoration(
                  color: LunanceColors.surfaceVariant,
                  borderRadius: BorderRadius.circular(12),
                ),
                child: TextField(
                  controller: _phoneController,
                  keyboardType: TextInputType.phone,
                  inputFormatters: [
                    IndonesianPhoneFormatter(),
                  ],
                  style: const TextStyle(
                    fontSize: 16,
                  ),
                  decoration: InputDecoration(
                    hintText: '+6281234567890',
                    hintStyle: const TextStyle(
                      color: LunanceColors.textSecondary,
                    ),
                    prefixIcon: const Icon(
                      Icons.phone,
                      color: LunanceColors.textSecondary,
                    ),
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
                    contentPadding: const EdgeInsets.symmetric(
                      horizontal: 16,
                      vertical: 16,
                    ),
                  ),
                  onTap: () {
                    // Pastikan cursor berada setelah +62
                    if (_phoneController.selection.start < 3) {
                      _phoneController.selection = const TextSelection.collapsed(offset: 3);
                    }
                  },
                ),
              ),
              const SizedBox(height: 4),
              const Text(
                'Format: +62 diikuti nomor HP tanpa angka 0 di depan',
                style: TextStyle(
                  fontSize: 12,
                  color: LunanceColors.textSecondary,
                ),
              ),
            ],
          ),
          
          const SizedBox(height: 24),
          
          // Terms and Conditions
          Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Checkbox(
                value: _agreeToTerms,
                onChanged: (value) {
                  setState(() {
                    _agreeToTerms = value ?? false;
                  });
                },
              ),
              Expanded(
                child: GestureDetector(
                  onTap: () {
                    setState(() {
                      _agreeToTerms = !_agreeToTerms;
                    });
                  },
                  child: const Text(
                    'Saya menyetujui Syarat dan Ketentuan serta Kebijakan Privasi Lunance',
                    style: TextStyle(
                      fontSize: 14,
                      color: LunanceColors.textSecondary,
                    ),
                  ),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  void _showUniversityPicker() {
    showModalBottomSheet(
      context: context,
      builder: (BuildContext context) {
        return Container(
          padding: const EdgeInsets.all(16),
          height: 400,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              const Text(
                'Pilih Universitas',
                style: TextStyle(
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                ),
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 16),
              Expanded(
                child: ListView.builder(
                  itemCount: _indonesianUniversities.length,
                  itemBuilder: (context, index) {
                    final university = _indonesianUniversities[index];
                    return ListTile(
                      title: Text(university),
                      onTap: () {
                        setState(() {
                          _universityController.text = university;
                        });
                        Navigator.pop(context);
                      },
                    );
                  },
                ),
              ),
            ],
          ),
        );
      },
    );
  }
}