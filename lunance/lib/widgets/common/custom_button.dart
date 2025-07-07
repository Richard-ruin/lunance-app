import 'package:flutter/material.dart';
import '../../themes/app_theme.dart';

enum ButtonVariant {
  primary,
  secondary,
  tertiary,
  danger,
}

enum ButtonSize {
  small,
  medium,
  large,
}

class CustomButton extends StatelessWidget {
  final VoidCallback? onPressed;
  final String text;
  final IconData? icon;
  final ButtonVariant variant;
  final ButtonSize size;
  final bool isLoading;
  final bool isFullWidth;
  final Widget? child;

  const CustomButton({
    super.key,
    required this.onPressed,
    required this.text,
    this.icon,
    this.variant = ButtonVariant.primary,
    this.size = ButtonSize.medium,
    this.isLoading = false,
    this.isFullWidth = true,
    this.child,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;

    // Button dimensions based on size
    final double height = _getHeight();
    final EdgeInsets padding = _getPadding();
    final double borderRadius = _getBorderRadius();

    // Button colors based on variant
    final ButtonColors colors = _getColors(colorScheme);

    Widget buttonChild = _buildButtonChild(theme);

    Widget button = SizedBox(
      height: height,
      width: isFullWidth ? double.infinity : null,
      child: ElevatedButton(
        onPressed: isLoading ? null : onPressed,
        style: ElevatedButton.styleFrom(
          backgroundColor: colors.backgroundColor,
          foregroundColor: colors.foregroundColor,
          disabledBackgroundColor: colors.disabledBackgroundColor,
          disabledForegroundColor: colors.disabledForegroundColor,
          elevation: _getElevation(),
          padding: padding,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(borderRadius),
            side: colors.borderSide ?? BorderSide.none,
          ),
        ),
        child: buttonChild,
      ),
    );

    return button;
  }

  double _getHeight() {
    switch (size) {
      case ButtonSize.small:
        return 36;
      case ButtonSize.medium:
        return 48;
      case ButtonSize.large:
        return 56;
    }
  }

  EdgeInsets _getPadding() {
    switch (size) {
      case ButtonSize.small:
        return const EdgeInsets.symmetric(
          horizontal: AppTheme.spacingM,
          vertical: AppTheme.spacingS,
        );
      case ButtonSize.medium:
        return const EdgeInsets.symmetric(
          horizontal: AppTheme.spacingL,
          vertical: AppTheme.spacingM,
        );
      case ButtonSize.large:
        return const EdgeInsets.symmetric(
          horizontal: AppTheme.spacingXL,
          vertical: AppTheme.spacingM,
        );
    }
  }

  double _getBorderRadius() {
    switch (size) {
      case ButtonSize.small:
        return AppTheme.borderRadiusSmall;
      case ButtonSize.medium:
        return AppTheme.borderRadiusMedium;
      case ButtonSize.large:
        return AppTheme.borderRadiusLarge;
    }
  }

  double _getElevation() {
    switch (variant) {
      case ButtonVariant.primary:
        return AppTheme.elevationLow;
      case ButtonVariant.secondary:
        return 0;
      case ButtonVariant.tertiary:
        return 0;
      case ButtonVariant.danger:
        return AppTheme.elevationLow;
    }
  }

  ButtonColors _getColors(ColorScheme colorScheme) {
    switch (variant) {
      case ButtonVariant.primary:
        return ButtonColors(
          backgroundColor: colorScheme.primary,
          foregroundColor: colorScheme.onPrimary,
          disabledBackgroundColor: colorScheme.onSurface.withOpacity(0.12),
          disabledForegroundColor: colorScheme.onSurface.withOpacity(0.38),
        );
      case ButtonVariant.secondary:
        return ButtonColors(
          backgroundColor: colorScheme.surface,
          foregroundColor: colorScheme.primary,
          disabledBackgroundColor: colorScheme.surface,
          disabledForegroundColor: colorScheme.onSurface.withOpacity(0.38),
          borderSide: BorderSide(color: colorScheme.primary),
        );
      case ButtonVariant.tertiary:
        return ButtonColors(
          backgroundColor: Colors.transparent,
          foregroundColor: colorScheme.primary,
          disabledBackgroundColor: Colors.transparent,
          disabledForegroundColor: colorScheme.onSurface.withOpacity(0.38),
        );
      case ButtonVariant.danger:
        return ButtonColors(
          backgroundColor: colorScheme.error,
          foregroundColor: colorScheme.onError,
          disabledBackgroundColor: colorScheme.onSurface.withOpacity(0.12),
          disabledForegroundColor: colorScheme.onSurface.withOpacity(0.38),
        );
    }
  }

  Widget _buildButtonChild(ThemeData theme) {
    if (isLoading) {
      return SizedBox(
        width: _getLoadingSize(),
        height: _getLoadingSize(),
        child: CircularProgressIndicator(
          strokeWidth: 2,
          valueColor: AlwaysStoppedAnimation<Color>(
            _getColors(theme.colorScheme).foregroundColor,
          ),
        ),
      );
    }

    if (child != null) {
      return child!;
    }

    final textStyle = _getTextStyle(theme);

    if (icon != null) {
      return Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(
            icon,
            size: _getIconSize(),
          ),
          const SizedBox(width: AppTheme.spacingS),
          Text(
            text,
            style: textStyle,
          ),
        ],
      );
    }

    return Text(
      text,
      style: textStyle,
    );
  }

  double _getLoadingSize() {
    switch (size) {
      case ButtonSize.small:
        return 16;
      case ButtonSize.medium:
        return 20;
      case ButtonSize.large:
        return 24;
    }
  }

  double _getIconSize() {
    switch (size) {
      case ButtonSize.small:
        return 16;
      case ButtonSize.medium:
        return 20;
      case ButtonSize.large:
        return 24;
    }
  }

  TextStyle? _getTextStyle(ThemeData theme) {
    switch (size) {
      case ButtonSize.small:
        return theme.textTheme.labelMedium?.copyWith(
          fontWeight: FontWeight.w600,
        );
      case ButtonSize.medium:
        return theme.textTheme.labelLarge?.copyWith(
          fontWeight: FontWeight.w600,
        );
      case ButtonSize.large:
        return theme.textTheme.labelLarge?.copyWith(
          fontWeight: FontWeight.w600,
        );
    }
  }
}

