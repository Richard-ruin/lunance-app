// lib/features/dashboard/presentation/pages/dashboard_page.dart
import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:go_router/go_router.dart';
import '../../../../core/theme/lunance_colors.dart';
import '../../../../shared/widgets/main_layout.dart';
import '../../../auth/presentation/bloc/auth_bloc.dart';
import '../../../auth/presentation/bloc/auth_state.dart';
import '../bloc/dashboard_bloc.dart';
import '../bloc/dashboard_event.dart';
import '../bloc/dashboard_state.dart';
import '../widgets/financial_card.dart';
import '../widgets/quick_action_buttons.dart';
import '../widgets/category_breakdown_chart.dart';
import '../widgets/recent_transactions_list.dart';
import '../widgets/chatbot_fab.dart';

class DashboardPage extends StatefulWidget {
  const DashboardPage({super.key});

  @override
  State<DashboardPage> createState() => _DashboardPageState();
}

class _DashboardPageState extends State<DashboardPage> {
  String _selectedPeriod = 'monthly';
  final _refreshKey = GlobalKey<RefreshIndicatorState>();

  @override
  void initState() {
    super.initState();
    // Load dashboard data when page initializes
    context.read<DashboardBloc>().add(LoadDashboardData(period: _selectedPeriod));
  }

