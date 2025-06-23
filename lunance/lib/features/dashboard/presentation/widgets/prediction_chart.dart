// lib/features/dashboard/presentation/widgets/prediction_chart.dart
import 'package:flutter/material.dart';
import '../../../../core/theme/lunance_colors.dart';
import '../../domain/entities/prediction.dart';

class PredictionChart extends StatelessWidget {
  final MonthlyPrediction monthlyPrediction;

  const PredictionChart({
    Key? key,
    required this.monthlyPrediction,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: LunanceColors.cardBackground,
        borderRadius: BorderRadius.circular(16),
        boxShadow: [
          BoxShadow(
            color: LunanceColors.shadowLight,
            blurRadius: 8,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(
                Icons.analytics_outlined,
                color: LunanceColors.primaryBlue,
                size: 20,
              ),
              const SizedBox(width: 8),
              Text(
                'Prediksi ${monthlyPrediction.month}',
                style: const TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.bold,
                  color: LunanceColors.primaryText,
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          
          // Chart bars
          _buildChartBar(
            'Pemasukan',
            monthlyPrediction.predictedIncome,
            LunanceColors.incomeGreen,
            monthlyPrediction.predictedIncome,
          ),
          const SizedBox(height: 12),
          _buildChartBar(
            'Pengeluaran',
            monthlyPrediction.predictedExpense,
            LunanceColors.expenseRed,
            monthlyPrediction.predictedIncome,
          ),
          const SizedBox(height: 12),
          _buildChartBar(
            'Tabungan',
            monthlyPrediction.predictedSavings,
            LunanceColors.secondaryTeal,
            monthlyPrediction.predictedIncome,
          ),
          
          const SizedBox(height: 16),
          const Divider(color: LunanceColors.borderLight),
          const SizedBox(height: 16),
          
          // Recommendations
          Text(
            'Rekomendasi AI',
            style: const TextStyle(
              fontSize: 14,
              fontWeight: FontWeight.bold,
              color: LunanceColors.primaryText,
            ),
          ),
          const SizedBox(height: 8),
          ...monthlyPrediction.recommendations.take(2).map(
            (recommendation) => Padding(
              padding: const EdgeInsets.only(bottom: 4),
              child: Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Container(
                    margin: const EdgeInsets.only(top: 6),
                    width: 4,
                    height: 4,
                    decoration: BoxDecoration(
                      color: LunanceColors.botAvatar,
                      borderRadius: BorderRadius.circular(2),
                    ),
                  ),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      recommendation,
                      style: const TextStyle(
                        fontSize: 12,
                        color: LunanceColors.secondaryText,
                        height: 1.4,
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildChartBar(String label, double value, Color color, double maxValue) {
    final percentage = (value / maxValue).clamp(0.0, 1.0);
    
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text(
              label,
              style: const TextStyle(
                fontSize: 12,
                color: LunanceColors.secondaryText,
                fontWeight: FontWeight.w500,
              ),
            ),
            Text(
              'Rp ${_formatCurrency(value)}',
              style: TextStyle(
                fontSize: 12,
                color: color,
                fontWeight: FontWeight.bold,
              ),
            ),
          ],
        ),
        const SizedBox(height: 4),
        Container(
          height: 8,
          decoration: BoxDecoration(
            color: LunanceColors.lightGray,
            borderRadius: BorderRadius.circular(4),
          ),
          child: FractionallySizedBox(
            alignment: Alignment.centerLeft,
            widthFactor: percentage,
            child: Container(
              decoration: BoxDecoration(
                color: color,
                borderRadius: BorderRadius.circular(4),
              ),
            ),
          ),
        ),
      ],
    );
  }

  String _formatCurrency(double amount) {
    if (amount >= 1000000) {
      return '${(amount / 1000000).toStringAsFixed(1)}M';
    } else if (amount >= 1000) {
      return '${(amount / 1000).toStringAsFixed(0)}K';
    }
    return amount.toStringAsFixed(0);
  }
}