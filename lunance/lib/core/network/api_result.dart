
// lib/core/network/api_result.dart
import 'package:equatable/equatable.dart';

abstract class ApiResult<T> extends Equatable {
  const ApiResult();

  @override
  List<Object?> get props => [];
}

class ApiSuccess<T> extends ApiResult<T> {
  final T data;
  final String? message;

  const ApiSuccess(this.data, {this.message});

  @override
  List<Object?> get props => [data, message];
}

class ApiError<T> extends ApiResult<T> {
  final String message;
  final int? statusCode;
  final T? data;

  const ApiError(this.message, {this.statusCode, this.data});

  @override
  List<Object?> get props => [message, statusCode, data];
}

class ApiLoading<T> extends ApiResult<T> {
  const ApiLoading();
}

// lib/core/network/network_exceptions.dart
class NetworkException implements Exception {
  final String message;
  final int? statusCode;

  NetworkException(this.message, {this.statusCode});

  @override
  String toString() {
    return 'NetworkException: $message${statusCode != null ? ' (Status: $statusCode)' : ''}';
  }
}

class ServerException extends NetworkException {
  ServerException([String message = 'Server error occurred']) 
      : super(message, statusCode: 500);
}

class CacheException extends NetworkException {
  CacheException([String message = 'Cache error occurred']) 
      : super(message);
}

class UnauthorizedException extends NetworkException {
  UnauthorizedException([String message = 'Unauthorized access']) 
      : super(message, statusCode: 401);
}

class ForbiddenException extends NetworkException {
  ForbiddenException([String message = 'Access forbidden']) 
      : super(message, statusCode: 403);
}

class NotFoundException extends NetworkException {
  NotFoundException([String message = 'Resource not found']) 
      : super(message, statusCode: 404);
}

class ValidationException extends NetworkException {
  ValidationException([String message = 'Validation failed']) 
      : super(message, statusCode: 422);
}

class TimeoutException extends NetworkException {
  TimeoutException([String message = 'Request timeout']) 
      : super(message);
}

class NoInternetException extends NetworkException {
  NoInternetException([String message = 'No internet connection']) 
      : super(message);
}