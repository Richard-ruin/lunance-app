import 'package:flutter/material.dart';
import '../../../../utils/app_colors.dart';
import '../../../../utils/app_text_styles.dart';
import '../../../../widgets/custom_widgets.dart';

class SavingsTips extends StatelessWidget {
  const SavingsTips({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return CustomCard(
      backgroundColor: AppColors.success.withOpacity(0.05),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _buildHeader(),
          const SizedBox(height: 16),
          
          // Tips List
          _buildTipItem(
            'Sisihkan 20% dari pemasukan setiap bulan',
            'Terapkan aturan 50/30/20: 50% kebutuhan, 30% keinginan, 20% tabungan',
            Icons.savings,
          ),
          const SizedBox(height: 12),
          
          _buildTipItem(
            'Kurangi pengeluaran untuk hiburan sebesar 10%',
            'Cari alternatif hiburan yang lebih murah atau gratis',
            Icons.trending_down,
          ),
          const SizedBox(height: 12),
          
          _buildTipItem(
            'Gunakan aplikasi e-wallet untuk tracking yang lebih baik',
            'Manfaatkan cashback dan promo dari berbagai platform digital',
            Icons.smartphone,
          ),
          const SizedBox(height: 12),
          
          _buildTipItem(
            'Otomatisasi tabungan dengan auto-debit',
            'Set up transfer otomatis ke rekening tabungan setiap gajian',
            Icons.autorenew,
          ),
          const SizedBox(height: 12),
          
          _buildTipItem(
            'Review dan evaluasi pengeluaran setiap minggu',
            'Analisis pola pengeluaran untuk menemukan area penghematan',
            Icons.analytics,
          ),
        ],
      ),
    );
  }

  Widget _buildHeader() {
    return Row(
      children: [
        Icon(
          Icons.lightbulb_outline,
          color: AppColors.success,
          size: 20,
        ),
        const SizedBox(width: 8),
        Text(
          'Tips Tabungan',
          style: AppTextStyles.labelLarge.copyWith(
            fontWeight: FontWeight.w600,
            color: AppColors.success,
          ),
        ),
      ],
    );
  }

  Widget _buildTipItem(String tip, String description, IconData icon) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: AppColors.white,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: AppColors.success.withOpacity(0.2)),
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Icon
          Container(
            width: 40,
            height: 40,
            decoration: BoxDecoration(
              color: AppColors.success.withOpacity(0.1),
              borderRadius: BorderRadius.circular(8),
            ),
            child: Icon(
              icon,
              color: AppColors.success,
              size: 20,
            ),
          ),
          const SizedBox(width: 12),
          
          // Content
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  tip,
                  style: AppTextStyles.labelMedium.copyWith(
                    fontWeight: FontWeight.w600,
                    color: AppColors.success,
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  description,
                  style: AppTextStyles.bodySmall.copyWith(
                    color: AppColors.textSecondary,
                  ),
                ),
              ],
            ),
          ),
          
          // Action Button
          InkWell(
            onTap: () {
              // Implementasi aksi tips (bookmark, share, dll)
            },
            borderRadius: BorderRadius.circular(20),
            child: Container(
              padding: const EdgeInsets.all(8),
              decoration: BoxDecoration(
                color: AppColors.success.withOpacity(0.1),
                borderRadius: BorderRadius.circular(20),
              ),
              child: Icon(
                Icons.bookmark_border,
                color: AppColors.success,
                size: 16,
              ),
            ),
          ),
        ],
      ),
    );
  }
}