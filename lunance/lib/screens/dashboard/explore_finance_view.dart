import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../providers/auth_provider.dart';
import '../../utils/app_colors.dart';
import '../../utils/app_text_styles.dart';
import '../../widgets/custom_widgets.dart';
import 'explore_finance/widgets/quick_stats_header.dart';
import 'explore_finance/tabs/overview_tab.dart';
import 'explore_finance/tabs/income_tab.dart';
import 'explore_finance/tabs/expense_tab.dart';
import 'explore_finance/tabs/savings_tab.dart';
import 'explore_finance/tabs/prediction_tab.dart';

class ExploreFinanceView extends StatefulWidget {
  const ExploreFinanceView({Key? key}) : super(key: key);

  @override
  State<ExploreFinanceView> createState() => _ExploreFinanceViewState();
}

class _ExploreFinanceViewState extends State<ExploreFinanceView>
    with SingleTickerProviderStateMixin {
  late TabController _tabController;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 5, vsync: this);
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      body: Column(
        children: [
          // Header with Quick Stats
          const QuickStatsHeader(),
          
          // Tab Bar
          _buildTabBar(),
          
          // Tab Content
          Expanded(
            child: TabBarView(
              controller: _tabController,
              children: const [
                OverviewTab(),
                IncomeTab(),
                ExpenseTab(),
                SavingsTab(),
                PredictionTab(),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildTabBar() {
    return Container(
      decoration: BoxDecoration(
        color: AppColors.white,
        border: Border(
          bottom: BorderSide(color: AppColors.border, width: 1),
        ),
      ),
      child: TabBar(
        controller: _tabController,
        isScrollable: true,
        labelColor: AppColors.primary,
        unselectedLabelColor: AppColors.textSecondary,
        labelStyle: AppTextStyles.labelMedium.copyWith(
          fontWeight: FontWeight.w600,
        ),
        unselectedLabelStyle: AppTextStyles.labelMedium,
        indicatorColor: AppColors.primary,
        indicatorWeight: 2,
        tabs: const [
          Tab(text: 'Ringkasan'),
          Tab(text: 'Pemasukan'),
          Tab(text: 'Pengeluaran'),
          Tab(text: 'Tabungan'),
          Tab(text: 'Prediksi'),
        ],
      ),
    );
  }
}