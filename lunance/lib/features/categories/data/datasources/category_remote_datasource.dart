// lib/features/categories/data/datasources/category_remote_datasource.dart
import 'package:dio/dio.dart';
import '../../../../core/constants/api_endpoints.dart';
import '../../../../core/utils/dio_client.dart';
import '../../../../core/network/network_exceptions.dart';
import '../models/category_model.dart';
import '../../domain/repositories/category_repository.dart';

abstract class CategoryRemoteDataSource {
  Future<List<CategoryModel>> getCategories({String? type});
  Future<List<CategoryWithStatsModel>> getCategoriesWithStats({String? type});
  Future<List<CategoryWithStatsModel>> getPopularCategories({String? type, int limit = 10});
  Future<List<CategoryModel>> searchCategories(String query, {String? type});
  Future<CategoryModel> getCategoryById(String id);
  Future<CategoryModel> createCategory(CategoryCreate categoryData);
  Future<CategoryModel> updateCategory(String id, CategoryUpdate categoryData);
  Future<void> deleteCategory(String id);
}

class CategoryRemoteDataSourceImpl implements CategoryRemoteDataSource {
  final DioClient client;

  CategoryRemoteDataSourceImpl(this.client);

  @override
  Future<List<CategoryModel>> getCategories({String? type}) async {
    try {
      final queryParams = <String, dynamic>{};
      if (type != null) queryParams['category_type'] = type;

      final response = await client.get(
        ApiEndpoints.categories,
        queryParameters: queryParams,
      );

      if (response.data is List) {
        return (response.data as List)
            .map((json) => CategoryModel.fromJson(json))
            .toList();
      } else {
        throw  NetworkException('Invalid response format');
      }
    } on DioException catch (e) {
      throw NetworkException(e.message ?? 'Failed to get categories');
    } catch (e) {
      throw NetworkException('Failed to get categories: $e');
    }
  }

  @override
  Future<List<CategoryWithStatsModel>> getCategoriesWithStats({String? type}) async {
    try {
      final queryParams = <String, dynamic>{};
      if (type != null) queryParams['category_type'] = type;

      final response = await client.get(
        '${ApiEndpoints.categories}/with-stats',
        queryParameters: queryParams,
      );

      if (response.data is List) {
        return (response.data as List)
            .map((json) => CategoryWithStatsModel.fromJson(json))
            .toList();
      } else {
        throw  NetworkException('Invalid response format');
      }
    } on DioException catch (e) {
      throw NetworkException(e.message ?? 'Failed to get categories with stats');
    } catch (e) {
      throw NetworkException('Failed to get categories with stats: $e');
    }
  }

  @override
  Future<List<CategoryWithStatsModel>> getPopularCategories({String? type, int limit = 10}) async {
    try {
      final queryParams = <String, dynamic>{'limit': limit};
      if (type != null) queryParams['category_type'] = type;

      final response = await client.get(
        '${ApiEndpoints.categories}/popular',
        queryParameters: queryParams,
      );

      if (response.data is List) {
        return (response.data as List)
            .map((json) => CategoryWithStatsModel.fromJson(json))
            .toList();
      } else {
        throw  NetworkException('Invalid response format');
      }
    } on DioException catch (e) {
      throw NetworkException(e.message ?? 'Failed to get popular categories');
    } catch (e) {
      throw NetworkException('Failed to get popular categories: $e');
    }
  }

  @override
  Future<List<CategoryModel>> searchCategories(String query, {String? type}) async {
    try {
      final queryParams = <String, dynamic>{'q': query};
      if (type != null) queryParams['category_type'] = type;

      final response = await client.get(
        '${ApiEndpoints.categories}/search',
        queryParameters: queryParams,
      );

      if (response.data is List) {
        return (response.data as List)
            .map((json) => CategoryModel.fromJson(json))
            .toList();
      } else {
        throw NetworkException('Invalid response format');
      }
    } on DioException catch (e) {
      throw NetworkException(e.message ?? 'Failed to search categories');
    } catch (e) {
      throw NetworkException('Failed to search categories: $e');
    }
  }

  @override
  Future<CategoryModel> getCategoryById(String id) async {
    try {
      final response = await client.get('${ApiEndpoints.categories}/$id');

      if (response.data is Map<String, dynamic>) {
        return CategoryModel.fromJson(response.data);
      } else {
        throw NetworkException('Invalid response format');
      }
    } on DioException catch (e) {
      throw NetworkException(e.message ?? 'Failed to get category');
    } catch (e) {
      throw NetworkException('Failed to get category: $e');
    }
  }

  @override
  Future<CategoryModel> createCategory(CategoryCreate categoryData) async {
    try {
      final response = await client.post(
        ApiEndpoints.categories,
        data: categoryData.toJson(),
      );

      if (response.data is Map<String, dynamic>) {
        return CategoryModel.fromJson(response.data);
      } else {
        throw NetworkException('Invalid response format');
      }
    } on DioException catch (e) {
      throw NetworkException(e.message ?? 'Failed to create category');
    } catch (e) {
      throw NetworkException('Failed to create category: $e');
    }
  }

  @override
  Future<CategoryModel> updateCategory(String id, CategoryUpdate categoryData) async {
    try {
      final response = await client.put(
        '${ApiEndpoints.categories}/$id',
        data: categoryData.toJson(),
      );

      if (response.data is Map<String, dynamic>) {
        return CategoryModel.fromJson(response.data);
      } else {
        throw  NetworkException('Invalid response format');
      }
    } on DioException catch (e) {
      throw NetworkException(e.message ?? 'Failed to update category');
    } catch (e) {
      throw NetworkException('Failed to update category: $e');
    }
  }

  @override
  Future<void> deleteCategory(String id) async {
    try {
      await client.delete('${ApiEndpoints.categories}/$id');
    } on DioException catch (e) {
      throw NetworkException(e.message ?? 'Failed to delete category');
    } catch (e) {
      throw NetworkException('Failed to delete category: $e');
    }
  }
}