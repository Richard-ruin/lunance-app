import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../providers/finance_provider.dart';
import '../../providers/auth_provider.dart';
import '../../utils/app_colors.dart';
import '../../utils/app_text_styles.dart';
import '../../utils/format_utils.dart';
import '../../widgets/custom_widgets.dart';
import '../../widgets/common_widgets.dart';
import 'finance/dashboard_tab.dart';
import 'finance/analytics_tab.dart';
import 'finance/history_tab.dart';
import 'finance/predictions_tab.dart';

class ExploreFinanceView extends StatefulWidget {
  const ExploreFinanceView({Key? key}) : super(key: key);

  @override
  State<ExploreFinanceView> createState() => _ExploreFinanceViewState();
}

class _ExploreFinanceViewState extends State<ExploreFinanceView>
    with SingleTickerProviderStateMixin {
  late TabController _tabController;
  bool _isInitialized = false;

  final List<Tab> _tabs = [
    const Tab(
      icon: Icon(Icons.dashboard_outlined),
      text: 'Dashboard',
    ),
    const Tab(
      icon: Icon(Icons.analytics_outlined),
      text: 'Analytics',
    ),
    const Tab(
      icon: Icon(Icons.history_outlined),
      text: 'History',
    ),
    const Tab(
      icon: Icon(Icons.trending_up_outlined),
      text: 'Predictions',
    ),
  ];

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: _tabs.length, vsync: this);
    
    // FIX: Use addPostFrameCallback to avoid setState during build
    WidgetsBinding.instance.addPostFrameCallback((_) {
      _initializeData();
    });
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  // FIX: Make this method more robust and prevent multiple calls
  Future<void> _initializeData() async {
    if (_isInitialized || !mounted) return;
    
    try {
      final financeProvider = Provider.of<FinanceProvider>(context, listen: false);
      
      // Load essential data untuk 50/30/20 only if not already loaded
      if (financeProvider.dashboardData == null && 
          financeProvider.budgetStatusData == null) {
        await financeProvider.loadAllEssentialData();
      }
      
      if (mounted) {
        setState(() {
          _isInitialized = true;
        });
      }
    } catch (e) {
      // Handle error gracefully
      if (mounted) {
        setState(() {
          _isInitialized = true; // Still set to true to prevent infinite loops
        });
      }
    }
  }

  Future<void> _refreshData() async {
    if (!mounted) return;
    
    try {
      final financeProvider = Provider.of<FinanceProvider>(context, listen: false);
      await financeProvider.refreshAllData();
    } catch (e) {
      // Handle error silently or show snackbar
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Gagal memuat data: ${e.toString()}'),
            backgroundColor: AppColors.error,
          ),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Consumer<AuthProvider>(
      builder: (context, authProvider, child) {
        final user = authProvider.user;
        final hasFinancialSetup = user?.financialSetupCompleted ?? false;
        
        if (!hasFinancialSetup) {
          return _buildSetupRequiredView();
        }
        
        return Scaffold(
          backgroundColor: AppColors.background,
          body: Column(
            children: [
              // Header dengan 50/30/20 Info
              _buildHeader(),
              
              // Tab Bar
              _buildTabBar(),
              
              // Tab Content
              Expanded(
                child: TabBarView(
                  controller: _tabController,
                  children: const [
                    DashboardTab(),
                    AnalyticsTab(),
                    HistoryTab(),
                    PredictionsTab(),
                  ],
                ),
              ),
            ],
          ),
        );
      },
    );
  }

  Widget _buildSetupRequiredView() {
    return Scaffold(
      backgroundColor: AppColors.background,
      body: Center(
        child: Padding(
          padding: const EdgeInsets.all(32),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Container(
                width: 120,
                height: 120,
                decoration: BoxDecoration(
                  color: AppColors.primary.withOpacity(0.1),
                  shape: BoxShape.circle,
                ),
                child: Icon(
                  Icons.account_balance_wallet_outlined,
                  size: 60,
                  color: AppColors.primary,
                ),
              ),
              
              const SizedBox(height: 32),
              
              Text(
                'Setup Keuangan Diperlukan',
                style: AppTextStyles.h5.copyWith(
                  fontWeight: FontWeight.w600,
                ),
                textAlign: TextAlign.center,
              ),
              
              const SizedBox(height: 16),
              
              Text(
                'Untuk menggunakan fitur keuangan dengan metode 50/30/20 Elizabeth Warren, silakan lengkapi setup keuangan Anda terlebih dahulu.',
                style: AppTextStyles.bodyMedium.copyWith(
                  color: AppColors.textSecondary,
                  height: 1.5,
                ),
                textAlign: TextAlign.center,
              ),
              
              const SizedBox(height: 32),
              
              Container(
                padding: const EdgeInsets.all(20),
                decoration: BoxDecoration(
                  color: AppColors.info.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(16),
                  border: Border.all(
                    color: AppColors.info.withOpacity(0.3),
                  ),
                ),
                child: Column(
                  children: [
                    Text(
                      '50/30/20 Method',
                      style: AppTextStyles.labelLarge.copyWith(
                        color: AppColors.info,
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                    const SizedBox(height: 12),
                    Text(
                      '• 50% Kebutuhan: Kos, makan, transport, pendidikan\n'
                      '• 30% Keinginan: Hiburan, jajan, target tabungan\n'
                      '• 20% Tabungan: Dana darurat, investasi masa depan',
                      style: AppTextStyles.bodySmall.copyWith(
                        color: AppColors.textSecondary,
                        height: 1.4,
                      ),
                    ),
                  ],
                ),
              ),
              
              const SizedBox(height: 32),
              
              ElevatedButton(
                onPressed: () {
                  // Navigate to financial setup
                  Navigator.pushNamed(context, '/financial-setup');
                },
                style: ElevatedButton.styleFrom(
                  backgroundColor: AppColors.primary,
                  foregroundColor: AppColors.white,
                  padding: const EdgeInsets.symmetric(
                    horizontal: 32,
                    vertical: 16,
                  ),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(12),
                  ),
                ),
                child: Text(
                  'Setup Keuangan Sekarang',
                  style: AppTextStyles.labelLarge.copyWith(
                    color: AppColors.white,
                    fontWeight: FontWeight.w600,
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildHeader() {
    return Consumer<FinanceProvider>(
      builder: (context, financeProvider, child) {
        final budgetStatus = financeProvider.budgetStatusData;
        final hasbudget = budgetStatus?['has_budget'] ?? false;
        
        return Container(
          color: AppColors.white,
          padding: const EdgeInsets.all(24),
          child: Column(
            children: [
              // Title & Refresh Button
              Row(
                children: [
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Row(
                          children: [
                            Container(
                              padding: const EdgeInsets.all(8),
                              decoration: BoxDecoration(
                                color: AppColors.primary.withOpacity(0.1),
                                borderRadius: BorderRadius.circular(8),
                              ),
                              child: Icon(
                                Icons.account_balance_wallet_outlined,
                                color: AppColors.primary,
                                size: 20,
                              ),
                            ),
                            const SizedBox(width: 12),
                            Flexible( // PERBAIKAN: Gunakan Flexible
                              child: Text(
                                'Keuangan Mahasiswa',
                                style: AppTextStyles.h5.copyWith(
                                  fontWeight: FontWeight.w700,
                                ),
                                overflow: TextOverflow.ellipsis,
                              ),
                            ),
                          ],
                        ),
                        const SizedBox(height: 8),
                        Text(
                          'Metode 50/30/20 Elizabeth Warren untuk mahasiswa Indonesia',
                          style: AppTextStyles.bodySmall.copyWith(
                            color: AppColors.textSecondary,
                          ),
                          maxLines: 2,
                          overflow: TextOverflow.ellipsis,
                        ),
                      ],
                    ),
                  ),
                  
                  // Refresh Button
                  Consumer<FinanceProvider>(
                    builder: (context, provider, child) {
                      final isAnyLoading = provider.isLoadingDashboard ||
                          provider.isLoadingAnalytics ||
                          provider.isLoadingHistory ||
                          provider.isLoadingStats ||
                          provider.isLoadingProgress;

                      return IconButton(
                        onPressed: isAnyLoading ? null : _refreshData,
                        icon: isAnyLoading
                            ? SizedBox(
                                width: 20,
                                height: 20,
                                child: CircularProgressIndicator(
                                  strokeWidth: 2,
                                  valueColor: AlwaysStoppedAnimation<Color>(AppColors.primary),
                                ),
                              )
                            : Icon(
                                Icons.refresh,
                                color: AppColors.primary,
                              ),
                        tooltip: 'Refresh Data',
                      );
                    },
                  ),
                ],
              ),
              
              const SizedBox(height: 20),
              
              // Budget Status Summary
              if (hasbudget) _buildBudgetSummary(budgetStatus),
            ],
          ),
        );
      },
    );
  }

  Widget _buildBudgetSummary(Map<String, dynamic>? budgetStatus) {
    if (budgetStatus == null) return Container();
    
    final budgetHealth = budgetStatus['budget_health'] ?? 'unknown';
    final currentMonth = budgetStatus['current_month'] ?? 'Bulan ini';
    final budgetAllocation = budgetStatus['budget_allocation'] ?? {};
    final percentageUsed = budgetStatus['percentage_used'] ?? {};
    
    final needsUsed = (percentageUsed['needs'] ?? 0.0) as double;
    final wantsUsed = (percentageUsed['wants'] ?? 0.0) as double;
    final savingsUsed = (percentageUsed['savings'] ?? 0.0) as double;
    
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: [
            AppColors.primary.withOpacity(0.1),
            AppColors.success.withOpacity(0.05),
          ],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(
          color: AppColors.primary.withOpacity(0.2),
        ),
      ),
      child: Column(
        children: [
          // PERBAIKAN: Header dengan Flexible
          Row(
            children: [
              Icon(
                Icons.track_changes,
                color: AppColors.primary,
                size: 20,
              ),
              const SizedBox(width: 8),
              Expanded( // PERBAIKAN: Gunakan Expanded
                child: Text(
                  'Budget Status - $currentMonth',
                  style: AppTextStyles.labelLarge.copyWith(
                    fontWeight: FontWeight.w600,
                  ),
                  overflow: TextOverflow.ellipsis,
                ),
              ),
              const SizedBox(width: 8),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4), // Kurangi padding
                decoration: BoxDecoration(
                  color: _getBudgetHealthColor(budgetHealth).withOpacity(0.1),
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(
                    color: _getBudgetHealthColor(budgetHealth).withOpacity(0.3),
                  ),
                ),
                child: Text(
                  _getBudgetHealthText(budgetHealth),
                  style: AppTextStyles.caption.copyWith( // Gunakan caption untuk text yang lebih kecil
                    color: _getBudgetHealthColor(budgetHealth),
                    fontWeight: FontWeight.w600,
                  ),
                ),
              ),
            ],
          ),
          
          const SizedBox(height: 16),
          
          // PERBAIKAN: Budget Bars dengan layout yang lebih responsive
          LayoutBuilder(
            builder: (context, constraints) {
              // Jika width terlalu kecil, gunakan column layout
              if (constraints.maxWidth < 300) {
                return Column(
                  children: [
                    _buildBudgetBar('Kebutuhan', '50%', needsUsed, AppColors.success, '🏠'),
                    const SizedBox(height: 12),
                    _buildBudgetBar('Keinginan', '30%', wantsUsed, AppColors.warning, '🎯'),
                    const SizedBox(height: 12),
                    _buildBudgetBar('Tabungan', '20%', savingsUsed, AppColors.primary, '💰'),
                  ],
                );
              } else {
                return Row(
                  children: [
                    Expanded(
                      child: _buildBudgetBar('Kebutuhan', '50%', needsUsed, AppColors.success, '🏠'),
                    ),
                    const SizedBox(width: 8), // Kurangi spacing
                    Expanded(
                      child: _buildBudgetBar('Keinginan', '30%', wantsUsed, AppColors.warning, '🎯'),
                    ),
                    const SizedBox(width: 8), // Kurangi spacing
                    Expanded(
                      child: _buildBudgetBar('Tabungan', '20%', savingsUsed, AppColors.primary, '💰'),
                    ),
                  ],
                );
              }
            },
          ),
        ],
      ),
    );
  }

  // PERBAIKAN: Budget Bar dengan text yang lebih compact
  Widget _buildBudgetBar(String title, String target, double percentageUsed, Color color, String emoji) {
    return Column(
      children: [
        // PERBAIKAN: Title dengan Flexible
        FittedBox(
          fit: BoxFit.scaleDown,
          child: Row(
            mainAxisAlignment: MainAxisAlignment.center,
            mainAxisSize: MainAxisSize.min,
            children: [
              Text(
                emoji,
                style: const TextStyle(fontSize: 14), // Kecilkan emoji
              ),
              const SizedBox(width: 4),
              Text(
                title,
                style: AppTextStyles.caption.copyWith(
                  fontWeight: FontWeight.w600,
                  color: AppColors.textSecondary,
                ),
              ),
            ],
          ),
        ),
        const SizedBox(height: 8),
        Container(
          height: 6, // Kecilkan tinggi bar
          decoration: BoxDecoration(
            color: AppColors.gray200,
            borderRadius: BorderRadius.circular(3),
          ),
          child: FractionallySizedBox(
            alignment: Alignment.centerLeft,
            widthFactor: (percentageUsed / 100).clamp(0.0, 1.0),
            child: Container(
              decoration: BoxDecoration(
                color: percentageUsed > 100 ? AppColors.error : color,
                borderRadius: BorderRadius.circular(3),
              ),
            ),
          ),
        ),
        const SizedBox(height: 6),
        Text(
          '${percentageUsed.toStringAsFixed(0)}%',
          style: AppTextStyles.caption.copyWith(
            color: percentageUsed > 100 ? AppColors.error : color,
            fontWeight: FontWeight.w600,
          ),
        ),
        Text(
          target,
          style: AppTextStyles.caption.copyWith(
            color: AppColors.textTertiary,
            fontSize: 10, // Kecilkan font size
          ),
        ),
      ],
    );
  }

  Widget _buildTabBar() {
    return Container(
      color: AppColors.white,
      padding: const EdgeInsets.symmetric(horizontal: 24),
      child: Column(
        children: [
          Container(
            decoration: BoxDecoration(
              color: AppColors.gray100,
              borderRadius: BorderRadius.circular(12),
            ),
            child: TabBar(
              controller: _tabController,
              labelColor: AppColors.white,
              unselectedLabelColor: AppColors.textSecondary,
              labelStyle: AppTextStyles.labelSmall.copyWith(
                fontWeight: FontWeight.w600,
              ),
              unselectedLabelStyle: AppTextStyles.labelSmall,
              indicator: BoxDecoration(
                color: AppColors.primary,
                borderRadius: BorderRadius.circular(10),
              ),
              indicatorSize: TabBarIndicatorSize.tab,
              indicatorPadding: const EdgeInsets.all(2),
              dividerColor: Colors.transparent,
              splashBorderRadius: BorderRadius.circular(10),
              tabs: _tabs,
            ),
          ),
          const SizedBox(height: 16),
        ],
      ),
    );
  }

  Color _getBudgetHealthColor(String health) {
    switch (health) {
      case 'excellent':
        return AppColors.success;
      case 'good':
        return AppColors.primary;
      case 'warning':
        return AppColors.warning;
      case 'over_budget':
        return AppColors.error;
      default:
        return AppColors.gray500;
    }
  }

  String _getBudgetHealthText(String health) {
    switch (health) {
      case 'excellent':
        return 'Sangat Baik';
      case 'good':
        return 'Baik';
      case 'warning':
        return 'Perlu Perhatian';
      case 'over_budget':
        return 'Over Budget';
      default:
        return 'Unknown';
    }
  }
}