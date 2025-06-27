// lib/features/settings/presentation/pages/profile_edit_page.dart (Fixed)
import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:go_router/go_router.dart';
import 'package:image_picker/image_picker.dart';
import 'dart:io';

import '../../../../shared/widgets/sub_layout.dart';
import '../../../../shared/widgets/custom_text_field.dart';
import '../../../../shared/widgets/loading_widget.dart';
import '../../../../shared/utils/validators.dart';
import '../../../../core/di/injection_container.dart';
import '../../../auth/presentation/bloc/auth_bloc.dart';
import '../../../auth/presentation/bloc/auth_event.dart';
import '../../../auth/presentation/bloc/auth_state.dart';

class ProfileEditPage extends StatelessWidget {
  const ProfileEditPage({super.key});

  @override
  Widget build(BuildContext context) {
    return BlocProvider(
      create: (context) => sl<AuthBloc>()..add(const AuthGetUserEvent()),
      child: const ProfileEditView(),
    );
  }
}

class ProfileEditView extends StatefulWidget {
  const ProfileEditView({super.key});

  @override
  State<ProfileEditView> createState() => _ProfileEditViewState();
}

class _ProfileEditViewState extends State<ProfileEditView> {
  final _formKey = GlobalKey<FormState>();
  final _nameController = TextEditingController();
  final _phoneController = TextEditingController();
  final _universityController = TextEditingController();
  final _facultyController = TextEditingController();
  final _majorController = TextEditingController();
  final _semesterController = TextEditingController();
  
  File? _selectedImage;
  final ImagePicker _picker = ImagePicker();
  bool _hasChanges = false;

  @override
  void initState() {
    super.initState();
    // Add listeners to detect changes
    _nameController.addListener(_onFieldChanged);
    _phoneController.addListener(_onFieldChanged);
    _universityController.addListener(_onFieldChanged);
    _facultyController.addListener(_onFieldChanged);
    _majorController.addListener(_onFieldChanged);
    _semesterController.addListener(_onFieldChanged);
  }

