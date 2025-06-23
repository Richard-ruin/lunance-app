// lib/features/dashboard/presentation/widgets/financial_card.dart
import 'package:flutter/material.dart';
import '../../../../core/theme/lunance_colors.dart';

class FinancialCard extends StatelessWidget {
  final String title;
  final String amount;
  final String subtitle;
  final IconData icon;
  final Color color;
  final bool isIncome;
  final VoidCallback? onTap;

  const FinancialCard({
    Key? key,
    required this.title,
    required this.amount,
    required this.subtitle,
    required this.icon,
    required this.color,
    this.isIncome = false,
    this.onTap,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.all(20),
        decoration: BoxDecoration(
          color: LunanceColors.cardBackground,
          borderRadius: BorderRadius.circular(16),
          border: Border.all(
            color: color.withOpacity(0.2),
            width: 1.5,
          ),
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
                Container(
                  padding: const EdgeInsets.all(8),
                  decoration: BoxDecoration(
                    color: color.withOpacity(0.1),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Icon(
                    icon,
                    color: color,
                    size: 20,
                  ),
                ),
                const Spacer(),
                if (isIncome)
                  Icon(
                    Icons.trending_up,
                    color: LunanceColors.incomeGreen,
                    size: 16,
                  )
                else
                  Icon(
                    Icons.trending_down,
                    color: LunanceColors.expenseRed,
                    size: 16,
                  ),
              ],
            ),
            const SizedBox(height: 12),
            Text(
              title,
              style: const TextStyle(
                fontSize: 12,
                color: LunanceColors.secondaryText,
                fontWeight: FontWeight.w500,
              ),
            ),
            const SizedBox(height: 4),
            Text(
              amount,
              style: TextStyle(
                fontSize: 18,
                color: LunanceColors.primaryText,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 4),
            Text(
              subtitle,
              style: const TextStyle(
                fontSize: 11,
                color: LunanceColors.lightText,
              ),
            ),
          ],
        ),
      ),
    );
  }
}