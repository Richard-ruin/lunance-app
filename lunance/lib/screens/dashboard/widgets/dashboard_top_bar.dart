import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../../providers/auth_provider.dart';
import '../../../utils/app_colors.dart';
import '../../../utils/app_text_styles.dart';

class DashboardTopBar extends StatelessWidget {
  final String title;
  final bool isLeftSidebarOpen;
  final bool isRightSidebarOpen;
  final VoidCallback onLeftToggle;
  final VoidCallback onRightToggle;

  const DashboardTopBar({
    Key? key,
    required this.title,
    required this.isLeftSidebarOpen,
    required this.isRightSidebarOpen,
    required this.onLeftToggle,
    required this.onRightToggle,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: AppColors.white,
        border: Border(
          bottom: BorderSide(color: AppColors.border, width: 1),
        ),
        boxShadow: [
          BoxShadow(
            color: AppColors.shadow.withOpacity(0.1),
            blurRadius: 8,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Row(
        children: [
          // Left Menu Toggle (when sidebar is closed)
          if (!isLeftSidebarOpen)
            _buildToggleButton(
              icon: Icons.menu,
              onTap: onLeftToggle,
              tooltip: 'Open Menu',
            ),
          
          if (!isLeftSidebarOpen) const SizedBox(width: 16),
          
          // Title with animated transition
          Expanded(
            child: AnimatedSwitcher(
              duration: const Duration(milliseconds: 300),
              child: Text(
                title,
                key: ValueKey(title),
                style: AppTextStyles.h6,
              ),
            ),
          ),
          
          // Right Profile Toggle (when sidebar is closed)
          if (!isRightSidebarOpen)
            Consumer<AuthProvider>(
              builder: (context, authProvider, child) {
                final user = authProvider.user;
                return _buildProfileButton(
                  user: user,
                  onTap: onRightToggle,
                );
              },
            ),
        ],
      ),
    );
  }

  Widget _buildToggleButton({
    required IconData icon,
    required VoidCallback onTap,
    required String tooltip,
  }) {
    return Tooltip(
      message: tooltip,
      child: Material(
        color: Colors.transparent,
        child: InkWell(
          onTap: onTap,
          borderRadius: BorderRadius.circular(8),
          child: Container(
            padding: const EdgeInsets.all(8),
            decoration: BoxDecoration(
              color: AppColors.gray100,
              borderRadius: BorderRadius.circular(8),
            ),
            child: Icon(
              icon,
              size: 20,
              color: AppColors.gray600,
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildProfileButton({
    required dynamic user,
    required VoidCallback onTap,
  }) {
    return Tooltip(
      message: 'Profile & Settings',
      child: Material(
        color: Colors.transparent,
        child: InkWell(
          onTap: onTap,
          borderRadius: BorderRadius.circular(20),
          child: Container(
            width: 40,
            height: 40,
            decoration: BoxDecoration(
              color: AppColors.primary.withOpacity(0.1),
              shape: BoxShape.circle,
              border: Border.all(
                color: AppColors.primary.withOpacity(0.2),
                width: 1,
              ),
            ),
            child: Center(
              child: Text(
                user?.profile?.fullName?.substring(0, 1).toUpperCase() ?? 'U',
                style: AppTextStyles.labelMedium.copyWith(
                  color: AppColors.primary,
                  fontWeight: FontWeight.w600,
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }
}