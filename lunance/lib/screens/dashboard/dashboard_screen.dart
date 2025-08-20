import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../utils/app_colors.dart';
import '../../providers/chat_provider.dart';
import '../../models/chat_model.dart'; // Added missing import for Conversation
import 'left_sidebar.dart';
import 'right_sidebar.dart';
import 'chat_view.dart';
import 'chat_history_view.dart';

class DashboardScreen extends StatefulWidget {
  const DashboardScreen({Key? key}) : super(key: key);

  @override
  State<DashboardScreen> createState() => _DashboardScreenState();
}

class _DashboardScreenState extends State<DashboardScreen> with TickerProviderStateMixin {
  int _selectedIndex = 0; // 0: Chat, 1: Explore Finance, 2: Chat History, 3: Predictions
  String? _selectedConversationId; // Added to track selected conversation
  
  // Sidebar states
  bool _isLeftSidebarOpen = false;
  bool _isRightSidebarOpen = false;
  
  // Animation controllers
  late AnimationController _leftSidebarController;
  late AnimationController _rightSidebarController;
  late AnimationController _overlayController;
  late Animation<double> _leftSidebarAnimation;
  late Animation<double> _rightSidebarAnimation;
  late Animation<double> _overlayAnimation;

  @override
  void initState() {
    super.initState();
    
    // Initialize animation controllers
    _leftSidebarController = AnimationController(
      duration: const Duration(milliseconds: 300),
      vsync: this,
    );
    _rightSidebarController = AnimationController(
      duration: const Duration(milliseconds: 300),
      vsync: this,
    );
    _overlayController = AnimationController(
      duration: const Duration(milliseconds: 300),
      vsync: this,
    );
    
    // Initialize animations
    _leftSidebarAnimation = Tween<double>(
      begin: 0.0,
      end: 280.0,
    ).animate(CurvedAnimation(
      parent: _leftSidebarController,
      curve: Curves.easeInOut,
    ));
    
    _rightSidebarAnimation = Tween<double>(
      begin: 0.0,
      end: 280.0,
    ).animate(CurvedAnimation(
      parent: _rightSidebarController,
      curve: Curves.easeInOut,
    ));

    _overlayAnimation = Tween<double>(
      begin: 0.0,
      end: 1.0,
    ).animate(CurvedAnimation(
      parent: _overlayController,
      curve: Curves.easeInOut,
    ));

    // Initialize chat provider
    WidgetsBinding.instance.addPostFrameCallback((_) {
      _initializeChatProvider();
    });
  }

  void _initializeChatProvider() {
    final chatProvider = Provider.of<ChatProvider>(context, listen: false);
    // The chat provider will be initialized in ChatView
  }

  @override
  void dispose() {
    _leftSidebarController.dispose();
    _rightSidebarController.dispose();
    _overlayController.dispose();
    super.dispose();
  }

  void _toggleLeftSidebar() {
    setState(() {
      // Close right sidebar if open
      if (_isRightSidebarOpen) {
        _isRightSidebarOpen = false;
        _rightSidebarController.reverse();
      }
      
      _isLeftSidebarOpen = !_isLeftSidebarOpen;
      if (_isLeftSidebarOpen) {
        _leftSidebarController.forward();
        _overlayController.forward();
      } else {
        _leftSidebarController.reverse();
        _overlayController.reverse();
      }
    });
  }

  void _toggleRightSidebar() {
    setState(() {
      // Close left sidebar if open
      if (_isLeftSidebarOpen) {
        _isLeftSidebarOpen = false;
        _leftSidebarController.reverse();
      }
      
      _isRightSidebarOpen = !_isRightSidebarOpen;
      if (_isRightSidebarOpen) {
        _rightSidebarController.forward();
        _overlayController.forward();
      } else {
        _rightSidebarController.reverse();
        _overlayController.reverse();
      }
    });
  }

  void _closeSidebars() {
    if (_isLeftSidebarOpen || _isRightSidebarOpen) {
      setState(() {
        if (_isLeftSidebarOpen) {
          _isLeftSidebarOpen = false;
          _leftSidebarController.reverse();
        }
        if (_isRightSidebarOpen) {
          _isRightSidebarOpen = false;
          _rightSidebarController.reverse();
        }
        _overlayController.reverse();
      });
    }
  }

