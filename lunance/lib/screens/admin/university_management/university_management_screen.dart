// lib/screens/admin/university_management/university_management_screen.dart
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../../providers/auth_provider.dart';
import '../../../providers/university_provider.dart';
import '../../../providers/university_request_provider.dart';
import '../../../models/university_model.dart';
import '../../../models/university_request_model.dart';
import '../../../widgets/common/loading_widget.dart';
import '../../../widgets/common/error_widget.dart';
import '../../../widgets/common/empty_state_widget.dart';
import '../../../widgets/common/snackbar_helper.dart';
import '../../../widgets/common/confirmation_dialog.dart';
import '../../../widgets/common/search_widget.dart';
import '../../../utils/extensions.dart';

class UniversityManagementScreen extends StatefulWidget {
  const UniversityManagementScreen({super.key});

  @override
  State<UniversityManagementScreen> createState() => _UniversityManagementScreenState();
}

class _UniversityManagementScreenState extends State<UniversityManagementScreen> {
  String _searchQuery = '';
  String _selectedTab = 'requests'; // 'requests' or 'universities'
  
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      _loadInitialData();
    });
  }

  Future<void> _loadInitialData() async {
    final authProvider = Provider.of<AuthProvider>(context, listen: false);
    final universityProvider = Provider.of<UniversityProvider>(context, listen: false);
    final requestProvider = Provider.of<UniversityRequestProvider>(context, listen: false);

    if (authProvider.tokens?.accessToken != null) {
      await Future.wait([
        requestProvider.loadAllRequests(
          token: authProvider.tokens!.accessToken,
          refresh: true,
        ),
        requestProvider.loadStats(authProvider.tokens!.accessToken),
        universityProvider.loadUniversities(
          token: authProvider.tokens!.accessToken,
          refresh: true,
        ),
        universityProvider.loadStats(authProvider.tokens!.accessToken),
      ]);
    }
  }

  Future<void> _refreshData() async {
    final authProvider = Provider.of<AuthProvider>(context, listen: false);
    final universityProvider = Provider.of<UniversityProvider>(context, listen: false);
    final requestProvider = Provider.of<UniversityRequestProvider>(context, listen: false);

    if (authProvider.tokens?.accessToken != null) {
      if (_selectedTab == 'requests') {
        await requestProvider.loadAllRequests(
          token: authProvider.tokens!.accessToken,
          refresh: true,
        );
      } else {
        await universityProvider.loadUniversities(
          token: authProvider.tokens!.accessToken,
          refresh: true,
        );
      }
    }
  }

  void _showAddUniversityDialog() {
    showDialog(
      context: context,
      builder: (context) => const _UniversityFormDialog(),
    );
  }

  void _showEditUniversityDialog(University university) {
    showDialog(
      context: context,
      builder: (context) => _UniversityFormDialog(university: university),
    );
  }

  Future<void> _deleteUniversity(University university) async {
    final confirmed = await ConfirmationDialog.show(
      context,
      title: 'Hapus Universitas',
      content: 'Apakah Anda yakin ingin menghapus universitas "${university.name}"?',
      confirmText: 'Hapus',
      isDestructive: true,
    );

    if (confirmed == true && mounted) {
      final authProvider = Provider.of<AuthProvider>(context, listen: false);
      final universityProvider = Provider.of<UniversityProvider>(context, listen: false);

      if (authProvider.tokens?.accessToken != null) {
        final success = await universityProvider.deleteUniversity(
          authProvider.tokens!.accessToken,
          university.id,
        );

        if (success && mounted) {
          SnackbarHelper.showSuccess(context, 'Universitas berhasil dihapus');
        } else if (mounted) {
          SnackbarHelper.showError(context, universityProvider.errorMessage ?? 'Gagal menghapus universitas');
        }
      }
    }
  }

  Future<void> _updateRequestStatus(String requestId, String status, String? notes) async {
    final authProvider = Provider.of<AuthProvider>(context, listen: false);
    final requestProvider = Provider.of<UniversityRequestProvider>(context, listen: false);

    if (authProvider.tokens?.accessToken != null) {
      final success = await requestProvider.updateRequestStatus(
        authProvider.tokens!.accessToken,
        requestId,
        status,
        adminNotes: notes,
      );

      if (success && mounted) {
        SnackbarHelper.showSuccess(context, 'Status permintaan berhasil diperbarui');
      } else if (mounted) {
        SnackbarHelper.showError(context, requestProvider.errorMessage ?? 'Gagal memperbarui status');
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return DefaultTabController(
      length: 2,
      child: Column(
        children: [
          // Tab Bar
          Container(
            margin: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: Theme.of(context).colorScheme.surface,
              borderRadius: BorderRadius.circular(8),
              border: Border.all(
                color: Theme.of(context).colorScheme.outline.withOpacity(0.2),
              ),
            ),
            child: TabBar(
              onTap: (index) {
                setState(() {
                  _selectedTab = index == 0 ? 'requests' : 'universities';
                });
              },
              tabs: const [
                Tab(text: 'Permintaan Universitas'),
                Tab(text: 'Kelola Universitas'),
              ],
            ),
          ),

          // Tab Content
          Expanded(
            child: TabBarView(
              children: [
                _buildRequestsTab(),
                _buildUniversitiesTab(),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildRequestsTab() {
    return Consumer<UniversityRequestProvider>(
      builder: (context, requestProvider, child) {
        if (requestProvider.isLoading && requestProvider.requests.isEmpty) {
          return const LoadingWidget(message: 'Memuat permintaan universitas...');
        }

        if (requestProvider.errorMessage != null && requestProvider.requests.isEmpty) {
          return ErrorDisplayWidget(
            message: requestProvider.errorMessage!,
            onRetry: _loadInitialData,
          );
        }

        return RefreshIndicator(
          onRefresh: _refreshData,
          child: CustomScrollView(
            slivers: [
              // Statistics Card
              SliverToBoxAdapter(
                child: _buildRequestStatsCard(requestProvider.stats),
              ),

              // Filter Section
              SliverToBoxAdapter(
                child: _buildRequestFilters(requestProvider),
              ),

              // Requests List
              if (requestProvider.requests.isEmpty)
                const SliverFillRemaining(
                  child: EmptyStateWidget(
                    icon: Icons.pending_actions,
                    title: 'Belum Ada Permintaan',
                    description: 'Permintaan universitas dari mahasiswa akan muncul di sini.',
                  ),
                )
              else
                SliverList(
                  delegate: SliverChildBuilderDelegate(
                    (context, index) {
                      final request = requestProvider.requests[index];
                      return _RequestItem(
                        request: request,
                        onStatusUpdate: (status, notes) => _updateRequestStatus(request.id, status, notes),
                      );
                    },
                    childCount: requestProvider.requests.length,
                  ),
                ),
            ],
          ),
        );
      },
    );
  }

  Widget _buildUniversitiesTab() {
    return Consumer<UniversityProvider>(
      builder: (context, universityProvider, child) {
        if (universityProvider.isLoading && universityProvider.universities.isEmpty) {
          return const LoadingWidget(message: 'Memuat universitas...');
        }

        if (universityProvider.errorMessage != null && universityProvider.universities.isEmpty) {
          return ErrorDisplayWidget(
            message: universityProvider.errorMessage!,
            onRetry: _loadInitialData,
          );
        }

        return RefreshIndicator(
          onRefresh: _refreshData,
          child: CustomScrollView(
            slivers: [
              // Statistics Card
              SliverToBoxAdapter(
                child: _buildUniversityStatsCard(universityProvider.stats),
              ),

              // Search and Add Button
              SliverToBoxAdapter(
                child: Padding(
                  padding: const EdgeInsets.all(16),
                  child: Row(
                    children: [
                      Expanded(
                        child: SearchWidget(
                          hint: 'Cari universitas...',
                          onChanged: (value) {
                            setState(() {
                              _searchQuery = value;
                            });
                          },
                        ),
                      ),
                      const SizedBox(width: 12),
                      ElevatedButton.icon(
                        onPressed: _showAddUniversityDialog,
                        icon: const Icon(Icons.add),
                        label: const Text('Tambah'),
                      ),
                    ],
                  ),
                ),
              ),

              // Universities List
              if (universityProvider.universities.isEmpty)
                const SliverFillRemaining(
                  child: EmptyStateWidget(
                    icon: Icons.school,
                    title: 'Belum Ada Universitas',
                    description: 'Kelola universitas dan fakultasnya di sini.',
                    buttonText: 'Tambah Universitas',
                  ),
                )
              else
                SliverList(
                  delegate: SliverChildBuilderDelegate(
                    (context, index) {
                      final university = universityProvider.universities[index];
                      if (_searchQuery.isNotEmpty && 
                          !university.name.toLowerCase().contains(_searchQuery.toLowerCase())) {
                        return const SizedBox.shrink();
                      }
                      return _UniversityItem(
                        university: university,
                        onEdit: () => _showEditUniversityDialog(university),
                        onDelete: () => _deleteUniversity(university),
                      );
                    },
                    childCount: universityProvider.universities.length,
                  ),
                ),
            ],
          ),
        );
      },
    );
  }

  Widget _buildRequestStatsCard(UniversityRequestStats? stats) {
    if (stats == null) return const SizedBox.shrink();

    return Card(
      margin: const EdgeInsets.all(16),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Statistik Permintaan',
              style: Theme.of(context).textTheme.titleMedium?.copyWith(
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 16),
            Row(
              children: [
                Expanded(
                  child: _StatItem(
                    title: 'Total',
                    count: stats.totalRequests,
                    icon: Icons.list,
                    color: Colors.blue,
                  ),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: _StatItem(
                    title: 'Pending',
                    count: stats.pendingRequests,
                    icon: Icons.pending,
                    color: Colors.orange,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),
            Row(
              children: [
                Expanded(
                  child: _StatItem(
                    title: 'Disetujui',
                    count: stats.approvedRequests,
                    icon: Icons.check_circle,
                    color: Colors.green,
                  ),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: _StatItem(
                    title: 'Ditolak',
                    count: stats.rejectedRequests,
                    icon: Icons.cancel,
                    color: Colors.red,
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildUniversityStatsCard(UniversityStats? stats) {
    if (stats == null) return const SizedBox.shrink();

    return Card(
      margin: const EdgeInsets.all(16),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Statistik Universitas',
              style: Theme.of(context).textTheme.titleMedium?.copyWith(
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 16),
            Row(
              children: [
                Expanded(
                  child: _StatItem(
                    title: 'Universitas',
                    count: stats.totalUniversities,
                    icon: Icons.school,
                    color: Colors.blue,
                  ),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: _StatItem(
                    title: 'Fakultas',
                    count: stats.totalFaculties,
                    icon: Icons.business,
                    color: Colors.green,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),
            Row(
              children: [
                Expanded(
                  child: _StatItem(
                    title: 'Jurusan',
                    count: stats.totalMajors,
                    icon: Icons.category,
                    color: Colors.purple,
                  ),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: _StatItem(
                    title: 'Aktif',
                    count: stats.activeUniversities,
                    icon: Icons.check_circle,
                    color: Colors.green,
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildRequestFilters(UniversityRequestProvider requestProvider) {
    return Card(
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Filter Permintaan',
              style: Theme.of(context).textTheme.titleMedium?.copyWith(
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 16),
            Row(
              children: [
                Expanded(
                  child: DropdownButtonFormField<String>(
                    value: requestProvider.statusFilter,
                    decoration: const InputDecoration(
                      labelText: 'Status',
                      border: OutlineInputBorder(),
                    ),
                    items: const [
                      DropdownMenuItem(value: null, child: Text('Semua Status')),
                      DropdownMenuItem(value: 'pending', child: Text('Pending')),
                      DropdownMenuItem(value: 'approved', child: Text('Disetujui')),
                      DropdownMenuItem(value: 'rejected', child: Text('Ditolak')),
                    ],
                    onChanged: (value) {
                      requestProvider.setStatusFilter(value);
                    },
                  ),
                ),
                const SizedBox(width: 16),
                ElevatedButton(
                  onPressed: () => _applyRequestFilters(requestProvider),
                  child: const Text('Terapkan'),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Future<void> _applyRequestFilters(UniversityRequestProvider requestProvider) async {
    final authProvider = Provider.of<AuthProvider>(context, listen: false);
    if (authProvider.tokens?.accessToken != null) {
      await requestProvider.applyFilters(authProvider.tokens!.accessToken);
    }
  }
}

class _StatItem extends StatelessWidget {
  final String title;
  final int count;
  final IconData icon;
  final Color color;

  const _StatItem({
    required this.title,
    required this.count,
    required this.icon,
    required this.color,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(8),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(icon, size: 16, color: color),
              const SizedBox(width: 4),
              Expanded(
                child: Text(
                  title,
                  style: Theme.of(context).textTheme.bodySmall,
                ),
              ),
            ],
          ),
          const SizedBox(height: 4),
          Text(
            count.toString(),
            style: Theme.of(context).textTheme.titleMedium?.copyWith(
              fontWeight: FontWeight.bold,
              color: color,
            ),
          ),
        ],
      ),
    );
  }
}

class _RequestItem extends StatelessWidget {
  final UniversityRequest request;
  final Function(String, String?) onStatusUpdate;

  const _RequestItem({
    required this.request,
    required this.onStatusUpdate,
  });

  @override
  Widget build(BuildContext context) {
    final statusColor = _getStatusColor(request.status);
    final statusText = _getStatusText(request.status);

    return Card(
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 4),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        request.universityName,
                        style: Theme.of(context).textTheme.titleMedium?.copyWith(
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        '${request.facultyName} - ${request.majorName}',
                        style: Theme.of(context).textTheme.bodyMedium,
                      ),
                    ],
                  ),
                ),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                  decoration: BoxDecoration(
                    color: statusColor.withOpacity(0.1),
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Text(
                    statusText,
                    style: TextStyle(
                      color: statusColor,
                      fontWeight: FontWeight.w500,
                      fontSize: 12,
                    ),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12),
            Row(
              children: [
                Icon(
                  Icons.person,
                  size: 16,
                  color: Theme.of(context).colorScheme.onSurface.withOpacity(0.6),
                ),
                const SizedBox(width: 4),
                Text(
                  request.userFullName ?? request.userEmail ?? 'Unknown',
                  style: Theme.of(context).textTheme.bodySmall?.copyWith(
                    color: Theme.of(context).colorScheme.onSurface.withOpacity(0.6),
                  ),
                ),
                const Spacer(),
                Text(
                  request.createdAt.toRelativeString(),
                  style: Theme.of(context).textTheme.bodySmall?.copyWith(
                    color: Theme.of(context).colorScheme.onSurface.withOpacity(0.6),
                  ),
                ),
              ],
            ),
            if (request.adminNotes != null) ...[
              const SizedBox(height: 8),
              Container(
                padding: const EdgeInsets.all(8),
                decoration: BoxDecoration(
                  color: Theme.of(context).colorScheme.surface,
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Row(
                  children: [
                    Icon(
                      Icons.note,
                      size: 16,
                      color: Theme.of(context).colorScheme.onSurface.withOpacity(0.6),
                    ),
                    const SizedBox(width: 8),
                    Expanded(
                      child: Text(
                        request.adminNotes!,
                        style: Theme.of(context).textTheme.bodySmall,
                      ),
                    ),
                  ],
                ),
              ),
            ],
            if (request.isPending) ...[
              const SizedBox(height: 12),
              Row(
                children: [
                  Expanded(
                    child: OutlinedButton(
                      onPressed: () => _showUpdateStatusDialog(context, request.id, 'rejected'),
                      style: OutlinedButton.styleFrom(
                        foregroundColor: Colors.red,
                        side: const BorderSide(color: Colors.red),
                      ),
                      child: const Text('Tolak'),
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: ElevatedButton(
                      onPressed: () => _showUpdateStatusDialog(context, request.id, 'approved'),
                      style: ElevatedButton.styleFrom(
                        backgroundColor: Colors.green,
                        foregroundColor: Colors.white,
                      ),
                      child: const Text('Setujui'),
                    ),
                  ),
                ],
              ),
            ],
          ],
        ),
      ),
    );
  }

  Color _getStatusColor(String status) {
    switch (status) {
      case 'pending':
        return Colors.orange;
      case 'approved':
        return Colors.green;
      case 'rejected':
        return Colors.red;
      default:
        return Colors.grey;
    }
  }

  String _getStatusText(String status) {
    switch (status) {
      case 'pending':
        return 'Pending';
      case 'approved':
        return 'Disetujui';
      case 'rejected':
        return 'Ditolak';
      default:
        return 'Unknown';
    }
  }

  void _showUpdateStatusDialog(BuildContext context, String requestId, String newStatus) {
    showDialog(
      context: context,
      builder: (context) => _UpdateStatusDialog(
        requestId: requestId,
        newStatus: newStatus,
        onUpdate: onStatusUpdate,
      ),
    );
  }
}

class _UpdateStatusDialog extends StatefulWidget {
  final String requestId;
  final String newStatus;
  final Function(String, String?) onUpdate;

  const _UpdateStatusDialog({
    required this.requestId,
    required this.newStatus,
    required this.onUpdate,
  });

  @override
  State<_UpdateStatusDialog> createState() => _UpdateStatusDialogState();
}

class _UpdateStatusDialogState extends State<_UpdateStatusDialog> {
  final _notesController = TextEditingController();

  @override
  void dispose() {
    _notesController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final isApproval = widget.newStatus == 'approved';
    final title = isApproval ? 'Setujui Permintaan' : 'Tolak Permintaan';
    final actionText = isApproval ? 'Setujui' : 'Tolak';

    return AlertDialog(
      title: Text(title),
      content: Column(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text('Apakah Anda yakin ingin $actionText permintaan ini?'),
          const SizedBox(height: 16),
          TextField(
            controller: _notesController,
            decoration: const InputDecoration(
              labelText: 'Catatan Admin (Opsional)',
              border: OutlineInputBorder(),
              hintText: 'Tambahkan catatan untuk pengguna...',
            ),
            maxLines: 3,
          ),
        ],
      ),
      actions: [
        TextButton(
          onPressed: () => Navigator.pop(context),
          child: const Text('Batal'),
        ),
        ElevatedButton(
          onPressed: () {
            widget.onUpdate(widget.newStatus, _notesController.text.trim().isNotEmpty ? _notesController.text.trim() : null);
            Navigator.pop(context);
          },
          style: ElevatedButton.styleFrom(
            backgroundColor: isApproval ? Colors.green : Colors.red,
            foregroundColor: Colors.white,
          ),
          child: Text(actionText),
        ),
      ],
    );
  }
}

class _UniversityItem extends StatelessWidget {
  final University university;
  final VoidCallback onEdit;
  final VoidCallback onDelete;

  const _UniversityItem({
    required this.university,
    required this.onEdit,
    required this.onDelete,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 4),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        university.name,
                        style: Theme.of(context).textTheme.titleMedium?.copyWith(
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      const SizedBox(height: 4),
                      Row(
                        children: [
                          Icon(
                            university.isActive ? Icons.check_circle : Icons.cancel,
                            size: 16,
                            color: university.isActive ? Colors.green : Colors.red,
                          ),
                          const SizedBox(width: 4),
                          Text(
                            university.isActive ? 'Aktif' : 'Tidak Aktif',
                            style: TextStyle(
                              color: university.isActive ? Colors.green : Colors.red,
                              fontWeight: FontWeight.w500,
                            ),
                          ),
                        ],
                      ),
                    ],
                  ),
                ),
                PopupMenuButton<String>(
                  onSelected: (value) {
                    if (value == 'edit') {
                      onEdit();
                    } else if (value == 'delete') {
                      onDelete();
                    }
                  },
                  itemBuilder: (context) => [
                    const PopupMenuItem(
                      value: 'edit',
                      child: Row(
                        children: [
                          Icon(Icons.edit, size: 16),
                          SizedBox(width: 8),
                          Text('Edit'),
                        ],
                      ),
                    ),
                    const PopupMenuItem(
                      value: 'delete',
                      child: Row(
                        children: [
                          Icon(Icons.delete, size: 16, color: Colors.red),
                          SizedBox(width: 8),
                          Text('Hapus', style: TextStyle(color: Colors.red)),
                        ],
                      ),
                    ),
                  ],
                ),
              ],
            ),
            const SizedBox(height: 12),
            Row(
              children: [
                _InfoChip(
                  icon: Icons.business,
                  label: '${university.facultyCount ?? university.faculties.length} Fakultas',
                ),
                const SizedBox(width: 8),
                _InfoChip(
                  icon: Icons.category,
                  label: '${university.majorCount ?? university.faculties.fold<int>(0, (sum, f) => sum + f.majors.length)} Jurusan',
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}

class _InfoChip extends StatelessWidget {
  final IconData icon;
  final String label;

  const _InfoChip({
    required this.icon,
    required this.label,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      decoration: BoxDecoration(
        color: Theme.of(context).colorScheme.primary.withOpacity(0.1),
        borderRadius: BorderRadius.circular(12),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, size: 14, color: Theme.of(context).colorScheme.primary),
          const SizedBox(width: 4),
          Text(
            label,
            style: TextStyle(
              color: Theme.of(context).colorScheme.primary,
              fontSize: 12,
              fontWeight: FontWeight.w500,
            ),
          ),
        ],
      ),
    );
  }
}

class _UniversityFormDialog extends StatefulWidget {
  final University? university;

  const _UniversityFormDialog({this.university});

  @override
  State<_UniversityFormDialog> createState() => _UniversityFormDialogState();
}

class _UniversityFormDialogState extends State<_UniversityFormDialog> {
  final _formKey = GlobalKey<FormState>();
  final _nameController = TextEditingController();
  bool _isActive = true;
  bool _isLoading = false;

  @override
  void initState() {
    super.initState();
    if (widget.university != null) {
      _nameController.text = widget.university!.name;
      _isActive = widget.university!.isActive;
    }
  }

  @override
  void dispose() {
    _nameController.dispose();
    super.dispose();
  }

  Future<void> _saveUniversity() async {
    if (!_formKey.currentState!.validate()) return;

    setState(() {
      _isLoading = true;
    });

    try {
      final authProvider = Provider.of<AuthProvider>(context, listen: false);
      final universityProvider = Provider.of<UniversityProvider>(context, listen: false);
      
      if (authProvider.tokens?.accessToken == null) {
        SnackbarHelper.showError(context, 'Sesi telah berakhir');
        return;
      }

      bool success;
      if (widget.university == null) {
        // Create new university
        final university = UniversityCreate(
          name: _nameController.text,
          isActive: _isActive,
          faculties: [],
        );
        success = await universityProvider.createUniversity(
          authProvider.tokens!.accessToken,
          university,
        );
      } else {
        // Update existing university
        final updates = {
          'name': _nameController.text,
          'is_active': _isActive,
        };
        success = await universityProvider.updateUniversity(
          authProvider.tokens!.accessToken,
          widget.university!.id,
          updates,
        );
      }

      if (success && mounted) {
        SnackbarHelper.showSuccess(
          context,
          widget.university == null ? 'Universitas berhasil dibuat' : 'Universitas berhasil diperbarui',
        );
        Navigator.pop(context);
      } else if (mounted) {
        SnackbarHelper.showError(context, universityProvider.errorMessage ?? 'Terjadi kesalahan');
      }
    } catch (e) {
      if (mounted) {
        SnackbarHelper.showError(context, 'Terjadi kesalahan: $e');
      }
    } finally {
      if (mounted) {
        setState(() {
          _isLoading = false;
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      title: Text(widget.university == null ? 'Tambah Universitas' : 'Edit Universitas'),
      content: Form(
        key: _formKey,
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            TextFormField(
              controller: _nameController,
              decoration: const InputDecoration(
                labelText: 'Nama Universitas',
                border: OutlineInputBorder(),
              ),
              validator: (value) {
                if (value == null || value.isEmpty) {
                  return 'Nama universitas tidak boleh kosong';
                }
                if (value.length < 2 || value.length > 150) {
                  return 'Nama universitas harus 2-150 karakter';
                }
                return null;
              },
            ),
            const SizedBox(height: 16),
            CheckboxListTile(
              title: const Text('Aktif'),
              value: _isActive,
              onChanged: (value) {
                setState(() {
                  _isActive = value ?? true;
                });
              },
            ),
          ],
        ),
      ),
      actions: [
        TextButton(
          onPressed: _isLoading ? null : () => Navigator.pop(context),
          child: const Text('Batal'),
        ),
        ElevatedButton(
          onPressed: _isLoading ? null : _saveUniversity,
          child: _isLoading
              ? const SizedBox(
                  height: 20,
                  width: 20,
                  child: CircularProgressIndicator(strokeWidth: 2),
                )
              : Text(widget.university == null ? 'Simpan' : 'Perbarui'),
        ),
      ],
    );
  }
}