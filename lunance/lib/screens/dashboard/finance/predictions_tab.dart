import 'package:flutter/material.dart';
import '../../../utils/app_colors.dart';
import '../../../utils/app_text_styles.dart';
import '../../../utils/format_eksplore.dart';
import '../../../widgets/custom_widgets.dart';
import '../../../widgets/common_widgets.dart';

class PredictionsTab extends StatefulWidget {
  const PredictionsTab({Key? key}) : super(key: key);

  @override
  State<PredictionsTab> createState() => _PredictionsTabState();
}

class _PredictionsTabState extends State<PredictionsTab> {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      body: Center(
        child: Padding(
          padding: const EdgeInsets.all(32),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Container(
                width: 120,
                height: 120,
                decoration: BoxDecoration(
                  color: AppColors.primary.withOpacity(0.1),
                  shape: BoxShape.circle,
                ),
                child: Icon(
                  Icons.trending_up_outlined,
                  size: 60,
                  color: AppColors.primary,
                ),
              ),
              
              const SizedBox(height: 32),
              
              Text(
                'Prediksi Keuangan',
                style: AppTextStyles.h5.copyWith(
                  fontWeight: FontWeight.w600,
                ),
                textAlign: TextAlign.center,
              ),
              
              const SizedBox(height: 16),
              
              Text(
                'Fitur prediksi keuangan sedang dalam pengembangan. Saat ini fokus pada tracking keuangan dengan metode 50/30/20.',
                style: AppTextStyles.bodyMedium.copyWith(
                  color: AppColors.textSecondary,
                  height: 1.5,
                ),
                textAlign: TextAlign.center,
              ),
              
              const SizedBox(height: 32),
              
              Container(
                padding: const EdgeInsets.all(20),
                decoration: BoxDecoration(
                  color: AppColors.info.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(16),
                  border: Border.all(
                    color: AppColors.info.withOpacity(0.3),
                  ),
                ),
                child: Column(
                  children: [
                    Text(
                      'Fitur yang Akan Datang',
                      style: AppTextStyles.labelLarge.copyWith(
                        color: AppColors.info,
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                    const SizedBox(height: 12),
                    Text(
                      '• Prediksi pengeluaran berdasarkan pola spending\n'
                      '• Estimasi waktu mencapai target tabungan\n'
                      '• Analisis tren keuangan bulanan\n'
                      '• Rekomendasi budget optimization',
                      style: AppTextStyles.bodySmall.copyWith(
                        color: AppColors.textSecondary,
                        height: 1.4,
                      ),
                    ),
                  ],
                ),
              ),
              
              const SizedBox(height: 32),
              
              TextButton(
                onPressed: () {
                  // Kembali ke Dashboard Tab
                  DefaultTabController.of(context)?.animateTo(0);
                },
                child: Text(
                  'Kembali ke Dashboard',
                  style: AppTextStyles.labelLarge.copyWith(
                    color: AppColors.primary,
                    fontWeight: FontWeight.w600,
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

// ===== REMOVED: SEMUA ENDPOINT CALLS =====
// - loadPredictions() (tidak dipakai karena endpoint tidak ada)
// - loadFinancialPredictions() (tidak dipakai karena endpoint tidak ada)
// - Semua logic yang bergantung pada data prediksi
// - Semua chart dan grafik prediksi