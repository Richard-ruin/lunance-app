// lib/core/constants/api_endpoints.dart
class ApiEndpoints {
  // Base URL - should be loaded from environment
  static const String baseUrl = 'http://192.168.190.195:8000';
  static const String apiVersion = '/api/v1';
  
  // Auth endpoints
  static const String login = '$baseUrl$apiVersion/login';
  static const String register = '$baseUrl$apiVersion/register';
  static const String logout = '$baseUrl$apiVersion/logout';
  static const String forgotPassword = '$baseUrl$apiVersion/forgot-password';
  static const String verifyOtp = '$baseUrl$apiVersion/verify-otp';
  static const String resetPassword = '$baseUrl$apiVersion/reset-password';
  static const String requestOtp = '$baseUrl$apiVersion/request-otp';
  static const String me = '$baseUrl$apiVersion/me';
  static const String refreshToken = '$baseUrl$apiVersion/refresh';
  static const String changePassword = '$baseUrl$apiVersion/change-password';
  
  // Student endpoints
  static const String students = '$baseUrl$apiVersion/students';
  static const String myProfile = '$baseUrl$apiVersion/students/me';
  static const String updateProfile = '$baseUrl$apiVersion/students/me/profile';
  static const String uploadProfilePicture = '$baseUrl$apiVersion/students/me/profile-picture';
  static const String savingsGoals = '$baseUrl$apiVersion/students/me/savings-goals';
  static const String incomeSources = '$baseUrl$apiVersion/students/me/income-sources';
  static const String profileCompletion = '$baseUrl$apiVersion/students/me/analytics/profile-completion';
  
  // Settings endpoints
  static const String settings = '$baseUrl$apiVersion/students/me/settings';
  static const String updateSettings = '$baseUrl$apiVersion/students/me/settings';
  static const String notificationSettings = '$baseUrl$apiVersion/students/me/settings/notifications';
  static const String displaySettings = '$baseUrl$apiVersion/students/me/settings/display';
  static const String privacySettings = '$baseUrl$apiVersion/students/me/settings/privacy';
  
  // Transaction endpoints
  static const String transactions = '$baseUrl$apiVersion/transactions';
  static const String addTransaction = '$baseUrl$apiVersion/transactions';
  static const String transactionHistory = '$baseUrl$apiVersion/transactions/history';
  static const String searchTransactions = '$baseUrl$apiVersion/transactions/search';
  
  // Category endpoints
  static const String categories = '$baseUrl$apiVersion/categories';
  static const String addCategory = '$baseUrl$apiVersion/categories';
  
  
  
  // Dashboard endpoints
  static const String dashboard = '$baseUrl$apiVersion/dashboard';
  static const String dashboardSummary = '$baseUrl$apiVersion/dashboard/summary';

  // Dashboard endpoints
  static const String dashboardBase = '$baseUrl/dashboard';
  static const String financialSummary = '$dashboardBase/financial-summary';
  static const String quickStats = '$dashboardBase/quick-stats';
  static const String categoryBreakdown = '$dashboardBase/category-breakdown';
  static const String recentTransactions = '$dashboardBase/recent-transactions';
  static const String predictions = '$dashboardBase/predictions';
  static const String insights = '$dashboardBase/insights';
  static const String academicContext = '$dashboardBase/academic-context';
  static const String spendingTrends = '$dashboardBase/spending-trends';
  
  // Chatbot endpoints
  static const String chatbot = '$baseUrl$apiVersion/chat';
  static const String chatHistory = '$baseUrl$apiVersion/chat/history';
  static const String chatWebSocket = 'ws://localhost:8000$apiVersion/chat/ws';
  
  // File upload endpoints
  static const String uploadReceipt = '$baseUrl$apiVersion/uploads/receipt';
  static const String uploadAvatar = '$baseUrl$apiVersion/uploads/avatar';
  
  // Search endpoints
  static const String searchStudents = '$baseUrl$apiVersion/students/search/students';
  static const String searchUniversities = '$baseUrl$apiVersion/students/search/universities';
  static const String studentsByUniversity = '$baseUrl$apiVersion/students/by-university';
  
  // Security endpoints
  static const String verificationStatus = '$baseUrl$apiVersion/verification-status';
  static const String resendVerification = '$baseUrl$apiVersion/resend-verification';
  static const String deactivateAccount = '$baseUrl$apiVersion/students/me';
  
  // Health check
  static const String health = '$baseUrl/health';
  static const String authHealth = '$baseUrl$apiVersion/health';
  
  // Helper methods for dynamic endpoints
  static String transactionById(String id) => '$transactions/$id';
  static String categoryById(String id) => '$categories/$id';
  static String studentById(String id) => '$students/$id';
  static String savingsGoalById(String id) => '$savingsGoals/$id';
  
  // Query parameter helpers
  static String withQuery(String endpoint, Map<String, dynamic> params) {
    if (params.isEmpty) return endpoint;
    
    final query = params.entries
        .where((entry) => entry.value != null)
        .map((entry) => '${entry.key}=${Uri.encodeComponent(entry.value.toString())}')
        .join('&');
    
    return '$endpoint?$query';
  }
}
