import 'package:flutter/material.dart';
import '../../../../utils/app_colors.dart';
import '../../../../utils/app_text_styles.dart';
import '../../../../widgets/custom_widgets.dart';
import '../widgets/chart_containers.dart';
import '../widgets/prediction_card.dart';

class PredictionTab extends StatelessWidget {
  const PredictionTab({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(20),
      child: Column(
        children: [
          // AI Prediction Overview
          const PredictionCard(),
          const SizedBox(height: 20),
          
          // Future Prediction Chart
          CustomCard(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                _buildSectionHeader(
                  'Proyeksi Keuangan 6 Bulan',
                  Icons.insights,
                  AppColors.info,
                ),
                const SizedBox(height: 20),
                SizedBox(
                  height: 200,
                  child: ChartContainers.predictionChart(),
                ),
                const SizedBox(height: 16),
                _buildChartLegend(),
              ],
            ),
          ),
          const SizedBox(height: 20),
          
          // Savings Goal Predictions
          _buildSavingsGoalPredictions(),
          const SizedBox(height: 20),
          
          // Financial Health Score
          _buildFinancialHealthScore(),
          const SizedBox(height: 20),
          
          // Action Recommendations
          _buildActionRecommendations(),
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

  Widget _buildChartLegend() {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceEvenly,
      children: [
        _buildLegendItem('Pemasukan', AppColors.success),
        _buildLegendItem('Pengeluaran', AppColors.error),
        _buildLegendItem('Tabungan', AppColors.primary),
        _buildLegendItem('Prediksi', AppColors.warning),
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
        const SizedBox(width: 4),
        Text(
          label,
          style: AppTextStyles.caption.copyWith(
            color: AppColors.textSecondary,
          ),
        ),
      ],
    );
  }

  Widget _buildSavingsGoalPredictions() {
    return CustomCard(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _buildSectionHeader(
            'Prediksi Target Tabungan',
            Icons.timeline,
            AppColors.success,
          ),
          const SizedBox(height: 16),
          
          _buildGoalPredictionItem(
            'iPhone 15 Pro',
            'Rp 20.000.000',
            '7 bulan',
            'Feb 2026',
            AppColors.success,
            85,
          ),
          const SizedBox(height: 12),
          _buildGoalPredictionItem(
            'MacBook Pro',
            'Rp 26.000.000',
            '18 bulan',
            'Jan 2027',
            AppColors.warning,
            45,
          ),
          const SizedBox(height: 12),
          _buildGoalPredictionItem(
            'Liburan Bali',
            'Rp 5.000.000',
            '1 bulan',
            'Agu 2025',
            AppColors.success,
            95,
          ),
        ],
      ),
    );
  }

  Widget _buildGoalPredictionItem(
    String goal,
    String target,
    String timeLeft,
    String completionDate,
    Color color,
    int probability,
  ) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: color.withOpacity(0.05),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: color.withOpacity(0.2)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    goal,
                    style: AppTextStyles.labelMedium.copyWith(
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                  Text(
                    target,
                    style: AppTextStyles.caption.copyWith(
                      color: AppColors.textSecondary,
                    ),
                  ),
                ],
              ),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                decoration: BoxDecoration(
                  color: color.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(16),
                ),
                child: Text(
                  '$probability%',
                  style: AppTextStyles.caption.copyWith(
                    color: color,
                    fontWeight: FontWeight.w600,
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 8),
          Row(
            children: [
              Icon(
                Icons.schedule,
                size: 14,
                color: AppColors.textSecondary,
              ),
              const SizedBox(width: 4),
              Text(
                'Estimasi: $timeLeft ($completionDate)',
                style: AppTextStyles.caption.copyWith(
                  color: AppColors.textSecondary,
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildFinancialHealthScore() {
    return CustomCard(
      backgroundColor: AppColors.primary.withOpacity(0.05),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _buildSectionHeader(
            'Skor Kesehatan Finansial',
            Icons.favorite,
            AppColors.primary,
          ),
          const SizedBox(height: 20),
          
          Center(
            child: Column(
              children: [
                Container(
                  width: 120,
                  height: 120,
                  decoration: BoxDecoration(
                    shape: BoxShape.circle,
                    border: Border.all(
                      color: AppColors.success,
                      width: 8,
                    ),
                  ),
                  child: Center(
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Text(
                          '78',
                          style: AppTextStyles.h4.copyWith(
                            color: AppColors.success,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                        Text(
                          'BAIK',
                          style: AppTextStyles.caption.copyWith(
                            color: AppColors.success,
                            fontWeight: FontWeight.w600,
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
                const SizedBox(height: 16),
                Text(
                  'Keuangan Anda dalam kondisi baik',
                  style: AppTextStyles.labelMedium.copyWith(
                    fontWeight: FontWeight.w600,
                  ),
                ),
                const SizedBox(height: 8),
                Text(
                  'Tingkatkan skor dengan mengurangi pengeluaran\ndan meningkatkan tabungan darurat',
                  style: AppTextStyles.bodySmall.copyWith(
                    color: AppColors.textSecondary,
                  ),
                  textAlign: TextAlign.center,
                ),
              ],
            ),
          ),
          const SizedBox(height: 20),
          
          _buildHealthMetric('Rasio Tabungan', 25, 85, AppColors.success),
          const SizedBox(height: 12),
          _buildHealthMetric('Pengeluaran vs Pemasukan', 75, 70, AppColors.warning),
          const SizedBox(height: 12),
          _buildHealthMetric('Dana Darurat', 60, 80, AppColors.info),
        ],
      ),
    );
  }

  Widget _buildHealthMetric(String metric, int currentValue, int targetValue, Color color) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text(
              metric,
              style: AppTextStyles.bodyMedium.copyWith(
                fontWeight: FontWeight.w500,
              ),
            ),
            Text(
              '$currentValue%',
              style: AppTextStyles.labelMedium.copyWith(
                color: color,
                fontWeight: FontWeight.w600,
              ),
            ),
          ],
        ),
        const SizedBox(height: 4),
        ClipRRect(
          borderRadius: BorderRadius.circular(4),
          child: LinearProgressIndicator(
            value: currentValue / 100,
            backgroundColor: AppColors.gray200,
            valueColor: AlwaysStoppedAnimation<Color>(color),
            minHeight: 6,
          ),
        ),
      ],
    );
  }

  Widget _buildActionRecommendations() {
    return CustomCard(
      backgroundColor: AppColors.info.withOpacity(0.05),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _buildSectionHeader(
            'Rekomendasi Aksi',
            Icons.lightbulb_outline,
            AppColors.info,
          ),
          const SizedBox(height: 16),
          
          _buildRecommendationCard(
            'Prioritas Tinggi',
            [
              'Tambah dana darurat hingga 6x pengeluaran bulanan',
              'Kurangi pengeluaran makanan sebesar 15%',
              'Mulai investasi reksadana dengan Rp 500K/bulan',
            ],
            AppColors.error,
            Icons.priority_high,
          ),
          const SizedBox(height: 16),
          
          _buildRecommendationCard(
            'Prioritas Sedang',
            [
              'Optimalkan cashback dari kartu kredit',
              'Cari sumber pemasukan tambahan (freelance)',
              'Review dan negosiasi kontrak asuransi',
            ],
            AppColors.warning,
            Icons.low_priority,
          ),
          const SizedBox(height: 16),
          
          _buildRecommendationCard(
            'Jangka Panjang',
            [
              'Mulai planning untuk pembelian properti',
              'Diversifikasi portfolio investasi',
              'Siapkan dana pendidikan anak',
            ],
            AppColors.success,
            Icons.schedule,
          ),
        ],
      ),
    );
  }

  Widget _buildRecommendationCard(
    String title,
    List<String> recommendations,
    Color color,
    IconData icon,
  ) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: AppColors.white,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: color.withOpacity(0.2)),
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
              const SizedBox(width: 8),
              Text(
                title,
                style: AppTextStyles.labelMedium.copyWith(
                  color: color,
                  fontWeight: FontWeight.w600,
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          ...recommendations.map((rec) => Padding(
            padding: const EdgeInsets.only(bottom: 4),
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Container(
                  width: 4,
                  height: 4,
                  margin: const EdgeInsets.only(top: 6, right: 8),
                  decoration: BoxDecoration(
                    color: color,
                    shape: BoxShape.circle,
                  ),
                ),
                Expanded(
                  child: Text(
                    rec,
                    style: AppTextStyles.bodySmall.copyWith(
                      color: AppColors.textSecondary,
                    ),
                  ),
                ),
              ],
            ),
          )),
        ],
      ),
    );
  }
}