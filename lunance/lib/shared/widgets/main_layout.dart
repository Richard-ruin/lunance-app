// lib/shared/widgets/main_layout.dart (Updated dengan floatingActionButton support)
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:go_router/go_router.dart';
import 'curved_navigation_bar.dart';
import '../../core/theme/lunance_colors.dart';

class MainLayout extends StatelessWidget {
  final Widget body;
  final int currentIndex;
  final bool showAppBar;
  final String? title;
  final List<Widget>? actions;
  final bool? centerTitle;
  final Widget? leading;
  final PreferredSizeWidget? customAppBar;
  final Widget? floatingActionButton; // Added this

  const MainLayout({
    super.key,
    required this.body,
    required this.currentIndex,
    this.showAppBar = false,
    this.title,
    this.actions,
    this.centerTitle,
    this.leading,
    this.customAppBar,
    this.floatingActionButton, // Added this
  });

  @override
  Widget build(BuildContext context) {
    return WillPopScope(
      onWillPop: () => _handleBackButton(context),
      child: Scaffold(
        appBar: _buildAppBar(context),
        body: body,
        bottomNavigationBar: _buildBottomNavigation(context),
        floatingActionButton: floatingActionButton, // Added this
      ),
    );
  }

  PreferredSizeWidget? _buildAppBar(BuildContext context) {
    if (!showAppBar) return null;
    
    if (customAppBar != null) return customAppBar;
    
    return AppBar(
      title: title != null ? Text(title!) : null,
      actions: actions,
      centerTitle: centerTitle ?? true,
      leading: leading,
      backgroundColor: LunanceColors.primary,
      foregroundColor: Colors.white,
      elevation: 0,
      systemOverlayStyle: SystemUiOverlayStyle.light,
    );
  }

  Widget _buildBottomNavigation(BuildContext context) {
    return CurvedNavigationBar(
      index: currentIndex,
      height: 75.0,
      items: const <Widget>[
        Icon(Icons.home_rounded, size: 28, color: Colors.white),
        Icon(Icons.history_rounded, size: 28, color: Colors.white),
        Icon(Icons.add_rounded, size: 32, color: Colors.white),
        Icon(Icons.folder_rounded, size: 28, color: Colors.white),
        Icon(Icons.settings_rounded, size: 28, color: Colors.white),
      ],
      color: LunanceColors.primary,
      buttonBackgroundColor: LunanceColors.primaryVariant,
      backgroundColor: Colors.white,
      animationCurve: Curves.easeInOutCubic,
      animationDuration: const Duration(milliseconds: 600),
      onTap: (index) => _navigateToPage(context, index),
      letIndexChange: (index) => true,
    );
  }

  void _navigateToPage(BuildContext context, int index) {
    // Prevent navigation to same page
    if (index == currentIndex) {
      // If clicking add button (index 2), show modal
      if (index == 2) {
        _showAddTransactionModal(context);
      }
      return;
    }

    String route;
    switch (index) {
      case 0:
        route = '/dashboard';
        break;
      case 1:
        route = '/history';
        break;
      case 2:
        _showAddTransactionModal(context);
        return;
      case 3:
        route = '/categories';
        break;
      case 4:
        route = '/settings';
        break;
      default:
        route = '/dashboard';
    }
    
    context.go(route);
  }

  void _showAddTransactionModal(BuildContext context) {
    showModalBottomSheet(
      context: context,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (context) => Container(
        padding: const EdgeInsets.all(20),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Container(
              width: 40,
              height: 4,
              decoration: BoxDecoration(
                color: Colors.grey[300],
                borderRadius: BorderRadius.circular(2),
              ),
            ),
            const SizedBox(height: 20),
            const Text(
              'Tambah Transaksi',
              style: TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 20),
            Row(
              children: [
                Expanded(
                  child: _buildTransactionButton(
                    context,
                    'Pemasukan',
                    Icons.trending_up,
                    Colors.green,
                    () {
                      Navigator.pop(context);
                      // Navigate to add income page
                      context.go('/add-income');
                    },
                  ),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: _buildTransactionButton(
                    context,
                    'Pengeluaran',
                    Icons.trending_down,
                    Colors.red,
                    () {
                      Navigator.pop(context);
                      // Navigate to add expense page
                      context.go('/add-expense');
                    },
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),
          ],
        ),
      ),
    );
  }

  Widget _buildTransactionButton(
    BuildContext context,
    String title,
    IconData icon,
    Color color,
    VoidCallback onTap,
  ) {
    return InkWell(
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.symmetric(vertical: 16),
        decoration: BoxDecoration(
          color: color.withOpacity(0.1),
          borderRadius: BorderRadius.circular(12),
          border: Border.all(color: color.withOpacity(0.3)),
        ),
        child: Column(
          children: [
            Icon(icon, color: color, size: 32),
            const SizedBox(height: 8),
            Text(
              title,
              style: TextStyle(
                color: color,
                fontWeight: FontWeight.w600,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Future<bool> _handleBackButton(BuildContext context) async {
    // Jika di dashboard (index 0), tanya konfirmasi keluar
    if (currentIndex == 0) {
      return await _showExitConfirmation(context);
    }
    
    // Jika di tab lain, kembali ke dashboard
    context.go('/dashboard');
    return false;
  }

  Future<bool> _showExitConfirmation(BuildContext context) async {
    return await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Keluar Aplikasi'),
        content: const Text('Apakah Anda yakin ingin keluar dari aplikasi?'),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(false),
            child: const Text('Batal'),
          ),
          TextButton(
            onPressed: () {
              Navigator.of(context).pop(true);
              SystemNavigator.pop();
            },
            child: const Text('Keluar'),
          ),
        ],
      ),
    ) ?? false;
  }
}