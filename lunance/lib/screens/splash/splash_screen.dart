// lib/screens/splash/splash_screen.dart
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../providers/auth_provider.dart';
import '../../utils/constants.dart';
import '../../utils/routes.dart';

class SplashScreen extends StatefulWidget {
  const SplashScreen({super.key});

  @override
  State<SplashScreen> createState() => _SplashScreenState();
}

class _SplashScreenState extends State<SplashScreen>
    with SingleTickerProviderStateMixin {
  late AnimationController _animationController;
  late Animation<double> _fadeAnimation;
  late Animation<double> _scaleAnimation;

  @override
  void initState() {
    super.initState();
    _initializeAnimations();
    _initializeApp();
  }

  void _initializeAnimations() {
    _animationController = AnimationController(
      duration: const Duration(seconds: 2),
      vsync: this,
    );

    _fadeAnimation = Tween<double>(
      begin: 0.0,
      end: 1.0,
    ).animate(CurvedAnimation(
      parent: _animationController,
      curve: Curves.easeInOut,
    ));

    _scaleAnimation = Tween<double>(
      begin: 0.5,
      end: 1.0,
    ).animate(CurvedAnimation(
      parent: _animationController,
      curve: Curves.elasticOut,
    ));

    _animationController.forward();
  }

  void _initializeApp() async {
    // Wait for AuthProvider to initialize
    final authProvider = Provider.of<AuthProvider>(context, listen: false);
    
    // Wait for minimum splash duration and auth initialization
    await Future.wait([
      Future.delayed(AppConstants.splashDuration),
      _waitForAuthInitialization(authProvider),
    ]);
    
    if (mounted) {
      _navigateToNextScreen(authProvider);
    }
  }

  Future<void> _waitForAuthInitialization(AuthProvider authProvider) async {
    // Wait until auth state is no longer initial
    while (authProvider.authState == AuthState.initial) {
      await Future.delayed(const Duration(milliseconds: 100));
    }
  }

  void _navigateToNextScreen(AuthProvider authProvider) {
    debugPrint('Auth state: ${authProvider.authState}');
    debugPrint('Is authenticated: ${authProvider.isAuthenticated}');
    debugPrint('User: ${authProvider.user?.toJson()}');
    debugPrint('User role: ${authProvider.user?.role}');
    debugPrint('Is admin: ${authProvider.isAdmin}');
    debugPrint('Is student: ${authProvider.isStudent}');
    
    switch (authProvider.authState) {
      case AuthState.authenticated:
        if (authProvider.isAdmin) {
          debugPrint('Navigating to admin main from splash');
          Navigator.pushReplacementNamed(context, AppRoutes.adminMain);
        } else if (authProvider.isStudent) {
          debugPrint('Navigating to student main from splash');
          Navigator.pushReplacementNamed(context, AppRoutes.studentMain);
        } else {
          debugPrint('Unknown role, navigating to login');
          Navigator.pushReplacementNamed(context, AppRoutes.login);
        }
        break;
      case AuthState.unauthenticated:
      case AuthState.loading:
      case AuthState.initial:
      default:
        debugPrint('Navigating to login from splash');
        Navigator.pushReplacementNamed(context, AppRoutes.login);
        break;
    }
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
        decoration: BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topCenter,
            end: Alignment.bottomCenter,
            colors: [
              Theme.of(context).colorScheme.primary,
              Theme.of(context).colorScheme.primaryContainer,
            ],
          ),
        ),
        child: Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              // App Logo/Icon
              AnimatedBuilder(
                animation: _animationController,
                builder: (context, child) {
                  return FadeTransition(
                    opacity: _fadeAnimation,
                    child: ScaleTransition(
                      scale: _scaleAnimation,
                      child: Container(
                        width: 120,
                        height: 120,
                        decoration: BoxDecoration(
                          color: Theme.of(context).colorScheme.onPrimary,
                          borderRadius: BorderRadius.circular(30),
                          boxShadow: [
                            BoxShadow(
                              color: Colors.black.withOpacity(0.2),
                              blurRadius: 20,
                              spreadRadius: 5,
                            ),
                          ],
                        ),
                        child: Icon(
                          Icons.account_balance_wallet,
                          size: 60,
                          color: Theme.of(context).colorScheme.primary,
                        ),
                      ),
                    ),
                  );
                },
              ),
              
              const SizedBox(height: 30),
              
              // App Name
              AnimatedBuilder(
                animation: _fadeAnimation,
                builder: (context, child) {
                  return FadeTransition(
                    opacity: _fadeAnimation,
                    child: Text(
                      AppConstants.appName,
                      style: Theme.of(context).textTheme.headlineMedium?.copyWith(
                        color: Theme.of(context).colorScheme.onPrimary,
                        fontWeight: FontWeight.bold,
                        letterSpacing: 1.2,
                      ),
                    ),
                  );
                },
              ),
              
              const SizedBox(height: 10),
              
              // App Tagline
              AnimatedBuilder(
                animation: _fadeAnimation,
                builder: (context, child) {
                  return FadeTransition(
                    opacity: _fadeAnimation,
                    child: Text(
                      'Manajemen Keuangan Mahasiswa',
                      style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                        color: Theme.of(context).colorScheme.onPrimary.withOpacity(0.8),
                        letterSpacing: 0.5,
                      ),
                    ),
                  );
                },
              ),
              
              const SizedBox(height: 80),
              
              // Loading Indicator
              AnimatedBuilder(
                animation: _fadeAnimation,
                builder: (context, child) {
                  return FadeTransition(
                    opacity: _fadeAnimation,
                    child: Column(
                      children: [
                        CircularProgressIndicator(
                          valueColor: AlwaysStoppedAnimation<Color>(
                            Theme.of(context).colorScheme.onPrimary,
                          ),
                        ),
                        const SizedBox(height: 20),
                        Consumer<AuthProvider>(
                          builder: (context, authProvider, child) {
                            return Text(
                              authProvider.authState == AuthState.loading
                                  ? 'Memeriksa autentikasi...'
                                  : 'Memuat...',
                              style: Theme.of(context).textTheme.bodySmall?.copyWith(
                                color: Theme.of(context).colorScheme.onPrimary.withOpacity(0.7),
                              ),
                            );
                          },
                        ),
                      ],
                    ),
                  );
                },
              ),
            ],
          ),
        ),
      ),
    );
  }
}