
// lib/utils/navigation_helper.dart
import 'package:flutter/material.dart';
import 'routes.dart';

class NavigationHelper {
  static final GlobalKey<NavigatorState> navigatorKey = GlobalKey<NavigatorState>();
  
  static BuildContext get context => navigatorKey.currentContext!;
  
  static void pushAndRemoveUntil(String routeName, {Object? arguments}) {
    Navigator.pushNamedAndRemoveUntil(
      context,
      routeName,
      (route) => false,
      arguments: arguments,
    );
  }
  
  static void pushReplacement(String routeName, {Object? arguments}) {
    Navigator.pushReplacementNamed(
      context,
      routeName,
      arguments: arguments,
    );
  }
  
  static void push(String routeName, {Object? arguments}) {
    Navigator.pushNamed(
      context,
      routeName,
      arguments: arguments,
    );
  }
  
  static void pop([Object? result]) {
    Navigator.pop(context, result);
  }
  
  static void popUntil(String routeName) {
    Navigator.popUntil(context, ModalRoute.withName(routeName));
  }
  
  static bool canPop() {
    return Navigator.canPop(context);
  }
  
  // Navigation methods for specific screens
  static void navigateToLogin() {
    pushAndRemoveUntil(AppRoutes.login);
  }
  
  static void navigateToRegister() {
    push(AppRoutes.register);
  }
  
  static void navigateToForgotPassword() {
    push(AppRoutes.forgotPassword);
  }
  
  static void navigateToStudentMain() {
    pushAndRemoveUntil(AppRoutes.studentMain);
  }
  
  static void navigateToAdminMain() {
    pushAndRemoveUntil(AppRoutes.adminMain);
  }
  
  static void navigateBasedOnRole(String role) {
    switch (role) {
      case 'student':
        navigateToStudentMain();
        break;
      case 'admin':
        navigateToAdminMain();
        break;
      default:
        navigateToLogin();
    }
  }
}

// lib/utils/permissions.dart
class Permissions {
  static bool canAccessAdminFeatures(String role) {
    return role == 'admin';
  }
  
  static bool canCreateGlobalCategory(String role) {
    return role == 'admin';
  }
  
  static bool canDeleteGlobalCategory(String role) {
    return role == 'admin';
  }
  
  static bool canViewUserManagement(String role) {
    return role == 'admin';
  }
  
  static bool canViewUniversityManagement(String role) {
    return role == 'admin';
  }
  
  static bool canManageUniversities(String role) {
    return role == 'admin';
  }
  
  static bool canApproveUniversityRequests(String role) {
    return role == 'admin';
  }
  
  static bool canCreatePersonalCategory(String role) {
    return role == 'student' || role == 'admin';
  }
  
  static bool canEditPersonalCategory(String role, String categoryUserId, String currentUserId) {
    return (role == 'student' || role == 'admin') && categoryUserId == currentUserId;
  }
  
  static bool canDeletePersonalCategory(String role, String categoryUserId, String currentUserId) {
    return (role == 'student' || role == 'admin') && categoryUserId == currentUserId;
  }
  
  static bool canViewAllTransactions(String role) {
    return role == 'admin';
  }
  
  static bool canExportData(String role) {
    return role == 'admin';
  }
  
  static bool canCreateUniversityRequest(String role) {
    return role == 'student';
  }
  
  static bool canViewUniversityRequests(String role) {
    return role == 'admin';
  }
}
