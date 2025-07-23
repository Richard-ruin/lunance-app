// lib/screens/dashboard/predictions/overview_tab.dart
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../../utils/app_colors.dart';
import '../../../utils/app_text_styles.dart';
import '../../../widgets/custom_widgets.dart';
import '../../../widgets/common_widgets.dart';
import '../../../providers/prediction_provider.dart';

class OverviewTab extends StatelessWidget {
  const OverviewTab({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Consumer<PredictionProvider>(
      builder: (context, predictionProvider, child) {
        return SingleChildScrollView(
          padding: const EdgeInsets.all(20),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              _buildQuickStatsCards(predictionProvider),
              const SizedBox(height: 20),
              _buildHealthScoreCard(predictionProvider),
              const SizedBox(height: 20),
              _buildRecentPredictionsCard(predictionProvider),
            ],
          ),
        );
      },
    );
  }

  Widget _buildQuickStatsCards(PredictionProvider predictionProvider) {
    return Row(
      children: [
        Expanded(
          child: _buildStatCard(
            title: 'Prediksi Income',
            value: predictionProvider.getFormattedPredictionValue('income', 'total'),
            subtitle: '${predictionProvider.forecastDays} hari kedepan',
            icon: Icons.trending_up,
            color: AppColors.success,
            isLoading: predictionProvider.isLoadingIncome,
          ),
        ),
        const SizedBox(width: 16),
        Expanded(
          child: _buildStatCard(
            title: 'Budget Health',
            value: predictionProvider.budgetPrediction?.budgetHealth.healthEmoji ?? '📊',
            subtitle: predictionProvider.overallHealthLevel,
            icon: Icons.favorite,
            color: AppColors.info,
            isLoading: predictionProvider.isLoadingBudget,
          ),
        ),
      ],
    );
  }

  Widget _buildStatCard({
    required String title,
    required String value,
    required String subtitle,
    required IconData icon,
    required Color color,
    bool isLoading = false,
  }) {
    return CustomCard(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(icon, color: color, size: 20),
              const SizedBox(width: 8),
              Expanded(
                child: Text(
                  title,
                  style: AppTextStyles.labelMedium.copyWith(
                    color: AppColors.textSecondary,
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          if (isLoading)
            const ShimmerWidget(width: 100, height: 24)
          else
            Text(
              value,
              style: AppTextStyles.h5.copyWith(
                fontWeight: FontWeight.w700,
                color: color,
              ),
            ),
          const SizedBox(height: 4),
          Text(
            subtitle,
            style: AppTextStyles.bodySmall.copyWith(
              color: AppColors.textTertiary,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildHealthScoreCard(PredictionProvider predictionProvider) {
    if (predictionProvider.budgetPrediction == null) {
      return CustomCard(
        child: Column(
          children: [
            const ShimmerWidget(width: double.infinity, height: 24),
            const SizedBox(height: 12),
            const ShimmerWidget(width: double.infinity, height: 100),
          ],
        ),
      );
    }

    final health = predictionProvider.budgetPrediction!.budgetHealth;
    
    return CustomCard(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Text(
                'Financial Health Score',
                style: AppTextStyles.h6.copyWith(
                  fontWeight: FontWeight.w600,
                ),
              ),
              const Spacer(),
              Text(
                '${health.healthScore.toStringAsFixed(1)}/100',
                style: AppTextStyles.h6.copyWith(
                  fontWeight: FontWeight.w700,
                  color: AppColors.primary,
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          _buildHealthProgress(health.healthScore),
          const SizedBox(height: 16),
          _buildBudgetTypeHealthIndicators(predictionProvider),
        ],
      ),
    );
  }

  Widget _buildHealthProgress(double score) {
    return Column(
      children: [
        LinearProgressIndicator(
          value: score / 100,
          backgroundColor: AppColors.gray200,
          valueColor: AlwaysStoppedAnimation(_getHealthColor(score)),
          minHeight: 8,
        ),
        const SizedBox(height: 8),
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text(
              _getHealthLabel(score),
              style: AppTextStyles.labelMedium.copyWith(
                color: _getHealthColor(score),
                fontWeight: FontWeight.w600,
              ),
            ),
            Text(
              '${score.toStringAsFixed(0)}%',
              style: AppTextStyles.labelMedium.copyWith(
                color: AppColors.textSecondary,
              ),
            ),
          ],
        ),
      ],
    );
  }

  Widget _buildBudgetTypeHealthIndicators(PredictionProvider predictionProvider) {
    if (predictionProvider.budgetPrediction == null) return const SizedBox();

    return Row(
      children: [
        Expanded(
          child: _buildBudgetHealthIndicator(
            'Needs',
            predictionProvider.budgetPrediction!.needsPercentage,
            50.0,
            AppColors.success,
          ),
        ),
        const SizedBox(width: 12),
        Expanded(
          child: _buildBudgetHealthIndicator(
            'Wants',
            predictionProvider.budgetPrediction!.wantsPercentage,
            30.0,
            AppColors.warning,
          ),
        ),
        const SizedBox(width: 12),
        Expanded(
          child: _buildBudgetHealthIndicator(
            'Savings',
            predictionProvider.budgetPrediction!.savingsPercentage,
            20.0,
            AppColors.info,
          ),
        ),
      ],
    );
  }

  Widget _buildBudgetHealthIndicator(String label, double actual, double target, Color color) {
    final variance = actual - target;
    final isGood = variance.abs() <= 5.0;
    
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
          color: color.withOpacity(0.3),
        ),
      ),
      child: Column(
        children: [
          Text(
            label,
            style: AppTextStyles.labelSmall.copyWith(
              color: color,
              fontWeight: FontWeight.w600,
            ),
          ),
          const SizedBox(height: 4),
          Text(
            '${actual.toStringAsFixed(1)}%',
            style: AppTextStyles.labelMedium.copyWith(
              color: color,
              fontWeight: FontWeight.w700,
            ),
          ),
          Text(
            'Target: ${target.toStringAsFixed(0)}%',
            style: AppTextStyles.caption.copyWith(
              color: AppColors.textTertiary,
            ),
          ),
          Icon(
            isGood ? Icons.check_circle : Icons.warning,
            size: 16,
            color: isGood ? AppColors.success : AppColors.warning,
          ),
        ],
      ),
    );
  }

  Widget _buildRecentPredictionsCard(PredictionProvider predictionProvider) {
    return CustomCard(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Prediksi Terkini',
            style: AppTextStyles.h6.copyWith(
              fontWeight: FontWeight.w600,
            ),
          ),
          const SizedBox(height: 16),
          if (predictionProvider.incomePrediction != null) ...[
            _buildPredictionSummaryItem(
              'Income Prediction',
              predictionProvider.incomePrediction!.summary.formattedTotal,
              'Confidence: ${predictionProvider.incomePrediction!.modelPerformance.confidenceLevel}',
              Icons.trending_up,
              AppColors.success,
            ),
            const Divider(),
          ],
          if (predictionProvider.expensePredictions.isNotEmpty) ...[
            for (final entry in predictionProvider.expensePredictions.entries) ...[
              _buildPredictionSummaryItem(
                '${entry.value.budgetTypeName} Prediction',
                entry.value.summary.formattedTotal,
                'Budget ${entry.value.budgetType}',
                Icons.pie_chart,
                Color(int.parse(entry.value.budgetTypeColorHex.substring(1), radix: 16) + 0xFF000000),
              ),
              if (entry.key != predictionProvider.expensePredictions.keys.last) const Divider(),
            ],
          ],
        ],
      ),
    );
  }

  Widget _buildPredictionSummaryItem(
    String title,
    String value,
    String subtitle,
    IconData icon,
    Color color,
  ) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8),
      child: Row(
        children: [
          Icon(icon, color: color, size: 20),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  title,
                  style: AppTextStyles.labelMedium.copyWith(
                    fontWeight: FontWeight.w600,
                  ),
                ),
                Text(
                  subtitle,
                  style: AppTextStyles.bodySmall.copyWith(
                    color: AppColors.textSecondary,
                  ),
                ),
              ],
            ),
          ),
          Text(
            value,
            style: AppTextStyles.labelLarge.copyWith(
              fontWeight: FontWeight.w700,
              color: color,
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

  String _getHealthLabel(double score) {
    if (score >= 80) return 'Sangat Sehat';
    if (score >= 60) return 'Sehat';
    if (score >= 40) return 'Cukup';
    return 'Perlu Perbaikan';
  }
}