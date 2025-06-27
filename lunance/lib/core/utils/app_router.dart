// lib/core/utils/app_router.dart (Simple version tanpa error)
import 'package:go_router/go_router.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_bloc/flutter_bloc.dart';

import '../../features/splash/presentation/pages/splash_page.dart';
import '../../features/auth/presentation/pages/login_page.dart';
import '../../features/auth/presentation/pages/register_page.dart';
import '../../features/auth/presentation/pages/forgot_password_page.dart';
import '../../features/auth/presentation/pages/verify_otp_page.dart';
import '../../features/auth/presentation/pages/reset_password_page.dart';
import '../../features/dashboard/presentation/pages/dashboard_page.dart';
import '../../features/history/presentation/pages/history_page.dart';
import '../../features/transactions/presentation/pages/add_transaction_page.dart';
import '../../features/categories/presentation/pages/categories_page.dart';
import '../../features/settings/presentation/pages/settings_page.dart';
import '../../features/settings/presentation/pages/change_password_page.dart';
import '../../features/settings/presentation/pages/profile_edit_page.dart';
import '../../features/auth/presentation/bloc/auth_bloc.dart';
import '../../features/auth/presentation/bloc/auth_state.dart';
import '../routes/route_names.dart';

class AppRouter {
  static final GoRouter router = GoRouter(
    initialLocation: '/splash',
    routes: [
      // Splash Route
      GoRoute(
        path: '/splash',
        name: 'splash',
        builder: (context, state) => const SplashPage(),
      ),

      // Auth Routes
      GoRoute(
        path: RouteNames.login,
        name: 'login',
        builder: (context, state) => const LoginPage(),
      ),
      GoRoute(
        path: RouteNames.register,
        name: 'register',
        builder: (context, state) => const RegisterPage(),
      ),
      GoRoute(
        path: RouteNames.forgotPassword,
        name: 'forgot-password',
        builder: (context, state) => const ForgotPasswordPage(),
      ),
      GoRoute(
        path: RouteNames.verifyOtp,
        name: 'verify-otp',
        builder: (context, state) {
          final extra = state.extra as Map<String, dynamic>?;
          return VerifyOtpPage(
            email: extra?['email']?.toString() ?? '',
            type: extra?['type']?.toString() ?? 'registration',
          );
        },
      ),
      GoRoute(
        path: RouteNames.resetPassword,
        name: 'reset-password',
        builder: (context, state) {
          final extra = state.extra as Map<String, dynamic>?;
          return ResetPasswordPage(
            email: extra?['email']?.toString() ?? '',
          );
        },
      ),
      
      // Main App Routes (dengan navbar)
      GoRoute(
        path: RouteNames.dashboard,
        name: 'dashboard',
        builder: (context, state) => WillPopScope(
          onWillPop: () => _showExitConfirmation(context),
          child: const DashboardPage(),
        ),
      ),
      GoRoute(
        path: RouteNames.history,
        name: 'history',
        builder: (context, state) => const HistoryPage(),
      ),
      GoRoute(
        path: RouteNames.addTransaction,
        name: 'add-transaction',
        builder: (context, state) => const AddTransactionPage(),
      ),
      GoRoute(
        path: RouteNames.categories,
        name: 'categories',
        builder: (context, state) => const CategoriesPage(),
      ),
      GoRoute(
        path: RouteNames.settings,
        name: 'settings',
        builder: (context, state) => const SettingsPage(),
      ),
      
      // Sub Menu Routes (tanpa navbar, dengan app bar)
      GoRoute(
        path: '/change-password',
        name: 'change-password',
        builder: (context, state) => const ChangePasswordPage(),
      ),
      GoRoute(
        path: '/profile-edit',
        name: 'profile-edit',
        builder: (context, state) => const ProfileEditPage(),
      ),
      
      // Additional transaction routes
      GoRoute(
        path: '/add-income',
        name: 'add-income',
        builder: (context, state) => const PlaceholderPage(
          title: 'Tambah Pemasukan',
          subtitle: 'Form tambah pemasukan',
        ),
      ),
      GoRoute(
        path: '/add-expense',
        name: 'add-expense',
        builder: (context, state) => const PlaceholderPage(
          title: 'Tambah Pengeluaran',
          subtitle: 'Form tambah pengeluaran',
        ),
      ),
    ],
    redirect: (context, state) {
      try {
        // Get current auth state
        final authBloc = BlocProvider.of<AuthBloc>(context, listen: false);
        final authState = authBloc.state;
        
        final isAuthRoute = [
          '/splash',
          RouteNames.login,
          RouteNames.register,
          RouteNames.forgotPassword,
          RouteNames.verifyOtp,
          RouteNames.resetPassword,
        ].contains(state.matchedLocation);
        
        // Skip redirect for splash screen
        if (state.matchedLocation == '/splash') {
          return null;
        }
        
        // If user is authenticated and trying to access auth routes
        if (authState is AuthAuthenticated && isAuthRoute) {
          return RouteNames.dashboard;
        }
        
        // If user is not authenticated and trying to access protected routes
        if (authState is AuthUnauthenticated && !isAuthRoute) {
          return RouteNames.login;
        }
        
        // No redirect needed
        return null;
      } catch (e) {
        // If there's an error getting auth state, allow navigation
        return null;
      }
    },
    errorBuilder: (context, state) => ErrorPage(
      error: state.error?.toString() ?? 'Unknown error',
      path: state.matchedLocation,
    ),
  );

