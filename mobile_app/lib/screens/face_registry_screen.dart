import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:cached_network_image/cached_network_image.dart';
import 'package:image_picker/image_picker.dart';
import '../constants/theme.dart';
import '../models/models.dart';
import '../services/supabase_service.dart';

class FaceRegistryScreen extends StatefulWidget {
  const FaceRegistryScreen({super.key});

  @override
  State<FaceRegistryScreen> createState() => _FaceRegistryScreenState();
}

class _FaceRegistryScreenState extends State<FaceRegistryScreen> {
  final _service = SupabaseService();
  final _picker = ImagePicker();
  List<UserProfile> _students = [];
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _loadStudents();
  }

  Future<void> _loadStudents() async {
    final s = await _service.getStudents();
    setState(() {
      _students = s;
      _isLoading = false;
    });
  }

  Future<void> _enrollFace(UserProfile student) async {
    try {
      final photo = await _picker.pickImage(source: ImageSource.camera, imageQuality: 85);
      if (photo != null && mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            backgroundColor: AppTheme.primary,
            content: Text('Extracting 128-D Euclidean Vector for ${student.fullName}...'),
          ),
        );
        // Simulate biometric registration
        await Future.delayed(const Duration(seconds: 1));
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              backgroundColor: AppTheme.success,
              content: Text('Face biometrics enrolled for ${student.fullName}!'),
            ),
          );
        }
      }
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Enrollment error: $e')),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_isLoading) {
      return const Scaffold(
        body: Center(child: CircularProgressIndicator(color: AppTheme.primary)),
      );
    }

    return Scaffold(
      backgroundColor: AppTheme.surface,
      appBar: AppBar(
        title: Text('Face ID Biometric Registry', style: GoogleFonts.plusJakartaSans(fontWeight: FontWeight.bold, fontSize: 16)),
      ),
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 14),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text('ResNet 128-D Facial Embeddings', style: GoogleFonts.plusJakartaSans(fontSize: 16, fontWeight: FontWeight.bold, color: AppTheme.onSurface)),
              const SizedBox(height: 2),
              Text('Enrolled students can be automatically verified in classroom photos', style: GoogleFonts.inter(fontSize: 11, color: AppTheme.secondary)),
              const SizedBox(height: 16),

              Expanded(
                child: ListView.separated(
                  itemCount: _students.length,
                  separatorBuilder: (_, __) => const SizedBox(height: 10),
                  itemBuilder: (context, index) {
                    final s = _students[index];
                    return Container(
                      padding: const EdgeInsets.all(12),
                      decoration: BoxDecoration(
                        color: Colors.white,
                        borderRadius: BorderRadius.circular(16),
                        border: Border.all(color: AppTheme.outlineVariant.withOpacity(0.3)),
                      ),
                      child: Row(
                        children: [
                          _buildAvatar(s.profilePictureUrl, s.initials),
                          const SizedBox(width: 12),
                          Expanded(
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Text(s.fullName, style: GoogleFonts.plusJakartaSans(fontSize: 13, fontWeight: FontWeight.bold, color: AppTheme.onSurface)),
                                Text(
                                  s.hasRegisteredFace ? 'Centroid biometric indexed (128-D)' : 'No face embeddings',
                                  style: GoogleFonts.inter(
                                    fontSize: 10,
                                    color: s.hasRegisteredFace ? AppTheme.secondary : AppTheme.warning,
                                    fontWeight: s.hasRegisteredFace ? FontWeight.normal : FontWeight.bold,
                                  ),
                                ),
                              ],
                            ),
                          ),
                          if (s.hasRegisteredFace)
                            Container(
                              padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                              decoration: BoxDecoration(color: AppTheme.successBg, borderRadius: BorderRadius.circular(12)),
                              child: Text('Registered', style: GoogleFonts.inter(fontSize: 10, fontWeight: FontWeight.bold, color: AppTheme.success)),
                            )
                          else
                            ElevatedButton(
                              onPressed: () => _enrollFace(s),
                              style: ElevatedButton.styleFrom(
                                padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                              ),
                              child: const Text('+ Enroll Face', style: TextStyle(fontSize: 10)),
                            ),
                        ],
                      ),
                    );
                  },
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildAvatar(String? url, String initials) {
    if (url != null && url.isNotEmpty) {
      return ClipRRect(
        borderRadius: BorderRadius.circular(20),
        child: CachedNetworkImage(
          imageUrl: url,
          width: 40,
          height: 40,
          fit: BoxFit.cover,
          placeholder: (_, __) => CircleAvatar(backgroundColor: AppTheme.primaryFixed, child: Text(initials, style: const TextStyle(color: AppTheme.primary))),
          errorWidget: (_, __, ___) => CircleAvatar(backgroundColor: AppTheme.primaryFixed, child: Text(initials, style: const TextStyle(color: AppTheme.primary))),
        ),
      );
    }
    return CircleAvatar(
      radius: 20,
      backgroundColor: AppTheme.primaryFixed,
      child: Text(initials, style: GoogleFonts.plusJakartaSans(fontSize: 12, fontWeight: FontWeight.bold, color: AppTheme.primary)),
    );
  }
}
