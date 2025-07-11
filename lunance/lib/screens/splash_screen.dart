import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/auth_provider.dart';
import '../utils/app_text_styles.dart';
import 'auth/login_screen.dart';
import 'onboarding/profile_setup_screen.dart';
import 'onboarding/financial_setup_screen.dart';
import 'dashboard/dashboard_screen.dart';

class SplashScreen extends StatefulWidget {
  const SplashScreen({Key? key}) : super(key: key);

  @override
  State<SplashScreen> createState() => _SplashScreenState();
}

class _SplashScreenState extends State<SplashScreen>
    with SingleTickerProviderStateMixin {
  late AnimationController _animationController;
  late Animation<double> _fadeAnimation;
  late Animation<double> _scaleAnimation;

  // Standalone colors - no dependency on AppColors
  static const Color _primary = Color(0xFF87CEEB); // Sky Blue
  static const Color _primaryDark = Color(0xFF5BB3D9);
  static const Color _white = Color(0xFFFFFFFF);
  static const Color _shadow = Color(0x1A000000);

  @override
  void initState() {
    super.initState();
    
    _animationController = AnimationController(
      duration: const Duration(milliseconds: 1500),
      vsync: this,
    );

    _fadeAnimation = Tween<double>(
      begin: 0.0,
      end: 1.0,
    ).animate(CurvedAnimation(
      parent: _animationController,
      curve: const Interval(0.0, 0.6, curve: Curves.easeOut),
    ));

    _scaleAnimation = Tween<double>(
      begin: 0.8,
      end: 1.0,
    ).animate(CurvedAnimation(
      parent: _animationController,
      curve: const Interval(0.0, 0.6, curve: Curves.elasticOut),
    ));

    _startSplashSequence();
  }

  void _startSplashSequence() async {
    // Start animation
    _animationController.forward();
    
    // Wait for animation to complete
    await Future.delayed(const Duration(milliseconds: 1500));
    
    // Initialize auth
    if (mounted) {
      await context.read<AuthProvider>().initialize();
      
      // Wait additional time to complete 3 seconds
      await Future.delayed(const Duration(milliseconds: 1500));
      
      // Navigate based on auth state
      if (mounted) {
        _navigateBasedOnAuthState();
      }
    }
  }

  void _navigateBasedOnAuthState() {
    final authProvider = context.read<AuthProvider>();
    
    Widget nextScreen;
    
    if (authProvider.isAuthenticated) {
      if (authProvider.needsProfileSetup) {
        nextScreen = const ProfileSetupScreen();
      } else if (authProvider.needsFinancialSetup) {
        nextScreen = const FinancialSetupScreen();
      } else {
        nextScreen = const DashboardScreen();
      }
    } else {
      nextScreen = const LoginScreen();
    }

    Navigator.of(context).pushReplacement(
      PageRouteBuilder(
        pageBuilder: (context, animation, secondaryAnimation) => nextScreen,
        transitionDuration: const Duration(milliseconds: 300),
        transitionsBuilder: (context, animation, secondaryAnimation, child) {
          return FadeTransition(opacity: animation, child: child);
        },
      ),
    );
  }

  @override
  void dispose() {
    _animationController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Container(
        decoration: const BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
            colors: [
              _primary,
              _primaryDark,
            ],
          ),
        ),
        child: Center(
          child: AnimatedBuilder(
            animation: _animationController,
            builder: (context, child) {
              return FadeTransition(
                opacity: _fadeAnimation,
                child: ScaleTransition(
                  scale: _scaleAnimation,
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      // Logo/Icon
                      Container(
                        width: 120,
                        height: 120,
                        decoration: BoxDecoration(
                          color: _white,
                          borderRadius: BorderRadius.circular(30),
                          boxShadow: [
                            BoxShadow(
                              color: _shadow,
                              blurRadius: 20,
                              offset: const Offset(0, 10),
                            ),
                          ],
                        ),
                        child: const Icon(
                          Icons.account_balance_wallet_rounded,
                          size: 60,
                          color: _primary,
                        ),
                      ),
                      
                      const SizedBox(height: 32),
                      
                      // App Name
                      Text(
                        'Lunance',
                        style: const TextStyle(
                          fontSize: 36,
                          fontWeight: FontWeight.w700,
                          color: _white,
                        ),
                      ),
                      
                      const SizedBox(height: 8),
                      
                      // Tagline
                      Text(
                        'Personal Finance AI Assistant',
                        style: TextStyle(
                          fontSize: 16,
                          color: _white.withOpacity(0.9),
                        ),
                      ),
                      
                      const SizedBox(height: 48),
                      
                      // Loading indicator
                      SizedBox(
                        width: 40,
                        height: 40,
                        child: CircularProgressIndicator(
                          strokeWidth: 3,
                          valueColor: AlwaysStoppedAnimation<Color>(
                            _white.withOpacity(0.8),
                          ),
                        ),
                      ),
                      
                      const SizedBox(height: 16),
                      
                      // Loading text
                      Text(
                        'Memuat aplikasi...',
                        style: TextStyle(
                          fontSize: 14,
                          color: _white.withOpacity(0.8),
                        ),
                      ),
                    ],
                  ),
                ),
              );
            },
          ),
        ),
      ),
    );
  }
}