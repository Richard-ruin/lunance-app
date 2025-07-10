import 'package:flutter/material.dart';
import '../../../utils/app_colors.dart';
import '../../../utils/app_text_styles.dart';

class ChatHistoryView extends StatefulWidget {
  const ChatHistoryView({Key? key}) : super(key: key);

  @override
  State<ChatHistoryView> createState() => _ChatHistoryViewState();
}

class _ChatHistoryViewState extends State<ChatHistoryView> 
    with TickerProviderStateMixin {
  
  final TextEditingController _searchController = TextEditingController();
  String _searchQuery = '';
  String _selectedFilter = 'All';
  
  late AnimationController _fadeController;
  late Animation<double> _fadeAnimation;

  // Mock data for chat history
  final List<ChatHistoryItem> _chatHistory = [
    ChatHistoryItem(
      id: '1',
      title: 'Analisis Pengeluaran Bulanan',
      lastMessage: 'Berdasarkan data Anda, pengeluaran terbesar ada di kategori makanan...',
      timestamp: DateTime.now().subtract(const Duration(hours: 2)),
      category: 'Analysis',
      messageCount: 12,
      icon: Icons.analytics_outlined,
      color: AppColors.primary,
    ),
    ChatHistoryItem(
      id: '2',
      title: 'Tips Menghemat Listrik',
      lastMessage: 'Beberapa cara untuk mengurangi tagihan listrik bulanan Anda...',
      timestamp: DateTime.now().subtract(const Duration(days: 1)),
      category: 'Tips',
      messageCount: 8,
      icon: Icons.lightbulb_outline,
      color: AppColors.warning,
    ),
    ChatHistoryItem(
      id: '3',
      title: 'Rencana Investasi 2025',
      lastMessage: 'Mari kita susun strategi investasi yang sesuai dengan profil risiko Anda...',
      timestamp: DateTime.now().subtract(const Duration(days: 3)),
      category: 'Planning',
      messageCount: 15,
      icon: Icons.trending_up,
      color: AppColors.success,
    ),
    ChatHistoryItem(
      id: '4',
      title: 'Budget Liburan ke Bali',
      lastMessage: 'Untuk liburan 5 hari ke Bali, estimasi budget yang diperlukan...',
      timestamp: DateTime.now().subtract(const Duration(days: 7)),
      category: 'Planning',
      messageCount: 6,
      icon: Icons.flight_outlined,
      color: AppColors.info,
    ),
    ChatHistoryItem(
      id: '5',
      title: 'Pencatatan Gaji Bulan Ini',
      lastMessage: 'Gaji bulan ini sebesar Rp 5.200.000 telah dicatat...',
      timestamp: DateTime.now().subtract(const Duration(days: 15)),
      category: 'Transaction',
      messageCount: 3,
      icon: Icons.account_balance_wallet,
      color: AppColors.success,
    ),
    ChatHistoryItem(
      id: '6',
      title: 'Setup Emergency Fund',
      lastMessage: 'Dana darurat sebaiknya setara dengan 6-12 bulan pengeluaran...',
      timestamp: DateTime.now().subtract(const Duration(days: 20)),
      category: 'Planning',
      messageCount: 10,
      icon: Icons.security,
      color: AppColors.error,
    ),
  ];

  List<ChatHistoryItem> get _filteredHistory {
    var filtered = _chatHistory.where((item) {
      final matchesSearch = _searchQuery.isEmpty ||
          item.title.toLowerCase().contains(_searchQuery.toLowerCase()) ||
          item.lastMessage.toLowerCase().contains(_searchQuery.toLowerCase());
      
      final matchesFilter = _selectedFilter == 'All' || 
          item.category == _selectedFilter;
      
      return matchesSearch && matchesFilter;
    }).toList();
    
    // Sort by timestamp (newest first)
    filtered.sort((a, b) => b.timestamp.compareTo(a.timestamp));
    return filtered;
  }

  @override
  void initState() {
    super.initState();
    
    _fadeController = AnimationController(
      duration: const Duration(milliseconds: 600),
      vsync: this,
    );
    
    _fadeAnimation = Tween<double>(
      begin: 0.0,
      end: 1.0,
    ).animate(CurvedAnimation(
      parent: _fadeController,
      curve: Curves.easeOut,
    ));
    
    _fadeController.forward();
    
    _searchController.addListener(() {
      setState(() {
        _searchQuery = _searchController.text;
      });
    });
  }

  @override
  void dispose() {
    _fadeController.dispose();
    _searchController.dispose();
    super.dispose();
  }

  String _formatTimestamp(DateTime timestamp) {
    final now = DateTime.now();
    final difference = now.difference(timestamp);
    
    if (difference.inDays == 0) {
      if (difference.inHours == 0) {
        return '${difference.inMinutes} menit yang lalu';
      }
      return '${difference.inHours} jam yang lalu';
    } else if (difference.inDays == 1) {
      return 'Kemarin';
    } else if (difference.inDays < 7) {
      return '${difference.inDays} hari yang lalu';
    } else if (difference.inDays < 30) {
      final weeks = (difference.inDays / 7).floor();
      return '$weeks minggu yang lalu';
    } else {
      final months = (difference.inDays / 30).floor();
      return '$months bulan yang lalu';
    }
  }

  void _showComingSoonDialog(String feature) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(16),
        ),
        title: Text(
          feature,
          style: AppTextStyles.h6,
        ),
        content: Text(
          'Fitur $feature akan segera tersedia dalam update mendatang.',
          style: AppTextStyles.bodyMedium,
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: Text(
              'OK',
              style: AppTextStyles.labelMedium.copyWith(
                color: AppColors.primary,
              ),
            ),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return FadeTransition(
      opacity: _fadeAnimation,
      child: Column(
        children: [
          // Search and Filter Header
          _buildHeader(),
          
          // Chat History List
          Expanded(
            child: _filteredHistory.isEmpty 
                ? _buildEmptyState()
                : _buildHistoryList(),
          ),
        ],
      ),
    );
  }

  Widget _buildHeader() {
    return Container(
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        color: AppColors.white,
        border: Border(
          bottom: BorderSide(color: AppColors.border, width: 1),
        ),
      ),
      child: Column(
        children: [
          // Search Bar
          Container(
            decoration: BoxDecoration(
              color: AppColors.gray50,
              borderRadius: BorderRadius.circular(12),
              border: Border.all(color: AppColors.border),
            ),
            child: TextField(
              controller: _searchController,
              decoration: InputDecoration(
                hintText: 'Cari riwayat chat...',
                hintStyle: AppTextStyles.bodyMedium.copyWith(
                  color: AppColors.gray400,
                ),
                prefixIcon: Icon(
                  Icons.search,
                  color: AppColors.gray400,
                ),
                border: InputBorder.none,
                contentPadding: const EdgeInsets.symmetric(
                  horizontal: 16,
                  vertical: 16,
                ),
              ),
              style: AppTextStyles.bodyMedium,
            ),
          ),
          
          const SizedBox(height: 16),
          
          // Filter Chips
          SingleChildScrollView(
            scrollDirection: Axis.horizontal,
            child: Row(
              children: [
                _buildFilterChip('All'),
                const SizedBox(width: 8),
                _buildFilterChip('Analysis'),
                const SizedBox(width: 8),
                _buildFilterChip('Planning'),
                const SizedBox(width: 8),
                _buildFilterChip('Transaction'),
                const SizedBox(width: 8),
                _buildFilterChip('Tips'),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildFilterChip(String filter) {
    final isSelected = _selectedFilter == filter;
    
    return FilterChip(
      label: Text(
        filter,
        style: AppTextStyles.labelMedium.copyWith(
          color: isSelected ? AppColors.white : AppColors.gray600,
          fontWeight: isSelected ? FontWeight.w600 : FontWeight.normal,
        ),
      ),
      selected: isSelected,
      onSelected: (selected) {
        setState(() {
          _selectedFilter = filter;
        });
      },
      backgroundColor: AppColors.gray100,
      selectedColor: AppColors.primary,
      checkmarkColor: AppColors.white,
      side: BorderSide(
        color: isSelected ? AppColors.primary : AppColors.border,
      ),
    );
  }

  Widget _buildHistoryList() {
    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: _filteredHistory.length,
      itemBuilder: (context, index) {
        final item = _filteredHistory[index];
        return _buildHistoryItem(item, index);
      },
    );
  }

  Widget _buildHistoryItem(ChatHistoryItem item, int index) {
    return Container(
      margin: const EdgeInsets.only(bottom: 16),
      child: Material(
        color: Colors.transparent,
        child: InkWell(
          onTap: () => _showComingSoonDialog('Open Chat: ${item.title}'),
          borderRadius: BorderRadius.circular(16),
          child: Container(
            padding: const EdgeInsets.all(20),
            decoration: BoxDecoration(
              color: AppColors.white,
              borderRadius: BorderRadius.circular(16),
              border: Border.all(color: AppColors.border.withOpacity(0.5)),
              boxShadow: [
                BoxShadow(
                  color: AppColors.shadow.withOpacity(0.1),
                  blurRadius: 8,
                  offset: const Offset(0, 2),
                ),
              ],
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Container(
                      width: 48,
                      height: 48,
                      decoration: BoxDecoration(
                        color: item.color.withOpacity(0.1),
                        borderRadius: BorderRadius.circular(12),
                      ),
                      child: Icon(
                        item.icon,
                        size: 24,
                        color: item.color,
                      ),
                    ),
                    const SizedBox(width: 16),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            item.title,
                            style: AppTextStyles.labelLarge.copyWith(
                              fontWeight: FontWeight.w600,
                              color: AppColors.gray800,
                            ),
                            maxLines: 1,
                            overflow: TextOverflow.ellipsis,
                          ),
                          const SizedBox(height: 4),
                          Row(
                            children: [
                              Container(
                                padding: const EdgeInsets.symmetric(
                                  horizontal: 8,
                                  vertical: 2,
                                ),
                                decoration: BoxDecoration(
                                  color: item.color.withOpacity(0.1),
                                  borderRadius: BorderRadius.circular(8),
                                ),
                                child: Text(
                                  item.category,
                                  style: AppTextStyles.caption.copyWith(
                                    color: item.color,
                                    fontWeight: FontWeight.w600,
                                  ),
                                ),
                              ),
                              const SizedBox(width: 8),
                              Text(
                                '${item.messageCount} pesan',
                                style: AppTextStyles.caption.copyWith(
                                  color: AppColors.textSecondary,
                                ),
                              ),
                            ],
                          ),
                        ],
                      ),
                    ),
                    Column(
                      crossAxisAlignment: CrossAxisAlignment.end,
                      children: [
                        Text(
                          _formatTimestamp(item.timestamp),
                          style: AppTextStyles.caption.copyWith(
                            color: AppColors.textSecondary,
                          ),
                        ),
                        const SizedBox(height: 8),
                        Icon(
                          Icons.arrow_forward_ios,
                          size: 14,
                          color: AppColors.gray400,
                        ),
                      ],
                    ),
                  ],
                ),
                const SizedBox(height: 16),
                Text(
                  item.lastMessage,
                  style: AppTextStyles.bodyMedium.copyWith(
                    color: AppColors.textSecondary,
                    height: 1.4,
                  ),
                  maxLines: 2,
                  overflow: TextOverflow.ellipsis,
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildEmptyState() {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(32),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Container(
              width: 100,
              height: 100,
              decoration: BoxDecoration(
                color: AppColors.gray100,
                shape: BoxShape.circle,
              ),
              child: Icon(
                _searchQuery.isNotEmpty ? Icons.search_off : Icons.history,
                size: 50,
                color: AppColors.textTertiary,
              ),
            ),
            const SizedBox(height: 24),
            Text(
              _searchQuery.isNotEmpty 
                  ? 'Tidak ada hasil ditemukan'
                  : 'Belum ada riwayat chat',
              style: AppTextStyles.h6.copyWith(
                color: AppColors.textSecondary,
              ),
            ),
            const SizedBox(height: 12),
            Text(
              _searchQuery.isNotEmpty
                  ? 'Coba gunakan kata kunci yang berbeda'
                  : 'Mulai chat dengan Luna untuk melihat riwayat percakapan',
              style: AppTextStyles.bodyMedium.copyWith(
                color: AppColors.textTertiary,
              ),
              textAlign: TextAlign.center,
            ),
            if (_searchQuery.isNotEmpty) ...[
              const SizedBox(height: 24),
              TextButton(
                onPressed: () {
                  _searchController.clear();
                  setState(() {
                    _searchQuery = '';
                    _selectedFilter = 'All';
                  });
                },
                child: Text(
                  'Clear Search',
                  style: AppTextStyles.labelMedium.copyWith(
                    color: AppColors.primary,
                  ),
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }
}

class ChatHistoryItem {
  final String id;
  final String title;
  final String lastMessage;
  final DateTime timestamp;
  final String category;
  final int messageCount;
  final IconData icon;
  final Color color;

  ChatHistoryItem({
    required this.id,
    required this.title,
    required this.lastMessage,
    required this.timestamp,
    required this.category,
    required this.messageCount,
    required this.icon,
    required this.color,
  });
}