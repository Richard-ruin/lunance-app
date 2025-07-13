import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:fl_chart/fl_chart.dart';
import '../../../providers/finance_provider.dart';
import '../../../utils/app_colors.dart';
import '../../../utils/app_text_styles.dart';
import '../../../utils/format_utils.dart';
import '../../../widgets/custom_widgets.dart';
import '../../../widgets/common_widgets.dart';
// Add this import

class PredictionsTab extends StatefulWidget {
  const PredictionsTab({Key? key}) : super(key: key);

  @override
  State<PredictionsTab> createState() => _PredictionsTabState();
}

class _PredictionsTabState extends State<PredictionsTab> {
  int _selectedDays = 30;
  String _selectedType = 'both';
  bool _isInitialized = false;

  final List<int> _dayOptions = [7, 14, 30, 60, 90];
  final List<String> _typeOptions = ['both', 'income', 'expense'];

  @override
  void initState() {
    super.initState();
    // Use addPostFrameCallback to avoid setState during build
    WidgetsBinding.instance.addPostFrameCallback((_) {
      _loadPredictions();
    });
  }

  Future<void> _loadPredictions() async {
    if (mounted) {
      final financeProvider =
          Provider.of<FinanceProvider>(context, listen: false);
      await financeProvider.loadFinancialPredictions(
        daysAhead: _selectedDays,
        type: _selectedType,
      );

      if (mounted) {
        setState(() {
          _isInitialized = true;
        });
      }
    }
  }

  String _getTypeDisplayName(String type) {
    switch (type) {
      case 'income':
        return 'Pemasukan';
      case 'expense':
        return 'Pengeluaran';
      case 'both':
        return 'Keduanya';
      default:
        return type;
    }
  }

