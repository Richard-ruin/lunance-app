import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../../providers/auth_provider.dart';
import '../../themes/app_theme.dart';
import '../../utils/constants.dart';
import '../../widgets/common/loading_overlay.dart';
import '../../widgets/auth/registration_progress_indicator.dart';
import '../../widgets/auth/register_step_1.dart';
import '../../widgets/auth/register_step_2.dart';
import '../../widgets/auth/register_step_3.dart';
import '../../widgets/auth/register_step_4.dart';
import '../../widgets/auth/register_step_5.dart';

class RegisterScreen extends StatefulWidget {
  const RegisterScreen({super.key});

  @override
  State<RegisterScreen> createState() => _RegisterScreenState();
}

class _RegisterScreenState extends State<RegisterScreen> {
  final PageController _pageController = PageController();

  @override
  void initState() {
    super.initState();
    // Reset registration when starting
    WidgetsBinding.instance.addPostFrameCallback((_) {
      context.read<AuthProvider>().resetRegistration();
    });
  }

  @override
  void dispose() {
    _pageController.dispose();
    super.dispose();
  }

  void _onStepCompleted() {
    final authProvider = context.read<AuthProvider>();
    final nextStep = authProvider.registrationStep;
    
    if (nextStep <= 5) {
      _pageController.animateToPage(
        nextStep - 1,
        duration: AppTheme.animationMedium,
        curve: Curves.easeInOut,
      );
    } else {
      // Registration complete, navigate to main screen
      Navigator.pushReplacementNamed(context, '/student');
    }
  }

  void _goToPreviousStep() {
    final authProvider = context.read<AuthProvider>();
    if (authProvider.registrationStep > 1) {
      authProvider.goToPreviousStep();
      _pageController.animateToPage(
        authProvider.registrationStep - 1,
        duration: AppTheme.animationMedium,
        curve: Curves.easeInOut,
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Daftar Akun'),
        leading: Consumer<AuthProvider>(
          builder: (context, authProvider, child) {
            return IconButton(
              icon: const Icon(Icons.arrow_back),
              onPressed: () {
                if (authProvider.registrationStep > 1) {
                  _goToPreviousStep();
                } else {
                  Navigator.pop(context);
                }
              },
            );
          },
        ),
      ),
      body: Consumer<AuthProvider>(
        builder: (context, authProvider, child) {
          return LoadingOverlay(
            isLoading: authProvider.isLoading,
            child: Column(
              children: [
                // Progress indicator
                RegistrationProgressIndicator(
                  currentStep: authProvider.registrationStep,
                  totalSteps: 5,
                ),
                
                // Step content - Expanded to fill available space
                Expanded(
                  child: PageView(
                    controller: _pageController,
                    physics: const NeverScrollableScrollPhysics(),
                    children: [
                      RegisterStep1(onCompleted: _onStepCompleted),
                      RegisterStep2(onCompleted: _onStepCompleted),
                      RegisterStep3(onCompleted: _onStepCompleted),
                      RegisterStep4(onCompleted: _onStepCompleted),
                      RegisterStep5(onCompleted: _onStepCompleted),
                    ],
                  ),
                ),
              ],
            ),
          );
        },
      ),
    );
  }
}