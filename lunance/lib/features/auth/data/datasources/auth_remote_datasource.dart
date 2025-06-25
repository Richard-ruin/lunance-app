// lib/features/auth/data/datasources/auth_remote_datasource.dart
import 'dart:convert';
import 'package:http/http.dart' as http;
import '../../../../core/constants/api_endpoints.dart';
import '../../../../core/storage/local_storage.dart';
import '../models/user_model.dart';
import '../models/login_request_model.dart';
import '../models/register_request_model.dart';

abstract class AuthRemoteDataSource {
  Future<Map<String, dynamic>> login(LoginRequestModel request);
  Future<void> register(RegisterRequestModel request);
  Future<void> logout();
  Future<void> forgotPassword(String email);
  Future<void> verifyOtp({
    required String email,
    required String code,
    required String type,
  });
  Future<void> resetPassword({
    required String email,
    required String otpCode,
    required String newPassword,
  });
  Future<UserModel?> getCurrentUser();
  Future<void> requestOtp({
    required String email,
    required String type,
  });
}

class AuthRemoteDataSourceImpl implements AuthRemoteDataSource {
  final http.Client client;
  final LocalStorage localStorage;

  AuthRemoteDataSourceImpl({
    required this.client,
    required this.localStorage,
  });

  @override
  Future<Map<String, dynamic>> login(LoginRequestModel request) async {
    try {
      print('\n🚀 LOGIN REQUEST STARTED');
      print('═══════════════════════════════════════');
      print('📡 URL: ${ApiEndpoints.login}');
      print('📋 Request Body: ${json.encode(request.toJson())}');
      
      final response = await client.post(
        Uri.parse(ApiEndpoints.login),
        headers: {
          'Content-Type': 'application/json',
        },
        body: json.encode(request.toJson()),
      );

      print('\n📥 LOGIN RESPONSE RECEIVED');
      print('═══════════════════════════════════════');
      print('📊 Status Code: ${response.statusCode}');
      print('📄 Raw Response Body:');
      print(response.body);
      print('═══════════════════════════════════════');

      if (response.statusCode == 200) {
        try {
          final data = json.decode(response.body) as Map<String, dynamic>;
          
          print('\n🔍 CHECKING LOGIN RESPONSE STRUCTURE');
          print('═══════════════════════════════════════');
          print('📋 Response keys: ${data.keys.toList()}');
          
          // Validate required fields for login response
          final accessToken = data['access_token']?.toString();
          final refreshToken = data['refresh_token']?.toString();
          final tokenType = data['token_type']?.toString();
          final message = data['message']?.toString();
          
          print('🔑 access_token: ${accessToken != null ? 'PRESENT (${accessToken.length} chars)' : 'MISSING'}');
          print('🔑 refresh_token: ${refreshToken != null ? 'PRESENT (${refreshToken.length} chars)' : 'MISSING'}');
          print('🏷️ token_type: $tokenType');
          print('💬 message: $message');
          
          if (accessToken == null || accessToken.isEmpty) {
            throw Exception('Missing or empty access_token in response');
          }
          
          if (refreshToken == null || refreshToken.isEmpty) {
            throw Exception('Missing or empty refresh_token in response');
          }
          
          // Save tokens
          print('\n💾 SAVING TOKENS TO LOCAL STORAGE');
          print('═══════════════════════════════════════');
          await localStorage.saveString('access_token', accessToken);
          await localStorage.saveString('refresh_token', refreshToken);
          print('✅ Tokens saved successfully');
          
          // Check if user data is included in response
          if (data['user'] != null) {
            print('\n👤 USER DATA FOUND IN LOGIN RESPONSE');
            print('═══════════════════════════════════════');
            final userData = data['user'] as Map<String, dynamic>;
            
            try {
              final userModel = UserModel.fromJson(userData);
              await localStorage.saveString('user_data', json.encode(userData));
              print('✅ User data saved successfully');
              print('📋 User: ${userModel.toString()}');
            } catch (userError) {
              print('❌ Failed to parse user data: $userError');
              // Don't fail login just because user data parsing failed
              // We'll fetch it separately
            }
          } else {
            print('\n👤 NO USER DATA IN LOGIN RESPONSE');
            print('═══════════════════════════════════════');
            print('🔄 Will fetch user data separately using /me endpoint');
            
            // Fetch user data separately
            try {
              final userModel = await _fetchCurrentUser(accessToken);
              if (userModel != null) {
                await localStorage.saveString('user_data', json.encode(userModel.toJson()));
                print('✅ User data fetched and saved successfully');
                print('📋 User: ${userModel.toString()}');
                
                // Add user data to response for consistency
                data['user'] = userModel.toJson();
              }
            } catch (fetchError) {
              print('⚠️ Failed to fetch user data: $fetchError');
              // Continue with login even if user fetch fails
              // User data can be fetched later
            }
          }
          
          print('\n🎉 LOGIN COMPLETED SUCCESSFULLY');
          print('═══════════════════════════════════════\n');
          
          return data;
          
        } catch (parseError, stackTrace) {
          print('\n❌ JSON PARSING ERROR');
          print('═══════════════════════════════════════');
          print('Error: $parseError');
          print('Stack trace: $stackTrace');
          print('Raw response: ${response.body}');
          print('═══════════════════════════════════════\n');
          throw Exception('Failed to parse server response: $parseError');
        }
      } else {
        print('\n❌ HTTP ERROR');
        print('═══════════════════════════════════════');
        print('Status: ${response.statusCode}');
        print('Body: ${response.body}');
        
        try {
          final errorData = json.decode(response.body) as Map<String, dynamic>?;
          final errorMessage = errorData?['detail']?.toString() ?? 
                              errorData?['message']?.toString() ?? 
                              'Login failed with status ${response.statusCode}';
          throw Exception(errorMessage);
        } catch (e) {
          throw Exception('HTTP ${response.statusCode}: ${response.body}');
        }
      }
    } catch (e, stackTrace) {
      print('\n💥 LOGIN EXCEPTION');
      print('═══════════════════════════════════════');
      print('Error: $e');
      print('Type: ${e.runtimeType}');
      print('Stack trace: $stackTrace');
      print('═══════════════════════════════════════\n');
      
      if (e is Exception) {
        rethrow;
      }
      throw Exception('Network error: ${e.toString()}');
    }
  }

