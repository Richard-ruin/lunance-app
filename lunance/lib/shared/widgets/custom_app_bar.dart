// lib/core/widgets/custom_app_bar.dart
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:lunance/core/theme/lunance_colors.dart';
class CustomAppBar extends StatelessWidget implements PreferredSizeWidget {
  final String title;
  final List<Widget>? actions;
  final Widget? leading;
  final bool centerTitle;
  final bool showBackButton;
  final VoidCallback? onBackPressed;
  final Color? backgroundColor;
  final Color? foregroundColor;
  final double elevation;
  final bool automaticallyImplyLeading;
  final PreferredSizeWidget? bottom;
  final SystemUiOverlayStyle? systemOverlayStyle;
  final double? leadingWidth;
  final TextStyle? titleTextStyle;
  final double toolbarOpacity;
  final double bottomOpacity;

  const CustomAppBar({
    Key? key,
    required this.title,
    this.actions,
    this.leading,
    this.centerTitle = true,
    this.showBackButton = true,
    this.onBackPressed,
    this.backgroundColor,
    this.foregroundColor,
    this.elevation = 0,
    this.automaticallyImplyLeading = true,
    this.bottom,
    this.systemOverlayStyle,
    this.leadingWidth,
    this.titleTextStyle,
    this.toolbarOpacity = 1.0,
    this.bottomOpacity = 1.0,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final isDark = theme.brightness == Brightness.dark;
    
    return AppBar(
      title: Text(
        title,
        style: titleTextStyle ?? TextStyle(
          fontSize: 20,
          fontWeight: FontWeight.w600,
          color: foregroundColor ?? (isDark ? Colors.white : LunanceColors.textPrimary),
        ),
      ),
      centerTitle: centerTitle,
      elevation: elevation,
      backgroundColor: backgroundColor ?? Colors.transparent,
      foregroundColor: foregroundColor ?? (isDark ? Colors.white : LunanceColors.textPrimary),
      leading: leading ?? (showBackButton && Navigator.of(context).canPop() 
        ? IconButton(
            icon: const Icon(Icons.arrow_back_ios_new),
            onPressed: onBackPressed ?? () => Navigator.of(context).pop(),
          )
        : null),
      actions: actions,
      automaticallyImplyLeading: automaticallyImplyLeading,
      bottom: bottom,
      systemOverlayStyle: systemOverlayStyle ?? SystemUiOverlayStyle(
        statusBarColor: Colors.transparent,
        statusBarIconBrightness: isDark ? Brightness.light : Brightness.dark,
        statusBarBrightness: isDark ? Brightness.dark : Brightness.light,
      ),
      leadingWidth: leadingWidth,
      toolbarOpacity: toolbarOpacity,
      bottomOpacity: bottomOpacity,
    );
  }

  @override
  Size get preferredSize => Size.fromHeight(
    kToolbarHeight + (bottom?.preferredSize.height ?? 0),
  );
}

// Custom AppBar dengan gradient background
class GradientAppBar extends StatelessWidget implements PreferredSizeWidget {
  final String title;
  final List<Widget>? actions;
  final Widget? leading;
  final bool centerTitle;
  final bool showBackButton;
  final VoidCallback? onBackPressed;
  final Gradient? gradient;
  final Color? foregroundColor;
  final PreferredSizeWidget? bottom;
  final TextStyle? titleTextStyle;

