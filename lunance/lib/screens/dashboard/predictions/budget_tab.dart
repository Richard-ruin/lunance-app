// lib/screens/dashboard/predictions/budget_tab.dart
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:fl_chart/fl_chart.dart';
import '../../../utils/app_colors.dart';
import '../../../utils/app_text_styles.dart';
import '../../../widgets/custom_widgets.dart';
import '../../../widgets/common_widgets.dart';
import '../../../providers/prediction_provider.dart';
import '../../../services/prediction_service.dart';

class BudgetTab extends StatefulWidget {
  const BudgetTab({Key? key}) : super(key: key);

  @override
  State<BudgetTab> createState() => _BudgetTabState();
}

class _BudgetTabState extends State<BudgetTab> {
  String _selectedBudgetType = 'needs';
  final PredictionService _predictionService = PredictionService();

  @override
  Widget build(BuildContext context) {
    return Consumer<PredictionProvider>(
      builder: (context, predictionProvider, child) {
        if (predictionProvider.isLoadingBudget) {
          return const Center(
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                CircularProgressIndicator(),
                SizedBox(height: 16),
                Text('Memuat prediksi budget...'),
              ],
            ),
          );
        }

        return SingleChildScrollView(
          padding: const EdgeInsets.all(20),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              _buildBudgetPerformanceCard(predictionProvider),
              const SizedBox(height: 20),
              _buildBudgetTypeSelector(),
              const SizedBox(height: 16),
              _buildBudgetTypeChart(predictionProvider),
              const SizedBox(height: 20),
              _buildBudgetRecommendationsCard(predictionProvider),
            ],
          ),
        );
      },
    );
  }

  Widget _buildBudgetPerformanceCard(PredictionProvider predictionProvider) {
    if (predictionProvider.budgetPrediction == null) {
      return CustomCard(
        child: Column(
          children: [
            const ShimmerWidget(width: double.infinity, height: 24),
            const SizedBox(height: 16),
            const ShimmerWidget(width: double.infinity, height: 100),
          ],
        ),
      );
    }

    return CustomCard(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Budget Performance Prediction',
            style: AppTextStyles.h6.copyWith(
              fontWeight: FontWeight.w600,
            ),
          ),
          const SizedBox(height: 16),
          _buildBudgetPerformanceMetrics(predictionProvider),
          const SizedBox(height: 20),
          _buildBudgetAllocationChart(predictionProvider),
        ],
      ),
    );
  }

  Widget _buildBudgetPerformanceMetrics(PredictionProvider predictionProvider) {
    if (predictionProvider.budgetPrediction == null) return const SizedBox();

    final predicted = predictionProvider.budgetPrediction!.predictedTotals;
    final formatted = predictionProvider.budgetPrediction!.formattedTotals;

    return Column(
      children: [
        Row(
          children: [
            Expanded(
              child: _buildBudgetMetric(
                'Needs Predicted',
                formatted['needs'] ?? 'N/A',
                '${predictionProvider.budgetPrediction!.needsPercentage.toStringAsFixed(1)}%',
                AppColors.success,
              ),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: _buildBudgetMetric(
                'Wants Predicted',
                formatted['wants'] ?? 'N/A',
                '${predictionProvider.budgetPrediction!.wantsPercentage.toStringAsFixed(1)}%',
                AppColors.warning,
              ),
            ),
          ],
        ),
        const SizedBox(height: 12),
        Row(
          children: [
            Expanded(
              child: _buildBudgetMetric(
                'Savings Predicted',
                formatted['savings'] ?? 'N/A',
                '${predictionProvider.budgetPrediction!.savingsPercentage.toStringAsFixed(1)}%',
                AppColors.info,
              ),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: _buildBudgetMetric(
                'Health Score',
                '${predictionProvider.budgetPrediction!.budgetHealth.healthScore.toStringAsFixed(1)}',
                predictionProvider.budgetPrediction!.budgetHealth.healthLevel,
                _getHealthColor(predictionProvider.budgetPrediction!.budgetHealth.healthScore),
              ),
            ),
          ],
        ),
      ],
    );
  }

  Widget _buildBudgetMetric(String title, String value, String subtitle, Color color) {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: color.withOpacity(0.3)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            title,
            style: AppTextStyles.labelSmall.copyWith(
              color: color,
              fontWeight: FontWeight.w600,
            ),
          ),
          const SizedBox(height: 6),
          Text(
            value,
            style: AppTextStyles.labelMedium.copyWith(
              fontWeight: FontWeight.w700,
              color: color,
            ),
          ),
          Text(
            subtitle,
            style: AppTextStyles.caption.copyWith(
              color: AppColors.textSecondary,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildBudgetAllocationChart(PredictionProvider predictionProvider) {
    if (predictionProvider.budgetPrediction == null) return const SizedBox();

    final data = [
      PieChartSectionData(
        value: predictionProvider.budgetPrediction!.needsPercentage,
        title: '${predictionProvider.budgetPrediction!.needsPercentage.toStringAsFixed(1)}%',
        color: AppColors.success,
        radius: 60,
        titleStyle: AppTextStyles.labelSmall.copyWith(
          color: AppColors.white,
          fontWeight: FontWeight.w600,
        ),
      ),
      PieChartSectionData(
        value: predictionProvider.budgetPrediction!.wantsPercentage,
        title: '${predictionProvider.budgetPrediction!.wantsPercentage.toStringAsFixed(1)}%',
        color: AppColors.warning,
        radius: 60,
        titleStyle: AppTextStyles.labelSmall.copyWith(
          color: AppColors.white,
          fontWeight: FontWeight.w600,
        ),
      ),
      PieChartSectionData(
        value: predictionProvider.budgetPrediction!.savingsPercentage,
        title: '${predictionProvider.budgetPrediction!.savingsPercentage.toStringAsFixed(1)}%',
        color: AppColors.info,
        radius: 60,
        titleStyle: AppTextStyles.labelSmall.copyWith(
          color: AppColors.white,
          fontWeight: FontWeight.w600,
        ),
      ),
    ];

    return Column(
      children: [
        SizedBox(
          height: 200,
          child: PieChart(
            PieChartData(
              sections: data,
              centerSpaceRadius: 40,
              sectionsSpace: 2,
            ),
          ),
        ),
        const SizedBox(height: 16),
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceEvenly,
          children: [
            _buildLegendItem('Needs (50%)', AppColors.success),
            _buildLegendItem('Wants (30%)', AppColors.warning),
            _buildLegendItem('Savings (20%)', AppColors.info),
          ],
        ),
      ],
    );
  }

  Widget _buildLegendItem(String label, Color color) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        Container(
          width: 12,
          height: 12,
          decoration: BoxDecoration(
            color: color,
            shape: BoxShape.circle,
          ),
        ),
        const SizedBox(width: 6),
        Text(
          label,
          style: AppTextStyles.caption.copyWith(
            fontWeight: FontWeight.w600,
          ),
        ),
      ],
    );
  }

  Widget _buildBudgetTypeSelector() {
    return Row(
      children: [
        Text(
          'Detail Prediksi:',
          style: AppTextStyles.labelMedium.copyWith(
            fontWeight: FontWeight.w600,
          ),
        ),
        const SizedBox(width: 12),
        Expanded(
          child: SingleChildScrollView(
            scrollDirection: Axis.horizontal,
            child: Row(
              children: ['needs', 'wants', 'savings'].map((type) {
                final isSelected = type == _selectedBudgetType;
                return Padding(
                  padding: const EdgeInsets.only(right: 8),
                  child: ChoiceChip(
                    label: Text(_predictionService.getBudgetTypeName(type)),
                    selected: isSelected,
                    onSelected: (selected) {
                      if (selected) {
                        setState(() {
                          _selectedBudgetType = type;
                        });
                      }
                    },
                    selectedColor: Color(int.parse(
                      _predictionService.getBudgetTypeColorHex(type).substring(1),
                      radix: 16,
                    ) + 0xFF000000).withOpacity(0.2),
                    labelStyle: AppTextStyles.labelSmall.copyWith(
                      color: isSelected 
                          ? Color(int.parse(
                              _predictionService.getBudgetTypeColorHex(type).substring(1),
                              radix: 16,
                            ) + 0xFF000000)
                          : AppColors.textSecondary,
                      fontWeight: isSelected ? FontWeight.w600 : FontWeight.normal,
                    ),
                  ),
                );
              }).toList(),
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildBudgetTypeChart(PredictionProvider predictionProvider) {
    final selectedExpense = predictionProvider.getExpensePrediction(_selectedBudgetType);

    if (selectedExpense == null) {
      return CustomCard(
        child: Container(
          height: 200,
          child: Center(
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Icon(
                  Icons.pie_chart_outline,
                  size: 48,
                  color: AppColors.gray400,
                ),
                const SizedBox(height: 12),
                Text(
                  'Data ${_predictionService.getBudgetTypeName(_selectedBudgetType)} tidak tersedia',
                  style: AppTextStyles.bodyMedium.copyWith(
                    color: AppColors.textSecondary,
                  ),
                  textAlign: TextAlign.center,
                ),
              ],
            ),
          ),
        ),
      );
    }

    return CustomCard(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(
                Icons.pie_chart,
                color: Color(int.parse(
                  selectedExpense.budgetTypeColorHex.substring(1),
                  radix: 16,
                ) + 0xFF000000),
                size: 20,
              ),
              const SizedBox(width: 8),
              Text(
                'Prediksi ${selectedExpense.budgetTypeName}',
                style: AppTextStyles.h6.copyWith(
                  fontWeight: FontWeight.w600,
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          Row(
            children: [
              Expanded(
                child: _buildBudgetTypeDetailMetric(
                  'Total Prediksi',
                  selectedExpense.summary.formattedTotal,
                  Icons.monetization_on,
                ),
              ),
              const SizedBox(width: 16),
              Expanded(
                child: _buildBudgetTypeDetailMetric(
                  'Rata-rata Harian',
                  selectedExpense.summary.formattedDailyAvg,
                  Icons.calendar_today,
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          _buildBudgetTypeConfidence(selectedExpense.modelPerformance),
        ],
      ),
    );
  }

  Widget _buildBudgetTypeDetailMetric(String title, String value, IconData icon) {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: AppColors.gray50,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: AppColors.border),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(icon, size: 16, color: AppColors.textSecondary),
              const SizedBox(width: 6),
              Text(
                title,
                style: AppTextStyles.labelSmall.copyWith(
                  color: AppColors.textSecondary,
                ),
              ),
            ],
          ),
          const SizedBox(height: 6),
          Text(
            value,
            style: AppTextStyles.labelMedium.copyWith(
              fontWeight: FontWeight.w700,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildBudgetTypeConfidence(modelPerformance) {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: AppColors.info.withOpacity(0.1),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: AppColors.info.withOpacity(0.3)),
      ),
      child: Row(
        children: [
          Icon(
            Icons.verified,
            color: AppColors.info,
            size: 16,
          ),
          const SizedBox(width: 8),
          Text(
            'Accuracy: ${modelPerformance.accuracyScore.toStringAsFixed(1)}%',
            style: AppTextStyles.labelSmall.copyWith(
              color: AppColors.info,
              fontWeight: FontWeight.w600,
            ),
          ),
          const Spacer(),
          Text(
            'Confidence: ${modelPerformance.confidenceLevel}',
            style: AppTextStyles.labelSmall.copyWith(
              color: AppColors.textSecondary,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildBudgetRecommendationsCard(PredictionProvider predictionProvider) {
    if (predictionProvider.budgetPrediction == null) return const SizedBox();

    return CustomCard(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Budget Optimization',
            style: AppTextStyles.h6.copyWith(
              fontWeight: FontWeight.w600,
            ),
          ),
          const SizedBox(height: 16),
          if (predictionProvider.budgetPrediction!.optimizationRecommendations.isNotEmpty) ...[
            for (final recommendation in predictionProvider.budgetPrediction!.optimizationRecommendations.take(5))
              Padding(
                padding: const EdgeInsets.only(bottom: 12),
                child: Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Icon(
                      Icons.trending_up,
                      size: 16,
                      color: AppColors.success,
                    ),
                    const SizedBox(width: 8),
                    Expanded(
                      child: Text(
                        recommendation,
                        style: AppTextStyles.bodySmall.copyWith(
                          height: 1.4,
                        ),
                      ),
                    ),
                  ],
                ),
              ),
          ] else
            Text(
              'Tidak ada rekomendasi optimasi saat ini.',
              style: AppTextStyles.bodyMedium.copyWith(
                color: AppColors.textSecondary,
              ),
            ),
        ],
      ),
    );
  }

  // Helper methods
  Color _getHealthColor(double score) {
    if (score >= 80) return AppColors.success;
    if (score >= 60) return AppColors.info;
    if (score >= 40) return AppColors.warning;
    return AppColors.error;
  }
}