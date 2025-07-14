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
      // Load student-specific data
      if (financeProvider.dashboardData == null) {
        await financeProvider.loadStudentDashboardSummary();
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
          await financeProvider.refreshAllStudentData();
        }
      },
      child: SingleChildScrollView(
        physics: const AlwaysScrollableScrollPhysics(),
        padding: const EdgeInsets.all(24),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Real Financial Totals Overview
            _buildRealFinancialTotalsCard(),
            
            const SizedBox(height: 24),
            
            // Monthly Financial Capacity
            _buildMonthlyCapacityCard(),
            
            const SizedBox(height: 16),
            
            // Savings Progress Card
            _buildSavingsProgressCard(),
            
            const SizedBox(height: 24),
            
            // Student Level & Health Score
            _buildStudentInsightsCard(),
            
            const SizedBox(height: 24),
            
            // Savings Goals Section
            _buildSavingsGoalsSection(),
            
            const SizedBox(height: 24),
            
            // Recent Activity
            _buildRecentActivityCard(),
            
            const SizedBox(height: 16),
            
            // Student Tips
            _buildStudentTipsCard(),
          ],
        ),
      ),
    );
  }

  Widget _buildRealFinancialTotalsCard() {
    return Consumer<FinanceProvider>(
      builder: (context, financeProvider, child) {
        if (financeProvider.isLoadingDashboard) {
          return _buildLoadingCard(height: 220);
        }

        if (financeProvider.dashboardError != null) {
          return ErrorMessage(
            message: financeProvider.dashboardError!,
            onRetry: () => financeProvider.loadStudentDashboardSummary(),
          );
        }

        final dashboardData = financeProvider.dashboardData;
        if (dashboardData == null) {
          return const EmptyStateWidget(
            icon: Icons.dashboard_outlined,
            title: 'Tidak ada data dashboard',
            subtitle: 'Data keuangan mahasiswa belum tersedia',
          );
        }

        final realTotals = dashboardData['real_financial_totals'] ?? {};
        final monthlyCapacity = dashboardData['monthly_financial_capacity'] ?? {};

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
                          'Total Tabungan Real-Time',
                          style: AppTextStyles.h6.copyWith(
                            fontWeight: FontWeight.w600,
                          ),
                        ),
                        Text(
                          'Berdasarkan transaksi aktual',
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
              
              // Real Total Savings - Highlighted
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
                  borderRadius: BorderRadius.circular(16),
                  border: Border.all(
                    color: AppColors.primary.withOpacity(0.2),
                  ),
                ),
                child: Column(
                  children: [
                    Text(
                      'Total Tabungan Anda',
                      style: AppTextStyles.labelMedium.copyWith(
                        color: AppColors.primary,
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                    const SizedBox(height: 8),
                    Text(
                      realTotals['formatted_real_total'] ?? 'Rp 0',
                      style: AppTextStyles.h4.copyWith(
                        color: AppColors.primary,
                        fontWeight: FontWeight.w700,
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      'Tabungan awal + Pemasukan - Pengeluaran',
                      style: AppTextStyles.caption.copyWith(
                        color: AppColors.textSecondary,
                      ),
                    ),
                  ],
                ),
              ),
              
              const SizedBox(height: 20),
              
              // Financial breakdown
              Row(
                children: [
                  Expanded(
                    child: _buildMetricItem(
                      'Pemasukan Total',
                      realTotals['formatted_total_income'] ?? 'Rp 0',
                      Icons.trending_up,
                      AppColors.success,
                    ),
                  ),
                  const SizedBox(width: 16),
                  Expanded(
                    child: _buildMetricItem(
                      'Pengeluaran Total',
                      realTotals['formatted_total_expense'] ?? 'Rp 0',
                      Icons.trending_down,
                      AppColors.error,
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

  Widget _buildMonthlyCapacityCard() {
    return Consumer<FinanceProvider>(
      builder: (context, financeProvider, child) {
        if (financeProvider.isLoadingDashboard) {
          return _buildLoadingCard(height: 160);
        }

        final dashboardData = financeProvider.dashboardData;
        if (dashboardData == null) return Container();

        final monthlyCapacity = dashboardData['monthly_financial_capacity'] ?? {};

        return CustomCard(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Icon(
                    Icons.calendar_month,
                    color: AppColors.info,
                    size: 20,
                  ),
                  const SizedBox(width: 8),
                  Text(
                    'Kapasitas Bulanan',
                    style: AppTextStyles.labelLarge.copyWith(
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                ],
              ),
              
              const SizedBox(height: 4),
              
              Text(
                monthlyCapacity['current_month'] ?? 'Bulan ini',
                style: AppTextStyles.caption.copyWith(
                  color: AppColors.textSecondary,
                ),
              ),
              
              const SizedBox(height: 16),
              
              _buildStatRow(
                'Pemasukan',
                monthlyCapacity['formatted_income'] ?? 'Rp 0',
                Icons.add_circle_outline,
                color: AppColors.success,
              ),
              
              const SizedBox(height: 8),
              
              _buildStatRow(
                'Pengeluaran',
                monthlyCapacity['formatted_expense'] ?? 'Rp 0',
                Icons.remove_circle_outline,
                color: AppColors.error,
              ),
              
              const SizedBox(height: 8),
              
              _buildStatRow(
                'Saldo Bersih',
                monthlyCapacity['formatted_actual_savings'] ?? 'Rp 0',
                Icons.account_balance,
                color: (monthlyCapacity['actual_monthly_savings'] ?? 0) >= 0 
                    ? AppColors.success 
                    : AppColors.error,
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
        if (financeProvider.isLoadingDashboard) {
          return _buildLoadingCard(height: 160);
        }

        final dashboardData = financeProvider.dashboardData;
        if (dashboardData == null) return Container();

        final monthlyCapacity = dashboardData['monthly_financial_capacity'] ?? {};
        final achievementPercentage = monthlyCapacity['achievement_percentage'] ?? 0.0;
        final status = monthlyCapacity['status'] ?? 'needs_improvement';

        Color statusColor;
        IconData statusIcon;
        
        switch (status) {
          case 'exceeds_target':
            statusColor = AppColors.success;
            statusIcon = Icons.trending_up;
            break;
          case 'on_track':
            statusColor = AppColors.primary;
            statusIcon = Icons.check_circle;
            break;
          default:
            statusColor = AppColors.warning;
            statusIcon = Icons.warning;
        }

        return CustomCard(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Icon(
                    statusIcon,
                    color: statusColor,
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
              
              LinearProgressIndicator(
                value: (achievementPercentage / 100).clamp(0.0, 1.0),
                backgroundColor: AppColors.gray200,
                valueColor: AlwaysStoppedAnimation<Color>(statusColor),
                minHeight: 8,
              ),
              
              const SizedBox(height: 12),
              
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text(
                    '${achievementPercentage.toStringAsFixed(1)}%',
                    style: AppTextStyles.labelLarge.copyWith(
                      color: statusColor,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                  Text(
                    monthlyCapacity['formatted_target_savings'] ?? 'Rp 0',
                    style: AppTextStyles.labelSmall.copyWith(
                      color: AppColors.textSecondary,
                    ),
                  ),
                ],
              ),
              
              const SizedBox(height: 8),
              
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                decoration: BoxDecoration(
                  color: statusColor.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Text(
                  _getStatusText(status),
                  style: AppTextStyles.caption.copyWith(
                    color: statusColor,
                    fontWeight: FontWeight.w500,
                  ),
                ),
              ),
            ],
          ),
        );
      },
    );
  }

  Widget _buildStudentInsightsCard() {
    return Consumer<FinanceProvider>(
      builder: (context, financeProvider, child) {
        if (financeProvider.isLoadingDashboard) {
          return _buildLoadingCard(height: 140);
        }

        final dashboardData = financeProvider.dashboardData;
        if (dashboardData == null) return Container();

        final insights = dashboardData['student_insights'] ?? {};
        final healthScore = insights['financial_health_score'] ?? 0.0;
        final studentLevel = insights['student_level'] ?? 'Pemula';
        final recommendation = insights['recommendation'] ?? 'needs_improvement';

        Color levelColor;
        switch (studentLevel) {
          case 'Expert':
            levelColor = AppColors.success;
            break;
          case 'Mahir':
            levelColor = AppColors.primary;
            break;
          case 'Berkembang':
            levelColor = AppColors.info;
            break;
          default:
            levelColor = AppColors.warning;
        }

        return CustomCard(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Icon(
                    Icons.school,
                    color: AppColors.primary,
                    size: 20,
                  ),
                  const SizedBox(width: 8),
                  Text(
                    'Level Keuangan Mahasiswa',
                    style: AppTextStyles.labelLarge.copyWith(
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                ],
              ),
              
              const SizedBox(height: 16),
              
              Row(
                children: [
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          'Health Score',
                          style: AppTextStyles.bodySmall.copyWith(
                            color: AppColors.textSecondary,
                          ),
                        ),
                        const SizedBox(height: 4),
                        Text(
                          '${healthScore.toStringAsFixed(0)}/100',
                          style: AppTextStyles.h6.copyWith(
                            color: AppColors.primary,
                            fontWeight: FontWeight.w700,
                          ),
                        ),
                      ],
                    ),
                  ),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          'Level Mahasiswa',
                          style: AppTextStyles.bodySmall.copyWith(
                            color: AppColors.textSecondary,
                          ),
                        ),
                        const SizedBox(height: 4),
                        Container(
                          padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 4),
                          decoration: BoxDecoration(
                            color: levelColor.withOpacity(0.1),
                            borderRadius: BorderRadius.circular(12),
                            border: Border.all(color: levelColor.withOpacity(0.3)),
                          ),
                          child: Text(
                            studentLevel,
                            style: AppTextStyles.labelSmall.copyWith(
                              color: levelColor,
                              fontWeight: FontWeight.w600,
                            ),
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
              
              const SizedBox(height: 12),
              
              if (insights['next_milestone'] != null) ...[
                Row(
                  children: [
                    Icon(
                      Icons.flag,
                      size: 16,
                      color: AppColors.warning,
                    ),
                    const SizedBox(width: 6),
                    Text(
                      'Target selanjutnya: ${insights['next_milestone']}',
                      style: AppTextStyles.bodySmall.copyWith(
                        color: AppColors.textSecondary,
                      ),
                    ),
                  ],
                ),
              ],
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
                      const SizedBox(height: 4),
                      Text(
                        'Buat target untuk laptop, HP, atau liburan',
                        style: AppTextStyles.bodySmall.copyWith(
                          color: AppColors.textTertiary,
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
    final isUrgent = goal['is_urgent'] ?? false;
    final affordability = goal['affordability'] ?? 'moderate';
    
    Color affordabilityColor;
    switch (affordability) {
      case 'easy':
        affordabilityColor = AppColors.success;
        break;
      case 'moderate':
        affordabilityColor = AppColors.primary;
        break;
      case 'challenging':
        affordabilityColor = AppColors.warning;
        break;
      default:
        affordabilityColor = AppColors.error;
    }

    return Container(
      margin: const EdgeInsets.only(bottom: 16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Expanded(
                child: Text(
                  goal['item_name'] ?? '',
                  style: AppTextStyles.bodyMedium.copyWith(
                    fontWeight: FontWeight.w500,
                  ),
                ),
              ),
              if (isUrgent)
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                  decoration: BoxDecoration(
                    color: AppColors.error.withOpacity(0.1),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Text(
                    'URGENT',
                    style: AppTextStyles.caption.copyWith(
                      color: AppColors.error,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                ),
              const SizedBox(width: 8),
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
          const SizedBox(height: 8),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                goal['formatted_current'] ?? 'Rp 0',
                style: AppTextStyles.caption.copyWith(
                  color: AppColors.textSecondary,
                ),
              ),
              Row(
                children: [
                  Container(
                    width: 8,
                    height: 8,
                    decoration: BoxDecoration(
                      color: affordabilityColor,
                      shape: BoxShape.circle,
                    ),
                  ),
                  const SizedBox(width: 4),
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
          
          // Placeholder recent activities
          _buildActivityItem(
            'Pengeluaran - Makan di kantin',
            'Rp 25.000',
            '2 jam lalu',
            Icons.restaurant,
            AppColors.error,
          ),
          _buildActivityItem(
            'Pemasukan - Freelance desain',
            'Rp 500.000',
            '1 hari lalu',
            Icons.work,
            AppColors.success,
          ),
          _buildActivityItem(
            'Pengeluaran - Ongkos angkot',
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

  Widget _buildStudentTipsCard() {
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
                'Tips Keuangan Mahasiswa',
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
                  '💡 Tip untuk Mahasiswa',
                  style: AppTextStyles.labelMedium.copyWith(
                    color: AppColors.warning,
                    fontWeight: FontWeight.w600,
                  ),
                ),
                const SizedBox(height: 8),
                Text(
                  'Alokasikan 15-20% dari uang saku untuk tabungan darurat. Masak sendiri minimal 3x seminggu untuk menghemat pengeluaran makan.',
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

  String _getStatusText(String status) {
    switch (status) {
      case 'exceeds_target':
        return 'Melebihi Target!';
      case 'on_track':
        return 'Sesuai Target';
      default:
        return 'Perlu Ditingkatkan';
    }
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