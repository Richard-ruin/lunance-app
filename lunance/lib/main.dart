// file: lib/main.dart
import 'package:flutter/material.dart';
import 'test_backend_connection.dart';

void main() {
  runApp(MyApp());
}

class MyApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Lunance Test',
      theme: ThemeData(
        primarySwatch: Colors.blue,
      ),
      home: BackendConnectionTest(), // Langsung ke test
    );
  }
}