import 'package:flutter/material.dart';
import '../../../../utils/app_colors.dart';
import '../../../../utils/app_text_styles.dart';
import '../../../../widgets/custom_widgets.dart';
import '../widgets/period_selector.dart';
import '../widgets/chart_containers.dart';
import '../widgets/income_source_item.dart';

class IncomeTab extends StatefulWidget {
  const IncomeTab({Key? key}) : super(key: key);

  @override
  State<IncomeTab> createState() => _IncomeTabState();
}

class _IncomeTabState extends State<IncomeTab> {
  int _selectedPeriod = 0; // 0: Harian, 1: Mingguan, 2: Bulanan

  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(20),
      child: Column(
        children: [
          // Period Selector
          PeriodSelector(
            selectedPeriod: _selectedPeriod,
            onPeriodChanged: (period) {
              setState(() {
                _selectedPeriod = period;
              });
            },
          ),
          const SizedBox(height: 20),
          
          // Income History Chart
          CustomCard(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                _buildSectionHeader(
                  'Riwayat Pemasukan',
                  Icons.trending_up,
                  AppColors.success,
                ),
                const SizedBox(height: 20),
                SizedBox(
                  height: 200,
                  child: ChartContainers.incomeLineChart(),
                ),
              ],
            ),
          ),
          const SizedBox(height: 20),
          
          // Income Summary Cards
          _buildIncomeSummaryCards(),
          const SizedBox(height: 20),
          
          // Income Sources
          CustomCard(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                _buildSectionHeader(
                  'Sumber Pemasukan',
                  Icons.account_balance_wallet,
                  AppColors.primary,
                ),
                const SizedBox(height: 16),
                const IncomeSourceItem(
                  source: 'Gaji Utama',
                  amount: 4200000,
                  percentage: 0.8,
                  icon: Icons.work,
                ),
                const SizedBox(height: 12),
                const IncomeSourceItem(
                  source: 'Freelance',
                  amount: 800000,
                  percentage: 0.15,
                  icon: Icons.laptop_mac,
                ),
                const SizedBox(height: 12),
                const IncomeSourceItem(
                  source: 'Investasi',
                  amount: 200000,
                  percentage: 0.05,
                  icon: Icons.trending_up,
                ),
              ],
            ),
          ),
          const SizedBox(height: 20),
          
          // Income Growth Card
          _buildIncomeGrowthCard(),
        ],
      ),
    );
  }

  Widget _buildSectionHeader(String title, IconData icon, Color color) {
    return Row(
      children: [
        Icon(
          icon,
          color: color,
          size: 20,
        ),
        const SizedBox(width: 8),
        Text(
          title,
          style: AppTextStyles.labelLarge.copyWith(
            fontWeight: FontWeight.w600,
          ),
        ),
      ],
    );
  }

  Widget _buildIncomeSummaryCards() {
    return Row(
      children: [
        Expanded(
          child: _buildSummaryCard(
            'Total Bulan Ini',
            'Rp 5.200.000',
            Icons.calendar_month,
            AppColors.success,
            '+12%',
          ),
        ),
        const SizedBox(width: 12),
        Expanded(
          child: _buildSummaryCard(
            'Rata-rata Harian',
            'Rp 173.333',
            Icons.today,
            AppColors.info,
            '+5%',
          ),
        ),
      ],
    );
  }

  Widget _buildSummaryCard(String title, String amount, IconData icon, Color color, String growth) {
    return CustomCard(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Container(
                padding: const EdgeInsets.all(8),
                decoration: BoxDecoration(
                  color: color.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Icon(
                  icon,
                  color: color,
                  size: 16,
                ),
              ),
              const Spacer(),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                decoration: BoxDecoration(
                  color: AppColors.success.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Text(
                  growth,
                  style: AppTextStyles.caption.copyWith(
                    color: AppColors.success,
                    fontWeight: FontWeight.w600,
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          Text(
            title,
            style: AppTextStyles.caption.copyWith(
              color: AppColors.textSecondary,
            ),
          ),
          const SizedBox(height: 4),
          Text(
            amount,
            style: AppTextStyles.labelLarge.copyWith(
              color: color,
              fontWeight: FontWeight.w600,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildIncomeGrowthCard() {
    return CustomCard(
      backgroundColor: AppColors.success.withOpacity(0.05),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(
                Icons.insights,
                color: AppColors.success,
                size: 20,
              ),
              const SizedBox(width: 8),
              Text(
                'Analisis Pertumbuhan',
                style: AppTextStyles.labelLarge.copyWith(
                  fontWeight: FontWeight.w600,
                  color: AppColors.success,
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: AppColors.white,
              borderRadius: BorderRadius.circular(12),
              border: Border.all(color: AppColors.success.withOpacity(0.2)),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Insight Pemasukan:',
                  style: AppTextStyles.labelMedium.copyWith(
                    fontWeight: FontWeight.w600,
                  ),
                ),
                const SizedBox(height: 12),
                _buildInsightItem(
                  '• Pemasukan freelance naik 25% bulan ini',
                  AppColors.success,
                ),
                const SizedBox(height: 4),
                _buildInsightItem(
                  '• Target pemasukan bulanan tercapai 104%',
                  AppColors.success,
                ),
                const SizedBox(height: 4),
                _buildInsightItem(
                  '• Potensi tambahan dari investasi: +15%',
                  AppColors.info,
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildInsightItem(String text, Color color) {
    return Text(
      text,
      style: AppTextStyles.bodySmall.copyWith(
        color: color,
      ),
    );
  }
}