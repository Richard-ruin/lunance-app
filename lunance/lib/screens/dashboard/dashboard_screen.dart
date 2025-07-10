import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../providers/auth_provider.dart';
import '../../utils/app_colors.dart';
import 'widgets/dashboard_top_bar.dart';
import 'widgets/left_sidebar.dart';
import 'widgets/right_sidebar.dart';
import 'widgets/animated_overlay.dart';
import 'views/chat_view.dart';
import 'views/explore_finance_view.dart';
import 'views/chat_history_view.dart';

class DashboardScreen extends StatefulWidget {
  const DashboardScreen({Key? key}) : super(key: key);

  @override
  State<DashboardScreen> createState() => _DashboardScreenState();
}

class _DashboardScreenState extends State<DashboardScreen> 
    with TickerProviderStateMixin {
  
  // Current view index
  int _selectedIndex = 0; // 0: Chat, 1: Explore Finance, 2: Chat History
  
  // Sidebar states
  bool _isLeftSidebarOpen = false;
  bool _isRightSidebarOpen = false;
  
  // Animation controllers
  late AnimationController _leftSidebarController;
  late AnimationController _rightSidebarController;
  late AnimationController _overlayController;
  
  // Animations
  late Animation<double> _leftSidebarAnimation;
  late Animation<double> _rightSidebarAnimation;
  late Animation<double> _overlayAnimation;

  @override
  void initState() {
    super.initState();
    _initializeAnimations();
  }

  void _initializeAnimations() {
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
    
    // Initialize sidebar animations
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
    
    // Initialize overlay animation
    _overlayAnimation = Tween<double>(
      begin: 0.0,
      end: 1.0,
    ).animate(CurvedAnimation(
      parent: _overlayController,
      curve: Curves.easeInOut,
    ));
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
        _closeRightSidebar();
      }
      
      _isLeftSidebarOpen = !_isLeftSidebarOpen;
      if (_isLeftSidebarOpen) {
        _leftSidebarController.forward();
        _overlayController.forward();
      } else {
        _closeLeftSidebar();
      }
    });
  }

  void _toggleRightSidebar() {
    setState(() {
      // Close left sidebar if open
      if (_isLeftSidebarOpen) {
        _closeLeftSidebar();
      }
      
      _isRightSidebarOpen = !_isRightSidebarOpen;
      if (_isRightSidebarOpen) {
        _rightSidebarController.forward();
        _overlayController.forward();
      } else {
        _closeRightSidebar();
      }
    });
  }

  void _closeLeftSidebar() {
    _isLeftSidebarOpen = false;
    _leftSidebarController.reverse();
    if (!_isRightSidebarOpen) {
      _overlayController.reverse();
    }
  }

  void _closeRightSidebar() {
    _isRightSidebarOpen = false;
    _rightSidebarController.reverse();
    if (!_isLeftSidebarOpen) {
      _overlayController.reverse();
    }
  }

  void _closeSidebars() {
    if (_isLeftSidebarOpen || _isRightSidebarOpen) {
      setState(() {
        if (_isLeftSidebarOpen) _closeLeftSidebar();
        if (_isRightSidebarOpen) _closeRightSidebar();
      });
    }
  }

  void _onNavigationChanged(int index) {
    setState(() {
      _selectedIndex = index;
    });
  }

  String _getPageTitle() {
    switch (_selectedIndex) {
      case 0:
        return 'Chat dengan Luna AI';
      case 1:
        return 'Explore Finance';
      case 2:
        return 'Chat History';
      default:
        return 'Lunance';
    }
  }

  Widget _getCurrentView() {
    switch (_selectedIndex) {
      case 0:
        return const ChatView();
      case 1:
        return const ExploreFinanceView();
      case 2:
        return const ChatHistoryView();
      default:
        return const ChatView();
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      resizeToAvoidBottomInset: false, // Important: Let us handle keyboard manually
      body: SafeArea(
        child: Stack(
          children: [
            // Main Content with translation animation
            AnimatedBuilder(
              animation: Listenable.merge([
                _leftSidebarAnimation,
                _rightSidebarAnimation,
              ]),
              builder: (context, child) {
                double translateX = 0.0;
                if (_isLeftSidebarOpen) {
                  translateX = _leftSidebarAnimation.value;
                } else if (_isRightSidebarOpen) {
                  translateX = -_rightSidebarAnimation.value;
                }
                
                return Transform.translate(
                  offset: Offset(translateX, 0.0),
                  child: GestureDetector(
                    onTap: _closeSidebars,
                    child: Container(
                      width: MediaQuery.of(context).size.width,
                      height: MediaQuery.of(context).size.height,
                      decoration: BoxDecoration(
                        color: AppColors.white,
                      ),
                      child: Column(
                        children: [
                          // Top Bar
                          DashboardTopBar(
                            title: _getPageTitle(),
                            isLeftSidebarOpen: _isLeftSidebarOpen,
                            isRightSidebarOpen: _isRightSidebarOpen,
                            onLeftToggle: _toggleLeftSidebar,
                            onRightToggle: _toggleRightSidebar,
                          ),
                          
                          // Main Content
                          Expanded(
                            child: _getCurrentView(),
                          ),
                        ],
                      ),
                    ),
                  ),
                );
              },
            ),
            
            // Animated Overlay
            AnimatedOverlay(
              animation: _overlayAnimation,
              isLeftSidebarOpen: _isLeftSidebarOpen,
              isRightSidebarOpen: _isRightSidebarOpen,
              leftSidebarAnimation: _leftSidebarAnimation,
              rightSidebarAnimation: _rightSidebarAnimation,
              onTap: _closeSidebars,
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
                          onNavigationChanged: _onNavigationChanged,
                          onToggle: _toggleLeftSidebar,
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
                          onToggle: _toggleRightSidebar,
                        )
                      : Container(),
                );
              },
            ),
          ],
        ),
      ),
    );
  }
}