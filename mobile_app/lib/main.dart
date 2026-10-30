import 'package:flutter/material.dart';
import 'constants/theme.dart';
import 'services/supabase_service.dart';
import 'screens/login_screen.dart';

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();

  // Initialize Supabase Cloud Service (guaranteed never to block UI startup)
  try {
    await SupabaseService.initialize().timeout(
      const Duration(seconds: 4),
      onTimeout: () {
        debugPrint('[SupabaseService] Fast init timeout reached; starting UI with instant cache');
      },
    );
  } catch (e) {
    debugPrint('[Main] Supabase init notice: $e');
  }

  runApp(const VeriFaceApp());
}

class VeriFaceApp extends StatelessWidget {
  const VeriFaceApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'VeriFace AI • Smart Attendance',
      debugShowCheckedModeBanner: false,
      theme: AppTheme.lightTheme,
      home: const LoginScreen(),
    );
  }
}
