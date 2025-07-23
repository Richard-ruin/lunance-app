import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../providers/finance_provider.dart';
import '../../providers/auth_provider.dart';
import '../../utils/app_colors.dart';
import '../../utils/app_text_styles.dart';
import '../../utils/format_eksplore.dart';
import '../../widgets/custom_widgets.dart';
import '../../widgets/common_widgets.dart';
import 'finance/dashboard_tab.dart';
import 'finance/analytics_tab.dart';
import 'finance/history_tab.dart';
import 'finance/reports_tab.dart'; // CHANGED: reports instead of predictions

class ExploreFinanceView extends StatefulWidget {
  const ExploreFinanceView({Key? key}) : super(key: key);

  @override
  State<ExploreFinanceView> createState() => _ExploreFinanceViewState();
}

class _ExploreFinanceViewState extends State<ExploreFinanceView>
    with SingleTickerProviderStateMixin {
  late TabController _tabController;
  bool _isInitialized = false;
  bool _hasError = false;
  String? _errorMessage;

  // UPDATED: Replace predictions with reports
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
      icon: Icon(Icons.assessment_outlined), // CHANGED: reports icon
      text: 'Reports', // CHANGED: reports text
    ),
  ];

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: _tabs.length, vsync: this);
    
    // FIXED: Add error handling for initialization
    WidgetsBinding.instance.addPostFrameCallback((_) {
      _safeInitializeData();
    });
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  // FIXED: Safe initialization with comprehensive error handling
  Future<void> _safeInitializeData() async {
    if (_isInitialized || !mounted) return;
    
    try {
      setState(() {
        _hasError = false;
        _errorMessage = null;
      });

      // Check auth state first
      final authProvider = Provider.of<AuthProvider>(context, listen: false);
      final user = authProvider.user;
      
      if (user == null) {
        if (mounted) {
          setState(() {
            _hasError = true;
            _errorMessage = 'User tidak ditemukan. Silakan login kembali.';
            _isInitialized = true;
          });
        }
        return;
      }

      // Check financial setup
      final hasFinancialSetup = user.financialSetupCompleted ?? false;
      if (!hasFinancialSetup) {
        if (mounted) {
          setState(() {
            _isInitialized = true;
          });
        }
        return; // Will show setup required view
      }

      // Initialize finance provider with error handling
      final financeProvider = Provider.of<FinanceProvider>(context, listen: false);
      
      // Only load if not already loaded and not currently loading
      if (financeProvider.dashboardData == null && !financeProvider.isLoadingDashboard) {
        try {
          await financeProvider.loadDashboard();
        } catch (e) {
          debugPrint('Error loading dashboard: $e');
          // Don't throw error here, let the UI handle it
        }
      }
      
      if (mounted) {
        setState(() {
          _isInitialized = true;
        });
      }
    } catch (e) {
      debugPrint('Error in _safeInitializeData: $e');
      if (mounted) {
        setState(() {
          _hasError = true;
          _errorMessage = 'Terjadi kesalahan saat memuat data: ${e.toString()}';
          _isInitialized = true;
        });
      }
    }
  }

  // FIXED: Safe refresh with error handling
  Future<void> _safeRefreshData() async {
    if (!mounted) return;
    
    try {
      final financeProvider = Provider.of<FinanceProvider>(context, listen: false);
      
      // Clear any existing errors
      setState(() {
        _hasError = false;
        _errorMessage = null;
      });
      
      await financeProvider.refreshAllData();
      
    } catch (e) {
      debugPrint('Error in _safeRefreshData: $e');
      if (mounted) {
        setState(() {
          _hasError = true;
          _errorMessage = 'Gagal memuat data: ${e.toString()}';
        });
        
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Gagal memuat data: ${e.toString()}'),
            backgroundColor: AppColors.error,
            action: SnackBarAction(
              label: 'Coba Lagi',
              textColor: AppColors.white,
              onPressed: _safeRefreshData,
            ),
          ),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    // FIXED: Show error state if initialization failed
    if (_hasError && _errorMessage != null) {
      return _buildErrorView();
    }

    return Consumer<AuthProvider>(
      builder: (context, authProvider, child) {
        final user = authProvider.user;
        
        if (user == null) {
          return _buildUserNotFoundView();
        }
        
        final hasFinancialSetup = user.financialSetupCompleted ?? false;
        
        if (!hasFinancialSetup) {
          return _buildSetupRequiredView();
        }
        
        return Scaffold(
          backgroundColor: AppColors.background,
          body: Column(
            children: [
              // Tab Bar
              _buildTabBar(),
              
              // Tab Content with Error Boundary
              Expanded(
                child: _buildTabContent(),
              ),
            ],
          ),
        );
      },
    );
  }

  // FIXED: Error boundary for tab content
  Widget _buildTabContent() {
    return Consumer<FinanceProvider>(
      builder: (context, financeProvider, child) {
        // Show loading during initialization
        if (!_isInitialized) {
          return Center(
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                CircularProgressIndicator(
                  valueColor: AlwaysStoppedAnimation<Color>(AppColors.primary),
                ),
                const SizedBox(height: 16),
                Text(
                  'Memuat data keuangan...',
                  style: AppTextStyles.bodyMedium.copyWith(
                    color: AppColors.textSecondary,
                  ),
                ),
              ],
            ),
          );
        }

        // Wrap TabBarView with error handling
        return TabBarView(
          controller: _tabController,
          children: [
            _buildSafeTab(const DashboardTab()),
            _buildSafeTab(const AnalyticsTab()),
            _buildSafeTab(const HistoryTab()),
            _buildSafeTab(const ReportsTab()), // CHANGED: ReportsTab instead of PredictionsTab
          ],
        );
      },
    );
  }

  // FIXED: Safe tab wrapper with error boundary
  Widget _buildSafeTab(Widget child) {
    return Builder(
      builder: (context) {
        try {
          return child;
        } catch (e) {
          debugPrint('Error in tab: $e');
          return _buildTabErrorView(e.toString());
        }
      },
    );
  }

  Widget _buildTabErrorView(String error) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(32),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              Icons.error_outline,
              size: 64,
              color: AppColors.error,
            ),
            const SizedBox(height: 16),
            Text(
              'Terjadi Kesalahan',
              style: AppTextStyles.h6.copyWith(
                color: AppColors.error,
                fontWeight: FontWeight.w600,
              ),
            ),
            const SizedBox(height: 8),
            Text(
              error,
              style: AppTextStyles.bodyMedium.copyWith(
                color: AppColors.textSecondary,
              ),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 24),
            ElevatedButton(
              onPressed: _safeRefreshData,
              style: ElevatedButton.styleFrom(
                backgroundColor: AppColors.primary,
                foregroundColor: AppColors.white,
              ),
              child: Text('Coba Lagi'),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildErrorView() {
    return Scaffold(
      backgroundColor: AppColors.background,
      body: Center(
        child: Padding(
          padding: const EdgeInsets.all(32),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(
                Icons.error_outline,
                size: 80,
                color: AppColors.error,
              ),
              const SizedBox(height: 24),
              Text(
                'Terjadi Kesalahan',
                style: AppTextStyles.h5.copyWith(
                  fontWeight: FontWeight.w600,
                  color: AppColors.error,
                ),
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 16),
              Text(
                _errorMessage ?? 'Kesalahan tidak diketahui',
                style: AppTextStyles.bodyMedium.copyWith(
                  color: AppColors.textSecondary,
                  height: 1.5,
                ),
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 32),
              Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  OutlinedButton(
                    onPressed: () => Navigator.pop(context),
                    child: Text('Kembali'),
                  ),
                  const SizedBox(width: 16),
                  ElevatedButton(
                    onPressed: () {
                      setState(() {
                        _isInitialized = false;
                        _hasError = false;
                        _errorMessage = null;
                      });
                      _safeInitializeData();
                    },
                    style: ElevatedButton.styleFrom(
                      backgroundColor: AppColors.primary,
                      foregroundColor: AppColors.white,
                    ),
                    child: Text('Coba Lagi'),
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildUserNotFoundView() {
    return Scaffold(
      backgroundColor: AppColors.background,
      body: Center(
        child: Padding(
          padding: const EdgeInsets.all(32),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(
                Icons.person_off_outlined,
                size: 80,
                color: AppColors.warning,
              ),
              const SizedBox(height: 24),
              Text(
                'User Tidak Ditemukan',
                style: AppTextStyles.h5.copyWith(
                  fontWeight: FontWeight.w600,
                ),
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 16),
              Text(
                'Silakan login kembali untuk mengakses fitur keuangan.',
                style: AppTextStyles.bodyMedium.copyWith(
                  color: AppColors.textSecondary,
                  height: 1.5,
                ),
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 32),
              ElevatedButton(
                onPressed: () {
                  Navigator.pushReplacementNamed(context, '/login');
                },
                style: ElevatedButton.styleFrom(
                  backgroundColor: AppColors.primary,
                  foregroundColor: AppColors.white,
                ),
                child: Text('Login'),
              ),
            ],
          ),
        ),
      ),
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
              
              CustomButton(
                text: 'Setup Keuangan Sekarang',
                icon: Icons.settings_outlined,
                onPressed: () {
                  Navigator.pushNamed(context, '/financial-setup');
                },
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildTabBar() {
    return Container(
      color: AppColors.white,
      padding: const EdgeInsets.symmetric(horizontal: 24),
      child: Column(
        children: [
          const SizedBox(height: 24),
          
          // Tab Bar Header
          Row(
            children: [
              Icon(
                Icons.account_balance_wallet_outlined,
                color: AppColors.primary,
                size: 24,
              ),
              const SizedBox(width: 12),
              Text(
                'Keuangan Mahasiswa',
                style: AppTextStyles.h6.copyWith(
                  fontWeight: FontWeight.w600,
                ),
              ),
              const Spacer(),
              
              // Refresh Button
              IconButton(
                onPressed: _safeRefreshData,
                icon: Icon(
                  Icons.refresh,
                  color: AppColors.textSecondary,
                ),
                style: IconButton.styleFrom(
                  backgroundColor: AppColors.gray100,
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(8),
                  ),
                ),
              ),
            ],
          ),
          
          const SizedBox(height: 16),
          
          // Tab Bar
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
          
          // Method Badge
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
            decoration: BoxDecoration(
              color: AppColors.success.withOpacity(0.1),
              borderRadius: BorderRadius.circular(20),
              border: Border.all(
                color: AppColors.success.withOpacity(0.3),
              ),
            ),
            child: Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                Icon(
                  Icons.check_circle_outline,
                  size: 16,
                  color: AppColors.success,
                ),
                const SizedBox(width: 6),
                Text(
                  'Metode 50/30/20 Elizabeth Warren',
                  style: AppTextStyles.caption.copyWith(
                    color: AppColors.success,
                    fontWeight: FontWeight.w600,
                  ),
                ),
              ],
            ),
          ),
          
          const SizedBox(height: 16),
        ],
      ),
    );
  }
}