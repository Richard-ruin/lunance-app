// file: lib/test_backend_connection.dart
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'dart:async';

class BackendConnectionTest extends StatefulWidget {
  @override
  _BackendConnectionTestState createState() => _BackendConnectionTestState();
}

class _BackendConnectionTestState extends State<BackendConnectionTest> {
  // Backend URL - sesuaikan dengan IP server Anda
  final String baseUrl = 'http://192.168.190.195:8000';
  
  // State variables
  bool isLoading = false;
  bool isConnected = false;
  String connectionStatus = 'Not tested';
  Map<String, dynamic>? healthData;
  String? errorMessage;
  Duration? responseTime;

  @override
  void initState() {
    super.initState();
    // Auto test saat aplikasi dimulai
    testConnection();
  }

  Future<void> testConnection() async {
    setState(() {
      isLoading = true;
      connectionStatus = 'Testing...';
      errorMessage = null;
      healthData = null;
    });

    try {
      final stopwatch = Stopwatch()..start();
      
      // Test koneksi ke endpoint /health
      final response = await http.get(
        Uri.parse('$baseUrl/health'),
        headers: {
          'Content-Type': 'application/json',
        },
      ).timeout(Duration(seconds: 10));

      stopwatch.stop();
      responseTime = stopwatch.elapsed;

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        
        setState(() {
          isConnected = true;
          connectionStatus = 'Connected Successfully';
          healthData = data;
          isLoading = false;
        });
      } else {
        setState(() {
          isConnected = false;
          connectionStatus = 'Connection Failed';
          errorMessage = 'HTTP ${response.statusCode}: ${response.reasonPhrase}';
          isLoading = false;
        });
      }
    } on TimeoutException {
      setState(() {
        isConnected = false;
        connectionStatus = 'Connection Timeout';
        errorMessage = 'Request timeout after 10 seconds';
        isLoading = false;
      });
    } on http.ClientException catch (e) {
      setState(() {
        isConnected = false;
        connectionStatus = 'Network Error';
        errorMessage = 'Network error: ${e.message}';
        isLoading = false;
      });
    } catch (e) {
      setState(() {
        isConnected = false;
        connectionStatus = 'Unknown Error';
        errorMessage = 'Unexpected error: $e';
        isLoading = false;
      });
    }
  }

  Future<void> testAllEndpoints() async {
    setState(() {
      isLoading = true;
      connectionStatus = 'Testing All Endpoints...';
    });

    try {
      // Test endpoint utama
      final endpoints = [
        '/',
        '/health',
        '/api-info',
      ];

      Map<String, dynamic> results = {};
      
      for (String endpoint in endpoints) {
        try {
          final response = await http.get(
            Uri.parse('$baseUrl$endpoint'),
            headers: {'Content-Type': 'application/json'},
          ).timeout(Duration(seconds: 5));
          
          results[endpoint] = {
            'status': response.statusCode,
            'success': response.statusCode == 200,
            'data': response.statusCode == 200 ? json.decode(response.body) : null
          };
        } catch (e) {
          results[endpoint] = {
            'status': 'error',
            'success': false,
            'error': e.toString()
          };
        }
      }

      setState(() {
        healthData = results;
        connectionStatus = 'All Endpoints Tested';
        isLoading = false;
      });
    } catch (e) {
      setState(() {
        errorMessage = 'Error testing endpoints: $e';
        connectionStatus = 'Test Failed';
        isLoading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Lunance Backend Test'),
        backgroundColor: Colors.blue[800],
        elevation: 0,
      ),
      body: Container(
        decoration: BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topCenter,
            end: Alignment.bottomCenter,
            colors: [Colors.blue[800]!, Colors.blue[50]!],
          ),
        ),
        child: Padding(
          padding: const EdgeInsets.all(16.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              // Header Card
              Card(
                elevation: 4,
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Padding(
                  padding: const EdgeInsets.all(20.0),
                  child: Column(
                    children: [
                      Icon(
                        isConnected ? Icons.cloud_done : Icons.cloud_off,
                        size: 50,
                        color: isConnected ? Colors.green : Colors.red,
                      ),
                      SizedBox(height: 12),
                      Text(
                        'Backend Connection Status',
                        style: TextStyle(
                          fontSize: 18,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      SizedBox(height: 8),
                      Text(
                        connectionStatus,
                        style: TextStyle(
                          fontSize: 16,
                          color: isConnected ? Colors.green : Colors.red,
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                      if (responseTime != null) ...[
                        SizedBox(height: 8),
                        Text(
                          'Response Time: ${responseTime!.inMilliseconds}ms',
                          style: TextStyle(
                            fontSize: 14,
                            color: Colors.grey[600],
                          ),
                        ),
                      ],
                    ],
                  ),
                ),
              ),
              
              SizedBox(height: 16),
              
              // Action Buttons
              Row(
                children: [
                  Expanded(
                    child: ElevatedButton.icon(
                      onPressed: isLoading ? null : testConnection,
                      icon: isLoading
                          ? SizedBox(
                              width: 20,
                              height: 20,
                              child: CircularProgressIndicator(
                                strokeWidth: 2,
                                valueColor: AlwaysStoppedAnimation<Color>(Colors.white),
                              ),
                            )
                          : Icon(Icons.refresh),
                      label: Text('Test Health'),
                      style: ElevatedButton.styleFrom(
                        backgroundColor: Colors.blue[600],
                        foregroundColor: Colors.white,
                        padding: EdgeInsets.symmetric(vertical: 12),
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(8),
                        ),
                      ),
                    ),
                  ),
                  SizedBox(width: 12),
                  Expanded(
                    child: ElevatedButton.icon(
                      onPressed: isLoading ? null : testAllEndpoints,
                      icon: Icon(Icons.api),
                      label: Text('Test All'),
                      style: ElevatedButton.styleFrom(
                        backgroundColor: Colors.green[600],
                        foregroundColor: Colors.white,
                        padding: EdgeInsets.symmetric(vertical: 12),
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(8),
                        ),
                      ),
                    ),
                  ),
                ],
              ),
              
              SizedBox(height: 16),
              
              // Server Info Card
              Card(
                elevation: 2,
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Padding(
                  padding: const EdgeInsets.all(16.0),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'Server Information',
                        style: TextStyle(
                          fontSize: 16,
                          fontWeight: FontWeight.bold,
                          color: Colors.blue[800],
                        ),
                      ),
                      SizedBox(height: 8),
                      Text('Base URL: $baseUrl'),
                      Text('Health Endpoint: $baseUrl/health'),
                      Text('Documentation: $baseUrl/docs'),
                    ],
                  ),
                ),
              ),
              
              SizedBox(height: 16),
              
              // Response Data
              Expanded(
                child: Card(
                  elevation: 2,
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Padding(
                    padding: const EdgeInsets.all(16.0),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          'Response Data',
                          style: TextStyle(
                            fontSize: 16,
                            fontWeight: FontWeight.bold,
                            color: Colors.blue[800],
                          ),
                        ),
                        SizedBox(height: 12),
                        Expanded(
                          child: SingleChildScrollView(
                            child: Container(
                              width: double.infinity,
                              padding: EdgeInsets.all(12),
                              decoration: BoxDecoration(
                                color: Colors.grey[100],
                                borderRadius: BorderRadius.circular(8),
                                border: Border.all(color: Colors.grey[300]!),
                              ),
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  if (errorMessage != null) ...[
                                    Text(
                                      'Error: $errorMessage',
                                      style: TextStyle(
                                        color: Colors.red,
                                        fontWeight: FontWeight.w500,
                                      ),
                                    ),
                                  ] else if (healthData != null) ...[
                                    Text(
                                      _formatJson(healthData!),
                                      style: TextStyle(
                                        fontFamily: 'monospace',
                                        fontSize: 12,
                                      ),
                                    ),
                                  ] else ...[
                                    Text(
                                      'No data available. Click "Test Health" to check connection.',
                                      style: TextStyle(
                                        color: Colors.grey[600],
                                        fontStyle: FontStyle.italic,
                                      ),
                                    ),
                                  ],
                                ],
                              ),
                            ),
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  String _formatJson(Map<String, dynamic> json) {
    JsonEncoder encoder = JsonEncoder.withIndent('  ');
    return encoder.convert(json);
  }
}

