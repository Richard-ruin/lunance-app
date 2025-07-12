import 'package:flutter/material.dart';
import '../../../../utils/app_colors.dart';
import '../../../../utils/app_text_styles.dart';
import '../../../../widgets/custom_widgets.dart';

class PredictionCard extends StatelessWidget {
  const PredictionCard({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return CustomCard(
      backgroundColor: AppColors.primary.withOpacity(0.05),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _buildHeader(),
          const SizedBox(height: 16),
          
          _buildMainPrediction(),
          const SizedBox(height: 16),
          
          _buildPredictionsList(),
        ],
      ),
    );
  }

  Widget _buildHeader() {
    return Row(
      children: [
        Container(
          padding: const EdgeInsets.all(8),
          decoration: BoxDecoration(
            color: AppColors.primary.withOpacity(0.1),
            borderRadius: BorderRadius.circular(8),
          ),
          child: Icon(
            Icons.auto_graph,
            color: AppColors.primary,
            size: 20,
          ),
        ),
        const SizedBox(width: 12),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                'Prediksi Keuangan AI',
                style: AppTextStyles.labelLarge.copyWith(
                  fontWeight: FontWeight.w600,
                  color: AppColors.primary,
                ),
              ),
              Text(
                'Analisis berdasarkan pola 6 bulan terakhir',
                style: AppTextStyles.caption.copyWith(
                  color: AppColors.textSecondary,
                ),
              ),
            ],
          ),
        ),
        Container(
          padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
          decoration: BoxDecoration(
            color: AppColors.success.withOpacity(0.1),
            borderRadius: BorderRadius.circular(12),
          ),
          child: Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              Container(
                width: 6,
                height: 6,
                decoration: BoxDecoration(
                  color: AppColors.success,
                  shape: BoxShape.circle,
                ),
              ),
              const SizedBox(width: 4),
              Text(
                'Akurat 87%',
                style: AppTextStyles.caption.copyWith(
                  color: AppColors.success,
                  fontWeight: FontWeight.w600,
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildMainPrediction() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: AppColors.white,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: AppColors.primary.withOpacity(0.2)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(
                Icons.trending_up,
                color: AppColors.success,
                size: 16,
              ),
              const SizedBox(width: 8),
              Text(
                'Prediksi 3 Bulan Ke Depan',
                style: AppTextStyles.labelMedium.copyWith(
                  fontWeight: FontWeight.w600,
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          
          _buildPredictionMetric(
            'Pemasukan',
            'Rp 5.460.000',
            '+5%',
            AppColors.success,
            'Berdasarkan tren kenaikan freelance',
          ),
          const SizedBox(height: 8),
          
          _buildPredictionMetric(
            'Pengeluaran',
            'Rp 4.290.000',
            '+10%',
            AppColors.warning,
            'Kenaikan kategori makanan & transport',
          ),
          const SizedBox(height: 8),
          
          _buildPredictionMetric(
            'Net Surplus',
            'Rp 1.170.000',
            '-12%',
            AppColors.error,
            'Perlu optimasi pengeluaran',
          ),
        ],
      ),
    );
  }

  Widget _buildPredictionMetric(
    String label,
    String amount,
    String change,
    Color color,
    String note,
  ) {
    return Row(
      children: [
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                label,
                style: AppTextStyles.bodySmall.copyWith(
                  color: AppColors.textSecondary,
                ),
              ),
              Text(
                amount,
                style: AppTextStyles.labelMedium.copyWith(
                  fontWeight: FontWeight.w600,
                ),
              ),
              Text(
                note,
                style: AppTextStyles.caption.copyWith(
                  color: AppColors.textTertiary,
                ),
              ),
            ],
          ),
        ),
        Container(
          padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
          decoration: BoxDecoration(
            color: color.withOpacity(0.1),
            borderRadius: BorderRadius.circular(12),
          ),
          child: Text(
            change,
            style: AppTextStyles.caption.copyWith(
              color: color,
              fontWeight: FontWeight.w600,
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildPredictionsList() {
    final predictions = [
      {
        'title': 'Target iPhone bisa tercapai dalam 8 bulan',
        'subtitle': 'Dengan pola tabungan saat ini',
        'icon': Icons.phone_iphone,
        'color': AppColors.success,
        'confidence': '92%',
      },
      {
        'title': 'Pengeluaran makanan cenderung naik 10%',
        'subtitle': 'Disarankan untuk meal prep lebih sering',
        'icon': Icons.restaurant,
        'color': AppColors.warning,
        'confidence': '78%',
      },
      {
        'title': 'Potensi pemasukan freelance +25%',
        'subtitle': 'Berdasarkan permintaan pasar Q3-Q4',
        'icon': Icons.laptop_mac,
        'color': AppColors.info,
        'confidence': '65%',
      },
      {
        'title': 'Dana darurat masih kurang optimal',
        'subtitle': 'Perlu tambahan Rp 2.4M untuk 6x pengeluaran',
        'icon': Icons.security,
        'color': AppColors.error,
        'confidence': '95%',
      },
    ];

    return Column(
      children: predictions.map((prediction) {
        return Container(
          margin: const EdgeInsets.only(bottom: 12),
          padding: const EdgeInsets.all(12),
          decoration: BoxDecoration(
            color: AppColors.white,
            borderRadius: BorderRadius.circular(8),
            border: Border.all(
              color: (prediction['color'] as Color).withOpacity(0.2),
            ),
          ),
          child: Row(
            children: [
              Container(
                width: 32,
                height: 32,
                decoration: BoxDecoration(
                  color: (prediction['color'] as Color).withOpacity(0.1),
                  borderRadius: BorderRadius.circular(6),
                ),
                child: Icon(
                  prediction['icon'] as IconData,
                  color: prediction['color'] as Color,
                  size: 16,
                ),
              ),
              const SizedBox(width: 12),
              
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      prediction['title'] as String,
                      style: AppTextStyles.bodySmall.copyWith(
                        fontWeight: FontWeight.w500,
                        color: prediction['color'] as Color,
                      ),
                    ),
                    Text(
                      prediction['subtitle'] as String,
                      style: AppTextStyles.caption.copyWith(
                        color: AppColors.textSecondary,
                      ),
                    ),
                  ],
                ),
              ),
              
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                decoration: BoxDecoration(
                  color: (prediction['color'] as Color).withOpacity(0.1),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Text(
                  prediction['confidence'] as String,
                  style: AppTextStyles.caption.copyWith(
                    color: prediction['color'] as Color,
                    fontWeight: FontWeight.w600,
                  ),
                ),
              ),
            ],
          ),
        );
      }).toList(),
    );
  }
}