  // Helper method to fetch current user data
  Future<UserModel?> _fetchCurrentUser(String accessToken) async {
    try {
      print('🔄 Fetching user data from /me endpoint...');
      
      final response = await client.get(
        Uri.parse(ApiEndpoints.me),
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer $accessToken',
        },
      );

      if (response.statusCode == 200) {
        final userData = json.decode(response.body) as Map<String, dynamic>;
        print('✅ User data fetched successfully from /me');
        return UserModel.fromJson(userData);
      } else {
        print('❌ Failed to fetch user data: HTTP ${response.statusCode}');
        print('Response: ${response.body}');
        return null;
      }
    } catch (e) {
      print('❌ Error fetching user data: $e');
      return null;
    }
  }

  @override
  Future<UserModel?> getCurrentUser() async {
    final token = localStorage.getString('access_token');
    final userData = localStorage.getString('user_data');
    
    print('\n🔍 GET CURRENT USER');
    print('═══════════════════════════════════════');
    print('🔑 Token present: ${token != null}');
    print('📋 Stored user data: ${userData != null}');

    if (token == null) {
      print('❌ No access token found');
      return null;
    }

    try {
      // First try to fetch fresh data from server
      final response = await client.get(
        Uri.parse(ApiEndpoints.me),
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer $token',
        },
      );

      print('📡 API call to /me: Status ${response.statusCode}');

      if (response.statusCode == 200) {
        final data = json.decode(response.body) as Map<String, dynamic>;
        print('✅ Fresh user data received from server');
        
        final user = UserModel.fromJson(data);
        
        // Update stored user data
        await localStorage.saveString('user_data', json.encode(data));
        print('💾 Updated stored user data');
        
        return user;
      } else {
        print('⚠️ Server request failed, trying stored data...');
        // Token might be invalid, use stored data if available
        if (userData != null) {
          try {
            final storedData = json.decode(userData) as Map<String, dynamic>;
            print('✅ Using stored user data');
            return UserModel.fromJson(storedData);
          } catch (e) {
            print('❌ Error parsing stored user data: $e');
            return null;
          }
        }
      }
    } catch (e) {
      print('💥 Network error: $e');
      // Network error, use stored data if available
      if (userData != null) {
        try {
          final storedData = json.decode(userData) as Map<String, dynamic>;
          print('✅ Using stored user data (fallback)');
          return UserModel.fromJson(storedData);
        } catch (parseError) {
          print('❌ Error parsing stored user data: $parseError');
          return null;
        }
      }
    }
    
    print('❌ No user data available');
    return null;
  }

  // Sisanya tetap sama...
  @override
  Future<void> register(RegisterRequestModel request) async {
    try {
      final response = await client.post(
        Uri.parse(ApiEndpoints.register),
        headers: {
          'Content-Type': 'application/json',
        },
        body: json.encode(request.toJson()),
      );

      if (response.statusCode != 200) {
        final errorData = json.decode(response.body) as Map<String, dynamic>?;
        final errorMessage = errorData?['detail']?.toString() ?? 
                            errorData?['message']?.toString() ?? 
                            'Registration failed';
        throw Exception(errorMessage);
      }
    } catch (e) {
      if (e is Exception) {
        rethrow;
      }
      throw Exception('Network error: ${e.toString()}');
    }
  }

  @override
  Future<void> logout() async {
    final token = localStorage.getString('access_token');
    
    if (token != null) {
      try {
        await client.post(
          Uri.parse(ApiEndpoints.logout),
          headers: {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer $token',
          },
        );
      } catch (e) {
        print('Server logout failed: $e');
      }
    }
    
    // Clear local storage
    await localStorage.remove('access_token');
    await localStorage.remove('refresh_token');
    await localStorage.remove('user_data');
  }

  @override
  Future<void> forgotPassword(String email) async {
    try {
      final response = await client.post(
        Uri.parse(ApiEndpoints.forgotPassword),
        headers: {
          'Content-Type': 'application/json',
        },
        body: json.encode({'email': email}),
      );

      if (response.statusCode != 200) {
        final errorData = json.decode(response.body) as Map<String, dynamic>?;
        final errorMessage = errorData?['detail']?.toString() ?? 
                            errorData?['message']?.toString() ?? 
                            'Failed to send reset code';
        throw Exception(errorMessage);
      }
    } catch (e) {
      if (e is Exception) {
        rethrow;
      }
      throw Exception('Network error: ${e.toString()}');
    }
  }

  @override
  Future<void> verifyOtp({
    required String email,
    required String code,
    required String type,
  }) async {
    try {
      final response = await client.post(
        Uri.parse(ApiEndpoints.verifyOtp),
        headers: {
          'Content-Type': 'application/json',
        },
        body: json.encode({
          'email': email,
          'code': code,
          'type': type,
        }),
      );

      if (response.statusCode != 200) {
        final errorData = json.decode(response.body) as Map<String, dynamic>?;
        final errorMessage = errorData?['detail']?.toString() ?? 
                            errorData?['message']?.toString() ?? 
                            'OTP verification failed';
        throw Exception(errorMessage);
      }
    } catch (e) {
      if (e is Exception) {
        rethrow;
      }
      throw Exception('Network error: ${e.toString()}');
    }
  }

  @override
  Future<void> resetPassword({
    required String email,
    required String otpCode,
    required String newPassword,
  }) async {
    try {
      final response = await client.post(
        Uri.parse(ApiEndpoints.resetPassword),
        headers: {
          'Content-Type': 'application/json',
        },
        body: json.encode({
          'email': email,
          'otp_code': otpCode,
          'new_password': newPassword,
        }),
      );

      if (response.statusCode != 200) {
        final errorData = json.decode(response.body) as Map<String, dynamic>?;
        final errorMessage = errorData?['detail']?.toString() ?? 
                            errorData?['message']?.toString() ?? 
                            'Password reset failed';
        throw Exception(errorMessage);
      }
    } catch (e) {
      if (e is Exception) {
        rethrow;
      }
      throw Exception('Network error: ${e.toString()}');
    }
  }

  @override
  Future<void> requestOtp({
    required String email,
    required String type,
  }) async {
    try {
      final response = await client.post(
        Uri.parse(ApiEndpoints.requestOtp),
        headers: {
          'Content-Type': 'application/json',
        },
        body: json.encode({
          'email': email,
          'type': type,
        }),
      );

      if (response.statusCode != 200) {
        final errorData = json.decode(response.body) as Map<String, dynamic>?;
        final errorMessage = errorData?['detail']?.toString() ?? 
                            errorData?['message']?.toString() ?? 
                            'Failed to send OTP';
        throw Exception(errorMessage);
      }
    } catch (e) {
      if (e is Exception) {
        rethrow;
      }
      throw Exception('Network error: ${e.toString()}');
    }
  }
}