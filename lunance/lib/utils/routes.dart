// lib/utils/routes.dart
import 'package:flutter/material.dart';
import '../screens/splash/splash_screen.dart';
import '../screens/auth/login_screen.dart';
import '../screens/auth/register_screen.dart';
import '../screens/auth/forgot_password_screen.dart';
import '../screens/student/student_main_screen.dart';
import '../screens/admin/admin_main_screen.dart';

class AppRoutes {
  static const String splash = '/';
  static const String login = '/login';
  static const String register = '/register';
  static const String forgotPassword = '/forgot-password';
  static const String studentMain = '/student-main';
  static const String adminMain = '/admin-main';
  
  static Map<String, WidgetBuilder> routes = {
    splash: (context) => const SplashScreen(),
    login: (context) => const LoginScreen(),
    register: (context) => const RegisterScreen(),
    forgotPassword: (context) => const ForgotPasswordScreen(),
    studentMain: (context) => const StudentMainScreen(),
    adminMain: (context) => const AdminMainScreen(),
  };
  
  static Route<dynamic> onGenerateRoute(RouteSettings settings) {
    final String? name = settings.name;
    final WidgetBuilder? builder = routes[name];
    
    if (builder != null) {
      return MaterialPageRoute(
        builder: builder,
        settings: settings,
      );
    }
    
    // Default route if not found
    return MaterialPageRoute(
      builder: (context) => const SplashScreen(),
    );
  }
}
