import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../../providers/finance_provider.dart';
import '../../../providers/auth_provider.dart';
import '../../../utils/app_colors.dart';
import '../../../utils/app_text_styles.dart';
import '../../../utils/format_eksplore.dart';
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
    // FIX: Use addPostFrameCallback to prevent setState during build
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (mounted) {
        _initializeData();
      }
    });
  }

  // FIX: Make this method more defensive
  Future<void> _initializeData() async {
    if (_isInitialized || !mounted) return;

    try {
      final financeProvider =
          Provider.of<FinanceProvider>(context, listen: false);

      // Only load data if not already loaded or loading
      final futures = <Future<void>>[];

      if (financeProvider.dashboardData == null &&
          !financeProvider.isLoadingDashboard) {
        futures.add(financeProvider.loadDashboard());
      }

      if (financeProvider.budgetStatusData == null &&
          !financeProvider.isLoadingBudgetStatus) {
        futures.add(financeProvider.loadBudgetStatus());
      }

      if (financeProvider.progressData == null &&
          !financeProvider.isLoadingProgress) {
        futures.add(financeProvider.loadProgress());
      }

      // Wait for all futures to complete
      if (futures.isNotEmpty) {
        await Future.wait(futures, eagerError: false);
      }

      if (mounted) {
        setState(() {
          _isInitialized = true;
        });
      }
    } catch (e) {
      // Handle errors gracefully
      if (mounted) {
        setState(() {
          _isInitialized = true; // Still set to true to prevent loops
        });
      }
      debugPrint('Error initializing dashboard data: $e');
    }
  }

  Future<void> _refreshData() async {
    if (!mounted) return;

    try {
      final financeProvider =
          Provider.of<FinanceProvider>(context, listen: false);

      // Load data in parallel
      await Future.wait([
        financeProvider.loadDashboard(),
        financeProvider.loadBudgetStatus(),
        financeProvider.loadProgress(),
      ], eagerError: false);
    } catch (e) {
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
    return RefreshIndicator(
      onRefresh: _refreshData,
      child: SingleChildScrollView(
        physics: const AlwaysScrollableScrollPhysics(),
        padding: const EdgeInsets.all(24),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Quick Stats Overview
            _buildQuickStatsOverview(),

            const SizedBox(height: 24),

            // Budget Health Card
            _buildBudgetHealthCard(),

            const SizedBox(height: 24),

            // 50/30/20 Budget Breakdown
            _buildBudgetBreakdownCard(),

            const SizedBox(height: 24),

            // Financial Summary
            _buildFinancialSummaryCard(),

            const SizedBox(height: 24),

            // Savings Goals Progress
            _buildSavingsGoalsCard(),

            const SizedBox(height: 24),

            // Recent Activity
            _buildRecentActivityCard(),

            const SizedBox(height: 24),

            // Student Tips
            _buildStudentTipsCard(),
          ],
        ),
      ),
    );
  }

  Widget _buildQuickStatsOverview() {
    return Consumer<FinanceProvider>(
      builder: (context, financeProvider, child) {
        if (financeProvider.isLoadingDashboard) {
          return _buildLoadingCard(height: 140);
        }

        if (financeProvider.dashboardError != null) {
          return ErrorMessage(
            message: financeProvider.dashboardError!,
            onRetry: () => financeProvider.loadDashboard(),
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

        // Extract quick stats
        final quickStats = dashboardData['quick_stats'] ?? {};
        final realTotalSavings =
            (quickStats['real_total_savings'] ?? 0.0).toDouble();
        final monthlyIncome = (quickStats['monthly_income'] ?? 0.0).toDouble();
        final currentSpending = quickStats['current_month_spending'] ?? {};

        final totalSpending = ((currentSpending['needs'] ?? 0.0) +
                (currentSpending['wants'] ?? 0.0) +
                (currentSpending['savings'] ?? 0.0))
            .toDouble();

        return CustomCard(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Container(
                    padding: const EdgeInsets.all(10),
                    decoration: BoxDecoration(
                      color: AppColors.primary.withOpacity(0.1),
                      borderRadius: BorderRadius.circular(10),
                    ),
                    child: Icon(
                      Icons.account_balance_wallet_outlined,
                      color: AppColors.primary,
                      size: 20,
                    ),
                  ),
                  const SizedBox(width: 12),
                  Flexible(
                    // PERBAIKAN: Gunakan Flexible
                    child: Text(
                      'Ringkasan Keuangan',
                      style: AppTextStyles.labelLarge.copyWith(
                        fontWeight: FontWeight.w600,
                      ),
                      overflow: TextOverflow.ellipsis,
                    ),
                  ),
                ],
              ),

              const SizedBox(height: 20),

              // Total Savings - Highlighted
              Container(
                width: double.infinity,
                padding: const EdgeInsets.all(20),
                decoration: BoxDecoration(
                  gradient: LinearGradient(
                    colors: [
                      AppColors.primary.withOpacity(0.1),
                      AppColors.success.withOpacity(0.1),
                    ],
                    begin: Alignment.topLeft,
                    end: Alignment.bottomRight,
                  ),
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(
                    color: AppColors.primary.withOpacity(0.3),
                  ),
                ),
                child: Column(
                  children: [
                    Text(
                      'Total Tabungan Real-Time',
                      style: AppTextStyles.bodySmall.copyWith(
                        color: AppColors.primary,
                        fontWeight: FontWeight.w600,
                      ),
                      textAlign: TextAlign.center, // Center text
                    ),
                    const SizedBox(height: 8),
                    // PERBAIKAN: FittedBox untuk currency yang panjang
                    FittedBox(
                      fit: BoxFit.scaleDown,
                      child: Text(
                        FormatUtils.formatCurrency(realTotalSavings),
                        style: AppTextStyles.h4.copyWith(
                          color: AppColors.primary,
                          fontWeight: FontWeight.w700,
                        ),
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      'Tabungan awal + Pemasukan - Pengeluaran',
                      style: AppTextStyles.caption.copyWith(
                        color: AppColors.textSecondary,
                      ),
                      textAlign: TextAlign.center,
                      maxLines: 2,
                      overflow: TextOverflow.ellipsis,
                    ),
                  ],
                ),
              ),

              const SizedBox(height: 20),

              // PERBAIKAN: Monthly Overview dengan Intrinsic untuk equal height
              IntrinsicHeight(
                child: Row(
                  children: [
                    Expanded(
                      child: _buildQuickStatItem(
                        'Pemasukan Bulanan',
                        FormatUtils.formatCurrency(monthlyIncome),
                        Icons.trending_up,
                        AppColors.success,
                      ),
                    ),
                    const SizedBox(width: 16),
                    Expanded(
                      child: _buildQuickStatItem(
                        'Pengeluaran Bulan Ini',
                        FormatUtils.formatCurrency(totalSpending),
                        Icons.trending_down,
                        AppColors.error,
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
        );
      },
    );
  }

  Widget _buildBudgetHealthCard() {
    return Consumer<FinanceProvider>(
      builder: (context, financeProvider, child) {
        if (financeProvider.isLoadingBudgetStatus) {
          return _buildLoadingCard(height: 160);
        }

        final budgetData = financeProvider.budgetStatusData;
        if (budgetData == null || budgetData['has_budget'] != true) {
          return CustomCard(
            child: Center(
              child: Column(
                children: [
                  Icon(
                    Icons.info_outline,
                    size: 48,
                    color: AppColors.warning,
                  ),
                  const SizedBox(height: 16),
                  Text(
                    'Budget 50/30/20 belum diatur',
                    style: AppTextStyles.bodyMedium.copyWith(
                      color: AppColors.textSecondary,
                    ),
                  ),
                ],
              ),
            ),
          );
        }

        final budgetHealth = budgetData['budget_health'] ?? 'unknown';
        final currentMonth = budgetData['current_month'] ?? 'Bulan ini';
        final percentageUsed = budgetData['percentage_used'] ?? {};
        final recommendations = budgetData['recommendations'] as List? ?? [];

        return CustomCard(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // PERBAIKAN: Header dengan Flexible untuk menghindari overflow
              Row(
                children: [
                  Icon(
                    _getBudgetHealthIcon(budgetHealth),
                    color: financeProvider.getBudgetHealthColor(budgetHealth),
                    size: 20,
                  ),
                  const SizedBox(width: 8),
                  Flexible(
                    // Gunakan Flexible untuk text yang panjang
                    child: Text(
                      'Kesehatan Budget - $currentMonth',
                      style: AppTextStyles.labelLarge.copyWith(
                        fontWeight: FontWeight.w600,
                      ),
                      overflow: TextOverflow.ellipsis, // Tambahkan ellipsis
                    ),
                  ),
                ],
              ),

              const SizedBox(height: 16),

              // PERBAIKAN: Budget Health Status dengan text wrapping
              Container(
                width: double
                    .infinity, // Pastikan container menggunakan full width
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: financeProvider
                      .getBudgetHealthColor(budgetHealth)
                      .withOpacity(0.1),
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(
                    color: financeProvider
                        .getBudgetHealthColor(budgetHealth)
                        .withOpacity(0.3),
                  ),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    // PERBAIKAN: Text dengan proper wrapping
                    Text(
                      _getBudgetHealthText(budgetHealth),
                      style: AppTextStyles.labelMedium.copyWith(
                        color:
                            financeProvider.getBudgetHealthColor(budgetHealth),
                        fontWeight: FontWeight.w600,
                      ),
                      maxLines: 2, // Batasi maksimal 2 baris
                      overflow: TextOverflow.ellipsis,
                    ),
                    const SizedBox(height: 8),
                    Text(
                      _getBudgetHealthDescription(budgetHealth),
                      style: AppTextStyles.bodySmall.copyWith(
                        color: AppColors.textSecondary,
                      ),
                      maxLines: 3, // Batasi maksimal 3 baris
                      overflow: TextOverflow.ellipsis,
                    ),
                  ],
                ),
              ),

              const SizedBox(height: 16),

              // PERBAIKAN: Budget Usage Overview dengan Flexible
              Column(
                children: [
                  _buildBudgetUsageRow(
                    'Kebutuhan (50%)',
                    ((percentageUsed['needs'] ?? 0.0) as num).toDouble(),
                    AppColors.success,
                    '🏠',
                  ),
                  const SizedBox(height: 8),
                  _buildBudgetUsageRow(
                    'Keinginan (30%)',
                    ((percentageUsed['wants'] ?? 0.0) as num).toDouble(),
                    AppColors.warning,
                    '🎯',
                  ),
                  const SizedBox(height: 8),
                  _buildBudgetUsageRow(
                    'Tabungan (20%)',
                    ((percentageUsed['savings'] ?? 0.0) as num).toDouble(),
                    AppColors.primary,
                    '💰',
                  ),
                ],
              ),

              // Recommendations
              if (recommendations.isNotEmpty) ...[
                const SizedBox(height: 16),
                Text(
                  'Rekomendasi:',
                  style: AppTextStyles.labelSmall.copyWith(
                    fontWeight: FontWeight.w600,
                    color: AppColors.textSecondary,
                  ),
                ),
                const SizedBox(height: 8),
                ...recommendations
                    .take(2)
                    .map(
                      (rec) => Padding(
                        padding: const EdgeInsets.only(bottom: 4),
                        child: Row(
                          crossAxisAlignment:
                              CrossAxisAlignment.start, // Align ke atas
                          children: [
                            Text(
                              '• ',
                              style: AppTextStyles.bodySmall.copyWith(
                                color: AppColors.primary,
                              ),
                            ),
                            Expanded(
                              // Gunakan Expanded untuk text yang panjang
                              child: Text(
                                rec.toString(),
                                style: AppTextStyles.bodySmall.copyWith(
                                  color: AppColors.textSecondary,
                                ),
                                maxLines: 3,
                                overflow: TextOverflow.ellipsis,
                              ),
                            ),
                          ],
                        ),
                      ),
                    )
                    .toList(),
              ],
            ],
          ),
        );
      },
    );
  }

  Widget _buildBudgetBreakdownCard() {
    return Consumer<FinanceProvider>(
      builder: (context, financeProvider, child) {
        if (financeProvider.isLoadingBudgetStatus) {
          return _buildLoadingCard(height: 200);
        }

        final budgetData = financeProvider.budgetStatusData;
        if (budgetData == null || budgetData['has_budget'] != true) {
          return Container();
        }

        final budgetAllocation = budgetData['budget_allocation'] ?? {};
        final currentSpending = budgetData['current_spending'] ?? {};
        final remainingBudget = budgetData['remaining_budget'] ?? {};

        return CustomCard(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Icon(
                    Icons.pie_chart_outline,
                    color: AppColors.primary,
                    size: 20,
                  ),
                  const SizedBox(width: 8),
                  Flexible(
                    // PERBAIKAN: Gunakan Flexible
                    child: Text(
                      'Breakdown Budget 50/30/20',
                      style: AppTextStyles.labelLarge.copyWith(
                        fontWeight: FontWeight.w600,
                      ),
                      overflow: TextOverflow.ellipsis,
                    ),
                  ),
                ],
              ),

              const SizedBox(height: 20),

              // Budget breakdown items
              _buildBudgetBreakdownItem(
                'Kebutuhan',
                '50%',
                ((budgetAllocation['needs'] ?? 0.0) as num).toDouble(),
                ((currentSpending['needs'] ?? 0.0) as num).toDouble(),
                ((remainingBudget['needs'] ?? 0.0) as num).toDouble(),
                AppColors.success,
                '🏠',
                'Kos, makan, transport, pendidikan',
              ),

              const SizedBox(height: 16),

              _buildBudgetBreakdownItem(
                'Keinginan',
                '30%',
                ((budgetAllocation['wants'] ?? 0.0) as num).toDouble(),
                ((currentSpending['wants'] ?? 0.0) as num).toDouble(),
                ((remainingBudget['wants'] ?? 0.0) as num).toDouble(),
                AppColors.warning,
                '🎯',
                'Hiburan, jajan, target tabungan',
              ),

              const SizedBox(height: 16),

              _buildBudgetBreakdownItem(
                'Tabungan',
                '20%',
                ((budgetAllocation['savings'] ?? 0.0) as num).toDouble(),
                ((currentSpending['savings'] ?? 0.0) as num).toDouble(),
                ((remainingBudget['savings'] ?? 0.0) as num).toDouble(),
                AppColors.primary,
                '💰',
                'Dana darurat, investasi masa depan',
              ),
            ],
          ),
        );
      },
    );
  }

  Widget _buildFinancialSummaryCard() {
    return Consumer<FinanceProvider>(
      builder: (context, financeProvider, child) {
        if (financeProvider.isLoadingDashboard) {
          return _buildLoadingCard(height: 160);
        }

        final dashboardData = financeProvider.dashboardData;
        if (dashboardData == null) return Container();

        final financialSummary = dashboardData['financial_summary'] ?? {};
        final monthlyIncome =
            ((financialSummary['monthly_income'] ?? 0.0) as num).toDouble();
        final monthlyExpense =
            ((financialSummary['monthly_expense'] ?? 0.0) as num).toDouble();
        final netBalance =
            ((financialSummary['net_balance'] ?? 0.0) as num).toDouble();
        final savingsRate =
            ((financialSummary['savings_rate'] ?? 0.0) as num).toDouble();

        return CustomCard(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Icon(
                    Icons.assessment_outlined,
                    color: AppColors.info,
                    size: 20,
                  ),
                  const SizedBox(width: 8),
                  Flexible(
                    // PERBAIKAN: Gunakan Flexible
                    child: Text(
                      'Ringkasan Bulanan',
                      style: AppTextStyles.labelLarge.copyWith(
                        fontWeight: FontWeight.w600,
                      ),
                      overflow: TextOverflow.ellipsis,
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 16),
              IntrinsicHeight(
                // PERBAIKAN: Equal height
                child: Row(
                  children: [
                    Expanded(
                      child: _buildSummaryItem(
                        'Pemasukan',
                        FormatUtils.formatCurrency(monthlyIncome),
                        Icons.arrow_upward,
                        AppColors.success,
                      ),
                    ),
                    const SizedBox(width: 16),
                    Expanded(
                      child: _buildSummaryItem(
                        'Pengeluaran',
                        FormatUtils.formatCurrency(monthlyExpense),
                        Icons.arrow_downward,
                        AppColors.error,
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 16),
              IntrinsicHeight(
                // PERBAIKAN: Equal height
                child: Row(
                  children: [
                    Expanded(
                      child: _buildSummaryItem(
                        'Saldo Bersih',
                        FormatUtils.formatCurrency(netBalance),
                        netBalance >= 0
                            ? Icons.trending_up
                            : Icons.trending_down,
                        netBalance >= 0 ? AppColors.success : AppColors.error,
                      ),
                    ),
                    const SizedBox(width: 16),
                    Expanded(
                      child: _buildSummaryItem(
                        'Savings Rate',
                        FormatUtils.formatPercentage(savingsRate),
                        Icons.savings_outlined,
                        AppColors.primary,
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
        );
      },
    );
  }

  Widget _buildSavingsGoalsCard() {
    return Consumer<FinanceProvider>(
      builder: (context, financeProvider, child) {
        if (financeProvider.isLoadingProgress) {
          return _buildLoadingCard(height: 200);
        }

        final progressData = financeProvider.progressData;
        if (progressData == null) return Container();

        final savingsGoals = progressData['savings_goals'] as List? ?? [];

        return CustomCard(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Icon(
                    Icons.flag_outlined,
                    color: AppColors.primary,
                    size: 20,
                  ),
                  const SizedBox(width: 8),
                  Flexible(
                    // PERBAIKAN: Gunakan Flexible
                    child: Text(
                      'Target Tabungan (dari 30% Wants)',
                      style: AppTextStyles.labelLarge.copyWith(
                        fontWeight: FontWeight.w600,
                      ),
                      overflow: TextOverflow.ellipsis,
                      maxLines: 2,
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
                        Icons.flag_outlined,
                        size: 48,
                        color: AppColors.gray400,
                      ),
                      const SizedBox(height: 16),
                      Text(
                        'Belum ada target tabungan',
                        style: AppTextStyles.bodyMedium.copyWith(
                          color: AppColors.textSecondary,
                        ),
                      ),
                      const SizedBox(height: 8),
                      Text(
                        'Buat target untuk laptop, HP, atau liburan',
                        style: AppTextStyles.bodySmall.copyWith(
                          color: AppColors.textTertiary,
                        ),
                        textAlign: TextAlign.center,
                      ),
                    ],
                  ),
                )
              else
                Column(
                  children: savingsGoals
                      .take(3)
                      .map((goal) => _buildSavingsGoalItem(goal))
                      .toList(),
                ),
              if (savingsGoals.length > 3) ...[
                const SizedBox(height: 16),
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

  Widget _buildRecentActivityCard() {
    return Consumer<FinanceProvider>(
      builder: (context, financeProvider, child) {
        if (financeProvider.isLoadingDashboard) {
          return _buildLoadingCard(height: 200);
        }

        final dashboardData = financeProvider.dashboardData;
        if (dashboardData == null) return Container();

        final recentActivity = dashboardData['recent_activity'] ?? {};
        final transactions = recentActivity['transactions'] as List? ?? [];

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
                  Flexible(
                    // PERBAIKAN: Gunakan Flexible
                    child: Text(
                      'Aktivitas Terbaru',
                      style: AppTextStyles.labelLarge.copyWith(
                        fontWeight: FontWeight.w600,
                      ),
                      overflow: TextOverflow.ellipsis,
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 16),
              if (transactions.isEmpty)
                Center(
                  child: Column(
                    children: [
                      Icon(
                        Icons.history,
                        size: 48,
                        color: AppColors.gray400,
                      ),
                      const SizedBox(height: 16),
                      Text(
                        'Belum ada aktivitas',
                        style: AppTextStyles.bodyMedium.copyWith(
                          color: AppColors.textSecondary,
                        ),
                      ),
                    ],
                  ),
                )
              else
                Column(
                  children: transactions
                      .take(5)
                      .map((transaction) => _buildTransactionItem(transaction))
                      .toList(),
                ),
              if (transactions.length > 5) ...[
                const SizedBox(height: 16),
                Center(
                  child: TextButton(
                    onPressed: () {
                      // Navigate to history tab
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
            ],
          ),
        );
      },
    );
  }

  Widget _buildStudentTipsCard() {
    return Consumer<FinanceProvider>(
      builder: (context, financeProvider, child) {
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
                  Flexible(
                    // PERBAIKAN: Gunakan Flexible
                    child: Text(
                      'Tips Keuangan Mahasiswa',
                      style: AppTextStyles.labelLarge.copyWith(
                        fontWeight: FontWeight.w600,
                      ),
                      overflow: TextOverflow.ellipsis,
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 16),
              Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: AppColors.warning.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(
                    color: AppColors.warning.withOpacity(0.3),
                  ),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        Text(
                          '💡',
                          style: const TextStyle(fontSize: 16),
                        ),
                        const SizedBox(width: 8),
                        Flexible(
                          // PERBAIKAN: Gunakan Flexible
                          child: Text(
                            'Metode 50/30/20 untuk Mahasiswa',
                            style: AppTextStyles.labelMedium.copyWith(
                              color: AppColors.warning,
                              fontWeight: FontWeight.w600,
                            ),
                            overflow: TextOverflow.ellipsis,
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 12),
                    Text(
                      '• Prioritaskan 50% untuk kebutuhan pokok (kos, makan, transport)\n'
                      '• Gunakan 30% untuk keinginan dan target tabungan barang\n'
                      '• Sisakan 20% untuk tabungan masa depan dan dana darurat\n'
                      '• Masak sendiri 3-4x seminggu untuk menghemat budget makan',
                      style: AppTextStyles.bodySmall.copyWith(
                        color: AppColors.textPrimary,
                        height: 1.5,
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
        );
      },
    );
  }

  // Helper widgets
  Widget _buildQuickStatItem(
      String label, String value, IconData icon, Color color) {
    return Container(
      padding: const EdgeInsets.all(12), // Tambahkan padding
      decoration: BoxDecoration(
        color: color.withOpacity(0.05),
        borderRadius: BorderRadius.circular(8),
        border: Border.all(
          color: color.withOpacity(0.1),
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        mainAxisSize: MainAxisSize.min,
        children: [
          Row(
            children: [
              Icon(
                icon,
                size: 16,
                color: color,
              ),
              const SizedBox(width: 6),
              Expanded(
                // PERBAIKAN: Gunakan Expanded untuk label
                child: Text(
                  label,
                  style: AppTextStyles.bodySmall.copyWith(
                    color: AppColors.textSecondary,
                  ),
                  maxLines: 2,
                  overflow: TextOverflow.ellipsis,
                ),
              ),
            ],
          ),
          const SizedBox(height: 8),
          // PERBAIKAN: FittedBox untuk value yang panjang
          FittedBox(
            fit: BoxFit.scaleDown,
            alignment: Alignment.centerLeft,
            child: Text(
              value,
              style: AppTextStyles.labelLarge.copyWith(
                color: color,
                fontWeight: FontWeight.w600,
              ),
            ),
          ),
        ],
      ),
    );
  }

  // PERBAIKAN: Budget Usage Row dengan Flexible
  Widget _buildBudgetUsageRow(
      String label, double percentage, Color color, String emoji) {
    return Row(
      children: [
        Text(
          emoji,
          style: const TextStyle(fontSize: 16),
        ),
        const SizedBox(width: 8),
        Expanded(
          // Gunakan Expanded untuk label
          child: Text(
            label,
            style: AppTextStyles.bodySmall.copyWith(
              color: AppColors.textSecondary,
            ),
            overflow: TextOverflow.ellipsis,
          ),
        ),
        const SizedBox(width: 8), // Tambahkan spacing
        Text(
          '${percentage.toStringAsFixed(0)}%',
          style: AppTextStyles.labelMedium.copyWith(
            color: percentage > 100 ? AppColors.error : color,
            fontWeight: FontWeight.w600,
          ),
        ),
      ],
    );
  }

  Widget _buildBudgetBreakdownItem(
    String title,
    String percentage,
    double budget,
    double spent,
    double remaining,
    Color color,
    String emoji,
    String description,
  ) {
    final usedPercentage = budget > 0 ? (spent / budget * 100) : 0;

    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: color.withOpacity(0.05),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
          color: color.withOpacity(0.2),
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Text(
                emoji,
                style: const TextStyle(fontSize: 20),
              ),
              const SizedBox(width: 8),
              Expanded(
                // PERBAIKAN: Gunakan Expanded
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      '$title ($percentage)',
                      style: AppTextStyles.labelMedium.copyWith(
                        fontWeight: FontWeight.w600,
                      ),
                      overflow: TextOverflow.ellipsis,
                    ),
                    Text(
                      description,
                      style: AppTextStyles.caption.copyWith(
                        color: AppColors.textSecondary,
                      ),
                      maxLines: 2,
                      overflow: TextOverflow.ellipsis,
                    ),
                  ],
                ),
              ),
            ],
          ),

          const SizedBox(height: 12),

          LinearProgressIndicator(
            value: (usedPercentage / 100).clamp(0.0, 1.0),
            backgroundColor: AppColors.gray200,
            valueColor: AlwaysStoppedAnimation<Color>(
              usedPercentage > 100 ? AppColors.error : color,
            ),
            minHeight: 6,
          ),

          const SizedBox(height: 8),

          // PERBAIKAN: Row dengan Flexible untuk text panjang
          Row(
            children: [
              Expanded(
                child: Text(
                  'Terpakai: ${FormatUtils.formatCurrency(spent)}',
                  style: AppTextStyles.caption.copyWith(
                    color: AppColors.textSecondary,
                  ),
                  overflow: TextOverflow.ellipsis,
                ),
              ),
              const SizedBox(width: 8),
              Expanded(
                child: Text(
                  'Sisa: ${FormatUtils.formatCurrency(remaining)}',
                  style: AppTextStyles.caption.copyWith(
                    color: AppColors.textSecondary,
                  ),
                  overflow: TextOverflow.ellipsis,
                  textAlign: TextAlign.end,
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildSummaryItem(
      String label, String value, IconData icon, Color color) {
    return Container(
      padding: const EdgeInsets.all(12), // Tambahkan padding
      decoration: BoxDecoration(
        color: color.withOpacity(0.05),
        borderRadius: BorderRadius.circular(8),
        border: Border.all(
          color: color.withOpacity(0.1),
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        mainAxisSize: MainAxisSize.min,
        children: [
          Row(
            children: [
              Icon(
                icon,
                size: 16,
                color: color,
              ),
              const SizedBox(width: 6),
              Expanded(
                // PERBAIKAN: Gunakan Expanded
                child: Text(
                  label,
                  style: AppTextStyles.bodySmall.copyWith(
                    color: AppColors.textSecondary,
                  ),
                  overflow: TextOverflow.ellipsis,
                ),
              ),
            ],
          ),
          const SizedBox(height: 8),
          FittedBox(
            // PERBAIKAN: FittedBox untuk value
            fit: BoxFit.scaleDown,
            alignment: Alignment.centerLeft,
            child: Text(
              value,
              style: AppTextStyles.labelLarge.copyWith(
                color: color,
                fontWeight: FontWeight.w600,
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildSavingsGoalItem(Map<String, dynamic> goal) {
    final itemName = goal['item_name'] ?? '';
    final targetAmount = ((goal['target_amount'] ?? 0.0) as num).toDouble();
    final currentAmount = ((goal['current_amount'] ?? 0.0) as num).toDouble();
    final progressPercentage =
        ((goal['progress_percentage'] ?? 0.0) as num).toDouble();

    return Container(
      margin: const EdgeInsets.only(bottom: 16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Expanded(
                // PERBAIKAN: Gunakan Expanded
                child: Text(
                  itemName,
                  style: AppTextStyles.bodyMedium.copyWith(
                    fontWeight: FontWeight.w500,
                  ),
                  overflow: TextOverflow.ellipsis,
                ),
              ),
              const SizedBox(width: 8),
              Text(
                '${progressPercentage.toStringAsFixed(0)}%',
                style: AppTextStyles.labelMedium.copyWith(
                  color: AppColors.primary,
                  fontWeight: FontWeight.w600,
                ),
              ),
            ],
          ),
          const SizedBox(height: 8),
          LinearProgressIndicator(
            value: (progressPercentage / 100).clamp(0.0, 1.0),
            backgroundColor: AppColors.gray200,
            valueColor: AlwaysStoppedAnimation<Color>(AppColors.primary),
            minHeight: 6,
          ),
          const SizedBox(height: 8),
          Row(
            children: [
              Expanded(
                // PERBAIKAN: Gunakan Expanded
                child: Text(
                  FormatUtils.formatCurrency(currentAmount),
                  style: AppTextStyles.caption.copyWith(
                    color: AppColors.textSecondary,
                  ),
                  overflow: TextOverflow.ellipsis,
                ),
              ),
              Text(
                FormatUtils.formatCurrency(targetAmount),
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

  // PERBAIKAN: Transaction Item untuk Aktivitas Terbaru
  Widget _buildTransactionItem(Map<String, dynamic> transaction) {
    final type = transaction['type'] ?? '';
    final amount = ((transaction['amount'] ?? 0.0) as num).toDouble();
    final description = transaction['description'] ?? '';
    final category = transaction['category'] ?? '';
    final budgetType = transaction['budget_type'] ?? '';
    final relativeTime = transaction['relative_time'] ?? '';

    final isIncome = type == 'income';
    final color = isIncome ? AppColors.success : AppColors.error;
    final icon = isIncome ? Icons.trending_up : Icons.trending_down;

    return Consumer<FinanceProvider>(
      builder: (context, financeProvider, child) {
        return Container(
          margin: const EdgeInsets.only(bottom: 12),
          padding: const EdgeInsets.all(12), // Tambahkan padding
          decoration: BoxDecoration(
            color: AppColors.gray50,
            borderRadius: BorderRadius.circular(8),
          ),
          child: Row(
            crossAxisAlignment: CrossAxisAlignment.start, // Align ke atas
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
                // PERBAIKAN: Gunakan Expanded untuk content
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      description,
                      style: AppTextStyles.bodySmall.copyWith(
                        fontWeight: FontWeight.w500,
                      ),
                      maxLines: 2,
                      overflow: TextOverflow.ellipsis,
                    ),
                    const SizedBox(height: 4),
                    // PERBAIKAN: Wrap untuk category info yang panjang
                    Wrap(
                      children: [
                        Text(
                          category,
                          style: AppTextStyles.caption.copyWith(
                            color: AppColors.textSecondary,
                          ),
                        ),
                        if (budgetType.isNotEmpty) ...[
                          Text(
                            ' • ',
                            style: AppTextStyles.caption.copyWith(
                              color: AppColors.textTertiary,
                            ),
                          ),
                          Text(
                            financeProvider.getBudgetTypeIcon(budgetType),
                            style: const TextStyle(fontSize: 10),
                          ),
                          Text(
                            ' ${financeProvider.getBudgetTypeName(budgetType)}',
                            style: AppTextStyles.caption.copyWith(
                              color: financeProvider
                                  .getBudgetTypeColor(budgetType),
                              fontWeight: FontWeight.w500,
                            ),
                          ),
                        ],
                      ],
                    ),
                  ],
                ),
              ),
              const SizedBox(width: 8),
              // PERBAIKAN: Amount section dengan fixed width
              SizedBox(
                width: 80, // Fixed width untuk amount
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.end,
                  children: [
                    FittedBox(
                      fit: BoxFit.scaleDown,
                      child: Text(
                        FormatUtils.formatTransactionAmount(amount, type),
                        style: AppTextStyles.labelMedium.copyWith(
                          color: color,
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                    ),
                    const SizedBox(height: 2),
                    Text(
                      relativeTime,
                      style: AppTextStyles.caption.copyWith(
                        color: AppColors.textTertiary,
                      ),
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                    ),
                  ],
                ),
              ),
            ],
          ),
        );
      },
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

  // Helper methods
  IconData _getBudgetHealthIcon(String health) {
    switch (health) {
      case 'excellent':
        return Icons.sentiment_very_satisfied;
      case 'good':
        return Icons.sentiment_satisfied;
      case 'warning':
        return Icons.sentiment_neutral;
      case 'over_budget':
        return Icons.sentiment_very_dissatisfied;
      default:
        return Icons.help_outline;
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

  String _getBudgetHealthDescription(String health) {
    switch (health) {
      case 'excellent':
        return 'Budget management Anda sangat baik! Pertahankan pola ini.';
      case 'good':
        return 'Budget masih dalam kendali. Sedikit penyesuaian akan lebih baik.';
      case 'warning':
        return 'Budget mulai menipis. Perlu lebih hati-hati dalam pengeluaran.';
      case 'over_budget':
        return 'Budget sudah terlampaui. Segera evaluasi pengeluaran Anda.';
      default:
        return 'Status budget tidak diketahui.';
    }
  }
}
