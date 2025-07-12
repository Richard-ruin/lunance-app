import 'package:flutter/material.dart';
import '../../../../utils/app_colors.dart';
import '../../../../utils/app_text_styles.dart';
import '../../../../widgets/custom_widgets.dart';
import '../widgets/period_selector.dart';
import '../widgets/chart_containers.dart';
import '../widgets/expense_category_item.dart';

class ExpenseTab extends StatefulWidget {
  const ExpenseTab({Key? key}) : super(key: key);

  @override
  State<ExpenseTab> createState() => _ExpenseTabState();
}

class _ExpenseTabState extends State<ExpenseTab> {
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
          
          // Expense Chart
          CustomCard(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                _buildSectionHeader(
                  'Riwayat Pengeluaran',
                  Icons.trending_down,
                  AppColors.error,
                ),
                const SizedBox(height: 20),
                SizedBox(
                  height: 200,
                  child: ChartContainers.expenseLineChart(),
                ),
              ],
            ),
          ),
          const SizedBox(height: 20),
          
          // Expense Summary Cards
          _buildExpenseSummaryCards(),
          const SizedBox(height: 20),
          
          // Top Categories
          CustomCard(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                _buildSectionHeader(
                  'Kategori Pengeluaran Tertinggi',
                  Icons.category,
                  AppColors.primary,
                ),
                const SizedBox(height: 16),
                const ExpenseCategoryItem(
                  category: 'Makanan & Minuman',
                  amount: 1200000,
                  percentage: 0.3,
                  color: AppColors.error,
                  icon: Icons.restaurant,
                ),
                const SizedBox(height: 12),
                const ExpenseCategoryItem(
                  category: 'Transportasi',
                  amount: 800000,
                  percentage: 0.2,
                  color: AppColors.warning,
                  icon: Icons.directions_car,
                ),
                const SizedBox(height: 12),
                const ExpenseCategoryItem(
                  category: 'Belanja & Shopping',
                  amount: 600000,
                  percentage: 0.15,
                  color: AppColors.info,
                  icon: Icons.shopping_bag,
                ),
                const SizedBox(height: 12),
                const ExpenseCategoryItem(
                  category: 'Hiburan',
                  amount: 400000,
                  percentage: 0.1,
                  color: AppColors.success,
                  icon: Icons.movie,
                ),
                const SizedBox(height: 12),
                const ExpenseCategoryItem(
                  category: 'Tagihan & Utilitas',
                  amount: 500000,
                  percentage: 0.125,
                  color: AppColors.gray600,
                  icon: Icons.receipt_long,
                ),
              ],
            ),
          ),
          const SizedBox(height: 20),
          
          // Budget vs Actual
          _buildBudgetComparisonCard(),
          const SizedBox(height: 20),
          
          // Expense Analysis
          _buildExpenseAnalysisCard(),
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

  Widget _buildExpenseSummaryCards() {
    return Row(
      children: [
        Expanded(
          child: _buildSummaryCard(
            'Total Bulan Ini',
            'Rp 3.900.000',
            Icons.calendar_month,
            AppColors.error,
            '+8%',
            isNegative: true,
          ),
        ),
        const SizedBox(width: 12),
        Expanded(
          child: _buildSummaryCard(
            'Rata-rata Harian',
            'Rp 130.000',
            Icons.today,
            AppColors.warning,
            '+3%',
            isNegative: true,
          ),
        ),
      ],
    );
  }

  Widget _buildSummaryCard(
    String title, 
    String amount, 
    IconData icon, 
    Color color, 
    String growth,
    {bool isNegative = false}
  ) {
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
                  color: isNegative 
                      ? AppColors.error.withOpacity(0.1)
                      : AppColors.success.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Text(
                  growth,
                  style: AppTextStyles.caption.copyWith(
                    color: isNegative ? AppColors.error : AppColors.success,
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

  Widget _buildBudgetComparisonCard() {
    return CustomCard(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _buildSectionHeader(
            'Budget vs Aktual',
            Icons.compare_arrows,
            AppColors.info,
          ),
          const SizedBox(height: 16),
          
          _buildBudgetItem('Makanan', 1000000, 1200000, AppColors.error),
          const SizedBox(height: 12),
          _buildBudgetItem('Transport', 700000, 800000, AppColors.warning),
          const SizedBox(height: 12),
          _buildBudgetItem('Belanja', 800000, 600000, AppColors.success),
          const SizedBox(height: 12),
          _buildBudgetItem('Hiburan', 500000, 400000, AppColors.success),
        ],
      ),
    );
  }

  Widget _buildBudgetItem(String category, double budget, double actual, Color color) {
    final isOverBudget = actual > budget;
    final percentage = (actual / budget * 100).round();
    
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text(
              category,
              style: AppTextStyles.bodyMedium.copyWith(
                fontWeight: FontWeight.w500,
              ),
            ),
            Row(
              children: [
                Text(
                  'Rp ${(actual / 1000).toInt()}K / ${(budget / 1000).toInt()}K',
                  style: AppTextStyles.caption.copyWith(
                    color: AppColors.textSecondary,
                  ),
                ),
                const SizedBox(width: 8),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                  decoration: BoxDecoration(
                    color: color.withOpacity(0.1),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Text(
                    '$percentage%',
                    style: AppTextStyles.caption.copyWith(
                      color: color,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                ),
              ],
            ),
          ],
        ),
        const SizedBox(height: 8),
        ClipRRect(
          borderRadius: BorderRadius.circular(4),
          child: LinearProgressIndicator(
            value: (actual / budget).clamp(0.0, 1.0),
            backgroundColor: AppColors.gray200,
            valueColor: AlwaysStoppedAnimation<Color>(color),
            minHeight: 6,
          ),
        ),
        if (isOverBudget) ...[
          const SizedBox(height: 4),
          Text(
            'Melebihi budget Rp ${((actual - budget) / 1000).toInt()}K',
            style: AppTextStyles.caption.copyWith(
              color: AppColors.error,
            ),
          ),
        ],
      ],
    );
  }

  Widget _buildExpenseAnalysisCard() {
    return CustomCard(
      backgroundColor: AppColors.warning.withOpacity(0.05),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(
                Icons.analytics,
                color: AppColors.warning,
                size: 20,
              ),
              const SizedBox(width: 8),
              Text(
                'Analisis Pengeluaran',
                style: AppTextStyles.labelLarge.copyWith(
                  fontWeight: FontWeight.w600,
                  color: AppColors.warning,
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
              border: Border.all(color: AppColors.warning.withOpacity(0.2)),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Rekomendasi Penghematan:',
                  style: AppTextStyles.labelMedium.copyWith(
                    fontWeight: FontWeight.w600,
                  ),
                ),
                const SizedBox(height: 12),
                _buildRecommendationItem(
                  '• Kurangi makan di luar 2x seminggu (hemat ~300K)',
                  AppColors.success,
                ),
                const SizedBox(height: 4),
                _buildRecommendationItem(
                  '• Gunakan transportasi umum lebih sering (hemat ~200K)',
                  AppColors.info,
                ),
                const SizedBox(height: 4),
                _buildRecommendationItem(
                  '• Budget hiburan sudah optimal, pertahankan!',
                  AppColors.success,
                ),
                const SizedBox(height: 4),
                _buildRecommendationItem(
                  '• Potensi penghematan total: Rp 500K/bulan',
                  AppColors.primary,
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildRecommendationItem(String text, Color color) {
    return Text(
      text,
      style: AppTextStyles.bodySmall.copyWith(
        color: color,
      ),
    );
  }
}