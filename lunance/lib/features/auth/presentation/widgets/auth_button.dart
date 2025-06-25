// lib/features/auth/presentation/widgets/auth_button.dart
import 'package:flutter/material.dart';
import '../../../../core/theme/lunance_colors.dart';

class AuthButton extends StatefulWidget {
  final String text;
  final VoidCallback? onPressed;
  final bool isLoading;
  final bool isOutlined;
  final IconData? icon;
  final Color? backgroundColor;
  final Color? textColor;
  final double? width;
  final double height;

  const AuthButton({
    super.key,
    required this.text,
    this.onPressed,
    this.isLoading = false,
    this.isOutlined = false,
    this.icon,
    this.backgroundColor,
    this.textColor,
    this.width,
    this.height = 50,
  });

  @override
  State<AuthButton> createState() => _AuthButtonState();
}

class _AuthButtonState extends State<AuthButton>
    with SingleTickerProviderStateMixin {
  late AnimationController _animationController;
  late Animation<double> _scaleAnimation;
  late Animation<double> _shadowAnimation;
  bool _isPressed = false;

  @override
  void initState() {
    super.initState();
    _animationController = AnimationController(
      duration: const Duration(milliseconds: 150),
      vsync: this,
    );
    _scaleAnimation = Tween<double>(
      begin: 1.0,
      end: 0.95,
    ).animate(CurvedAnimation(
      parent: _animationController,
      curve: Curves.easeInOut,
    ));
    _shadowAnimation = Tween<double>(
      begin: 8.0,
      end: 2.0,
    ).animate(CurvedAnimation(
      parent: _animationController,
      curve: Curves.easeInOut,
    ));
  }

  @override
  void dispose() {
    _animationController.dispose();
    super.dispose();
  }

  void _onTapDown(TapDownDetails details) {
    setState(() {
      _isPressed = true;
    });
    _animationController.forward();
  }

  void _onTapUp(TapUpDetails details) {
    setState(() {
      _isPressed = false;
    });
    _animationController.reverse();
  }

  void _onTapCancel() {
    setState(() {
      _isPressed = false;
    });
    _animationController.reverse();
  }

  @override
  Widget build(BuildContext context) {
    final bool isEnabled = widget.onPressed != null && !widget.isLoading;

    return AnimatedBuilder(
      animation: _animationController,
      builder: (context, child) {
        return Transform.scale(
          scale: _scaleAnimation.value,
          child: Container(
            width: widget.width,
            height: widget.height,
            decoration: BoxDecoration(
              borderRadius: BorderRadius.circular(12),
              boxShadow: !widget.isOutlined
                  ? [
                      BoxShadow(
                        color: widget.backgroundColor?.withOpacity(0.3) ??
                            LunanceColors.primary.withOpacity(0.3),
                        blurRadius: _shadowAnimation.value,
                        offset: Offset(0, _shadowAnimation.value / 2),
                      ),
                    ]
                  : null,
            ),
            child: GestureDetector(
              onTapDown: isEnabled ? _onTapDown : null,
              onTapUp: isEnabled ? _onTapUp : null,
              onTapCancel: isEnabled ? _onTapCancel : null,
              onTap: isEnabled ? widget.onPressed : null,
              child: AnimatedContainer(
                duration: const Duration(milliseconds: 200),
                decoration: BoxDecoration(
                  gradient: !widget.isOutlined
                      ? LinearGradient(
                          begin: Alignment.topLeft,
                          end: Alignment.bottomRight,
                          colors: isEnabled
                              ? [
                                  widget.backgroundColor ?? LunanceColors.primary,
                                  widget.backgroundColor?.withOpacity(0.8) ??
                                      LunanceColors.primary.withOpacity(0.8),
                                ]
                              : [
                                  Colors.grey.withOpacity(0.6),
                                  Colors.grey.withOpacity(0.4),
                                ],
                        )
                      : null,
                  color: widget.isOutlined
                      ? Colors.transparent
                      : null,
                  borderRadius: BorderRadius.circular(12),
                  border: widget.isOutlined
                      ? Border.all(
                          color: isEnabled
                              ? widget.backgroundColor ?? LunanceColors.primary
                              : Colors.grey.withOpacity(0.6),
                          width: 2,
                        )
                      : null,
                ),
                child: Center(
                  child: widget.isLoading
                      ? SizedBox(
                          width: 20,
                          height: 20,
                          child: CircularProgressIndicator(
                            strokeWidth: 2,
                            valueColor: AlwaysStoppedAnimation<Color>(
                              widget.isOutlined
                                  ? widget.backgroundColor ?? LunanceColors.primary
                                  : Colors.white,
                            ),
                          ),
                        )
                      : Row(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            if (widget.icon != null) ...[
                              Icon(
                                widget.icon,
                                color: widget.isOutlined
                                    ? widget.textColor ??
                                        widget.backgroundColor ??
                                        LunanceColors.primary
                                    : widget.textColor ?? Colors.white,
                                size: 20,
                              ),
                              const SizedBox(width: 8),
                            ],
                            Text(
                              widget.text,
                              style: TextStyle(
                                color: widget.isOutlined
                                    ? widget.textColor ??
                                        widget.backgroundColor ??
                                        LunanceColors.primary
                                    : widget.textColor ?? Colors.white,
                                fontSize: 16,
                                fontWeight: FontWeight.w600,
                                letterSpacing: 0.5,
                              ),
                            ),
                          ],
                        ),
                ),
              ),
            ),
          ),
        );
      },
    );
  }
}