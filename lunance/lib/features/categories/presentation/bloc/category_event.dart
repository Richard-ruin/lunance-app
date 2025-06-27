// lib/features/categories/presentation/bloc/category_event.dart
import 'package:equatable/equatable.dart';
import '../../domain/repositories/category_repository.dart';

abstract class CategoryEvent extends Equatable {
  const CategoryEvent();

  @override
  List<Object?> get props => [];
}

class LoadCategoriesEvent extends CategoryEvent {
  final String? type;
  final bool withStats;

  const LoadCategoriesEvent({this.type, this.withStats = false});

  @override
  List<Object?> get props => [type, withStats];
}

class LoadPopularCategoriesEvent extends CategoryEvent {
  final String? type;
  final int limit;

  const LoadPopularCategoriesEvent({this.type, this.limit = 10});

  @override
  List<Object?> get props => [type, limit];
}

class SearchCategoriesEvent extends CategoryEvent {
  final String query;
  final String? type;

  const SearchCategoriesEvent(this.query, {this.type});

  @override
  List<Object?> get props => [query, type];
}

class ClearSearchEvent extends CategoryEvent {}

class CreateCategoryEvent extends CategoryEvent {
  final CategoryCreate categoryData;

  const CreateCategoryEvent(this.categoryData);

  @override
  List<Object> get props => [categoryData];
}

class UpdateCategoryEvent extends CategoryEvent {
  final String id;
  final CategoryUpdate categoryData;

  const UpdateCategoryEvent(this.id, this.categoryData);

  @override
  List<Object> get props => [id, categoryData];
}

class DeleteCategoryEvent extends CategoryEvent {
  final String id;

  const DeleteCategoryEvent(this.id);

  @override
  List<Object> get props => [id];
}

class FilterCategoriesByTypeEvent extends CategoryEvent {
  final String? type;

  const FilterCategoriesByTypeEvent(this.type);

  @override
  List<Object?> get props => [type];
}
