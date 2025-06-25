// lib/core/utils/debug_utils.dart
class DebugUtils {
  static void printResponseStructure(dynamic data, {String prefix = '', int maxDepth = 3, int currentDepth = 0}) {
    if (currentDepth >= maxDepth) {
      print('$prefix... (max depth reached)');
      return;
    }
    
    if (data == null) {
      print('${prefix}null');
    } else if (data is Map<String, dynamic>) {
      print('${prefix}Map<String, dynamic> with ${data.length} keys:');
      data.forEach((key, value) {
        print('$prefix  ├─ $key (${value.runtimeType}):');
        if (value is String && value.length > 100) {
          print('$prefix  │   └─ "${value.substring(0, 50)}..." (${value.length} chars)');
        } else if (value is Map || value is List) {
          printResponseStructure(value, prefix: '$prefix  │   ', maxDepth: maxDepth, currentDepth: currentDepth + 1);
        } else {
          print('$prefix  │   └─ $value');
        }
      });
    } else if (data is List) {
      print('${prefix}List with ${data.length} items:');
      for (int i = 0; i < data.length && i < 3; i++) {
        print('$prefix  ├─ [$i] (${data[i].runtimeType}):');
        printResponseStructure(data[i], prefix: '$prefix  │   ', maxDepth: maxDepth, currentDepth: currentDepth + 1);
      }
      if (data.length > 3) {
        print('$prefix  └─ ... (${data.length - 3} more items)');
      }
    } else {
      String valueStr = data.toString();
      if (valueStr.length > 100) {
        valueStr = '${valueStr.substring(0, 100)}...';
      }
      print('$prefix$valueStr (${data.runtimeType})');
    }
  }
  
  static void analyzeUserData(Map<String, dynamic> userData) {
    print('\n🔍 ANALYZING USER DATA STRUCTURE:');
    print('═══════════════════════════════════════');
    
    // Check top level fields
    print('\n📋 TOP LEVEL FIELDS:');
    userData.forEach((key, value) {
      print('  ├─ $key: ${value.runtimeType} = ${value.toString().length > 50 ? '${value.toString().substring(0, 50)}...' : value}');
    });
    
    // Check for profile structure
    print('\n👤 PROFILE ANALYSIS:');
    if (userData['profile'] != null) {
      print('  ✅ Found nested profile object');
      final profile = userData['profile'] as Map<String, dynamic>;
      profile.forEach((key, value) {
        print('    ├─ profile.$key: ${value.runtimeType} = $value');
      });
    } else {
      print('  ❌ No nested profile object found');
      print('  🔍 Checking for profile fields at root level:');
      final profileFields = ['full_name', 'fullName', 'name', 'university', 'faculty', 'major', 'semester'];
      for (String field in profileFields) {
        if (userData[field] != null) {
          print('    ✅ Found $field at root: ${userData[field]}');
        }
      }
    }
    
    // Check for verification structure
    print('\n✅ VERIFICATION ANALYSIS:');
    if (userData['verification'] != null) {
      print('  ✅ Found nested verification object');
      final verification = userData['verification'] as Map<String, dynamic>;
      verification.forEach((key, value) {
        print('    ├─ verification.$key: ${value.runtimeType} = $value');
      });
    } else {
      print('  ❌ No nested verification object found');
      print('  🔍 Checking for verification fields at root level:');
      final verificationFields = ['email_verified', 'emailVerified', 'is_email_verified', 'verified'];
      for (String field in verificationFields) {
        if (userData[field] != null) {
          print('    ✅ Found $field at root: ${userData[field]}');
        }
      }
    }
    
    // Check required fields
    print('\n🎯 REQUIRED FIELDS CHECK:');
    final requiredFields = {
      'id': userData['id'],
      'email': userData['email'],
      'profile.full_name': userData['profile']?['full_name'] ?? userData['full_name'] ?? userData['fullName'] ?? userData['name'],
    };
    
    requiredFields.forEach((field, value) {
      if (value != null && value.toString().isNotEmpty) {
        print('  ✅ $field: OK ($value)');
      } else {
        print('  ❌ $field: MISSING OR EMPTY');
      }
    });
    
    print('═══════════════════════════════════════\n');
  }
}