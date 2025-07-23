// lib/screens/dashboard/predictions/income_tab.dart
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:fl_chart/fl_chart.dart';
import '../../../utils/app_colors.dart';
import '../../../utils/app_text_styles.dart';
import '../../../utils/format_eksplore.dart';
import '../../../widgets/custom_widgets.dart';
import '../../../providers/prediction_provider.dart';

class IncomeTab extends StatelessWidget {
  const IncomeTab({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Consumer<PredictionProvider>(
      builder: (context, predictionProvider, child) {
        if (predictionProvider.isLoadingIncome) {
          return const Center(
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                CircularProgressIndicator(),
                SizedBox(height: 16),
                Text('Memuat prediksi income...'),
              ],
            ),
          );
        }

        if (predictionProvider.incomePrediction == null) {
          return Center(
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Icon(
                  Icons.trending_up,
                  size: 64,
                  color: AppColors.gray400,
                ),
                const SizedBox(height: 16),
                Text(
                  'Data Tidak Cukup',
                  style: AppTextStyles.h6,
                ),
                const SizedBox(height: 8),
                Text(
                  'Minimal 10 transaksi income diperlukan untuk prediksi',
                  style: AppTextStyles.bodyMedium.copyWith(
                    color: AppColors.textSecondary,
                  ),
                  textAlign: TextAlign.center,
                ),
              ],
            ),
          );
        }

