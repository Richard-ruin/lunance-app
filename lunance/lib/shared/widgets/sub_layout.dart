
// lib/shared/widgets/sub_layout.dart (New - untuk sub pages)
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import '../../core/theme/lunance_colors.dart';

class SubLayout extends StatelessWidget {
  final Widget body;
  final String title;
  final List<Widget>? actions;
  final VoidCallback? onBackPressed;
  final bool showBackButton;
  final Color? backgroundColor;
  final Widget? floatingActionButton;

  const SubLayout({
    super.key,
    required this.body,
    required this.title,
    this.actions,
    this.onBackPressed,
    this.showBackButton = true,
    this.backgroundColor,
    this.floatingActionButton,
  });

  @override
  Widget build(BuildContext context) {
    return WillPopScope(
      onWillPop: () async {
        if (onBackPressed != null) {
          onBackPressed!();
          return false;
        }
        return true;
      },
      child: Scaffold(
        backgroundColor: backgroundColor ?? Theme.of(context).scaffoldBackgroundColor,
        appBar: AppBar(
          title: Text(
            title,
            style: const TextStyle(
              fontWeight: FontWeight.w600,
            ),
          ),
          backgroundColor: LunanceColors.primary,
          foregroundColor: Colors.white,
          elevation: 0,
          leading: showBackButton
              ? IconButton(
                  icon: const Icon(Icons.arrow_back),
                  onPressed: onBackPressed ?? () => Navigator.of(context).pop(),
                )
              : null,
          actions: actions,
          systemOverlayStyle: SystemUiOverlayStyle.light,
        ),
        body: body,
        floatingActionButton: floatingActionButton,
      ),
    );
  }
}