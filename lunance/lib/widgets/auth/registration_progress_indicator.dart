import 'package:flutter/material.dart';
import '../../themes/app_theme.dart';

class RegistrationProgressIndicator extends StatelessWidget {
  final int currentStep;
  final int totalSteps;

  const RegistrationProgressIndicator({
    super.key,
    required this.currentStep,
    required this.totalSteps,
  });

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;

    return Container(
      padding: const EdgeInsets.all(AppTheme.spacingM),
      decoration: BoxDecoration(
        color: colorScheme.surface,
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.05),
            blurRadius: 4,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Column(
        children: [
          // Step indicators
          Row(
            children: List.generate(totalSteps, (index) {
              final stepNumber = index + 1;
              final isCompleted = stepNumber < currentStep;
              final isCurrent = stepNumber == currentStep;
              
              return Expanded(
                child: Row(
                  children: [
                    // Step circle
                    Container(
                      width: 32,
                      height: 32,
                      decoration: BoxDecoration(
                        shape: BoxShape.circle,
                        color: isCompleted
                            ? colorScheme.primary
                            : isCurrent
                                ? colorScheme.primaryContainer
                                : colorScheme.outline.withOpacity(0.3),
                      ),
                      child: Center(
                        child: isCompleted
                            ? Icon(
                                Icons.check,
                                size: 16,
                                color: colorScheme.onPrimary,
                              )
                            : Text(
                                stepNumber.toString(),
                                style: Theme.of(context).textTheme.labelMedium?.copyWith(
                                  color: isCurrent
                                      ? colorScheme.onPrimaryContainer
                                      : colorScheme.onSurfaceVariant,
                                  fontWeight: FontWeight.w600,
                                ),
                              ),
                      ),
                    ),
                    
                    // Connecting line (except for last step)
                    if (index < totalSteps - 1)
                      Expanded(
                        child: Container(
                          height: 2,
                          margin: const EdgeInsets.symmetric(horizontal: AppTheme.spacingS),
                          decoration: BoxDecoration(
                            color: isCompleted
                                ? colorScheme.primary
                                : colorScheme.outline.withOpacity(0.3),
                            borderRadius: BorderRadius.circular(1),
                          ),
                        ),
                      ),
                  ],
                ),
              );
            }),
          ),
          
          const SizedBox(height: AppTheme.spacingM),
          
          // Step labels
          Row(
            children: [
              Expanded(
                child: Text(
                  'Data Pribadi',
                  style: Theme.of(context).textTheme.bodySmall?.copyWith(
                    fontWeight: currentStep == 1 ? FontWeight.w600 : FontWeight.normal,
                    color: currentStep == 1
                        ? colorScheme.primary
                        : colorScheme.onSurfaceVariant,
                  ),
                  textAlign: TextAlign.center,
                ),
              ),
              Expanded(
                child: Text(
                  'Data Akademik',
                  style: Theme.of(context).textTheme.bodySmall?.copyWith(
                    fontWeight: currentStep == 2 ? FontWeight.w600 : FontWeight.normal,
                    color: currentStep == 2
                        ? colorScheme.primary
                        : colorScheme.onSurfaceVariant,
                  ),
                  textAlign: TextAlign.center,
                ),
              ),
              Expanded(
                child: Text(
                  'Verifikasi',
                  style: Theme.of(context).textTheme.bodySmall?.copyWith(
                    fontWeight: currentStep == 3 ? FontWeight.w600 : FontWeight.normal,
                    color: currentStep == 3
                        ? colorScheme.primary
                        : colorScheme.onSurfaceVariant,
                  ),
                  textAlign: TextAlign.center,
                ),
              ),
              Expanded(
                child: Text(
                  'Tabungan',
                  style: Theme.of(context).textTheme.bodySmall?.copyWith(
                    fontWeight: currentStep == 4 ? FontWeight.w600 : FontWeight.normal,
                    color: currentStep == 4
                        ? colorScheme.primary
                        : colorScheme.onSurfaceVariant,
                  ),
                  textAlign: TextAlign.center,
                ),
              ),
              Expanded(
                child: Text(
                  'Selesai',
                  style: Theme.of(context).textTheme.bodySmall?.copyWith(
                    fontWeight: currentStep == 5 ? FontWeight.w600 : FontWeight.normal,
                    color: currentStep == 5
                        ? colorScheme.primary
                        : colorScheme.onSurfaceVariant,
                  ),
                  textAlign: TextAlign.center,
                ),
              ),
            ],
          ),
          
          const SizedBox(height: AppTheme.spacingS),
          
          // Progress bar
          LinearProgressIndicator(
            value: currentStep / totalSteps,
            backgroundColor: colorScheme.outline.withOpacity(0.3),
            valueColor: AlwaysStoppedAnimation<Color>(colorScheme.primary),
          ),
        ],
      ),
    );
  }
}