  // Show exit confirmation dialog
  static Future<bool> _showExitConfirmation(BuildContext context) async {
    return await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Keluar Aplikasi'),
        content: const Text('Apakah Anda yakin ingin keluar dari aplikasi?'),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(false),
            child: const Text('Batal'),
          ),
          TextButton(
            onPressed: () {
              Navigator.of(context).pop(true);
              SystemNavigator.pop();
            },
            child: const Text('Keluar'),
          ),
        ],
      ),
    ) ?? false;
  }
}

// Error page untuk handling routing errors
class ErrorPage extends StatelessWidget {
  final String error;
  final String path;

  const ErrorPage({
    super.key,
    required this.error,
    required this.path,
  });

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Error'),
        backgroundColor: Colors.red,
        foregroundColor: Colors.white,
      ),
      body: Center(
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const Icon(
                Icons.error_outline,
                size: 64,
                color: Colors.red,
              ),
              const SizedBox(height: 16),
              Text(
                'Terjadi Kesalahan',
                style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: 8),
              Text(
                'Path: $path',
                style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                  color: Colors.grey,
                ),
              ),
              const SizedBox(height: 8),
              Text(
                'Error: $error',
                style: Theme.of(context).textTheme.bodySmall?.copyWith(
                  color: Colors.grey,
                ),
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 24),
              Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  ElevatedButton(
                    onPressed: () => context.go('/dashboard'),
                    child: const Text('Kembali ke Dashboard'),
                  ),
                  const SizedBox(width: 16),
                  OutlinedButton(
                    onPressed: () => context.go('/settings'),
                    child: const Text('Ke Pengaturan'),
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }
}

// Simple placeholder page
class PlaceholderPage extends StatelessWidget {
  final String title;
  final String? subtitle;

  const PlaceholderPage({
    super.key,
    required this.title,
    this.subtitle,
  });

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(title),
        backgroundColor: Theme.of(context).primaryColor,
        foregroundColor: Colors.white,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          onPressed: () {
            if (context.canPop()) {
              context.pop();
            } else {
              context.go('/dashboard');
            }
          },
        ),
      ),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(
              Icons.construction,
              size: 64,
              color: Colors.grey,
            ),
            const SizedBox(height: 16),
            Text(
              title,
              style: const TextStyle(
                fontSize: 24,
                fontWeight: FontWeight.bold,
                color: Colors.grey,
              ),
            ),
            if (subtitle != null) ...[
              const SizedBox(height: 8),
              Text(
                subtitle!,
                style: const TextStyle(
                  fontSize: 16,
                  color: Colors.grey,
                ),
              ),
            ],
            const SizedBox(height: 8),
            const Text(
              'Fitur ini sedang dalam pengembangan',
              style: TextStyle(
                fontSize: 16,
                color: Colors.grey,
              ),
            ),
            const SizedBox(height: 24),
            ElevatedButton(
              onPressed: () {
                if (context.canPop()) {
                  context.pop();
                } else {
                  context.go('/dashboard');
                }
              },
              child: const Text('Kembali'),
            ),
          ],
        ),
      ),
    );
  }
}