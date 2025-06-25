// lib/shared/widgets/main_navigation.dart
import 'package:flutter/material.dart';
import '../../core/theme/lunance_colors.dart';
import '../../core/routes/route_names.dart';
import 'curved_navigation_bar.dart';

class MainNavigation extends StatelessWidget {
  final int currentIndex;
  final Function(int)? onTap;

  const MainNavigation({
    super.key,
    required this.currentIndex,
    this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return CurvedNavigationBar(
      index: currentIndex,
      height: 75.0,
      items: const [
        Icon(
          Icons.home_rounded,
          size: 28,
          color: Colors.white,
        ),
        Icon(
          Icons.history_rounded,
          size: 28,
          color: Colors.white,
        ),
        Icon(
          Icons.add_rounded,
          size: 32,
          color: Colors.white,
        ),
        Icon(
          Icons.folder_rounded,
          size: 28,
          color: Colors.white,
        ),
        Icon(
          Icons.settings_rounded,
          size: 28,
          color: Colors.white,
        ),
      ],
      color: LunanceColors.primary,
      buttonBackgroundColor: LunanceColors.primary,
      backgroundColor: LunanceColors.background,
      animationCurve: Curves.easeInOutCubic,
      animationDuration: const Duration(milliseconds: 600),
      onTap: onTap ?? (index) => _handleNavigation(context, index),
      letIndexChange: (index) => true,
    );
  }

  void _handleNavigation(BuildContext context, int index) {
    // Prevent navigation to same page
    if (index == currentIndex) return;

    String routeName;
    switch (index) {
      case 0:
        routeName = RouteNames.dashboard;
        break;
      case 1:
        routeName = RouteNames.history;
        break;
      case 2:
        routeName = RouteNames.addTransaction;
        break;
      case 3:
        routeName = RouteNames.categories;
        break;
      case 4:
        routeName = RouteNames.settings;
        break;
      default:
        return;
    }

    Navigator.pushReplacementNamed(context, routeName);
  }
}