  @override
  Widget build(BuildContext context) {
    return RefreshIndicator(
      onRefresh: _loadPredictions,
      child: SingleChildScrollView(
        physics: const AlwaysScrollableScrollPhysics(),
        padding: const EdgeInsets.all(24),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Prediction Settings
            _buildPredictionSettings(),

            const SizedBox(height: 24),

            // Prediction Results
            _buildPredictionResults(),

            const SizedBox(height: 24),

            // Prediction Chart
            _buildPredictionChart(),

            const SizedBox(height: 24),

            _buildPredictionInsights(),

            const SizedBox(height: 24),

            _buildRecommendations(),

            const SizedBox(height: 24),

            // Insights and Recommendations
          ],
        ),
      ),
    );
  }

  Widget _buildPredictionSettings() {
    return CustomCard(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(
                Icons.settings_outlined,
                color: AppColors.primary,
                size: 20,
              ),
              const SizedBox(width: 8),
              Text(
                'Pengaturan Prediksi',
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
                      'Periode Prediksi',
                      style: AppTextStyles.bodySmall.copyWith(
                        color: AppColors.textSecondary,
                        fontWeight: FontWeight.w500,
                      ),
                    ),
                    const SizedBox(height: 8),
                    Container(
                      width: double.infinity,
                      padding: const EdgeInsets.symmetric(
                          horizontal: 12, vertical: 8),
                      decoration: BoxDecoration(
                        border: Border.all(color: AppColors.border),
                        borderRadius: BorderRadius.circular(8),
                      ),
                      child: DropdownButtonHideUnderline(
                        child: DropdownButton<int>(
                          value: _selectedDays,
                          isExpanded: true,
                          style: AppTextStyles.bodyMedium,
                          onChanged: (value) {
                            if (value != null) {
                              setState(() {
                                _selectedDays = value;
                              });
                              _loadPredictions();
                            }
                          },
                          items: _dayOptions.map((days) {
                            return DropdownMenuItem(
                              value: days,
                              child: Text('$days hari ke depan'),
                            );
                          }).toList(),
                        ),
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(width: 16),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Jenis Prediksi',
                      style: AppTextStyles.bodySmall.copyWith(
                        color: AppColors.textSecondary,
                        fontWeight: FontWeight.w500,
                      ),
                    ),
                    const SizedBox(height: 8),
                    Container(
                      width: double.infinity,
                      padding: const EdgeInsets.symmetric(
                          horizontal: 12, vertical: 8),
                      decoration: BoxDecoration(
                        border: Border.all(color: AppColors.border),
                        borderRadius: BorderRadius.circular(8),
                      ),
                      child: DropdownButtonHideUnderline(
                        child: DropdownButton<String>(
                          value: _selectedType,
                          isExpanded: true,
                          style: AppTextStyles.bodyMedium,
                          onChanged: (value) {
                            if (value != null) {
                              setState(() {
                                _selectedType = value;
                              });
                              _loadPredictions();
                            }
                          },
                          items: _typeOptions.map((type) {
                            return DropdownMenuItem(
                              value: type,
                              child: Text(_getTypeDisplayName(type)),
                            );
                          }).toList(),
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: AppColors.info.withOpacity(0.1),
              borderRadius: BorderRadius.circular(8),
              border: Border.all(
                color: AppColors.info.withOpacity(0.3),
              ),
            ),
            child: Row(
              children: [
                Icon(
                  Icons.info_outline,
                  color: AppColors.info,
                  size: 16,
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: Text(
                    'Prediksi berdasarkan data historis menggunakan model Prophet',
                    style: AppTextStyles.bodySmall.copyWith(
                      color: AppColors.info,
                    ),
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildPredictionResults() {
    return Consumer<FinanceProvider>(
      builder: (context, financeProvider, child) {
        if (financeProvider.isLoadingPredictions) {
          return _buildLoadingCard(height: 200);
        }

        if (financeProvider.predictionsError != null) {
          return ErrorMessage(
            message: financeProvider.predictionsError!,
            onRetry: _loadPredictions,
          );
        }

        final predictionsData = financeProvider.predictionsData;
        if (predictionsData == null) {
          return const EmptyStateWidget(
            icon: Icons.trending_up,
            title: 'Tidak ada data prediksi',
            subtitle: 'Data historis tidak mencukupi untuk prediksi',
          );
        }

        final predictions = predictionsData['predictions'] ?? {};
        final netPredictions =
            predictionsData['net_balance_predictions'] as List? ?? [];
        final summary = predictionsData['summary'] ?? {};

        return CustomCard(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Icon(
                    Icons.trending_up,
                    color: AppColors.success,
                    size: 20,
                  ),
                  const SizedBox(width: 8),
                  Text(
                    'Hasil Prediksi',
                    style: AppTextStyles.labelLarge.copyWith(
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                ],
              ),

              const SizedBox(height: 16),

              // Summary cards
              if (predictions.isNotEmpty) ...[
                Row(
                  children: [
                    if (predictions['income'] != null) ...[
                      Expanded(
                        child: _buildPredictionSummaryCard(
                          'Total Pemasukan',
                          predictions['income']['total_predicted'] ?? 0,
                          Icons.trending_up,
                          AppColors.success,
                        ),
                      ),
                      const SizedBox(width: 12),
                    ],
                    if (predictions['expense'] != null) ...[
                      Expanded(
                        child: _buildPredictionSummaryCard(
                          'Total Pengeluaran',
                          predictions['expense']['total_predicted'] ?? 0,
                          Icons.trending_down,
                          AppColors.error,
                        ),
                      ),
                    ],
                  ],
                ),
                if (netPredictions.isNotEmpty) ...[
                  const SizedBox(height: 12),
                  _buildNetBalanceSummary(netPredictions),
                ],
              ],

              const SizedBox(height: 16),

              // Prediction period info
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: AppColors.gray50,
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Detail Prediksi',
                      style: AppTextStyles.labelSmall.copyWith(
                        fontWeight: FontWeight.w600,
                        color: AppColors.textSecondary,
                      ),
                    ),
                    const SizedBox(height: 8),
                    Row(
                      children: [
                        Icon(
                          Icons.calendar_today,
                          size: 14,
                          color: AppColors.textTertiary,
                        ),
                        const SizedBox(width: 6),
                        Text(
                          'Periode: ${summary['prediction_period'] ?? 'N/A'}',
                          style: AppTextStyles.bodySmall.copyWith(
                            color: AppColors.textSecondary,
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 4),
                    Row(
                      children: [
                        Icon(
                          Icons.data_usage,
                          size: 14,
                          color: AppColors.textTertiary,
                        ),
                        const SizedBox(width: 6),
                        Text(
                          'Data historis: ${summary['historical_data_period'] ?? 'N/A'}',
                          style: AppTextStyles.bodySmall.copyWith(
                            color: AppColors.textSecondary,
                          ),
                        ),
                      ],
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

  Widget _buildPredictionChart() {
    return Consumer<FinanceProvider>(
      builder: (context, financeProvider, child) {
        if (financeProvider.isLoadingPredictions) {
          return _buildLoadingCard(height: 300);
        }

        final predictionsData = financeProvider.predictionsData;
        if (predictionsData == null) return Container();

        final netPredictions =
            predictionsData['net_balance_predictions'] as List? ?? [];

        if (netPredictions.isEmpty) {
          return CustomCard(
            child: SizedBox(
              height: 250,
              child: Center(
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Icon(
                      Icons.show_chart,
                      size: 48,
                      color: AppColors.gray400,
                    ),
                    const SizedBox(height: 8),
                    Text(
                      'Tidak ada data chart prediksi',
                      style: AppTextStyles.bodyMedium.copyWith(
                        color: AppColors.textSecondary,
                      ),
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
                    Icons.show_chart,
                    color: AppColors.primary,
                    size: 20,
                  ),
                  const SizedBox(width: 8),
                  Text(
                    'Grafik Prediksi Saldo Bersih',
                    style: AppTextStyles.labelLarge.copyWith(
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 20),
              SizedBox(
                height: 250,
                child: LineChart(
                  LineChartData(
                    gridData: FlGridData(
                      show: true,
                      drawHorizontalLine: true,
                      drawVerticalLine: false,
                      horizontalInterval: 500000,
                      getDrawingHorizontalLine: (value) {
                        return FlLine(
                          color: AppColors.gray200,
                          strokeWidth: 1,
                        );
                      },
                    ),
                    titlesData: FlTitlesData(
                      leftTitles: AxisTitles(
                        sideTitles: SideTitles(
                          showTitles: true,
                          interval: 500000,
                          getTitlesWidget: (value, meta) {
                            return Text(
                              FormatUtils.formatCompactNumber(value),
                              style: AppTextStyles.caption.copyWith(
                                color: AppColors.textTertiary,
                              ),
                            );
                          },
                        ),
                      ),
                      bottomTitles: AxisTitles(
                        sideTitles: SideTitles(
                          showTitles: true,
                          interval: 5,
                          getTitlesWidget: (value, meta) {
                            if (value.toInt() >= 0 &&
                                value.toInt() < netPredictions.length) {
                              final item = netPredictions[value.toInt()];
                              final date =
                                  item['formatted_date'] as String? ?? '';
                              return Padding(
                                padding: const EdgeInsets.only(top: 8),
                                child: Text(
                                  date.split(' ').first, // Show only day
                                  style: AppTextStyles.caption.copyWith(
                                    color: AppColors.textTertiary,
                                  ),
                                ),
                              );
                            }
                            return const Text('');
                          },
                        ),
                      ),
                      topTitles:
                          AxisTitles(sideTitles: SideTitles(showTitles: false)),
                      rightTitles:
                          AxisTitles(sideTitles: SideTitles(showTitles: false)),
                    ),
                    borderData: FlBorderData(show: false),
                    lineBarsData: [
                      LineChartBarData(
                        spots: netPredictions.asMap().entries.map((entry) {
                          final index = entry.key.toDouble();
                          final data = entry.value;
                          final netAmount =
                              (data['predicted_net'] as num?)?.toDouble() ?? 0;
                          return FlSpot(index, netAmount);
                        }).toList(),
                        isCurved: true,
                        color: AppColors.primary,
                        barWidth: 3,
                        dotData: FlDotData(
                          show: true,
                          getDotPainter: (spot, percent, barData, index) {
                            return FlDotCirclePainter(
                              radius: 3,
                              color: AppColors.primary,
                              strokeWidth: 2,
                              strokeColor: AppColors.white,
                            );
                          },
                        ),
                        belowBarData: BarAreaData(
                          show: true,
                          color: AppColors.primary.withOpacity(0.1),
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ],
          ),
        );
      },
    );
  }

  Widget _buildPredictionInsights() {
    return Consumer<FinanceProvider>(
      builder: (context, financeProvider, child) {
        final predictionsData = financeProvider.predictionsData;
        if (predictionsData == null) return Container();

        final netPredictions =
            predictionsData['net_balance_predictions'] as List? ?? [];

        if (netPredictions.isEmpty) {
          return CustomCard(
            child: Column(
              children: [
                Icon(
                  Icons.insights,
                  size: 48,
                  color: AppColors.gray400,
                ),
                const SizedBox(height: 8),
                Text(
                  'Tidak ada insight',
                  style: AppTextStyles.bodyMedium.copyWith(
                    color: AppColors.textSecondary,
                  ),
                ),
              ],
            ),
          );
        }

        // Calculate insights
        final positiveCount = netPredictions
            .where((p) => (p['predicted_net'] as num? ?? 0) > 0)
            .length;
        final negativeCount = netPredictions.length - positiveCount;

        final totalPredictedNet = netPredictions.fold<double>(0,
            (sum, p) => sum + ((p['predicted_net'] as num?)?.toDouble() ?? 0));

        final averageDailyNet = totalPredictedNet / netPredictions.length;

        return CustomCard(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Icon(
                    Icons.insights,
                    color: AppColors.info,
                    size: 20,
                  ),
                  const SizedBox(width: 8),
                  Text(
                    'Insight Prediksi',
                    style: AppTextStyles.labelLarge.copyWith(
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 16),
              _buildInsightItem(
                'Hari dengan surplus',
                '$positiveCount dari ${netPredictions.length} hari',
                positiveCount > negativeCount
                    ? Icons.trending_up
                    : Icons.trending_down,
                positiveCount > negativeCount
                    ? AppColors.success
                    : AppColors.warning,
              ),
              const SizedBox(height: 12),
              _buildInsightItem(
                'Rata-rata harian',
                FormatUtils.formatCurrency(averageDailyNet),
                averageDailyNet >= 0
                    ? Icons.add_circle_outline
                    : Icons.remove_circle_outline,
                averageDailyNet >= 0 ? AppColors.success : AppColors.error,
              ),
              const SizedBox(height: 12),
              _buildInsightItem(
                'Total prediksi',
                FormatUtils.formatCurrency(totalPredictedNet),
                totalPredictedNet >= 0
                    ? Icons.account_balance_wallet
                    : Icons.warning,
                totalPredictedNet >= 0 ? AppColors.primary : AppColors.warning,
              ),
            ],
          ),
        );
      },
    );
  }

  Widget _buildRecommendations() {
    return Consumer<FinanceProvider>(
      builder: (context, financeProvider, child) {
        final predictionsData = financeProvider.predictionsData;
        if (predictionsData == null) return Container();

        final netPredictions =
            predictionsData['net_balance_predictions'] as List? ?? [];

        if (netPredictions.isEmpty) {
          return CustomCard(
            child: Column(
              children: [
                Icon(
                  Icons.lightbulb_outline,
                  size: 48,
                  color: AppColors.gray400,
                ),
                const SizedBox(height: 8),
                Text(
                  'Tidak ada rekomendasi',
                  style: AppTextStyles.bodyMedium.copyWith(
                    color: AppColors.textSecondary,
                  ),
                ),
              ],
            ),
          );
        }

        // Generate recommendations based on predictions
        final totalPredictedNet = netPredictions.fold<double>(0,
            (sum, p) => sum + ((p['predicted_net'] as num?)?.toDouble() ?? 0));

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
                    'Rekomendasi',
                    style: AppTextStyles.labelLarge.copyWith(
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 16),
              if (totalPredictedNet > 0) ...[
                _buildRecommendationItem(
                  '💰',
                  'Surplus Diperkirakan',
                  'Pertimbangkan untuk menambah tabungan atau investasi.',
                  AppColors.success,
                ),
              ] else ...[
                _buildRecommendationItem(
                  '⚠️',
                  'Defisit Diperkirakan',
                  'Perlu mengurangi pengeluaran atau mencari pemasukan tambahan.',
                  AppColors.warning,
                ),
              ],
              const SizedBox(height: 12),
              _buildRecommendationItem(
                '📊',
                'Monitor Reguler',
                'Pantau perkembangan keuangan secara berkala untuk akurasi prediksi.',
                AppColors.info,
              ),
              const SizedBox(height: 12),
              _buildRecommendationItem(
                '🎯',
                'Sesuaikan Target',
                'Review dan sesuaikan target tabungan berdasarkan prediksi ini.',
                AppColors.primary,
              ),
            ],
          ),
        );
      },
    );
  }

  Widget _buildPredictionSummaryCard(
      String title, double amount, IconData icon, Color color) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
          color: color.withOpacity(0.3),
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(
                icon,
                color: color,
                size: 16,
              ),
              const SizedBox(width: 6),
              Text(
                title,
                style: AppTextStyles.bodySmall.copyWith(
                  color: color,
                  fontWeight: FontWeight.w500,
                ),
              ),
            ],
          ),
          const SizedBox(height: 8),
          Text(
            FormatUtils.formatCurrency(amount),
            style: AppTextStyles.labelLarge.copyWith(
              color: color,
              fontWeight: FontWeight.w600,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildNetBalanceSummary(List netPredictions) {
    final totalNet = netPredictions.fold<double>(
        0, (sum, p) => sum + ((p['predicted_net'] as num?)?.toDouble() ?? 0));

    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: totalNet >= 0
            ? AppColors.success.withOpacity(0.1)
            : AppColors.error.withOpacity(0.1),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
          color: totalNet >= 0
              ? AppColors.success.withOpacity(0.3)
              : AppColors.error.withOpacity(0.3),
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.center,
        children: [
          Icon(
            totalNet >= 0 ? Icons.trending_up : Icons.trending_down,
            color: totalNet >= 0 ? AppColors.success : AppColors.error,
            size: 24,
          ),
          const SizedBox(height: 8),
          Text(
            'Prediksi Saldo Bersih',
            style: AppTextStyles.bodySmall.copyWith(
              color: AppColors.textSecondary,
            ),
          ),
          const SizedBox(height: 4),
          Text(
            FormatUtils.formatCurrency(totalNet),
            style: AppTextStyles.h6.copyWith(
              color: totalNet >= 0 ? AppColors.success : AppColors.error,
              fontWeight: FontWeight.w700,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildInsightItem(
      String label, String value, IconData icon, Color color) {
    return Row(
      children: [
        Icon(
          icon,
          color: color,
          size: 16,
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
            color: color,
            fontWeight: FontWeight.w600,
          ),
        ),
      ],
    );
  }

  Widget _buildRecommendationItem(
      String emoji, String title, String description, Color color) {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: color.withOpacity(0.05),
        borderRadius: BorderRadius.circular(8),
        border: Border.all(
          color: color.withOpacity(0.2),
        ),
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            emoji,
            style: const TextStyle(fontSize: 16),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  title,
                  style: AppTextStyles.labelMedium.copyWith(
                    color: color,
                    fontWeight: FontWeight.w600,
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  description,
                  style: AppTextStyles.bodySmall.copyWith(
                    color: AppColors.textSecondary,
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