  const GradientAppBar({
    Key? key,
    required this.title,
    this.actions,
    this.leading,
    this.centerTitle = true,
    this.showBackButton = true,
    this.onBackPressed,
    this.gradient,
    this.foregroundColor,
    this.bottom,
    this.titleTextStyle,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    final defaultGradient = LinearGradient(
      colors: [
        LunanceColors.primary,
        LunanceColors.primaryVariant,
      ],
      begin: Alignment.topLeft,
      end: Alignment.bottomRight,
    );

    return Container(
      decoration: BoxDecoration(
        gradient: gradient ?? defaultGradient,
      ),
      child: AppBar(
        title: Text(
          title,
          style: titleTextStyle ?? const TextStyle(
            fontSize: 20,
            fontWeight: FontWeight.w600,
            color: Colors.white,
          ),
        ),
        centerTitle: centerTitle,
        elevation: 0,
        backgroundColor: Colors.transparent,
        foregroundColor: foregroundColor ?? Colors.white,
        leading: leading ?? (showBackButton && Navigator.of(context).canPop() 
          ? IconButton(
              icon: const Icon(Icons.arrow_back_ios_new, color: Colors.white),
              onPressed: onBackPressed ?? () => Navigator.of(context).pop(),
            )
          : null),
        actions: actions,
        bottom: bottom,
        systemOverlayStyle: const SystemUiOverlayStyle(
          statusBarColor: Colors.transparent,
          statusBarIconBrightness: Brightness.light,
          statusBarBrightness: Brightness.dark,
        ),
      ),
    );
  }

  @override
  Size get preferredSize => Size.fromHeight(
    kToolbarHeight + (bottom?.preferredSize.height ?? 0),
  );
}

// Custom AppBar dengan search functionality
class SearchAppBar extends StatefulWidget implements PreferredSizeWidget {
  final String title;
  final String hintText;
  final ValueChanged<String>? onSearchChanged;
  final VoidCallback? onSearchPressed;
  final VoidCallback? onClearPressed;
  final List<Widget>? actions;
  final bool automaticallyImplyLeading;

  const SearchAppBar({
    Key? key,
    required this.title,
    this.hintText = 'Search...',
    this.onSearchChanged,
    this.onSearchPressed,
    this.onClearPressed,
    this.actions,
    this.automaticallyImplyLeading = true,
  }) : super(key: key);

  @override
  State<SearchAppBar> createState() => _SearchAppBarState();

  @override
  Size get preferredSize => const Size.fromHeight(kToolbarHeight);
}

class _SearchAppBarState extends State<SearchAppBar> {
  bool _isSearchActive = false;
  final TextEditingController _searchController = TextEditingController();

  @override
  void dispose() {
    _searchController.dispose();
    super.dispose();
  }

  void _toggleSearch() {
    setState(() {
      _isSearchActive = !_isSearchActive;
      if (!_isSearchActive) {
        _searchController.clear();
        widget.onClearPressed?.call();
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final isDark = theme.brightness == Brightness.dark;

    return AppBar(
      title: _isSearchActive
          ? TextField(
              controller: _searchController,
              autofocus: true,
              decoration: InputDecoration(
                hintText: widget.hintText,
                border: InputBorder.none,
                hintStyle: TextStyle(
                  color: isDark ? Colors.white70 : LunanceColors.textSecondary,
                ),
              ),
              style: TextStyle(
                color: isDark ? Colors.white : LunanceColors.textPrimary,
              ),
              onChanged: widget.onSearchChanged,
            )
          : Text(
              widget.title,
              style: TextStyle(
                fontSize: 20,
                fontWeight: FontWeight.w600,
                color: isDark ? Colors.white : LunanceColors.textPrimary,
              ),
            ),
      backgroundColor: Colors.transparent,
      elevation: 0,
      automaticallyImplyLeading: widget.automaticallyImplyLeading && !_isSearchActive,
      leading: _isSearchActive
          ? IconButton(
              icon: const Icon(Icons.arrow_back),
              onPressed: _toggleSearch,
            )
          : null,
      actions: [
        if (!_isSearchActive)
          IconButton(
            icon: const Icon(Icons.search),
            onPressed: () {
              _toggleSearch();
              widget.onSearchPressed?.call();
            },
          ),
        if (_isSearchActive)
          IconButton(
            icon: const Icon(Icons.clear),
            onPressed: () {
              _searchController.clear();
              widget.onClearPressed?.call();
            },
          ),
        ...?widget.actions,
      ],
    );
  }
}