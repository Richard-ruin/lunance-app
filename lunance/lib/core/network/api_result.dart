// lib/core/network/api_result.dart
import 'package:equatable/equatable.dart';

abstract class ApiResult<T> extends Equatable {
  const ApiResult();

  // Factory constructors
  factory ApiResult.success(T data) = Success<T>;
  factory ApiResult.failure(String error) = Failure<T>;

  // When method for pattern matching
  R when<R>({
    required R Function(T data) success,
    required R Function(String error) failure,
  }) {
    if (this is Success<T>) {
      return success((this as Success<T>).data);
    } else if (this is Failure<T>) {
      return failure((this as Failure<T>).error);
    } else {
      throw Exception('Unknown ApiResult type');
    }
  }

  // Convenience getters
  bool get isSuccess => this is Success<T>;
  bool get isFailure => this is Failure<T>;

  T? get data => isSuccess ? (this as Success<T>).data : null;
  String? get error => isFailure ? (this as Failure<T>).error : null;

  @override
  List<Object?> get props => [];
}

class Success<T> extends ApiResult<T> {
  final T data;

  const Success(this.data);

  @override
  List<Object?> get props => [data];

  @override
  String toString() => 'Success(data: $data)';
}

class Failure<T> extends ApiResult<T> {
  final String error;

  const Failure(this.error);

  @override
  List<Object?> get props => [error];

  @override
  String toString() => 'Failure(error: $error)';
}