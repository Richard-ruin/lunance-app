
// lib/shared/widgets/profile_image_widget.dart
import 'package:flutter/material.dart';
import 'package:cached_network_image/cached_network_image.dart';
import 'package:lunance/core/constants/api_endpoints.dart';

class ProfileImageWidget extends StatelessWidget {
  final String? imagePath;
  final double size;
  final bool showBorder;
  final VoidCallback? onTap;
  final bool showEditIcon;

  const ProfileImageWidget({
    super.key,
    this.imagePath,
    this.size = 50,
    this.showBorder = true,
    this.onTap,
    this.showEditIcon = false,
  });

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Stack(
        children: [
          Container(
            width: size,
            height: size,
            decoration: BoxDecoration(
              shape: BoxShape.circle,
              border: showBorder
                  ? Border.all(
                      color: Theme.of(context).primaryColor.withOpacity(0.3),
                      width: 2,
                    )
                  : null,
            ),
            child: ClipOval(
              child: _buildImage(context),
            ),
          ),
          if (showEditIcon)
            Positioned(
              bottom: 0,
              right: 0,
              child: Container(
                width: size * 0.3,
                height: size * 0.3,
                decoration: BoxDecoration(
                  color: Theme.of(context).primaryColor,
                  shape: BoxShape.circle,
                  border: Border.all(color: Colors.white, width: 2),
                ),
                child: Icon(
                  Icons.camera_alt,
                  size: size * 0.15,
                  color: Colors.white,
                ),
              ),
            ),
        ],
      ),
    );
  }

  Widget _buildImage(BuildContext context) {
    if (imagePath == null || imagePath!.isEmpty) {
      return _buildPlaceholder(context);
    }

    final imageUrl = _buildImageUrl(imagePath!);

    return CachedNetworkImage(
      imageUrl: imageUrl,
      fit: BoxFit.cover,
      placeholder: (context, url) => _buildLoadingPlaceholder(),
      errorWidget: (context, url, error) {
        debugPrint('Error loading profile image: $error');
        debugPrint('Image URL: $imageUrl');
        return _buildPlaceholder(context);
      },
    );
  }

  String _buildImageUrl(String path) {
    // Jika path sudah berupa URL lengkap, gunakan langsung
    if (path.startsWith('http://') || path.startsWith('https://')) {
      return path;
    }

    // Jika path dimulai dengan '/static', tambahkan base URL
    if (path.startsWith('/static')) {
      return '${ApiEndpoints.baseUrl}$path';
    }

    // Jika path tidak dimulai dengan '/', tambahkan prefix
    if (!path.startsWith('/')) {
      return '${ApiEndpoints.baseUrl}/static/uploads/profile_pictures/$path';
    }

    return '${ApiEndpoints.baseUrl}$path';
  }

  Widget _buildPlaceholder(BuildContext context) {
    return Container(
      color: Theme.of(context).colorScheme.surfaceContainerHighest,
      child: Icon(
        Icons.person,
        size: size * 0.6,
        color: Theme.of(context).colorScheme.onSurface.withOpacity(0.5),
      ),
    );
  }

  Widget _buildLoadingPlaceholder() {
    return Container(
      color: Colors.grey[200],
      child: Center(
        child: SizedBox(
          width: size * 0.3,
          height: size * 0.3,
          child: CircularProgressIndicator(
            strokeWidth: 2,
            valueColor: AlwaysStoppedAnimation<Color>(
              Colors.grey[400]!,
            ),
          ),
        ),
      ),
    );
  }
}
