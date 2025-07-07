import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../../providers/auth_provider.dart';
import '../../providers/university_provider.dart';
import '../../models/university_model.dart';
import '../../themes/app_theme.dart';
import '../../utils/constants.dart';
import '../../utils/validators.dart';
import '../common/custom_button.dart';
import '../common/custom_dropdown.dart';

class RegisterStep2 extends StatefulWidget {
  final VoidCallback onCompleted;

  const RegisterStep2({
    super.key,
    required this.onCompleted,
  });

  @override
  State<RegisterStep2> createState() => _RegisterStep2State();
}

class _RegisterStep2State extends State<RegisterStep2> {
  final _formKey = GlobalKey<FormState>();
  
  String? _selectedUniversityId;
  String? _selectedFakultasId;
  String? _selectedProdiId;

  @override
  void initState() {
    super.initState();
    _loadUniversities();
  }

  void _loadUniversities() {
    WidgetsBinding.instance.addPostFrameCallback((_) {
      context.read<UniversityProvider>().getUniversities();
    });
  }

  void _onUniversityChanged(String? universityId) {
    setState(() {
      _selectedUniversityId = universityId;
      _selectedFakultasId = null;
      _selectedProdiId = null;
    });

    if (universityId != null) {
      context.read<UniversityProvider>().getFakultasByUniversityId(universityId);
    }
  }

  void _onFakultasChanged(String? fakultasId) {
    setState(() {
      _selectedFakultasId = fakultasId;
      _selectedProdiId = null;
    });

    if (fakultasId != null) {
      context.read<UniversityProvider>().getProdiByfakultasId(fakultasId);
    }
  }

  void _onProdiChanged(String? prodiId) {
    setState(() {
      _selectedProdiId = prodiId;
    });
  }

