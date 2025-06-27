// lib/core/widgets/error_widget.dart
import 'package:flutter/material.dart';
import 'package:lunance/core/theme/lunance_colors.dart';

class CustomErrorWidget extends StatelessWidget {
  final String? title;
  final String message;
  final IconData? icon;
  final VoidCallback? onRetry;
  final String? retryButtonText;
  final bool showRetryButton;
  final Widget? customAction;
  final Color? iconColor;
  final TextStyle? titleStyle;
  final TextStyle? messageStyle;

  const CustomErrorWidget({
    Key? key,
    this.title,
    required this.message,
    this.icon,
    this.onRetry,
    this.retryButtonText,
    this.showRetryButton = true,
    this.customAction,
    this.iconColor,
    this.titleStyle,
    this.messageStyle,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final isDark = theme.brightness == Brightness.dark;

    return Center(
      child: Padding(
        padding: const EdgeInsets.all(24.0),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              icon ?? Icons.error_outline,
              size: 80,
              color: iconColor ?? LunanceColors.error,
            ),
            const SizedBox(height: 24),
            if (title != null) ...[
              Text(
                title!,
                style: titleStyle ?? TextStyle(
                  fontSize: 24,
                  fontWeight: FontWeight.bold,
                  color: isDark ? Colors.white : LunanceColors.textPrimary,
                ),
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 16),
            ],
            Text(
              message,
              style: messageStyle ?? TextStyle(
                fontSize: 16,
                color: isDark ? Colors.white70 : LunanceColors.textSecondary,
                height: 1.5,
              ),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 32),
            if (customAction != null)
              customAction!
            else if (showRetryButton && onRetry != null)
              ElevatedButton.icon(
                onPressed: onRetry,
                icon: const Icon(Icons.refresh),
                label: Text(retryButtonText ?? 'Try Again'),
                style: ElevatedButton.styleFrom(
                  backgroundColor: LunanceColors.primary,
                  foregroundColor: Colors.white,
                  padding: const EdgeInsets.symmetric(
                    horizontal: 32,
                    vertical: 16,
                  ),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(12),
                  ),
                ),
              ),
          ],
        ),
      ),
    );
  }
}

// Network Error Widget
class NetworkErrorWidget extends StatelessWidget {
  final VoidCallback? onRetry;
  final String? customMessage;

  const NetworkErrorWidget({
    Key? key,
    this.onRetry,
    this.customMessage,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return CustomErrorWidget(
      title: 'No Internet Connection',
      message: customMessage ?? 
          'Please check your internet connection and try again.',
      icon: Icons.wifi_off,
      iconColor: LunanceColors.warning,
      onRetry: onRetry,
      retryButtonText: 'Retry',
    );
  }
}

// Server Error Widget
class ServerErrorWidget extends StatelessWidget {
  final VoidCallback? onRetry;
  final String? customMessage;

  const ServerErrorWidget({
    Key? key,
    this.onRetry,
    this.customMessage,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return CustomErrorWidget(
      title: 'Server Error',
      message: customMessage ?? 
          'Something went wrong on our end. Please try again later.',
      icon: Icons.cloud_off,
      iconColor: LunanceColors.error,
      onRetry: onRetry,
      retryButtonText: 'Try Again',
    );
  }
}

// Not Found Error Widget
class NotFoundErrorWidget extends StatelessWidget {
  final String? title;
  final String? message;
  final VoidCallback? onGoBack;
  final String? actionButtonText;

  const NotFoundErrorWidget({
    Key? key,
    this.title,
    this.message,
    this.onGoBack,
    this.actionButtonText,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return CustomErrorWidget(
      title: title ?? '404 - Not Found',
      message: message ?? 
          'The page you are looking for could not be found.',
      icon: Icons.search_off,
      iconColor: LunanceColors.info,
      showRetryButton: false,
      customAction: ElevatedButton.icon(
        onPressed: onGoBack ?? () => Navigator.of(context).pop(),
        icon: const Icon(Icons.arrow_back),
        label: Text(actionButtonText ?? 'Go Back'),
        style: ElevatedButton.styleFrom(
          backgroundColor: LunanceColors.primary,
          foregroundColor: Colors.white,
          padding: const EdgeInsets.symmetric(
            horizontal: 32,
            vertical: 16,
          ),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(12),
          ),
        ),
      ),
    );
  }
}

// Empty State Widget
class EmptyStateWidget extends StatelessWidget {
  final String title;
  final String message;
  final IconData? icon;
  final Widget? action;
  final String? actionButtonText;
  final VoidCallback? onActionPressed;

