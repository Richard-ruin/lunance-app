// lib/screens/dashboard/predictions/insights_tab.dart
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../../utils/app_colors.dart';
import '../../../utils/app_text_styles.dart';
import '../../../widgets/custom_widgets.dart';
import '../../../providers/prediction_provider.dart';

class InsightsTab extends StatelessWidget {
  const InsightsTab({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Consumer<PredictionProvider>(
      builder: (context, predictionProvider, child) {
        return SingleChildScrollView(
          padding: const EdgeInsets.all(20),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              _buildComprehensiveInsightsCard(predictionProvider),
              const SizedBox(height: 20),
              _buildDataQualityCard(predictionProvider),
              const SizedBox(height: 20),
              _buildActionableRecommendationsCard(predictionProvider),
            ],
          ),
        );
      },
    );
  }

  Widget _buildComprehensiveInsightsCard(PredictionProvider predictionProvider) {
    final insights = predictionProvider.allInsights;

    return CustomCard(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(
                Icons.auto_awesome,
                color: AppColors.primary,
                size: 20,
              ),
              const SizedBox(width: 8),
              Text(
                'AI Comprehensive Insights',
                style: AppTextStyles.h6.copyWith(
                  fontWeight: FontWeight.w600,
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          if (insights.isNotEmpty) ...[
            for (final insight in insights.take(6))
              Padding(
                padding: const EdgeInsets.only(bottom: 12),
                child: Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: AppColors.primary.withOpacity(0.05),
                    borderRadius: BorderRadius.circular(12),
                    border: Border.all(
                      color: AppColors.primary.withOpacity(0.2),
                    ),
                  ),
                  child: Row(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Icon(
                        Icons.lightbulb,
                        size: 16,
                        color: AppColors.primary,
                      ),
                      const SizedBox(width: 8),
                      Expanded(
                        child: Text(
                          insight,
                          style: AppTextStyles.bodySmall.copyWith(
                            height: 1.4,
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
              ),
          ] else
            Text(
              'Insights akan tersedia setelah data mencukupi.',
              style: AppTextStyles.bodyMedium.copyWith(
                color: AppColors.textSecondary,
              ),
            ),
        ],
      ),
    );
  }

  Widget _buildDataQualityCard(PredictionProvider predictionProvider) {
    final qualityData = predictionProvider.getDataQuality();
    
    return CustomCard(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(
                Icons.analytics,
                color: qualityData['quality_color'],
                size: 20,
              ),
              const SizedBox(width: 8),
              Text(
                'Data Quality Assessment',
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
                child: _buildQualityMetric(
                  'Data Points',
                  qualityData['data_points'].toString(),
                  Icons.data_usage,
                  qualityData['quality_color'],
                ),
              ),
              const SizedBox(width: 16),
              Expanded(
                child: _buildQualityMetric(
                  'Model Accuracy',
                  '${qualityData['model_accuracy'].toStringAsFixed(1)}%',
                  Icons.verified,
                  qualityData['quality_color'],
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: qualityData['quality_color'].withOpacity(0.1),
              borderRadius: BorderRadius.circular(12),
              border: Border.all(color: qualityData['quality_color'].withOpacity(0.3)),
            ),
            child: Row(
              children: [
                Icon(
                  Icons.assessment,
                  color: qualityData['quality_color'],
                  size: 16,
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'Quality: ${qualityData['quality_level']}',
                        style: AppTextStyles.labelMedium.copyWith(
                          color: qualityData['quality_color'],
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                      Text(
                        qualityData['description'],
                        style: AppTextStyles.bodySmall.copyWith(
                          color: AppColors.textSecondary,
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildQualityMetric(String title, String value, IconData icon, Color color) {
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
          Row(
            children: [
              Icon(icon, color: color, size: 16),
              const SizedBox(width: 6),
              Text(
                title,
                style: AppTextStyles.labelSmall.copyWith(
                  color: color,
                  fontWeight: FontWeight.w600,
                ),
              ),
            ],
          ),
          const SizedBox(height: 6),
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

  Widget _buildActionableRecommendationsCard(PredictionProvider predictionProvider) {
    final recommendations = predictionProvider.allRecommendations;

    return CustomCard(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(
                Icons.recommend,
                color: AppColors.success,
                size: 20,
              ),
              const SizedBox(width: 8),
              Text(
                'Actionable Recommendations',
                style: AppTextStyles.h6.copyWith(
                  fontWeight: FontWeight.w600,
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          if (recommendations.isNotEmpty) ...[
            for (int i = 0; i < recommendations.take(5).length; i++)
              Padding(
                padding: const EdgeInsets.only(bottom: 12),
                child: Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: AppColors.success.withOpacity(0.05),
                    borderRadius: BorderRadius.circular(12),
                    border: Border.all(
                      color: AppColors.success.withOpacity(0.2),
                    ),
                  ),
                  child: Row(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Container(
                        width: 20,
                        height: 20,
                        decoration: BoxDecoration(
                          color: AppColors.success,
                          shape: BoxShape.circle,
                        ),
                        child: Center(
                          child: Text(
                            '${i + 1}',
                            style: AppTextStyles.caption.copyWith(
                              color: AppColors.white,
                              fontWeight: FontWeight.w600,
                            ),
                          ),
                        ),
                      ),
                      const SizedBox(width: 12),
                      Expanded(
                        child: Text(
                          recommendations[i],
                          style: AppTextStyles.bodySmall.copyWith(
                            height: 1.4,
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
              ),
          ] else
            Text(
              'Recommendations akan tersedia setelah analisis selesai.',
              style: AppTextStyles.bodyMedium.copyWith(
                color: AppColors.textSecondary,
              ),
            ),
        ],
      ),
    );
  }
}