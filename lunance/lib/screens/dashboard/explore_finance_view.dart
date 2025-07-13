import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../providers/finance_provider.dart';
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
    _initializeData();
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  Future<void> _initializeData() async {
    if (!_isInitialized) {
      final financeProvider = Provider.of<FinanceProvider>(context, listen: false);
      await financeProvider.loadAllEssentialData();
      setState(() {
        _isInitialized = true;
      });
    }
  }

  Future<void> _refreshData() async {
    final financeProvider = Provider.of<FinanceProvider>(context, listen: false);
    await financeProvider.loadAllEssentialData();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      body: Column(
        children: [
          // Tab Bar Header
          _buildTabBarHeader(),
          
          // Tab Bar Content
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
  }

  Widget _buildTabBarHeader() {
    return Container(
      color: AppColors.white,
      child: Column(
        children: [
          // Header with refresh button
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 16),
            child: Row(
              children: [
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'Jelajahi Keuangan',
                        style: AppTextStyles.h5.copyWith(
                          fontWeight: FontWeight.w700,
                        ),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        'Analisis lengkap kondisi keuangan Anda',
                        style: AppTextStyles.bodySmall.copyWith(
                          color: AppColors.textSecondary,
                        ),
                      ),
                    ],
                  ),
                ),
                Consumer<FinanceProvider>(
                  builder: (context, financeProvider, child) {
                    final isAnyLoading = financeProvider.isLoadingDashboard ||
                        financeProvider.isLoadingStats ||
                        financeProvider.isLoadingProgress;

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
          ),
          
          // Tab Bar
          Container(
            margin: const EdgeInsets.symmetric(horizontal: 24),
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
}