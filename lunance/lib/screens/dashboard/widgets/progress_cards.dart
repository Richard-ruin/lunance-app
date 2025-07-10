import 'package:flutter/material.dart';
import '../../../utils/app_colors.dart';
import '../../../utils/app_text_styles.dart';
import '../../../widgets/custom_widgets.dart';

class ProgressCards extends StatefulWidget {
  const ProgressCards({Key? key}) : super(key: key);

  @override
  State<ProgressCards> createState() => _ProgressCardsState();
}

class _ProgressCardsState extends State<ProgressCards> 
    with TickerProviderStateMixin {
  
  late AnimationController _animationController;
  late List<Animation<double>> _progressAnimations;

  // Mock progress data
  final List<ProgressGoal> _goals = [
    ProgressGoal(
      id: '1',
      icon: Icons.track_changes,
      title: 'Monthly Auto-Target',
      subtitle: 'Auto-calculated from income',
      current: 800000,
      target: 1000000,
      color: AppColors.primary,
      type: GoalType.monthly,
    ),
    ProgressGoal(
      id: '2',
      icon: Icons.phone_iphone,
      title: 'iPhone 15 Pro',
      subtitle: 'Target: Dec 2025',
      current: 13000000,
      target: 20000000,
      color: AppColors.success,
      type: GoalType.purchase,
    ),
    ProgressGoal(
      id: '3',
      icon: Icons.laptop_mac,
      title: 'MacBook Pro',
      subtitle: 'Target: Mar 2026',
      current: 6000000,
      target: 26000000,
      color: AppColors.warning,
      type: GoalType.purchase,
    ),
    ProgressGoal(
      id: '4',
      icon: Icons.flight,
      title: 'Vacation to Japan',
      subtitle: 'Target: Jul 2025',
      current: 8500000,
      target: 15000000,
      color: AppColors.info,
      type: GoalType.vacation,
    ),
  ];

  @override
  void initState() {
    super.initState();
    
    _animationController = AnimationController(
      duration: const Duration(milliseconds: 2000),
      vsync: this,
    );
    
    // Create progress bar animations for each goal
    _progressAnimations = _goals.map((goal) {
      final percentage = goal.current / goal.target;
      return Tween<double>(
        begin: 0.0,
        end: percentage,
      ).animate(CurvedAnimation(
        parent: _animationController,
        curve: const Interval(0.3, 1.0, curve: Curves.easeOutCubic),
      ));
    }).toList();
    
    // Start animation after a short delay
    Future.delayed(const Duration(milliseconds: 500), () {
      if (mounted) {
        _animationController.forward();
      }
    });
  }

  @override
  void dispose() {
    _animationController.dispose();
    super.dispose();
  }

  String _formatCurrency(double amount) {
    return 'Rp ${amount.toInt().toString().replaceAllMapped(
      RegExp(r'(\d{1,3})(?=(\d{3})+(?!\d))'),
      (Match m) => '${m[1]}.',
    )}';
  }

  void _showComingSoonDialog(String feature) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(16),
        ),
        title: Text(
          feature,
          style: AppTextStyles.h6,
        ),
        content: Text(
          'Fitur $feature akan segera tersedia dalam update mendatang.',
          style: AppTextStyles.bodyMedium,
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: Text(
              'OK',
              style: AppTextStyles.labelMedium.copyWith(
                color: AppColors.primary,
              ),
            ),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      children: _goals.asMap().entries.map((entry) {
        final index = entry.key;
        final goal = entry.value;
        return _buildProgressCard(goal, index);
      }).toList(),
    );
  }

  Widget _buildProgressCard(ProgressGoal goal, int index) {
    final percentage = ((goal.current / goal.target) * 100).round();
    
    return Container(
      margin: const EdgeInsets.only(bottom: 16),
      child: CustomCard(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Header
            Row(
              children: [
                Container(
                  width: 48,
                  height: 48,
                  decoration: BoxDecoration(
                    color: goal.color.withOpacity(0.1),
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Icon(
                    goal.icon,
                    color: goal.color,
                    size: 24,
                  ),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        goal.title,
                        style: AppTextStyles.labelLarge.copyWith(
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                      const SizedBox(height: 2),
                      Text(
                        goal.subtitle,
                        style: AppTextStyles.bodySmall.copyWith(
                          color: AppColors.textSecondary,
                        ),
                      ),
                    ],
                  ),
                ),
                _buildPercentageBadge(percentage, goal.color),
              ],
            ),
            
            const SizedBox(height: 20),
            
            // Progress Bar
            Column(
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text(
                      'Progress',
                      style: AppTextStyles.bodySmall.copyWith(
                        color: AppColors.textSecondary,
                      ),
                    ),
                    Text(
                      '$percentage%',
                      style: AppTextStyles.bodySmall.copyWith(
                        color: goal.color,
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 8),
                ClipRRect(
                  borderRadius: BorderRadius.circular(6),
                  child: Container(
                    height: 8,
                    decoration: BoxDecoration(
                      color: AppColors.gray200,
                      borderRadius: BorderRadius.circular(6),
                    ),
                    child: AnimatedBuilder(
                      animation: _progressAnimations[index],
                      builder: (context, child) {
                        return LinearProgressIndicator(
                          value: _progressAnimations[index].value,
                          backgroundColor: Colors.transparent,
                          valueColor: AlwaysStoppedAnimation<Color>(goal.color),
                          minHeight: 8,
                        );
                      },
                    ),
                  ),
                ),
              ],
            ),
            
            const SizedBox(height: 16),
            
            // Amount Details
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Current',
                      style: AppTextStyles.caption.copyWith(
                        color: AppColors.textSecondary,
                      ),
                    ),
                    const SizedBox(height: 2),
                    Text(
                      _formatCurrency(goal.current),
                      style: AppTextStyles.labelMedium.copyWith(
                        color: goal.color,
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                  ],
                ),
                Column(
                  crossAxisAlignment: CrossAxisAlignment.end,
                  children: [
                    Text(
                      'Target',
                      style: AppTextStyles.caption.copyWith(
                        color: AppColors.textSecondary,
                      ),
                    ),
                    const SizedBox(height: 2),
                    Text(
                      _formatCurrency(goal.target),
                      style: AppTextStyles.labelMedium.copyWith(
                        color: AppColors.textSecondary,
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                  ],
                ),
              ],
            ),
            
            const SizedBox(height: 16),
            
            // Action Buttons
            Row(
              children: [
                Expanded(
                  child: _buildActionButton(
                    'Add Funds',
                    Icons.add,
                    goal.color.withOpacity(0.1),
                    goal.color,
                    () => _showComingSoonDialog('Add Funds to ${goal.title}'),
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: _buildActionButton(
                    'Edit Goal',
                    Icons.edit,
                    AppColors.gray100,
                    AppColors.gray600,
                    () => _showComingSoonDialog('Edit ${goal.title}'),
                  ),
                ),
              ],
            ),
            
            // Goal Type Indicator
            if (goal.type == GoalType.monthly) ...[
              const SizedBox(height: 12),
              Container(
                padding: const EdgeInsets.all(8),
                decoration: BoxDecoration(
                  color: AppColors.info.withOpacity(0.05),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Row(
                  children: [
                    Icon(
                      Icons.auto_awesome,
                      size: 16,
                      color: AppColors.info,
                    ),
                    const SizedBox(width: 8),
                    Expanded(
                      child: Text(
                        'Auto-calculated monthly target based on your income surplus',
                        style: AppTextStyles.caption.copyWith(
                          color: AppColors.info,
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }

  Widget _buildPercentageBadge(int percentage, Color color) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: color.withOpacity(0.3)),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          if (percentage >= 100)
            Icon(
              Icons.check_circle,
              size: 16,
              color: color,
            )
          else
            Icon(
              Icons.trending_up,
              size: 16,
              color: color,
            ),
          const SizedBox(width: 4),
          Text(
            '$percentage%',
            style: AppTextStyles.labelMedium.copyWith(
              color: color,
              fontWeight: FontWeight.w600,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildActionButton(
    String label,
    IconData icon,
    Color backgroundColor,
    Color foregroundColor,
    VoidCallback onTap,
  ) {
    return Material(
      color: Colors.transparent,
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(8),
        child: Container(
          padding: const EdgeInsets.symmetric(vertical: 12),
          decoration: BoxDecoration(
            color: backgroundColor,
            borderRadius: BorderRadius.circular(8),
          ),
          child: Row(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(
                icon,
                size: 16,
                color: foregroundColor,
              ),
              const SizedBox(width: 6),
              Text(
                label,
                style: AppTextStyles.labelSmall.copyWith(
                  color: foregroundColor,
                  fontWeight: FontWeight.w600,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

// Data Models
class ProgressGoal {
  final String id;
  final IconData icon;
  final String title;
  final String subtitle;
  final double current;
  final double target;
  final Color color;
  final GoalType type;

  ProgressGoal({
    required this.id,
    required this.icon,
    required this.title,
    required this.subtitle,
    required this.current,
    required this.target,
    required this.color,
    required this.type,
  });
}

enum GoalType {
  monthly,
  purchase,
  vacation,
  emergency,
  investment,
}