        return SingleChildScrollView(
          padding: const EdgeInsets.all(20),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              _buildIncomeSummaryCard(predictionProvider),
              const SizedBox(height: 20),
              _buildIncomeChart(predictionProvider),
              const SizedBox(height: 20),
              _buildIncomeInsightsCard(predictionProvider),
            ],
          ),
        );
      },
    );
  }

  Widget _buildIncomeSummaryCard(PredictionProvider predictionProvider) {
    if (predictionProvider.incomePrediction == null) return const SizedBox();

    final summary = predictionProvider.incomePrediction!.summary;
    final performance = predictionProvider.incomePrediction!.modelPerformance;

    return CustomCard(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Prediksi Income ${predictionProvider.forecastDays} Hari',
            style: AppTextStyles.h6.copyWith(
              fontWeight: FontWeight.w600,
            ),
          ),
          const SizedBox(height: 16),
          Row(
            children: [
              Expanded(
                child: _buildSummaryItem(
                  'Total Prediksi',
                  summary.formattedTotal,
                  Icons.monetization_on,
                  AppColors.success,
                ),
              ),
              const SizedBox(width: 16),
              Expanded(
                child: _buildSummaryItem(
                  'Rata-rata Harian',
                  summary.formattedDailyAvg,
                  Icons.calendar_today,
                  AppColors.info,
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          _buildConfidenceBadge(summary.confidenceLevel),
          const SizedBox(height: 12),
          Text(
            'Model Performance',
            style: AppTextStyles.labelMedium.copyWith(
              color: AppColors.textSecondary,
              fontWeight: FontWeight.w600,
            ),
          ),
          const SizedBox(height: 8),
          Row(
            children: [
              _buildPerformanceMetric('Accuracy', '${performance.accuracyScore.toStringAsFixed(1)}%'),
              const SizedBox(width: 16),
              _buildPerformanceMetric('Data Points', '${performance.dataPoints}'),
              const SizedBox(width: 16),
              _buildPerformanceMetric('MAPE', '${performance.mape.toStringAsFixed(1)}%'),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildSummaryItem(String title, String value, IconData icon, Color color) {
    return Container(
      padding: const EdgeInsets.all(16),
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
          const SizedBox(height: 8),
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

  Widget _buildConfidenceBadge(String confidenceLevel) {
    Color badgeColor;
    switch (confidenceLevel.toLowerCase()) {
      case 'tinggi':
        badgeColor = AppColors.success;
        break;
      case 'menengah':
        badgeColor = AppColors.warning;
        break;
      default:
        badgeColor = AppColors.error;
    }

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
      decoration: BoxDecoration(
        color: badgeColor.withOpacity(0.1),
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: badgeColor.withOpacity(0.3)),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(
            Icons.verified,
            size: 16,
            color: badgeColor,
          ),
          const SizedBox(width: 6),
          Text(
            'Confidence: $confidenceLevel',
            style: AppTextStyles.caption.copyWith(
              color: badgeColor,
              fontWeight: FontWeight.w600,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildPerformanceMetric(String label, String value) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          label,
          style: AppTextStyles.caption.copyWith(
            color: AppColors.textTertiary,
          ),
        ),
        Text(
          value,
          style: AppTextStyles.labelMedium.copyWith(
            fontWeight: FontWeight.w600,
          ),
        ),
      ],
    );
  }

  Widget _buildIncomeChart(PredictionProvider predictionProvider) {
    if (predictionProvider.incomePrediction == null || 
        predictionProvider.incomePrediction!.dailyPredictions.isEmpty) {
      return CustomCard(
        child: Container(
          height: 200,
          child: Center(
            child: Text(
              'Chart tidak tersedia',
              style: AppTextStyles.bodyMedium.copyWith(
                color: AppColors.textSecondary,
              ),
            ),
          ),
        ),
      );
    }

    return CustomCard(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Tren Prediksi Income',
            style: AppTextStyles.h6.copyWith(
              fontWeight: FontWeight.w600,
            ),
          ),
          const SizedBox(height: 20),
          SizedBox(
            height: 200,
            child: LineChart(
              _buildIncomeLineChartData(predictionProvider.incomePrediction!),
            ),
          ),
        ],
      ),
    );
  }

  LineChartData _buildIncomeLineChartData(incomePrediction) {
    final predictions = incomePrediction.dailyPredictions;
    
    return LineChartData(
      gridData: FlGridData(
        show: true,
        drawVerticalLine: false,
        horizontalInterval: null,
        getDrawingHorizontalLine: (value) {
          return FlLine(
            color: AppColors.border,
            strokeWidth: 1,
          );
        },
      ),
      titlesData: FlTitlesData(
        leftTitles: AxisTitles(
          sideTitles: SideTitles(
            showTitles: true,
            reservedSize: 60,
            getTitlesWidget: (value, meta) {
              return Text(
                FormatUtils.formatCompactCurrency(value),
                style: AppTextStyles.caption.copyWith(
                  color: AppColors.textSecondary,
                ),
              );
            },
          ),
        ),
        bottomTitles: AxisTitles(
          sideTitles: SideTitles(
            showTitles: true,
            reservedSize: 30,
            interval: predictions.length > 20 ? (predictions.length / 5).floor().toDouble() : 5,
            getTitlesWidget: (value, meta) {
              final index = value.toInt();
              if (index >= 0 && index < predictions.length) {
                final date = predictions[index].date;
                return Text(
                  '${date.day}/${date.month}',
                  style: AppTextStyles.caption.copyWith(
                    color: AppColors.textSecondary,
                  ),
                );
              }
              return const SizedBox();
            },
          ),
        ),
        topTitles: AxisTitles(sideTitles: SideTitles(showTitles: false)),
        rightTitles: AxisTitles(sideTitles: SideTitles(showTitles: false)),
      ),
      borderData: FlBorderData(show: false),
      lineBarsData: [
        // Main prediction line
        LineChartBarData(
          spots: predictions.asMap().entries.map((entry) {
            return FlSpot(entry.key.toDouble(), entry.value.predictedValue);
          }).toList(),
          isCurved: true,
          color: AppColors.success,
          barWidth: 3,
          isStrokeCapRound: true,
          belowBarData: BarAreaData(
            show: true,
            color: AppColors.success.withOpacity(0.1),
          ),
          dotData: FlDotData(show: false),
        ),
        // Upper bound
        LineChartBarData(
          spots: predictions.asMap().entries.map((entry) {
            return FlSpot(entry.key.toDouble(), entry.value.upperBound);
          }).toList(),
          isCurved: true,
          color: AppColors.success.withOpacity(0.3),
          barWidth: 1,
          dashArray: [5, 5],
          dotData: FlDotData(show: false),
        ),
        // Lower bound
        LineChartBarData(
          spots: predictions.asMap().entries.map((entry) {
            return FlSpot(entry.key.toDouble(), entry.value.lowerBound);
          }).toList(),
          isCurved: true,
          color: AppColors.success.withOpacity(0.3),
          barWidth: 1,
          dashArray: [5, 5],
          dotData: FlDotData(show: false),
        ),
      ],
      lineTouchData: LineTouchData(
        touchTooltipData: LineTouchTooltipData(
          tooltipBgColor: AppColors.white,
          tooltipBorder: BorderSide(color: AppColors.border),
          getTooltipItems: (touchedSpots) {
            return touchedSpots.map((spot) {
              final index = spot.x.toInt();
              if (index >= 0 && index < predictions.length) {
                final prediction = predictions[index];
                return LineTooltipItem(
                  '${prediction.formattedDate}\n${FormatUtils.formatCurrency(spot.y)}',
                  AppTextStyles.bodySmall.copyWith(
                    color: AppColors.textPrimary,
                  ),
                );
              }
              return null;
            }).toList();
          },
        ),
      ),
    );
  }

  Widget _buildIncomeInsightsCard(PredictionProvider predictionProvider) {
    if (predictionProvider.incomePrediction == null) return const SizedBox();

    return CustomCard(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'AI Insights & Recommendations',
            style: AppTextStyles.h6.copyWith(
              fontWeight: FontWeight.w600,
            ),
          ),
          const SizedBox(height: 16),
          if (predictionProvider.incomePrediction!.aiInsights.isNotEmpty) ...[
            Text(
              'Insights',
              style: AppTextStyles.labelMedium.copyWith(
                color: AppColors.info,
                fontWeight: FontWeight.w600,
              ),
            ),
            const SizedBox(height: 8),
            for (final insight in predictionProvider.incomePrediction!.aiInsights.take(3))
              Padding(
                padding: const EdgeInsets.only(bottom: 8),
                child: Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Icon(
                      Icons.lightbulb_outline,
                      size: 16,
                      color: AppColors.info,
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
            const SizedBox(height: 16),
          ],
          if (predictionProvider.incomePrediction!.recommendations.isNotEmpty) ...[
            Text(
              'Recommendations',
              style: AppTextStyles.labelMedium.copyWith(
                color: AppColors.success,
                fontWeight: FontWeight.w600,
              ),
            ),
            const SizedBox(height: 8),
            for (final recommendation in predictionProvider.incomePrediction!.recommendations.take(3))
              Padding(
                padding: const EdgeInsets.only(bottom: 8),
                child: Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Icon(
                      Icons.check_circle_outline,
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
          ],
        ],
      ),
    );
  }
}