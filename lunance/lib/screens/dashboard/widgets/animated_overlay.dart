import 'package:flutter/material.dart';
import '../../../utils/app_colors.dart';

class AnimatedOverlay extends StatelessWidget {
  final Animation<double> animation;
  final bool isLeftSidebarOpen;
  final bool isRightSidebarOpen;
  final Animation<double> leftSidebarAnimation;
  final Animation<double> rightSidebarAnimation;
  final VoidCallback onTap;

  const AnimatedOverlay({
    Key? key,
    required this.animation,
    required this.isLeftSidebarOpen,
    required this.isRightSidebarOpen,
    required this.leftSidebarAnimation,
    required this.rightSidebarAnimation,
    required this.onTap,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: animation,
      builder: (context, child) {
        if (animation.value == 0.0) {
          return Container(); // Don't show overlay when closed
        }

        double translateX = 0.0;
        if (isLeftSidebarOpen) {
          translateX = leftSidebarAnimation.value;
        } else if (isRightSidebarOpen) {
          translateX = -rightSidebarAnimation.value;
        }

        return Positioned.fill(
          child: Transform.translate(
            offset: Offset(translateX, 0.0),
            child: GestureDetector(
              onTap: onTap,
              child: AnimatedContainer(
                duration: const Duration(milliseconds: 300),
                decoration: BoxDecoration(
                  gradient: LinearGradient(
                    begin: isLeftSidebarOpen 
                        ? Alignment.centerLeft 
                        : Alignment.centerRight,
                    end: isLeftSidebarOpen 
                        ? Alignment.centerRight 
                        : Alignment.centerLeft,
                    stops: const [0.0, 0.3, 0.7, 1.0],
                    colors: [
                      Colors.black.withOpacity(0.1 * animation.value),
                      Colors.black.withOpacity(0.2 * animation.value),
                      Colors.black.withOpacity(0.3 * animation.value),
                      Colors.black.withOpacity(0.4 * animation.value),
                    ],
                  ),
                ),
                child: _buildAnimatedPattern(),
              ),
            ),
          ),
        );
      },
    );
  }

  Widget _buildAnimatedPattern() {
    return AnimatedBuilder(
      animation: animation,
      builder: (context, child) {
        return CustomPaint(
          painter: OverlayPatternPainter(
            animationValue: animation.value,
            isLeftSidebar: isLeftSidebarOpen,
          ),
          size: Size.infinite,
        );
      },
    );
  }
}

class OverlayPatternPainter extends CustomPainter {
  final double animationValue;
  final bool isLeftSidebar;

  OverlayPatternPainter({
    required this.animationValue,
    required this.isLeftSidebar,
  });

  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..style = PaintingStyle.fill;

    // Create subtle animated dots pattern
    final dotRadius = 1.0 * animationValue;
    final spacing = 30.0;
    
    for (double x = 0; x < size.width; x += spacing) {
      for (double y = 0; y < size.height; y += spacing) {
        // Offset pattern based on sidebar direction
        final offsetX = isLeftSidebar ? x + (10 * animationValue) : x - (10 * animationValue);
        final offsetY = y + (5 * animationValue);
        
        paint.color = Colors.white.withOpacity(0.02 * animationValue);
        canvas.drawCircle(
          Offset(offsetX, offsetY),
          dotRadius,
          paint,
        );
      }
    }

    // Add subtle wave effect
    final wavePath = Path();
    final waveHeight = 5.0 * animationValue;
    final waveWidth = size.width / 4;
    
    wavePath.moveTo(0, size.height / 2);
    
    for (double x = 0; x <= size.width; x += waveWidth) {
  final y = (size.height / 2) +
            (waveHeight * (isLeftSidebar ? 1 : -1)) *
            (((x / waveWidth).remainder(2.0) == 0) ? 1 : -1);
  wavePath.lineTo(x, y);
}

    
    paint.color = AppColors.primary.withOpacity(0.01 * animationValue);
    paint.style = PaintingStyle.stroke;
    paint.strokeWidth = 1.0 * animationValue;
    canvas.drawPath(wavePath, paint);
  }

  @override
  bool shouldRepaint(OverlayPatternPainter oldDelegate) {
    return animationValue != oldDelegate.animationValue ||
           isLeftSidebar != oldDelegate.isLeftSidebar;
  }
}