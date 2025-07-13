import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../../providers/finance_provider.dart';
import '../../../providers/auth_provider.dart';
import '../../../utils/app_colors.dart';
import '../../../utils/app_text_styles.dart';
import '../../../utils/format_utils.dart';
import '../../../widgets/custom_widgets.dart';
import '../../../widgets/common_widgets.dart';

class DashboardTab extends StatefulWidget {
  const DashboardTab({Key? key}) : super(key: key);

  @override
  State<DashboardTab> createState() => _DashboardTabState();
}

class _DashboardTabState extends State<DashboardTab> {
  bool _isInitialized = false;

  @override
  void initState() {
    super.initState();
    // Use addPostFrameCallback to avoid setState during build
    WidgetsBinding.instance.addPostFrameCallback((_) {
      _initializeData();
    });
  }

  Future<void> _initializeData() async {
    if (!_isInitialized && mounted) {
      final financeProvider = Provider.of<FinanceProvider>(context, listen: false);
      // Only load if data doesn't exist
      if (financeProvider.dashboardData == null) {
        await financeProvider.loadDashboardSummary();
      }
      if (financeProvider.statsData == null) {
        await financeProvider.loadBasicStats();
      }
      if (financeProvider.progressData == null) {
        await financeProvider.loadProgressData();
      }
      
      if (mounted) {
        setState(() {
          _isInitialized = true;
        });
      }
    }
  }
  @override
  Widget build(BuildContext context) {
    return RefreshIndicator(
      onRefresh: () async {
        if (mounted) {
          final financeProvider = Provider.of<FinanceProvider>(context, listen: false);
          await financeProvider.loadAllEssentialData();
        }
      },
      child: SingleChildScrollView(
        physics: const AlwaysScrollableScrollPhysics(),
        padding: const EdgeInsets.all(24),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Financial Overview Card
            _buildFinancialOverviewCard(),
            
            const SizedBox(height: 24),
            
            // Quick Stats Row
            Row(
              children: [
                Expanded(child: _buildQuickStatCard()),
                const SizedBox(width: 16),
                Expanded(child: _buildSavingsProgressCard()),
              ],
            ),
            
            const SizedBox(height: 24),
            
            // Savings Goals Section
            _buildSavingsGoalsSection(),
            
            const SizedBox(height: 24),
            
            // Recent Activity & Tips Section - Stacked vertically instead of side by side
            _buildRecentActivityCard(),
            
            const SizedBox(height: 16),
            
            _buildFinancialTipsCard(),
          ],
        ),
      ),
    );
  }

  Widget _buildFinancialOverviewCard() {
    return Consumer<FinanceProvider>(
      builder: (context, financeProvider, child) {
        if (financeProvider.isLoadingDashboard) {
          return _buildLoadingCard(height: 200);
        }

        if (financeProvider.dashboardError != null) {
          return ErrorMessage(
            message: financeProvider.dashboardError!,
            onRetry: () => financeProvider.loadDashboardSummary(),
          );
        }

        final dashboardData = financeProvider.dashboardData;
        if (dashboardData == null) {
          return const EmptyStateWidget(
            icon: Icons.dashboard_outlined,
            title: 'Tidak ada data dashboard',
            subtitle: 'Data keuangan belum tersedia',
          );
        }

        final monthlyTotals = dashboardData['monthly_totals'] ?? {};
        final savingsSummary = dashboardData['savings_summary'] ?? {};
        final period = dashboardData['period'] ?? {};

        return CustomCard(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Container(
                    padding: const EdgeInsets.all(12),
                    decoration: BoxDecoration(
                      color: AppColors.primary.withOpacity(0.1),
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: Icon(
                      Icons.account_balance_wallet_outlined,
                      color: AppColors.primary,
                      size: 24,
                    ),
                  ),
                  const SizedBox(width: 16),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          'Ringkasan Keuangan',
                          style: AppTextStyles.h6.copyWith(
                            fontWeight: FontWeight.w600,
                          ),
                        ),
                        Text(
                          period['month_year'] ?? 'Bulan ini',
                          style: AppTextStyles.bodySmall.copyWith(
                            color: AppColors.textSecondary,
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
              
              const SizedBox(height: 24),
              
              // Financial metrics
              Row(
                children: [
                  Expanded(
                    child: _buildMetricItem(
                      'Pemasukan',
                      monthlyTotals['formatted_income'] ?? 'Rp 0',
                      Icons.trending_up,
                      AppColors.success,
                    ),
                  ),
                  const SizedBox(width: 16),
                  Expanded(
                    child: _buildMetricItem(
                      'Pengeluaran',
                      monthlyTotals['formatted_expense'] ?? 'Rp 0',
                      Icons.trending_down,
                      AppColors.error,
                    ),
                  ),
                ],
              ),
              
              const SizedBox(height: 16),
              
              Row(
                children: [
                  Expanded(
                    child: _buildMetricItem(
                      'Saldo Bersih',
                      monthlyTotals['formatted_balance'] ?? 'Rp 0',
                      Icons.account_balance,
                      monthlyTotals['net_balance'] != null && monthlyTotals['net_balance'] >= 0
                          ? AppColors.success
                          : AppColors.error,
                    ),
                  ),
                  const SizedBox(width: 16),
                  Expanded(
                    child: _buildMetricItem(
                      'Total Tabungan',
                      savingsSummary['formatted_total_savings'] ?? 'Rp 0',
                      Icons.savings,
                      AppColors.primary,
                    ),
                  ),
                ],
              ),
            ],
          ),
        );
      },
    );
  }

  Widget _buildQuickStatCard() {
    return Consumer<FinanceProvider>(
      builder: (context, financeProvider, child) {
        if (financeProvider.isLoadingStats) {
          return _buildLoadingCard(height: 120);
        }

        final statsData = financeProvider.statsData;
        if (statsData == null) return Container();

        final currentMonth = statsData['current_month'] ?? {};
        final changeData = statsData['month_over_month_change'] ?? {};

        return CustomCard(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                'Statistik Cepat',
                style: AppTextStyles.labelLarge.copyWith(
                  fontWeight: FontWeight.w600,
                ),
              ),
              const SizedBox(height: 16),
              
              _buildStatRow(
                'Transaksi Bulan Ini',
                '${currentMonth['transactions'] ?? 0}',
                Icons.receipt_long,
              ),
              
              const SizedBox(height: 12),
              
              _buildStatRow(
                'Perubahan Pemasukan',
                '${changeData['income_change_percent'] ?? 0}%',
                changeData['income_trend'] == 'up' ? Icons.arrow_upward : Icons.arrow_downward,
                color: changeData['income_trend'] == 'up' ? AppColors.success : AppColors.error,
              ),
            ],
          ),
        );
      },
    );
  }

  Widget _buildSavingsProgressCard() {
    return Consumer<FinanceProvider>(
      builder: (context, financeProvider, child) {
        if (financeProvider.isLoadingProgress) {
          return _buildLoadingCard(height: 120);
        }

        final progressData = financeProvider.progressData;
        if (progressData == null) return Container();

        final monthlyProgress = progressData['monthly_savings_progress'] ?? {};

        return CustomCard(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                'Target Tabungan Bulanan',
                style: AppTextStyles.labelLarge.copyWith(
                  fontWeight: FontWeight.w600,
                ),
              ),
              const SizedBox(height: 16),
              
              LinearProgressIndicator(
                value: (monthlyProgress['progress_percentage'] ?? 0) / 100,
                backgroundColor: AppColors.gray200,
                valueColor: AlwaysStoppedAnimation<Color>(AppColors.primary),
                minHeight: 8,
              ),
              
              const SizedBox(height: 12),
              
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text(
                    '${monthlyProgress['progress_percentage'] ?? 0}%',
                    style: AppTextStyles.labelMedium.copyWith(
                      color: AppColors.primary,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                  Text(
                    monthlyProgress['formatted_target'] ?? 'Rp 0',
                    style: AppTextStyles.labelSmall.copyWith(
                      color: AppColors.textSecondary,
                    ),
                  ),
                ],
              ),
            ],
          ),
        );
      },
    );
  }

  Widget _buildSavingsGoalsSection() {
    return Consumer<FinanceProvider>(
      builder: (context, financeProvider, child) {
        if (financeProvider.isLoadingProgress) {
          return _buildLoadingCard(height: 200);
        }

        final progressData = financeProvider.progressData;
        if (progressData == null) return Container();

        final savingsGoals = progressData['savings_goals_progress'] ?? [];

        return CustomCard(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Icon(
                    Icons.savings_outlined,
                    color: AppColors.primary,
                    size: 20,
                  ),
                  const SizedBox(width: 8),
                  Text(
                    'Target Tabungan',
                    style: AppTextStyles.labelLarge.copyWith(
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                ],
              ),
              
              const SizedBox(height: 16),
              
              if (savingsGoals.isEmpty)
                Center(
                  child: Column(
                    children: [
                      Icon(
                        Icons.savings_outlined,
                        size: 48,
                        color: AppColors.gray400,
                      ),
                      const SizedBox(height: 8),
                      Text(
                        'Belum ada target tabungan',
                        style: AppTextStyles.bodyMedium.copyWith(
                          color: AppColors.textSecondary,
                        ),
                      ),
                    ],
                  ),
                )
              else
                ...savingsGoals.take(3).map((goal) => 
                  _buildSavingsGoalItem(goal)
                ).toList(),
              
              if (savingsGoals.length > 3) ...[
                const SizedBox(height: 12),
                Center(
                  child: TextButton(
                    onPressed: () {
                      // Navigate to full goals view
                    },
                    child: Text(
                      'Lihat Semua (${savingsGoals.length})',
                      style: AppTextStyles.labelMedium.copyWith(
                        color: AppColors.primary,
                      ),
                    ),
                  ),
                ),
              ],
            ],
          ),
        );
      },
    );
  }

  Widget _buildSavingsGoalItem(Map<String, dynamic> goal) {
    return Container(
      margin: const EdgeInsets.only(bottom: 16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                goal['item_name'] ?? '',
                style: AppTextStyles.bodyMedium.copyWith(
                  fontWeight: FontWeight.w500,
                ),
              ),
              Text(
                '${goal['progress_percentage'] ?? 0}%',
                style: AppTextStyles.labelMedium.copyWith(
                  color: AppColors.primary,
                  fontWeight: FontWeight.w600,
                ),
              ),
            ],
          ),
          const SizedBox(height: 8),
          LinearProgressIndicator(
            value: (goal['progress_percentage'] ?? 0) / 100,
            backgroundColor: AppColors.gray200,
            valueColor: AlwaysStoppedAnimation<Color>(AppColors.primary),
            minHeight: 6,
          ),
          const SizedBox(height: 4),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                goal['formatted_current'] ?? 'Rp 0',
                style: AppTextStyles.caption.copyWith(
                  color: AppColors.textSecondary,
                ),
              ),
              Text(
                goal['formatted_target'] ?? 'Rp 0',
                style: AppTextStyles.caption.copyWith(
                  color: AppColors.textSecondary,
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildRecentActivityCard() {
    return CustomCard(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(
                Icons.history,
                color: AppColors.primary,
                size: 20,
              ),
              const SizedBox(width: 8),
              Text(
                'Aktivitas Terbaru',
                style: AppTextStyles.labelLarge.copyWith(
                  fontWeight: FontWeight.w600,
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          
          // Placeholder for recent transactions
          _buildActivityItem(
            'Pengeluaran - Makan Siang',
            'Rp 25.000',
            '2 jam lalu',
            Icons.restaurant,
            AppColors.error,
          ),
          _buildActivityItem(
            'Pemasukan - Freelance',
            'Rp 500.000',
            '1 hari lalu',
            Icons.work,
            AppColors.success,
          ),
          _buildActivityItem(
            'Pengeluaran - Transport',
            'Rp 15.000',
            '2 hari lalu',
            Icons.directions_bus,
            AppColors.error,
          ),
          
          const SizedBox(height: 12),
          Center(
            child: TextButton(
              onPressed: () {
                // Navigate to full history
              },
              child: Text(
                'Lihat Semua History',
                style: AppTextStyles.labelMedium.copyWith(
                  color: AppColors.primary,
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildFinancialTipsCard() {
    return CustomCard(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(
                Icons.lightbulb_outline,
                color: AppColors.warning,
                size: 20,
              ),
              const SizedBox(width: 8),
              Text(
                'Tips Keuangan',
                style: AppTextStyles.labelLarge.copyWith(
                  fontWeight: FontWeight.w600,
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: AppColors.warning.withOpacity(0.1),
              borderRadius: BorderRadius.circular(8),
              border: Border.all(
                color: AppColors.warning.withOpacity(0.3),
              ),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  '💡 Tip Hari Ini',
                  style: AppTextStyles.labelMedium.copyWith(
                    color: AppColors.warning,
                    fontWeight: FontWeight.w600,
                  ),
                ),
                const SizedBox(height: 8),
                Text(
                  'Alokasikan 20% dari pemasukan untuk tabungan darurat. Ini akan membantu Anda menghadapi situasi tak terduga.',
                  style: AppTextStyles.bodySmall.copyWith(
                    color: AppColors.textPrimary,
                    height: 1.4,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildMetricItem(String label, String value, IconData icon, Color color) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            Icon(
              icon,
              size: 16,
              color: color,
            ),
            const SizedBox(width: 6),
            Text(
              label,
              style: AppTextStyles.bodySmall.copyWith(
                color: AppColors.textSecondary,
              ),
            ),
          ],
        ),
        const SizedBox(height: 4),
        Text(
          value,
          style: AppTextStyles.labelLarge.copyWith(
            color: color,
            fontWeight: FontWeight.w600,
          ),
        ),
      ],
    );
  }

  Widget _buildStatRow(String label, String value, IconData icon, {Color? color}) {
    return Row(
      children: [
        Icon(
          icon,
          size: 16,
          color: color ?? AppColors.textSecondary,
        ),
        const SizedBox(width: 8),
        Expanded(
          child: Text(
            label,
            style: AppTextStyles.bodySmall.copyWith(
              color: AppColors.textSecondary,
            ),
          ),
        ),
        Text(
          value,
          style: AppTextStyles.labelMedium.copyWith(
            color: color ?? AppColors.textPrimary,
            fontWeight: FontWeight.w600,
          ),
        ),
      ],
    );
  }

  Widget _buildActivityItem(String title, String amount, String time, IconData icon, Color color) {
    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      child: Row(
        children: [
          Container(
            width: 32,
            height: 32,
            decoration: BoxDecoration(
              color: color.withOpacity(0.1),
              borderRadius: BorderRadius.circular(8),
            ),
            child: Icon(
              icon,
              size: 16,
              color: color,
            ),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  title,
                  style: AppTextStyles.bodySmall.copyWith(
                    fontWeight: FontWeight.w500,
                  ),
                ),
                Text(
                  time,
                  style: AppTextStyles.caption.copyWith(
                    color: AppColors.textTertiary,
                  ),
                ),
              ],
            ),
          ),
          Text(
            amount,
            style: AppTextStyles.labelMedium.copyWith(
              color: color,
              fontWeight: FontWeight.w600,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildLoadingCard({double? height}) {
    return CustomCard(
      child: SizedBox(
        height: height,
        child: Center(
          child: CircularProgressIndicator(
            valueColor: AlwaysStoppedAnimation<Color>(AppColors.primary),
          ),
        ),
      ),
    );
  }
}