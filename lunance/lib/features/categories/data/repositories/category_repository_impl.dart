// lib/features/categories/data/repositories/category_repository_impl.dart
import '../../../../core/network/api_result.dart';
import '../../../../core/network/network_info.dart';
import '../../../../core/network/network_exceptions.dart';
import '../../domain/entities/category.dart';
import '../../domain/repositories/category_repository.dart';
import '../datasources/category_remote_datasource.dart';
import '../models/category_model.dart';

class CategoryRepositoryImpl implements CategoryRepository {
  final CategoryRemoteDataSource remoteDataSource;
  final NetworkInfo networkInfo;

  CategoryRepositoryImpl({
    required this.remoteDataSource,
    required this.networkInfo,
  });

  @override
  Future<ApiResult<List<Category>>> getCategories({String? type}) async {
    if (!await networkInfo.isConnected) {
      return  ApiResult.failure('Tidak ada koneksi internet');
    }

    try {
      final categories = await remoteDataSource.getCategories(type: type);
      return ApiResult.success(
        categories.map((model) => model.toEntity()).toList(),
      );
    } on NetworkException catch (e) {
      return ApiResult.failure(e.message);
    } catch (e) {
      return ApiResult.failure('Gagal memuat kategori: $e');
    }
  }

  @override
  Future<ApiResult<List<CategoryWithStats>>> getCategoriesWithStats({String? type}) async {
    if (!await networkInfo.isConnected) {
      return  ApiResult.failure('Tidak ada koneksi internet');
    }

    try {
      final categories = await remoteDataSource.getCategoriesWithStats(type: type);
      return ApiResult.success(
        categories.map((model) => model.toEntity()).toList(),
      );
    } on NetworkException catch (e) {
      return ApiResult.failure(e.message);
    } catch (e) {
      return ApiResult.failure('Gagal memuat kategori dengan statistik: $e');
    }
  }

  @override
  Future<ApiResult<List<CategoryWithStats>>> getPopularCategories({String? type, int limit = 10}) async {
    if (!await networkInfo.isConnected) {
      return  ApiResult.failure('Tidak ada koneksi internet');
    }

    try {
      final categories = await remoteDataSource.getPopularCategories(
        type: type,
        limit: limit,
      );
      return ApiResult.success(
        categories.map((model) => model.toEntity()).toList(),
      );
    } on NetworkException catch (e) {
      return ApiResult.failure(e.message);
    } catch (e) {
      return ApiResult.failure('Gagal memuat kategori populer: $e');
    }
  }

  @override
  Future<ApiResult<List<Category>>> searchCategories(String query, {String? type}) async {
    if (!await networkInfo.isConnected) {
      return  ApiResult.failure('Tidak ada koneksi internet');
    }

    try {
      final categories = await remoteDataSource.searchCategories(query, type: type);
      return ApiResult.success(
        categories.map((model) => model.toEntity()).toList(),
      );
    } on NetworkException catch (e) {
      return ApiResult.failure(e.message);
    } catch (e) {
      return ApiResult.failure('Gagal mencari kategori: $e');
    }
  }

  @override
  Future<ApiResult<Category>> getCategoryById(String id) async {
    if (!await networkInfo.isConnected) {
      return  ApiResult.failure('Tidak ada koneksi internet');
    }

    try {
      final category = await remoteDataSource.getCategoryById(id);
      return ApiResult.success(category.toEntity());
    } on NetworkException catch (e) {
      return ApiResult.failure(e.message);
    } catch (e) {
      return ApiResult.failure('Gagal memuat detail kategori: $e');
    }
  }

  @override
  Future<ApiResult<Category>> createCategory(CategoryCreate categoryData) async {
    if (!await networkInfo.isConnected) {
      return  ApiResult.failure('Tidak ada koneksi internet');
    }

    try {
      final category = await remoteDataSource.createCategory(categoryData);
      return ApiResult.success(category.toEntity());
    } on NetworkException catch (e) {
      return ApiResult.failure(e.message);
    } catch (e) {
      return ApiResult.failure('Gagal membuat kategori: $e');
    }
  }

  @override
  Future<ApiResult<Category>> updateCategory(String id, CategoryUpdate categoryData) async {
    if (!await networkInfo.isConnected) {
      return  ApiResult.failure('Tidak ada koneksi internet');
    }

    try {
      final category = await remoteDataSource.updateCategory(id, categoryData);
      return ApiResult.success(category.toEntity());
    } on NetworkException catch (e) {
      return ApiResult.failure(e.message);
    } catch (e) {
      return ApiResult.failure('Gagal memperbarui kategori: $e');
    }
  }

  @override
  Future<ApiResult<void>> deleteCategory(String id) async {
    if (!await networkInfo.isConnected) {
      return  ApiResult.failure('Tidak ada koneksi internet');
    }

    try {
      await remoteDataSource.deleteCategory(id);
      return  ApiResult.success(null);
    } on NetworkException catch (e) {
      return ApiResult.failure(e.message);
    } catch (e) {
      return ApiResult.failure('Gagal menghapus kategori: $e');
    }
  }
}