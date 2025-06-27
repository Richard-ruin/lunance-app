// lib/features/categories/presentation/bloc/category_bloc.dart
import 'package:flutter_bloc/flutter_bloc.dart';
import '../../domain/usecases/get_categories_usecase.dart';
import '../../domain/usecases/get_categories_with_stats_usecase.dart';
import '../../domain/usecases/get_popular_categories_usecase.dart';
import '../../domain/usecases/search_categories_usecase.dart';
import '../../domain/usecases/create_category_usecase.dart';
import '../../domain/usecases/update_category_usecase.dart';
import '../../domain/usecases/delete_category_usecase.dart';
import 'category_event.dart';
import 'category_state.dart';

class CategoryBloc extends Bloc<CategoryEvent, CategoryState> {
  final GetCategoriesUseCase getCategoriesUseCase;
  final GetCategoriesWithStatsUseCase getCategoriesWithStatsUseCase;
  final GetPopularCategoriesUseCase getPopularCategoriesUseCase;
  final SearchCategoriesUseCase searchCategoriesUseCase;
  final CreateCategoryUseCase createCategoryUseCase;
  final UpdateCategoryUseCase updateCategoryUseCase;
  final DeleteCategoryUseCase deleteCategoryUseCase;

  CategoryBloc({
    required this.getCategoriesUseCase,
    required this.getCategoriesWithStatsUseCase,
    required this.getPopularCategoriesUseCase,
    required this.searchCategoriesUseCase,
    required this.createCategoryUseCase,
    required this.updateCategoryUseCase,
    required this.deleteCategoryUseCase,
  }) : super(CategoryInitialState()) {
    on<LoadCategoriesEvent>(_onLoadCategories);
    on<LoadPopularCategoriesEvent>(_onLoadPopularCategories);
    on<SearchCategoriesEvent>(_onSearchCategories);
    on<ClearSearchEvent>(_onClearSearch);
    on<CreateCategoryEvent>(_onCreateCategory);
    on<UpdateCategoryEvent>(_onUpdateCategory);
    on<DeleteCategoryEvent>(_onDeleteCategory);
    on<FilterCategoriesByTypeEvent>(_onFilterByType);
  }

  Future<void> _onLoadCategories(
    LoadCategoriesEvent event,
    Emitter<CategoryState> emit,
  ) async {
    emit(CategoryLoadingState());

    if (event.withStats) {
      final result = await getCategoriesWithStatsUseCase(type: event.type);
      result.when(
        success: (categoriesWithStats) {
          emit(CategoryLoadedState(
            categoriesWithStats: categoriesWithStats,
            currentFilter: event.type,
          ));
        },
        failure: (error) => emit(CategoryErrorState(error)),
      );
    } else {
      final result = await getCategoriesUseCase(type: event.type);
      result.when(
        success: (categories) {
          emit(CategoryLoadedState(
            categories: categories,
            currentFilter: event.type,
          ));
        },
        failure: (error) => emit(CategoryErrorState(error)),
      );
    }
  }

  Future<void> _onLoadPopularCategories(
    LoadPopularCategoriesEvent event,
    Emitter<CategoryState> emit,
  ) async {
    emit(CategoryLoadingState());

    final result = await getPopularCategoriesUseCase(
      type: event.type,
      limit: event.limit,
    );

    result.when(
      success: (popularCategories) {
        emit(CategoryLoadedState(
          categoriesWithStats: popularCategories,
          currentFilter: event.type,
        ));
      },
      failure: (error) => emit(CategoryErrorState(error)),
    );
  }

  Future<void> _onSearchCategories(
    SearchCategoriesEvent event,
    Emitter<CategoryState> emit,
  ) async {
    if (state is CategoryLoadedState) {
      final currentState = state as CategoryLoadedState;
      emit(currentState.copyWith(isSearching: true));

      final result = await searchCategoriesUseCase(event.query, type: event.type);
      result.when(
        success: (searchResults) {
          emit(currentState.copyWith(
            searchResults: searchResults,
            isSearching: false,
          ));
        },
        failure: (error) {
          emit(CategoryErrorState(error));
        },
      );
    } else {
      emit(CategoryLoadingState());
      final result = await searchCategoriesUseCase(event.query, type: event.type);
      result.when(
        success: (searchResults) {
          emit(CategoryLoadedState(
            searchResults: searchResults,
            isSearching: false,
          ));
        },
        failure: (error) => emit(CategoryErrorState(error)),
      );
    }
  }

  Future<void> _onClearSearch(
    ClearSearchEvent event,
    Emitter<CategoryState> emit,
  ) async {
    if (state is CategoryLoadedState) {
      final currentState = state as CategoryLoadedState;
      emit(currentState.copyWith(
        searchResults: [],
        isSearching: false,
      ));
    }
  }

  Future<void> _onCreateCategory(
    CreateCategoryEvent event,
    Emitter<CategoryState> emit,
  ) async {
    final result = await createCategoryUseCase(event.categoryData);
    result.when(
      success: (category) {
        emit(const CategoryOperationSuccessState('Kategori berhasil dibuat'));
        // Reload categories
        add(LoadCategoriesEvent(type: category.type));
      },
      failure: (error) => emit(CategoryErrorState(error)),
    );
  }

  Future<void> _onUpdateCategory(
    UpdateCategoryEvent event,
    Emitter<CategoryState> emit,
  ) async {
    final result = await updateCategoryUseCase(event.id, event.categoryData);
    result.when(
      success: (category) {
        emit(const CategoryOperationSuccessState('Kategori berhasil diperbarui'));
        // Reload categories
        add(LoadCategoriesEvent(type: category.type));
      },
      failure: (error) => emit(CategoryErrorState(error)),
    );
  }

  Future<void> _onDeleteCategory(
    DeleteCategoryEvent event,
    Emitter<CategoryState> emit,
  ) async {
    final result = await deleteCategoryUseCase(event.id);
    result.when(
      success: (_) {
        emit(const CategoryOperationSuccessState('Kategori berhasil dihapus'));
        // Reload categories
        if (state is CategoryLoadedState) {
          final currentState = state as CategoryLoadedState;
          add(LoadCategoriesEvent(type: currentState.currentFilter));
        } else {
          add(const LoadCategoriesEvent());
        }
      },
      failure: (error) => emit(CategoryErrorState(error)),
    );
  }

  Future<void> _onFilterByType(
    FilterCategoriesByTypeEvent event,
    Emitter<CategoryState> emit,
  ) async {
    add(LoadCategoriesEvent(type: event.type, withStats: true));
  }
}