  void _onNavigationItemSelected(int index) {
    setState(() {
      _selectedIndex = index;
      // Clear conversation selection when changing views
      if (index != 0) {
        _selectedConversationId = null;
      }
    });
    // Close sidebars when navigating
    _closeSidebars();
  }

  void _onConversationSelected(String conversationId) async {
    // Handle conversation selection from sidebar or history
    try {
      final chatProvider = Provider.of<ChatProvider>(context, listen: false);
      
      // Find the conversation in the existing list
      Conversation? conversation;
      try {
        conversation = chatProvider.conversations.firstWhere(
          (conv) => conv.id == conversationId,
        );
      } catch (e) {
        conversation = null;
      }

      if (conversation != null) {
        // Set the conversation as active
        await chatProvider.setActiveConversation(conversation);
      } else {
        // If conversation not found in list, try to load it by ID
        await chatProvider.loadConversationById(conversationId);
      }
      
      // Navigate to chat view and set conversation ID
      setState(() {
        _selectedIndex = 0;
        _selectedConversationId = conversationId;
      });
      
      // Close sidebars
      _closeSidebars();
      
    } catch (e) {
      // Handle error
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Gagal membuka percakapan: ${e.toString()}'),
            backgroundColor: AppColors.error,
            duration: const Duration(seconds: 3),
          ),
        );
      }
    }
  }

  Widget _getMainContentView() {
    switch (_selectedIndex) {
      case 0:
        return ChatView(conversationId: _selectedConversationId); // Pass conversation ID
      case 2:
        return ChatHistoryView(
          onNavigationItemSelected: _onNavigationItemSelected,
          onConversationSelected: _onConversationSelected,
        );
      default:
        return ChatView(conversationId: _selectedConversationId);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      body: SafeArea(
        child: Stack(
          children: [
            // Main Content
            AnimatedBuilder(
              animation: Listenable.merge([_leftSidebarAnimation, _rightSidebarAnimation]),
              builder: (context, child) {
                return Transform.translate(
                  offset: Offset(
                    _isLeftSidebarOpen 
                        ? _leftSidebarAnimation.value 
                        : (_isRightSidebarOpen ? -_rightSidebarAnimation.value : 0.0),
                    0.0,
                  ),
                  child: GestureDetector(
                    onTap: _closeSidebars,
                    child: Container(
                      width: MediaQuery.of(context).size.width,
                      height: MediaQuery.of(context).size.height,
                      decoration: const BoxDecoration(
                        color: AppColors.white,
                      ),
                      child: Column(
                        children: [
                          // Top Bar
                          _buildTopBar(),
                          
                          // Main Content
                          Expanded(
                            child: _getMainContentView(),
                          ),
                        ],
                      ),
                    ),
                  ),
                );
              },
            ),
            
            // Left Sidebar
            AnimatedBuilder(
              animation: _leftSidebarAnimation,
              builder: (context, child) {
                return Positioned(
                  left: -280 + _leftSidebarAnimation.value,
                  top: 0,
                  bottom: 0,
                  child: _leftSidebarAnimation.value > 0
                      ? LeftSidebar(
                          selectedIndex: _selectedIndex,
                          onNavigationItemSelected: _onNavigationItemSelected,
                          onToggleSidebar: _toggleLeftSidebar,
                          onConversationSelected: _onConversationSelected,
                        )
                      : Container(),
                );
              },
            ),
            
            // Right Sidebar
            AnimatedBuilder(
              animation: _rightSidebarAnimation,
              builder: (context, child) {
                return Positioned(
                  right: -280 + _rightSidebarAnimation.value,
                  top: 0,
                  bottom: 0,
                  child: _rightSidebarAnimation.value > 0
                      ? RightSidebar(
                          onToggleSidebar: _toggleRightSidebar,
                        )
                      : Container(),
                );
              },
            ),
            
            // Animated Overlay
            AnimatedBuilder(
              animation: _overlayAnimation,
              builder: (context, child) {
                if (_overlayAnimation.value == 0) return Container();
                
                return Positioned.fill(
                  child: Transform.translate(
                    offset: Offset(
                      _isLeftSidebarOpen 
                          ? _leftSidebarAnimation.value 
                          : (_isRightSidebarOpen ? -_rightSidebarAnimation.value : 0.0),
                      0.0,
                    ),
                    child: AnimatedContainer(
                      duration: const Duration(milliseconds: 300),
                      color: AppColors.overlayLight.withOpacity(_overlayAnimation.value * 0.5),
                      child: GestureDetector(
                        onTap: _closeSidebars,
                        child: Container(
                          color: Colors.transparent,
                        ),
                      ),
                    ),
                  ),
                );
              },
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildTopBar() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: AppColors.white,
        border: Border(
          bottom: BorderSide(color: AppColors.border, width: 1),
        ),
        boxShadow: [
          BoxShadow(
            color: AppColors.shadow,
            blurRadius: 4,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Row(
        children: [
          // Left Menu Toggle (when sidebar is closed)
          if (!_isLeftSidebarOpen)
            InkWell(
              onTap: _toggleLeftSidebar,
              borderRadius: BorderRadius.circular(8),
              child: Container(
                padding: const EdgeInsets.all(8),
                decoration: BoxDecoration(
                  color: AppColors.gray100,
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Icon(
                  Icons.menu,
                  size: 20,
                  color: AppColors.gray600,
                ),
              ),
            ),
          
          if (!_isLeftSidebarOpen) const SizedBox(width: 16),
          
          // Title
          Expanded(
            child: _selectedIndex == 0
                ? Consumer<ChatProvider>(
                    builder: (context, chatProvider, child) {
                      return Text(
                        chatProvider.hasActiveConversation 
                            ? chatProvider.activeConversation!.displayTitle
                            : 'Chat dengan Luna AI',
                        style: const TextStyle(
                          fontSize: 18,
                          fontWeight: FontWeight.w600,
                          color: AppColors.textPrimary,
                        ),
                      );
                    },
                  )
                : Text(
                    _getPageTitleString(),
                    style: const TextStyle(
                      fontSize: 18,
                      fontWeight: FontWeight.w600,
                      color: AppColors.textPrimary,
                    ),
                  ),
          ),
          
          // Connection Status Indicator (only for chat view)
          if (_selectedIndex == 0)
            Consumer<ChatProvider>(
              builder: (context, chatProvider, child) {
                return Container(
                  margin: const EdgeInsets.only(right: 12),
                  child: Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Container(
                        width: 8,
                        height: 8,
                        decoration: BoxDecoration(
                          color: chatProvider.isConnected 
                              ? AppColors.success 
                              : AppColors.error,
                          shape: BoxShape.circle,
                        ),
                      ),
                      const SizedBox(width: 6),
                      Text(
                        chatProvider.isConnected ? 'Online' : 'Offline',
                        style: TextStyle(
                          fontSize: 12,
                          color: chatProvider.isConnected 
                              ? AppColors.success 
                              : AppColors.error,
                          fontWeight: FontWeight.w500,
                        ),
                      ),
                    ],
                  ),
                );
              },
            ),
          
          // Right Profile Toggle (when sidebar is closed)
          if (!_isRightSidebarOpen)
            InkWell(
              onTap: _toggleRightSidebar,
              borderRadius: BorderRadius.circular(20),
              child: CircleAvatar(
                radius: 20,
                backgroundColor: AppColors.gray200,
                child: Text(
                  'U',
                  style: const TextStyle(
                    color: AppColors.gray700,
                    fontWeight: FontWeight.w600,
                  ),
                ),
              ),
            ),
        ],
      ),
    );
  }

  String _getPageTitleString() {
    switch (_selectedIndex) {
      case 1:
        return 'Explore Finance';
      case 2:
        return 'Chat History';
      case 3:
        return 'Prediksi';
      default:
        return 'Chat dengan Luna AI';
    }
  }
}