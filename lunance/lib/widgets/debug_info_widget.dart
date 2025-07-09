import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/auth_provider.dart';

class DebugInfoWidget extends StatelessWidget {
  const DebugInfoWidget({super.key});

  @override
  Widget build(BuildContext context) {
    return Consumer<AuthProvider>(
      builder: (context, authProvider, child) {
        return Card(
          margin: const EdgeInsets.all(16),
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Debug Info:',
                  style: Theme.of(context).textTheme.titleMedium?.copyWith(
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const SizedBox(height: 8),
                Text('Auth State: ${authProvider.authState}'),
                Text('Is Authenticated: ${authProvider.isAuthenticated}'),
                Text('Access Token: ${authProvider.accessToken != null ? 'Available' : 'Not available'}'),
                Text('User ID: ${authProvider.user?.id ?? 'N/A'}'),
                Text('User Email: ${authProvider.user?.email ?? 'N/A'}'),
                Text('User Role: ${authProvider.user?.role ?? 'N/A'}'),
                Text('User Verified: ${authProvider.user?.isVerified ?? 'N/A'}'),
                Text('Error Message: ${authProvider.errorMessage.isEmpty ? 'None' : authProvider.errorMessage}'),
                const SizedBox(height: 8),
                if (authProvider.user != null)
                  ExpansionTile(
                    title: const Text('Raw User Data'),
                    children: [
                      Container(
                        width: double.infinity,
                        padding: const EdgeInsets.all(8),
                        color: Theme.of(context).colorScheme.surfaceVariant,
                        child: Text(
                          authProvider.user!.toJson().toString(),
                          style: const TextStyle(
                            fontFamily: 'monospace',
                            fontSize: 12,
                          ),
                        ),
                      ),
                    ],
                  ),
              ],
            ),
          ),
        );
      },
    );
  }
}