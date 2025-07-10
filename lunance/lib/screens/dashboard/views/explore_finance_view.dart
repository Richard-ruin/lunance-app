import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../../providers/auth_provider.dart';
import '../../../utils/app_colors.dart';
import '../../../utils/app_text_styles.dart';
import '../../../widgets/custom_widgets.dart';
import '../widgets/finance_overview_cards.dart';
import '../widgets/progress_cards.dart';

class ExploreFinanceView extends StatefulWidget {
  const ExploreFinanceView({Key? key}) : super(key: key);

  @override
  State<ExploreFinanceView> createState() => _ExploreFinanceViewState();
}

class _ExploreFinanceViewState extends State<ExploreFinanceView> 
    with TickerProviderStateMixin {
  
  late AnimationController _fadeController;
  late AnimationController _slideController;
  late Animation<double> _fadeAnimation;
  late Animation<Offset> _slideAnimation;

  @override
  void initState() {
    super.initState();
    
    _fadeController = AnimationController(
      duration: const Duration(milliseconds: 600),
      vsync: this,
    );
    
    _slideController = AnimationController(
      duration: const Duration(milliseconds: 800),
      vsync: this,
    );
    
    _fadeAnimation = Tween<double>(
      begin: 0.0,
      end: 1.0,
    ).animate(CurvedAnimation(
      parent: _fadeController,
      curve: Curves.easeOut,
    ));
    
    _slideAnimation = Tween<Offset>(
      begin: const Offset(0.0, 0.3),
      end: Offset.zero,
    ).animate(CurvedAnimation(
      parent: _slideController,
      curve: Curves.easeOutCubic,
    ));
    
    _fadeController.forward();
    _slideController.forward();
  }

  @override
  void dispose() {
    _fadeController.dispose();
    _slideController.dispose();
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
    return FadeTransition(
      opacity: _fadeAnimation,
      child: SlideTransition(
        position: _slideAnimation,
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(24),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Welcome Header
              _buildWelcomeHeader(),
              
              const SizedBox(height: 32),
              
              // Financial Overview Cards
              _buildFinancialOverview(),
              
              const SizedBox(height: 32),
              
              // Progress Tracking Section
              _buildProgressSection(),
              
              const SizedBox(height: 32),
              
              // Quick Actions
              _buildQuickActions(),
              
              const SizedBox(height: 32),
              
              // Recent Insights
              _buildRecentInsights(),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildWelcomeHeader() {
    return Consumer<AuthProvider>(
      builder: (context, authProvider, child) {
        final user = authProvider.user;
        final hour = DateTime.now().hour;
        String greeting = 'Selamat ';
        if (hour < 12) greeting += 'pagi';
        else if (hour < 17) greeting += 'siang';
        else greeting += 'malam';

        return Container(
          padding: const EdgeInsets.all(24),
          decoration: BoxDecoration(
            gradient: LinearGradient(
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
              colors: [
                AppColors.primary.withOpacity(0.1),
                AppColors.primary.withOpacity(0.05),
              ],
            ),
            borderRadius: BorderRadius.circular(20),
            border: Border.all(color: AppColors.primary.withOpacity(0.2)),
          ),
          child: Row(
            children: [
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      '$greeting, ${user?.profile?.fullName?.split(' ').first ?? 'User'}!',
                      style: AppTextStyles.h5.copyWith(
                        color: AppColors.primary,
                        fontWeight: FontWeight.w700,
                      ),
                    ),
                    const SizedBox(height: 8),
                    Text(
                      'Lihat ringkasan keuangan dan progress tabungan Anda',
                      style: AppTextStyles.bodyMedium.copyWith(
                        color: AppColors.textSecondary,
                      ),
                    ),
                  ],
                ),
              ),
              Container(
                width: 60,
                height: 60,
                decoration: BoxDecoration(
                  color: AppColors.primary.withOpacity(0.1),
                  shape: BoxShape.circle,
                ),
                child: Icon(
                  Icons.analytics,
                  size: 30,
                  color: AppColors.primary,
                ),
              ),
            ],
          ),
        );
      },
    );
  }

  Widget _buildFinancialOverview() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            Icon(
              Icons.account_balance_wallet,
              size: 24,
              color: AppColors.primary,
            ),
            const SizedBox(width: 12),
            Text(
              'Financial Overview',
              style: AppTextStyles.h6.copyWith(
                fontWeight: FontWeight.w600,
              ),
            ),
          ],
        ),
        const SizedBox(height: 16),
        
        const FinanceOverviewCards(),
      ],
    );
  }

  Widget _buildProgressSection() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Row(
              children: [
                Icon(
                  Icons.track_changes,
                  size: 24,
                  color: AppColors.success,
                ),
                const SizedBox(width: 12),
                Text(
                  'Progress Tracking',
                  style: AppTextStyles.h6.copyWith(
                    fontWeight: FontWeight.w600,
                  ),
                ),
              ],
            ),
            TextButton.icon(
              onPressed: () => _showComingSoonDialog('Manage Goals'),
              icon: Icon(
                Icons.add,
                size: 18,
                color: AppColors.primary,
              ),
              label: Text(
                'Add Goal',
                style: AppTextStyles.labelMedium.copyWith(
                  color: AppColors.primary,
                ),
              ),
            ),
          ],
        ),
        const SizedBox(height: 16),
        
        const ProgressCards(),
      ],
    );
  }

  Widget _buildQuickActions() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            Icon(
              Icons.bolt,
              size: 24,
              color: AppColors.warning,
            ),
            const SizedBox(width: 12),
            Text(
              'Quick Actions',
              style: AppTextStyles.h6.copyWith(
                fontWeight: FontWeight.w600,
              ),
            ),
          ],
        ),
        const SizedBox(height: 16),
        
        GridView.count(
          shrinkWrap: true,
          physics: const NeverScrollableScrollPhysics(),
          crossAxisCount: 2,
          mainAxisSpacing: 16,
          crossAxisSpacing: 16,
          childAspectRatio: 1.5,
          children: [
            _buildActionCard(
              icon: Icons.add_circle_outline,
              title: 'Add Transaction',
              subtitle: 'Record income or expense',
              color: AppColors.primary,
              onTap: () => _showComingSoonDialog('Add Transaction'),
            ),
            _buildActionCard(
              icon: Icons.savings,
              title: 'Set Goal',
              subtitle: 'Create new saving target',
              color: AppColors.success,
              onTap: () => _showComingSoonDialog('Set Goal'),
            ),
            _buildActionCard(
              icon: Icons.pie_chart,
              title: 'View Reports',
              subtitle: 'Detailed analytics',
              color: AppColors.info,
              onTap: () => _showComingSoonDialog('View Reports'),
            ),
            _buildActionCard(
              icon: Icons.category,
              title: 'Manage Categories',
              subtitle: 'Organize expenses',
              color: AppColors.warning,
              onTap: () => _showComingSoonDialog('Manage Categories'),
            ),
          ],
        ),
      ],
    );
  }

  Widget _buildActionCard({
    required IconData icon,
    required String title,
    required String subtitle,
    required Color color,
    required VoidCallback onTap,
  }) {
    return Material(
      color: Colors.transparent,
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(16),
        child: Container(
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: color.withOpacity(0.05),
            borderRadius: BorderRadius.circular(16),
            border: Border.all(color: color.withOpacity(0.2)),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Container(
                width: 40,
                height: 40,
                decoration: BoxDecoration(
                  color: color.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(10),
                ),
                child: Icon(
                  icon,
                  size: 22,
                  color: color,
                ),
              ),
              const SizedBox(height: 12),
              Text(
                title,
                style: AppTextStyles.labelMedium.copyWith(
                  fontWeight: FontWeight.w600,
                  color: AppColors.gray800,
                ),
              ),
              const SizedBox(height: 4),
              Text(
                subtitle,
                style: AppTextStyles.bodySmall.copyWith(
                  color: AppColors.textSecondary,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildRecentInsights() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            Icon(
              Icons.lightbulb_outline,
              size: 24,
              color: AppColors.info,
            ),
            const SizedBox(width: 12),
            Text(
              'AI Insights',
              style: AppTextStyles.h6.copyWith(
                fontWeight: FontWeight.w600,
              ),
            ),
          ],
        ),
        const SizedBox(height: 16),
        
        Container(
          padding: const EdgeInsets.all(20),
          decoration: BoxDecoration(
            color: AppColors.info.withOpacity(0.05),
            borderRadius: BorderRadius.circular(16),
            border: Border.all(color: AppColors.info.withOpacity(0.2)),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Container(
                    width: 32,
                    height: 32,
                    decoration: BoxDecoration(
                      color: AppColors.info.withOpacity(0.1),
                      shape: BoxShape.circle,
                    ),
                    child: Icon(
                      Icons.auto_awesome,
                      size: 18,
                      color: AppColors.info,
                    ),
                  ),
                  const SizedBox(width: 12),
                  Text(
                    'Luna\'s Suggestion',
                    style: AppTextStyles.labelLarge.copyWith(
                      color: AppColors.info,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 16),
              
              _buildInsightItem(
                'Pengeluaran makanan Anda 15% lebih tinggi dari bulan lalu. Coba atur budget untuk makan di luar.',
                Icons.restaurant,
              ),
              const SizedBox(height: 12),
              
              _buildInsightItem(
                'Anda sudah mencapai 80% target tabungan bulanan! Pertahankan momentum ini.',
                Icons.trending_up,
              ),
              const SizedBox(height: 12),
              
              _buildInsightItem(
                'Ada peluang menghemat Rp 200.000 dari kategori transportasi bulan ini.',
                Icons.directions_car,
              ),
              
              const SizedBox(height: 16),
              
              InkWell(
                onTap: () => _showComingSoonDialog('More Insights'),
                borderRadius: BorderRadius.circular(8),
                child: Container(
                  width: double.infinity,
                  padding: const EdgeInsets.symmetric(vertical: 12),
                  decoration: BoxDecoration(
                    color: AppColors.info.withOpacity(0.1),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Text(
                    'Lihat Semua Insights',
                    style: AppTextStyles.labelMedium.copyWith(
                      color: AppColors.info,
                      fontWeight: FontWeight.w600,
                    ),
                    textAlign: TextAlign.center,
                  ),
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildInsightItem(String text, IconData icon) {
    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Container(
          width: 24,
          height: 24,
          decoration: BoxDecoration(
            color: AppColors.white,
            borderRadius: BorderRadius.circular(6),
          ),
          child: Icon(
            icon,
            size: 14,
            color: AppColors.info,
          ),
        ),
        const SizedBox(width: 12),
        Expanded(
          child: Text(
            text,
            style: AppTextStyles.bodyMedium.copyWith(
              color: AppColors.gray700,
              height: 1.5,
            ),
          ),
        ),
      ],
    );
  }
}