  const EmptyStateWidget({
    Key? key,
    required this.title,
    required this.message,
    this.icon,
    this.action,
    this.actionButtonText,
    this.onActionPressed,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final isDark = theme.brightness == Brightness.dark;

    return Center(
      child: Padding(
        padding: const EdgeInsets.all(24.0),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              icon ?? Icons.inbox_outlined,
              size: 80,
              color: isDark ? Colors.white38 : LunanceColors.textHint,
            ),
            const SizedBox(height: 24),
            Text(
              title,
              style: TextStyle(
                fontSize: 24,
                fontWeight: FontWeight.bold,
                color: isDark ? Colors.white : LunanceColors.textPrimary,
              ),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 16),
            Text(
              message,
              style: TextStyle(
                fontSize: 16,
                color: isDark ? Colors.white70 : LunanceColors.textSecondary,
                height: 1.5,
              ),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 32),
            if (action != null)
              action!
            else if (onActionPressed != null)
              ElevatedButton(
                onPressed: onActionPressed,
                style: ElevatedButton.styleFrom(
                  backgroundColor: LunanceColors.primary,
                  foregroundColor: Colors.white,
                  padding: const EdgeInsets.symmetric(
                    horizontal: 32,
                    vertical: 16,
                  ),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(12),
                  ),
                ),
                child: Text(actionButtonText ?? 'Get Started'),
              ),
          ],
        ),
      ),
    );
  }
}

// Loading Error Widget
class LoadingErrorWidget extends StatelessWidget {
  final String? message;
  final VoidCallback? onRetry;

  const LoadingErrorWidget({
    Key? key,
    this.message,
    this.onRetry,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return CustomErrorWidget(
      title: 'Loading Failed',
      message: message ?? 'Failed to load data. Please try again.',
      icon: Icons.refresh,
      iconColor: LunanceColors.warning,
      onRetry: onRetry,
      retryButtonText: 'Reload',
    );
  }
}

// Permission Error Widget
class PermissionErrorWidget extends StatelessWidget {
  final String title;
  final String message;
  final VoidCallback? onRequestPermission;
  final VoidCallback? onOpenSettings;

  const PermissionErrorWidget({
    Key? key,
    required this.title,
    required this.message,
    this.onRequestPermission,
    this.onOpenSettings,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return CustomErrorWidget(
      title: title,
      message: message,
      icon: Icons.lock_outline,
      iconColor: LunanceColors.warning,
      showRetryButton: false,
      customAction: Column(
        children: [
          if (onRequestPermission != null)
            ElevatedButton.icon(
              onPressed: onRequestPermission,
              icon: const Icon(Icons.security),
              label: const Text('Grant Permission'),
              style: ElevatedButton.styleFrom(
                backgroundColor: LunanceColors.primary,
                foregroundColor: Colors.white,
                padding: const EdgeInsets.symmetric(
                  horizontal: 32,
                  vertical: 16,
                ),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(12),
                ),
              ),
            ),
          if (onRequestPermission != null && onOpenSettings != null)
            const SizedBox(height: 12),
          if (onOpenSettings != null)
            OutlinedButton.icon(
              onPressed: onOpenSettings,
              icon: const Icon(Icons.settings),
              label: const Text('Open Settings'),
              style: OutlinedButton.styleFrom(
                foregroundColor: LunanceColors.primary,
                side: const BorderSide(color: LunanceColors.primary),
                padding: const EdgeInsets.symmetric(
                  horizontal: 32,
                  vertical: 16,
                ),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(12),
                ),
              ),
            ),
        ],
      ),
    );
  }
}