class ButtonColors {
  final Color backgroundColor;
  final Color foregroundColor;
  final Color disabledBackgroundColor;
  final Color disabledForegroundColor;
  final BorderSide? borderSide;

  const ButtonColors({
    required this.backgroundColor,
    required this.foregroundColor,
    required this.disabledBackgroundColor,
    required this.disabledForegroundColor,
    this.borderSide,
  });
}

// Icon button variant
class CustomIconButton extends StatelessWidget {
  final VoidCallback? onPressed;
  final IconData icon;
  final ButtonVariant variant;
  final ButtonSize size;
  final bool isLoading;
  final String? tooltip;

  const CustomIconButton({
    super.key,
    required this.onPressed,
    required this.icon,
    this.variant = ButtonVariant.primary,
    this.size = ButtonSize.medium,
    this.isLoading = false,
    this.tooltip,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;

    final double buttonSize = _getButtonSize();
    final double iconSize = _getIconSize();
    final ButtonColors colors = _getColors(colorScheme);

    Widget buttonChild = isLoading
        ? SizedBox(
            width: iconSize,
            height: iconSize,
            child: CircularProgressIndicator(
              strokeWidth: 2,
              valueColor: AlwaysStoppedAnimation<Color>(colors.foregroundColor),
            ),
          )
        : Icon(
            icon,
            size: iconSize,
          );

    Widget button = SizedBox(
      width: buttonSize,
      height: buttonSize,
      child: ElevatedButton(
        onPressed: isLoading ? null : onPressed,
        style: ElevatedButton.styleFrom(
          backgroundColor: colors.backgroundColor,
          foregroundColor: colors.foregroundColor,
          disabledBackgroundColor: colors.disabledBackgroundColor,
          disabledForegroundColor: colors.disabledForegroundColor,
          elevation: _getElevation(),
          padding: EdgeInsets.zero,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(buttonSize / 2),
            side: colors.borderSide ?? BorderSide.none,
          ),
        ),
        child: buttonChild,
      ),
    );

    if (tooltip != null) {
      return Tooltip(
        message: tooltip!,
        child: button,
      );
    }

    return button;
  }

  double _getButtonSize() {
    switch (size) {
      case ButtonSize.small:
        return 36;
      case ButtonSize.medium:
        return 48;
      case ButtonSize.large:
        return 56;
    }
  }

  double _getIconSize() {
    switch (size) {
      case ButtonSize.small:
        return 16;
      case ButtonSize.medium:
        return 20;
      case ButtonSize.large:
        return 24;
    }
  }

  double _getElevation() {
    switch (variant) {
      case ButtonVariant.primary:
        return AppTheme.elevationLow;
      case ButtonVariant.secondary:
        return 0;
      case ButtonVariant.tertiary:
        return 0;
      case ButtonVariant.danger:
        return AppTheme.elevationLow;
    }
  }

  ButtonColors _getColors(ColorScheme colorScheme) {
    switch (variant) {
      case ButtonVariant.primary:
        return ButtonColors(
          backgroundColor: colorScheme.primary,
          foregroundColor: colorScheme.onPrimary,
          disabledBackgroundColor: colorScheme.onSurface.withOpacity(0.12),
          disabledForegroundColor: colorScheme.onSurface.withOpacity(0.38),
        );
      case ButtonVariant.secondary:
        return ButtonColors(
          backgroundColor: colorScheme.surface,
          foregroundColor: colorScheme.primary,
          disabledBackgroundColor: colorScheme.surface,
          disabledForegroundColor: colorScheme.onSurface.withOpacity(0.38),
          borderSide: BorderSide(color: colorScheme.primary),
        );
      case ButtonVariant.tertiary:
        return ButtonColors(
          backgroundColor: colorScheme.surfaceVariant,
          foregroundColor: colorScheme.onSurfaceVariant,
          disabledBackgroundColor: colorScheme.surfaceVariant.withOpacity(0.5),
          disabledForegroundColor: colorScheme.onSurface.withOpacity(0.38),
        );
      case ButtonVariant.danger:
        return ButtonColors(
          backgroundColor: colorScheme.error,
          foregroundColor: colorScheme.onError,
          disabledBackgroundColor: colorScheme.onSurface.withOpacity(0.12),
          disabledForegroundColor: colorScheme.onSurface.withOpacity(0.38),
        );
    }
  }
}

// Floating action button variant
class CustomFAB extends StatelessWidget {
  final VoidCallback? onPressed;
  final IconData icon;
  final String? tooltip;
  final bool isExtended;
  final String? label;

  const CustomFAB({
    super.key,
    required this.onPressed,
    required this.icon,
    this.tooltip,
    this.isExtended = false,
    this.label,
  });

  @override
  Widget build(BuildContext context) {
    if (isExtended && label != null) {
      return FloatingActionButton.extended(
        onPressed: onPressed,
        icon: Icon(icon),
        label: Text(label!),
        tooltip: tooltip,
      );
    }

    return FloatingActionButton(
      onPressed: onPressed,
      tooltip: tooltip,
      child: Icon(icon),
    );
  }
}