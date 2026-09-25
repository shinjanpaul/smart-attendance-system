import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'routes/app_router.dart';
import 'providers/auth_provider.dart';
import 'providers/attendance_provider.dart';

void main() {
  runApp(const SmartAttendanceApp());
}

class SmartAttendanceApp extends StatelessWidget {
  const SmartAttendanceApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MultiProvider(
      providers: [
        ChangeNotifierProvider(create: (_) => AuthProvider()),
        ChangeNotifierProvider(create: (_) => AttendanceProvider()),
      ],
      child: MaterialApp(
        title: 'Smart Attendance & Productivity',
        debugShowCheckedModeBanner: false,
        theme: ThemeData(
          useMaterial3: true,
          colorScheme: ColorScheme.fromSeed(
            seedColor: const Color(0xFF6366F1), // Indigo
            brightness: Brightness.dark,
          ),
          fontFamily: 'Roboto',
        ),
        initialRoute: AppRouter.loginRoute,
        onGenerateRoute: AppRouter.generateRoute,
      ),
    );
  }
}
