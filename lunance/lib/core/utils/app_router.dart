// lib/core/utils/app_router.dart
import 'package:go_router/go_router.dart';
import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';

import '../../features/auth/presentation/pages/login_page.dart';
import '../../features/auth/presentation/pages/register_page.dart';
import '../../features/auth/presentation/pages/forgot_password_page.dart';
import '../../features/auth/presentation/pages/verify_otp_page.dart';
import '../../features/auth/presentation/pages/reset_password_page.dart';
import '../../features/dashboard/presentation/pages/dashboard_page.dart';
import '../../features/auth/presentation/bloc/auth_bloc.dart';
import '../../features/auth/presentation/bloc/auth_state.dart';
import '../routes/route_names.dart';

class AppRouter {
  static final GoRouter router = GoRouter(
    initialLocation: RouteNames.login,
    refreshListenable: GoRouterRefreshStream(
      // This will rebuild routes when auth state changes
    ),
    routes: [
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
      
      // Main App Routes
      GoRoute(
        path: RouteNames.dashboard,
        name: 'dashboard',
        builder: (context, state) => const DashboardPage(),
      ),
      
      // Placeholder routes for other features
      GoRoute(
        path: RouteNames.history,
        name: 'history',
        builder: (context, state) => const PlaceholderPage(title: 'Riwayat Transaksi'),
      ),
      GoRoute(
        path: RouteNames.addTransaction,
        name: 'add-transaction',
        builder: (context, state) => const PlaceholderPage(title: 'Tambah Transaksi'),
      ),
      GoRoute(
        path: RouteNames.categories,
        name: 'categories',
        builder: (context, state) => const PlaceholderPage(title: 'Kategori'),
      ),
      GoRoute(
        path: RouteNames.settings,
        name: 'settings',
        builder: (context, state) => const PlaceholderPage(title: 'Pengaturan'),
      ),
    ],
    redirect: (context, state) {
      // Get current auth state
      final authBloc = context.read<AuthBloc>();
      final authState = authBloc.state;
      
      final isAuthRoute = [
        RouteNames.login,
        RouteNames.register,
        RouteNames.forgotPassword,
        RouteNames.verifyOtp,
        RouteNames.resetPassword,
      ].contains(state.matchedLocation);
      
      // If user is authenticated and trying to access auth routes
      if (authState is AuthAuthenticated && isAuthRoute) {
        return RouteNames.dashboard;
      }
      
      // If user is not authenticated and trying to access protected routes
      if (authState is AuthUnauthenticated && !isAuthRoute) {
        return RouteNames.login;
      }
      
      // If loading state, don't redirect yet
      if (authState is AuthLoading) {
        return null;
      }
      
      // No redirect needed
      return null;
    },
    errorBuilder: (context, state) => Scaffold(
      body: Center(
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
              'Halaman tidak ditemukan',
              style: Theme.of(context).textTheme.headlineSmall,
            ),
            const SizedBox(height: 8),
            Text(
              'Path: ${state.matchedLocation}',
              style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                color: Colors.grey,
              ),
            ),
            const SizedBox(height: 16),
            ElevatedButton(
              onPressed: () => context.go(RouteNames.login),
              child: const Text('Kembali ke Login'),
            ),
          ],
        ),
      ),
    ),
  );
}

// Helper class for router refresh
class GoRouterRefreshStream extends ChangeNotifier {
  GoRouterRefreshStream();
}

// Placeholder page for features not yet implemented - IMPROVED
class PlaceholderPage extends StatelessWidget {
  final String title;

  const PlaceholderPage({
    super.key,
    required this.title,
  });

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(title),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          onPressed: () => context.go(RouteNames.dashboard),
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
              onPressed: () => context.go(RouteNames.dashboard),
              child: const Text('Kembali ke Dashboard'),
            ),
          ],
        ),
      ),
    );
  }
}