  void _onFieldChanged() {
    if (!_hasChanges) {
      setState(() {
        _hasChanges = true;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return SubLayout(
      title: 'Edit Profil',
      onBackPressed: () => _handleBackPressed(context),
      body: BlocConsumer<AuthBloc, AuthState>(
        listener: (context, state) {
          if (state is AuthUpdateProfileSuccess) {
            _showSuccessDialog(context, state.message);
          } else if (state is AuthError) {
            ScaffoldMessenger.of(context).showSnackBar(
              SnackBar(
                content: Text(state.message),
                backgroundColor: Colors.red,
                behavior: SnackBarBehavior.floating,
              ),
            );
          } else if (state is AuthAuthenticated) {
            _populateFields(state);
          }
        },
        builder: (context, state) {
          if (state is AuthLoading && _nameController.text.isEmpty) {
            return const LoadingWidget(message: 'Memuat data profil...');
          }

          final isLoading = state is AuthLoading;
          
          return SingleChildScrollView(
            padding: const EdgeInsets.all(16),
            child: Form(
              key: _formKey,
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // Profile Picture Section
                  Center(
                    child: Column(
                      children: [
                        Stack(
                          children: [
                            CircleAvatar(
                              radius: 60,
                              backgroundColor: Theme.of(context).colorScheme.surfaceContainerHighest,
                              backgroundImage: _selectedImage != null 
                                  ? FileImage(_selectedImage!)
                                  : null,
                              child: _selectedImage == null 
                                  ? Icon(
                                      Icons.person,
                                      size: 60,
                                      color: Theme.of(context).colorScheme.onSurface,
                                    )
                                  : null,
                            ),
                            Positioned(
                              bottom: 0,
                              right: 0,
                              child: CircleAvatar(
                                radius: 20,
                                backgroundColor: Theme.of(context).colorScheme.primary,
                                child: IconButton(
                                  icon: const Icon(
                                    Icons.camera_alt,
                                    size: 20,
                                    color: Colors.white,
                                  ),
                                  onPressed: isLoading ? null : _pickImage,
                                ),
                              ),
                            ),
                          ],
                        ),
                        const SizedBox(height: 8),
                        Text(
                          'Tap untuk mengubah foto profil',
                          style: Theme.of(context).textTheme.bodySmall?.copyWith(
                            color: Theme.of(context).colorScheme.onSurface.withOpacity(0.6),
                          ),
                        ),
                      ],
                    ),
                  ),
                  
                  const SizedBox(height: 32),
                  
                  // Personal Information
                  Text(
                    'Informasi Pribadi',
                    style: Theme.of(context).textTheme.titleMedium?.copyWith(
                      fontWeight: FontWeight.bold,
                      color: Theme.of(context).colorScheme.primary,
                    ),
                  ),
                  const SizedBox(height: 16),
                  
                  CustomTextField(
                    label: 'Nama Lengkap *',
                    controller: _nameController,
                    prefixIcon: const Icon(Icons.person_outline),
                    validator: (value) => Validators.required(value, 'Nama lengkap'),
                    enabled: !isLoading,
                  ),
                  
                  const SizedBox(height: 16),
                  
                  CustomTextField(
                    label: 'Nomor Telepon',
                    controller: _phoneController,
                    prefixIcon: const Icon(Icons.phone_outlined),
                    keyboardType: TextInputType.phone,
                    validator: Validators.phone,
                    enabled: !isLoading,
                  ),
                  
                  const SizedBox(height: 24),
                  
                  // Academic Information
                  Text(
                    'Informasi Akademik',
                    style: Theme.of(context).textTheme.titleMedium?.copyWith(
                      fontWeight: FontWeight.bold,
                      color: Theme.of(context).colorScheme.primary,
                    ),
                  ),
                  const SizedBox(height: 16),
                  
                  CustomTextField(
                    label: 'Universitas *',
                    controller: _universityController,
                    prefixIcon: const Icon(Icons.school_outlined),
                    validator: (value) => Validators.required(value, 'Universitas'),
                    enabled: !isLoading,
                  ),
                  
                  const SizedBox(height: 16),
                  
                  CustomTextField(
                    label: 'Fakultas *',
                    controller: _facultyController,
                    prefixIcon: const Icon(Icons.account_balance_outlined),
                    validator: (value) => Validators.required(value, 'Fakultas'),
                    enabled: !isLoading,
                  ),
                  
                  const SizedBox(height: 16),
                  
                  CustomTextField(
                    label: 'Jurusan *',
                    controller: _majorController,
                    prefixIcon: const Icon(Icons.book_outlined),
                    validator: (value) => Validators.required(value, 'Jurusan'),
                    enabled: !isLoading,
                  ),
                  
                  const SizedBox(height: 16),
                  
                  CustomTextField(
                    label: 'Semester *',
                    controller: _semesterController,
                    prefixIcon: const Icon(Icons.schedule_outlined),
                    keyboardType: TextInputType.number,
                    validator: (value) {
                      if (value == null || value.isEmpty) {
                        return 'Semester harus diisi';
                      }
                      final semester = int.tryParse(value);
                      if (semester == null || semester < 1 || semester > 14) {
                        return 'Semester harus antara 1-14';
                      }
                      return null;
                    },
                    enabled: !isLoading,
                  ),
                  
                  const SizedBox(height: 32),
                  
                  // Action Buttons
                  Row(
                    children: [
                      Expanded(
                        child: OutlinedButton(
                          onPressed: isLoading ? null : () => _handleBackPressed(context),
                          child: const Text('Batal'),
                        ),
                      ),
                      const SizedBox(width: 16),
                      Expanded(
                        child: ElevatedButton(
                          onPressed: isLoading || !_hasChanges ? null : _handleSaveProfile,
                          child: isLoading 
                              ? const SizedBox(
                                  width: 20,
                                  height: 20,
                                  child: CircularProgressIndicator(strokeWidth: 2),
                                )
                              : const Text('Simpan'),
                        ),
                      ),
                    ],
                  ),
                  
                  const SizedBox(height: 24),
                ],
              ),
            ),
          );
        },
      ),
    );
  }

  void _populateFields(AuthAuthenticated state) {
    final user = state.user;
    _nameController.text = user.fullName;
    _phoneController.text = user.phoneNumber ?? '';
    _universityController.text = user.university;
    _facultyController.text = user.faculty;
    _majorController.text = user.major;
    _semesterController.text = user.semester.toString();
    
    // Reset change detection after populating
    setState(() {
      _hasChanges = false;
    });
  }

  Future<void> _pickImage() async {
    try {
      final pickedFile = await _picker.pickImage(
        source: ImageSource.gallery,
        maxWidth: 500,
        maxHeight: 500,
        imageQuality: 80,
      );

      if (pickedFile != null) {
        setState(() {
          _selectedImage = File(pickedFile.path);
          _hasChanges = true;
        });
      }
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Gagal memilih gambar: ${e.toString()}'),
          backgroundColor: Colors.red,
        ),
      );
    }
  }

  void _handleSaveProfile() {
    if (_formKey.currentState?.validate() ?? false) {
      context.read<AuthBloc>().add(
        AuthUpdateProfileEvent(
          fullName: _nameController.text,
          phoneNumber: _phoneController.text.isEmpty ? null : _phoneController.text,
          university: _universityController.text,
          faculty: _facultyController.text,
          major: _majorController.text,
          semester: int.parse(_semesterController.text),
          profileImage: _selectedImage,
        ),
      );
    }
  }

  void _handleBackPressed(BuildContext context) {
    if (_hasChanges) {
      _showUnsavedChangesDialog(context);
    } else {
      context.go('/settings');
    }
  }

  void _showUnsavedChangesDialog(BuildContext context) {
    showDialog(
      context: context,
      builder: (dialogContext) => AlertDialog(
        title: const Text('Perubahan Belum Disimpan'),
        content: const Text('Anda memiliki perubahan yang belum disimpan. Apakah Anda yakin ingin keluar?'),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(dialogContext).pop(),
            child: const Text('Tetap di Sini'),
          ),
          TextButton(
            onPressed: () {
              Navigator.of(dialogContext).pop();
              context.go('/settings');
            },
            style: TextButton.styleFrom(foregroundColor: Colors.red),
            child: const Text('Keluar Tanpa Menyimpan'),
          ),
        ],
      ),
    );
  }

  void _showSuccessDialog(BuildContext context, String message) {
    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (dialogContext) => AlertDialog(
        icon: const Icon(
          Icons.check_circle,
          color: Colors.green,
          size: 48,
        ),
        title: const Text('Berhasil'),
        content: Text(message),
        actions: [
          ElevatedButton(
            onPressed: () {
              Navigator.of(dialogContext).pop();
              setState(() {
                _hasChanges = false;
              });
              context.go('/settings');
            },
            child: const Text('OK'),
          ),
        ],
      ),
    );
  }

  @override
  void dispose() {
    _nameController.removeListener(_onFieldChanged);
    _phoneController.removeListener(_onFieldChanged);
    _universityController.removeListener(_onFieldChanged);
    _facultyController.removeListener(_onFieldChanged);
    _majorController.removeListener(_onFieldChanged);
    _semesterController.removeListener(_onFieldChanged);
    
    _nameController.dispose();
    _phoneController.dispose();
    _universityController.dispose();
    _facultyController.dispose();
    _majorController.dispose();
    _semesterController.dispose();
    super.dispose();
  }
}