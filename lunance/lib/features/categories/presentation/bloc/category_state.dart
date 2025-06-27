
// lib/features/categories/presentation/bloc/category_state.dart
import 'package:equatable/equatable.dart';
import '../../domain/entities/category.dart';

abstract class CategoryState extends Equatable {
  const CategoryState();

  @override
  List<Object?> get props => [];
}

class CategoryInitialState extends CategoryState {}

class CategoryLoadingState extends CategoryState {}

class CategoryLoadedState extends CategoryState {
  final List<Category> categories;
  final List<CategoryWithStats> categoriesWithStats;
  final List<Category> searchResults;
  final String? currentFilter;
  final bool isSearching;

  const CategoryLoadedState({
    this.categories = const [],
    this.categoriesWithStats = const [],
    this.searchResults = const [],
    this.currentFilter,
    this.isSearching = false,
  });

  CategoryLoadedState copyWith({
    List<Category>? categories,
    List<CategoryWithStats>? categoriesWithStats,
    List<Category>? searchResults,
    String? currentFilter,
    bool? isSearching,
  }) {
    return CategoryLoadedState(
      categories: categories ?? this.categories,
      categoriesWithStats: categoriesWithStats ?? this.categoriesWithStats,
      searchResults: searchResults ?? this.searchResults,
      currentFilter: currentFilter ?? this.currentFilter,
      isSearching: isSearching ?? this.isSearching,
    );
  }

  @override
  List<Object?> get props => [
        categories,
        categoriesWithStats,
        searchResults,
        currentFilter,
        isSearching,
      ];
}

class CategoryErrorState extends CategoryState {
  final String message;

  const CategoryErrorState(this.message);

  @override
  List<Object> get props => [message];
}

class CategoryOperationSuccessState extends CategoryState {
  final String message;

  const CategoryOperationSuccessState(this.message);

  @override
  List<Object> get props => [message];
}