  Future<void> _handleNext() async {
    if (!_formKey.currentState!.validate()) return;

    final authProvider = context.read<AuthProvider>();

    final success = await authProvider.registerStep2(
      universityId: _selectedUniversityId!,
      fakultasId: _selectedFakultasId!,
      prodiId: _selectedProdiId!,
    );

    if (success) {
      widget.onCompleted();
    } else {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(authProvider.errorMessage ?? 'Gagal menyimpan data akademik'),
            backgroundColor: Theme.of(context).colorScheme.error,
          ),
        );
      }
    }
  }

  void _showRequestUniversityDialog() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Request Universitas Baru'),
        content: const Text(
          'Fitur request universitas baru akan segera tersedia. '
          'Untuk sementara, silakan hubungi admin untuk menambahkan universitas Anda.',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('OK'),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        // Form content - menggunakan Expanded untuk mengisi ruang yang tersedia
        Expanded(
          child: SingleChildScrollView(
            padding: const EdgeInsets.all(AppTheme.spacingL),
            child: Form(
              key: _formKey,
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  // Step header
                  _buildStepHeader(),
                  
                  const SizedBox(height: AppTheme.spacingXL),
                  
                  // Form fields
                  Consumer<UniversityProvider>(
                    builder: (context, universityProvider, child) {
                      return Column(
                        children: [
                          // University dropdown
                          CustomDropdown<String>(
                            label: AppConstants.universityLabel,
                            value: _selectedUniversityId,
                            onChanged: _onUniversityChanged,
                            validator: Validators.validateUniversitySelection,
                            items: universityProvider.universities
                                .map((uni) => DropdownMenuItem<String>(
                                      value: uni.id,
                                      child: Text(uni.nama),
                                    ))
                                .toList(),
                            isLoading: universityProvider.isLoading && 
                                      universityProvider.universities.isEmpty,
                            hintText: 'Pilih universitas Anda',
                          ),
                          
                          const SizedBox(height: AppTheme.spacingS),
                          
                          // Request new university button
                          Align(
                            alignment: Alignment.centerRight,
                            child: TextButton.icon(
                              onPressed: _showRequestUniversityDialog,
                              icon: const Icon(Icons.add, size: 16),
                              label: const Text('Request Universitas Baru'),
                            ),
                          ),
                          
                          const SizedBox(height: AppTheme.spacingM),
                          
                          // Fakultas dropdown
                          CustomDropdown<String>(
                            label: AppConstants.fakultasLabel,
                            value: _selectedFakultasId,
                            onChanged: _onFakultasChanged,
                            validator: Validators.validateFakultasSelection,
                            items: universityProvider.fakultasList
                                .map((fakultas) => DropdownMenuItem<String>(
                                      value: fakultas.id,
                                      child: Text(fakultas.nama),
                                    ))
                                .toList(),
                            isLoading: universityProvider.isLoading && 
                                      _selectedUniversityId != null &&
                                      universityProvider.fakultasList.isEmpty,
                            hintText: 'Pilih fakultas Anda',
                            enabled: _selectedUniversityId != null,
                          ),
                          
                          const SizedBox(height: AppTheme.spacingM),
                          
                          // Prodi dropdown
                          CustomDropdown<String>(
                            label: AppConstants.prodiLabel,
                            value: _selectedProdiId,
                            onChanged: _onProdiChanged,
                            validator: Validators.validateProdiSelection,
                            items: universityProvider.prodiList
                                .map((prodi) => DropdownMenuItem<String>(
                                      value: prodi.id,
                                      child: Text('${prodi.nama} (${prodi.jenjang.value})'),
                                    ))
                                .toList(),
                            isLoading: universityProvider.isLoading && 
                                      _selectedFakultasId != null &&
                                      universityProvider.prodiList.isEmpty,
                            hintText: 'Pilih program studi Anda',
                            enabled: _selectedFakultasId != null,
                          ),
                          
                          const SizedBox(height: AppTheme.spacingL),
                          
                          // Selected info
                          if (_selectedUniversityId != null ||
                              _selectedFakultasId != null ||
                              _selectedProdiId != null)
                            _buildSelectedInfo(universityProvider),
                        ],
                      );
                    },
                  ),
                ],
              ),
            ),
          ),
        ),
        
        // Next button - fixed di bawah, tidak ikut scroll
        Container(
          padding: const EdgeInsets.all(AppTheme.spacingL),
          decoration: BoxDecoration(
            color: Theme.of(context).scaffoldBackgroundColor,
            border: Border(
              top: BorderSide(
                color: Theme.of(context).dividerColor,
                width: 0.5,
              ),
            ),
          ),
          child: Consumer<AuthProvider>(
            builder: (context, authProvider, child) {
              return CustomButton(
                onPressed: authProvider.isLoading ? null : _handleNext,
                text: AppConstants.nextButton,
                isLoading: authProvider.isLoading,
                variant: ButtonVariant.primary,
              );
            },
          ),
        ),
      ],
    );
  }

  Widget _buildStepHeader() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'Data Akademik',
          style: Theme.of(context).textTheme.headlineMedium?.copyWith(
            fontWeight: FontWeight.bold,
          ),
        ),
        
        const SizedBox(height: AppTheme.spacingS),
        
        Text(
          'Pilih universitas, fakultas, dan program studi Anda',
          style: Theme.of(context).textTheme.bodyMedium?.copyWith(
            color: Theme.of(context).colorScheme.onSurfaceVariant,
          ),
        ),
      ],
    );
  }

  Widget _buildSelectedInfo(UniversityProvider provider) {
    final selectedUniversity = provider.universities
        .where((uni) => uni.id == _selectedUniversityId)
        .firstOrNull;
    final selectedFakultas = provider.fakultasList
        .where((fakultas) => fakultas.id == _selectedFakultasId)
        .firstOrNull;
    final selectedProdi = provider.prodiList
        .where((prodi) => prodi.id == _selectedProdiId)
        .firstOrNull;

    return Container(
      padding: const EdgeInsets.all(AppTheme.spacingM),
      decoration: BoxDecoration(
        color: Theme.of(context).colorScheme.surfaceVariant,
        borderRadius: BorderRadius.circular(AppTheme.borderRadiusSmall),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Data yang dipilih:',
            style: Theme.of(context).textTheme.labelMedium?.copyWith(
              fontWeight: FontWeight.w600,
            ),
          ),
          const SizedBox(height: AppTheme.spacingS),
          if (selectedUniversity != null) ...[
            _buildInfoRow('Universitas', selectedUniversity.nama),
          ],
          if (selectedFakultas != null) ...[
            _buildInfoRow('Fakultas', selectedFakultas.nama),
          ],
          if (selectedProdi != null) ...[
            _buildInfoRow('Program Studi', '${selectedProdi.nama} (${selectedProdi.jenjang.value})'),
          ],
        ],
      ),
    );
  }

  Widget _buildInfoRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.only(bottom: AppTheme.spacingXS),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SizedBox(
            width: 100,
            child: Text(
              label,
              style: Theme.of(context).textTheme.bodySmall?.copyWith(
                color: Theme.of(context).colorScheme.onSurfaceVariant,
              ),
            ),
          ),
          const Text(': '),
          Expanded(
            child: Text(
              value,
              style: Theme.of(context).textTheme.bodySmall?.copyWith(
                fontWeight: FontWeight.w500,
              ),
            ),
          ),
        ],
      ),
    );
  }
}