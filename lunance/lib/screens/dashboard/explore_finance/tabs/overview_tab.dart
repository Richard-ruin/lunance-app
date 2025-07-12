import 'package:flutter/material.dart';
import '../../../../utils/app_colors.dart';
import '../../../../utils/app_text_styles.dart';
import '../../../../widgets/custom_widgets.dart';
import '../widgets/period_selector.dart';
import '../widgets/chart_containers.dart';
import '../widgets/category_legend.dart';

class OverviewTab extends StatefulWidget {
  const OverviewTab({Key? key}) : super(key: key);

  @override
  State<OverviewTab> createState() => _OverviewTabState();
}

class _OverviewTabState extends State<OverviewTab> {
  int _selectedPeriod = 0; // 0: Harian, 1: Mingguan, 2: Bulanan

  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
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
          
          // Income vs Expense Chart
          CustomCard(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                _buildChartHeader(
                  'Pemasukan vs Pengeluaran',
                  Icons.bar_chart,
                  AppColors.primary,
                ),
                const SizedBox(height: 20),
                SizedBox(
                  height: 200,
                  child: ChartContainers.incomeExpenseChart(),
                ),
              ],
            ),
          ),
          const SizedBox(height: 20),
          
          // Category Breakdown
          CustomCard(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                _buildChartHeader(
                  'Pengeluaran per Kategori',
                  Icons.pie_chart,
                  AppColors.success,
                ),
                const SizedBox(height: 20),
                Row(
                  children: [
                    Expanded(
                      child: SizedBox(
                        height: 150,
                        child: ChartContainers.categoryPieChart(),
                      ),
                    ),
                    const SizedBox(width: 16),
                    const Expanded(
                      child: CategoryLegend(),
                    ),
                  ],
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildChartHeader(String title, IconData icon, Color color) {
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
}