  @override
  Widget build(BuildContext context) {
    return MainLayout(
      currentIndex: 0,
      floatingActionButton: ChatbotFAB(
        onPressed: () => _showChatbotModal(context),
      ),
      body: RefreshIndicator(
        key: _refreshKey,
        onRefresh: _onRefresh,
        color: LunanceColors.primary,
        child: SingleChildScrollView(
          physics: const AlwaysScrollableScrollPhysics(),
          padding: const EdgeInsets.all(16.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Welcome Header
              _buildWelcomeHeader(),
              
              const SizedBox(height: 24),
              
              // Period Selector
              _buildPeriodSelector(),
              
              const SizedBox(height: 20),
              
              // Dashboard Content
              BlocBuilder<DashboardBloc, DashboardState>(
                builder: (context, state) {
                  return Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      // Error Banner (if any)
                      if (state is DashboardPartialError)
                        _buildErrorBanner(state.errorMessage),
                      
                      // Financial Summary Card
                      FinancialCard(
                        financialSummary: state is DashboardLoaded 
                            ? state.financialSummary 
                            : null,
                        isLoading: _isComponentLoading(state, 'financial_summary'),
                        onRefresh: () => _refreshComponent('financial_summary'),
                      ),
                      
                      const SizedBox(height: 24),
                      
                      // Quick Actions
                      const QuickActionButtons(),
                      
                      const SizedBox(height: 24),
                      
                      // Category Breakdown Chart
                      CategoryBreakdownChart(
                        categoryBreakdown: state is DashboardLoaded 
                            ? state.categoryBreakdown 
                            : null,
                        isLoading: _isComponentLoading(state, 'category_breakdown'),
                      ),
                      
                      const SizedBox(height: 24),
                      
                      // Recent Transactions List
                      RecentTransactionsList(
                        recentTransactions: state is DashboardLoaded 
                            ? state.recentTransactions 
                            : null,
                        isLoading: _isComponentLoading(state, 'recent_transactions'),
                      ),
                      
                      const SizedBox(height: 24),
                      
                      // AI Insights (if available)
                      if (state is DashboardLoaded && state.insights != null)
                        _buildInsightsCard(state.insights!),
                      
                      const SizedBox(height: 24),
                      
                      // Predictions (if available)
                      if (state is DashboardLoaded && state.predictions != null)
                        _buildPredictionsCard(state.predictions!),
                      
                      // Error State
                      if (state is DashboardError)
                        _buildErrorState(state.message),
                      
                      // Loading State
                      if (state is DashboardLoading)
                        _buildLoadingState(),
                      
                      const SizedBox(height: 100), // Space for FAB
                    ],
                  );
                },
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildWelcomeHeader() {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        gradient: const LinearGradient(
          colors: [LunanceColors.primary, LunanceColors.primaryVariant],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(16),
        boxShadow: [
          BoxShadow(
            color: LunanceColors.primary.withOpacity(0.3),
            spreadRadius: 1,
            blurRadius: 10,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Row(
        children: [
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text(
                  'Selamat Datang!',
                  style: TextStyle(
                    color: Colors.white,
                    fontSize: 24,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const SizedBox(height: 4),
                BlocBuilder<AuthBloc, AuthState>(
                  builder: (context, state) {
                    if (state is AuthAuthenticated) {
                      return Text(
                        state.user.fullName,
                        style: const TextStyle(
                          color: Colors.white70,
                          fontSize: 16,
                        ),
                      );
                    }
                    return const Text(
                      'Mahasiswa',
                      style: TextStyle(
                        color: Colors.white70,
                        fontSize: 16,
                      ),
                    );
                  },
                ),
              ],
            ),
          ),
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: Colors.white.withOpacity(0.2),
              borderRadius: BorderRadius.circular(12),
            ),
            child: const Icon(
              Icons.account_balance_wallet,
              color: Colors.white,
              size: 32,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildPeriodSelector() {
    return Container(
      padding: const EdgeInsets.all(4),
      decoration: BoxDecoration(
        color: Colors.grey[100],
        borderRadius: BorderRadius.circular(12),
      ),
      child: Row(
        children: [
          _buildPeriodTab('daily', 'Harian'),
          _buildPeriodTab('weekly', 'Mingguan'),
          _buildPeriodTab('monthly', 'Bulanan'),
          _buildPeriodTab('yearly', 'Tahunan'),
        ],
      ),
    );
  }

  Widget _buildPeriodTab(String period, String label) {
    final isSelected = _selectedPeriod == period;
    return Expanded(
      child: GestureDetector(
        onTap: () => _changePeriod(period),
        child: Container(
          padding: const EdgeInsets.symmetric(vertical: 12),
          decoration: BoxDecoration(
            color: isSelected ? LunanceColors.primary : Colors.transparent,
            borderRadius: BorderRadius.circular(8),
          ),
          child: Text(
            label,
            textAlign: TextAlign.center,
            style: TextStyle(
              color: isSelected ? Colors.white : LunanceColors.textSecondary,
              fontWeight: isSelected ? FontWeight.w600 : FontWeight.normal,
              fontSize: 12,
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildErrorBanner(String message) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(12),
      margin: const EdgeInsets.only(bottom: 16),
      decoration: BoxDecoration(
        color: Colors.orange[50],
        border: Border.all(color: Colors.orange[200]!),
        borderRadius: BorderRadius.circular(8),
      ),
      child: Row(
        children: [
          Icon(
            Icons.warning_amber_rounded,
            color: Colors.orange[700],
            size: 20,
          ),
          const SizedBox(width: 8),
          Expanded(
            child: Text(
              message,
              style: TextStyle(
                color: Colors.orange[700],
                fontSize: 14,
              ),
            ),
          ),
          GestureDetector(
            onTap: () => _onRefresh(),
            child: Icon(
              Icons.refresh,
              color: Colors.orange[700],
              size: 20,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildInsightsCard(insights) {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        boxShadow: [
          BoxShadow(
            color: Colors.grey.withOpacity(0.1),
            spreadRadius: 1,
            blurRadius: 10,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Row(
            children: [
              Icon(
                Icons.lightbulb_outline,
                color: LunanceColors.primary,
                size: 24,
              ),
              SizedBox(width: 8),
              Text(
                'Insight Keuangan',
                style: TextStyle(
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                  color: LunanceColors.textPrimary,
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          const Text(
            'Fitur insight akan segera hadir untuk memberikan rekomendasi keuangan yang personal!',
            style: TextStyle(
              color: LunanceColors.textSecondary,
              fontSize: 14,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildPredictionsCard(predictions) {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        boxShadow: [
          BoxShadow(
            color: Colors.grey.withOpacity(0.1),
            spreadRadius: 1,
            blurRadius: 10,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Row(
            children: [
              Icon(
                Icons.trending_up,
                color: LunanceColors.primary,
                size: 24,
              ),
              SizedBox(width: 8),
              Text(
                'Prediksi Keuangan',
                style: TextStyle(
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                  color: LunanceColors.textPrimary,
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          const Text(
            'Fitur prediksi AI akan segera hadir untuk membantu perencanaan keuangan Anda!',
            style: TextStyle(
              color: LunanceColors.textSecondary,
              fontSize: 14,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildErrorState(String message) {
    return Center(
      child: Column(
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
            message,
            style: const TextStyle(color: LunanceColors.textSecondary),
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: 24),
          ElevatedButton(
            onPressed: () => _onRefresh(),
            child: const Text('Coba Lagi'),
          ),
        ],
      ),
    );
  }

  Widget _buildLoadingState() {
    return const Center(
      child: Column(
        children: [
          CircularProgressIndicator(
            color: LunanceColors.primary,
          ),
          SizedBox(height: 16),
          Text(
            'Memuat data dashboard...',
            style: TextStyle(color: LunanceColors.textSecondary),
          ),
        ],
      ),
    );
  }

  bool _isComponentLoading(DashboardState state, String component) {
    if (state is DashboardLoading) return true;
    if (state is DashboardComponentLoading) {
      return state.loadingComponents.contains(component);
    }
    return false;
  }

  void _changePeriod(String period) {
    if (_selectedPeriod != period) {
      setState(() {
        _selectedPeriod = period;
      });
      context.read<DashboardBloc>().add(ChangePeriod(period));
    }
  }

  void _refreshComponent(String component) {
    switch (component) {
      case 'financial_summary':
        context.read<DashboardBloc>().add(LoadFinancialSummary(period: _selectedPeriod));
        break;
      case 'quick_stats':
        context.read<DashboardBloc>().add(LoadQuickStats());
        break;
      case 'category_breakdown':
        context.read<DashboardBloc>().add(LoadCategoryBreakdown(period: _selectedPeriod));
        break;
      case 'recent_transactions':
        context.read<DashboardBloc>().add(LoadRecentTransactions());
        break;
    }
  }

  Future<void> _onRefresh() async {
    context.read<DashboardBloc>().add(RefreshDashboard(period: _selectedPeriod));
    
    // Wait a bit for the refresh to complete
    await Future.delayed(const Duration(milliseconds: 500));
  }

  void _showChatbotModal(BuildContext context) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (context) => _buildChatbotModal(context),
    );
  }

  Widget _buildChatbotModal(BuildContext context) {
    return Container(
      height: MediaQuery.of(context).size.height * 0.8,
      decoration: const BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      child: Column(
        children: [
          // Handle bar
          Container(
            width: 40,
            height: 4,
            margin: const EdgeInsets.symmetric(vertical: 12),
            decoration: BoxDecoration(
              color: Colors.grey[300],
              borderRadius: BorderRadius.circular(2),
            ),
          ),
          
          // Header
          Padding(
            padding: const EdgeInsets.all(20),
            child: Row(
              children: [
                Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: LunanceColors.primary.withOpacity(0.1),
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: const Icon(
                    Icons.smart_toy,
                    color: LunanceColors.primary,
                    size: 24,
                  ),
                ),
                const SizedBox(width: 12),
                const Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'AI Assistant Lunance',
                        style: TextStyle(
                          fontSize: 18,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      Text(
                        'Tanya apa saja tentang keuanganmu!',
                        style: TextStyle(
                          color: LunanceColors.textSecondary,
                          fontSize: 14,
                        ),
                      ),
                    ],
                  ),
                ),
                IconButton(
                  onPressed: () => Navigator.of(context).pop(),
                  icon: const Icon(Icons.close),
                ),
              ],
            ),
          ),
          
          // Content
          Expanded(
            child: Container(
              padding: const EdgeInsets.all(20),
              child: const Center(
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Icon(
                      Icons.construction,
                      size: 64,
                      color: LunanceColors.textHint,
                    ),
                    SizedBox(height: 16),
                    Text(
                      'Chatbot AI',
                      style: TextStyle(
                        fontSize: 24,
                        fontWeight: FontWeight.bold,
                        color: LunanceColors.textSecondary,
                      ),
                    ),
                    SizedBox(height: 8),
                    Text(
                      'Fitur ini sedang dalam pengembangan.\nSegera hadir untuk membantu Anda!',
                      style: TextStyle(
                        fontSize: 16,
                        color: LunanceColors.textHint,
                      ),
                      textAlign: TextAlign.center,
                    ),
                  ],
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
}