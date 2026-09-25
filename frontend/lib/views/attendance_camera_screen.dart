import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/attendance_provider.dart';

class AttendanceCameraScreen extends StatefulWidget {
  const AttendanceCameraScreen({super.key});

  @override
  State<AttendanceCameraScreen> createState() => _AttendanceCameraScreenState();
}

class _AttendanceCameraScreenState extends State<AttendanceCameraScreen> {
  bool _isProcessing = false;
  String? _statusMessage;

  void _simulateFaceCapture() async {
    setState(() {
      _isProcessing = true;
      _statusMessage = "Detecting face and extracting embeddings...";
    });

    await Future.delayed(const Duration(seconds: 2));

    if (!mounted) return;
    Provider.of<AttendanceProvider>(context, listen: false).markAttendance('PRESENT', 0.96);

    setState(() {
      _isProcessing = false;
      _statusMessage = "Attendance Verified Successfully! (Match Confidence: 96.4%)";
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Face Attendance Camera'),
        backgroundColor: const Color(0xFF1E1B4B),
      ),
      body: Container(
        color: const Color(0xFF0F172A),
        child: Padding(
          padding: const EdgeInsets.all(24.0),
          child: Column(
            children: [
              Expanded(
                child: Container(
                  decoration: BoxDecoration(
                    color: const Color(0xFF1E293B),
                    borderRadius: BorderRadius.circular(16),
                    border: Border.all(color: const Color(0xFF6366F1), width: 2),
                  ),
                  child: Center(
                    child: _isProcessing
                        ? const CircularProgressIndicator(color: Color(0xFF6366F1))
                        : Column(
                            mainAxisAlignment: MainAxisAlignment.center,
                            children: const [
                              Icon(Icons.face_retouching_natural, size: 96, color: Color(0xFF818CF8)),
                              SizedBox(height: 16),
                              Text('Position face inside frame', style: TextStyle(color: Colors.white70)),
                            ],
                          ),
                  ),
                ),
              ),
              const SizedBox(height: 16),
              if (_statusMessage != null)
                Text(
                  _statusMessage!,
                  style: const TextStyle(color: Color(0xFF10B981), fontWeight: FontWeight.bold),
                  textAlign: TextAlign.center,
                ),
              const SizedBox(height: 16),
              SizedBox(
                width: double.infinity,
                height: 48,
                child: ElevatedButton.icon(
                  style: ElevatedButton.styleFrom(
                    backgroundColor: const Color(0xFF6366F1),
                  ),
                  icon: const Icon(Icons.camera, color: Colors.white),
                  label: const Text('Capture & Verify Face', style: TextStyle(color: Colors.white, fontSize: 16)),
                  onPressed: _isProcessing ? null : _simulateFaceCapture,
                ),
              )
            ],
          ),
        ),
      ),
    );
  }
}
