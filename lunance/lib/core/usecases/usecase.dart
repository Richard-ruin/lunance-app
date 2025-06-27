
// lib/core/usecases/usecase.dart
import 'package:equatable/equatable.dart';
import '../network/api_result.dart';

abstract class UseCase<Type, Params> {
  Future<ApiResult<Type>> call(Params params);
}

class NoParams extends Equatable {
  @override
  List<Object> get props => [];
}