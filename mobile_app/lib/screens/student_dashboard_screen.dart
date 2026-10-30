import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:cached_network_image/cached_network_image.dart';
import '../constants/theme.dart';
import '../models/models.dart';
import '../services/supabase_service.dart';
import 'login_screen.dart';

class StudentDashboardScreen extends StatefulWidget {
  final UserProfile student;

  const StudentDashboardScreen({super.key, required this.student});

  @override
  State<StudentDashboardScreen> createState() => _StudentDashboardScreenState();
}

class _StudentDashboardScreenState extends State<StudentDashboardScreen> {
  final _service = SupabaseService();
  late StudentAttendanceStats _stats;
  String _selectedFacultyCode = 'IT802'; // Default to Prof. Rituparna Sinha's IT802
  String _selectedFacultyName = 'Prof. Rituparna Sinha';
  bool _isLoading = true;

  final List<Map<String, String>> _faculties = [
    {'name': 'Prof. Rituparna Sinha', 'code': 'IT802', 'dept': 'Machine Learning'},
    {'name': 'Prof. Sudipta Bhadra', 'code': 'IT801', 'dept': 'Cloud Computing'},
    {'name': 'Prof. Ananya Mukherjee', 'code': 'IT803', 'dept': 'Cyber Security'},
    {'name': 'Prof. Rajesh Sharma', 'code': 'AD401', 'dept': 'AI & Data Science'},
    {'name': 'Prof. Debashis Roy', 'code': 'CS601', 'dept': 'Computer Science'},
  ];

  @override
  void initState() {
    super.initState();
    _loadAttendance();
  }

  Future<void> _loadAttendance() async {
    final logs = await _service.getAttendanceLogs(studentId: widget.student.id);
    setState(() {
      _stats = _service.calculateStats(widget.student, logs);
      _isLoading = false;
    });
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
        title: Row(
          children: [
            Container(
              padding: const EdgeInsets.all(6),
              decoration: BoxDecoration(
                color: AppTheme.primary,
                borderRadius: BorderRadius.circular(10),
              ),
              child: const Icon(Icons.fingerprint, color: Colors.white, size: 18),
            ),
            const SizedBox(width: 8),
            Text('Student Portal', style: GoogleFonts.plusJakartaSans(fontWeight: FontWeight.bold, fontSize: 16)),
          ],
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.logout_rounded, size: 20),
            onPressed: () {
              Navigator.pushReplacement(
                context,
                MaterialPageRoute(builder: (_) => const LoginScreen()),
              );
            },
          ),
        ],
      ),
      body: RefreshIndicator(
        onRefresh: _loadAttendance,
        color: AppTheme.primary,
        child: SingleChildScrollView(
          physics: const AlwaysScrollableScrollPhysics(),
          padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // 1. Student Identity Header
              _buildStudentHeader(),
              const SizedBox(height: 16),

              // 2. Big Attendance Percentage Card
              _buildAttendanceMetricCard(),
              const SizedBox(height: 20),

              // 3. Faculty In-Charge Selector Chips
              Text(
                'Select Faculty Course',
                style: GoogleFonts.plusJakartaSans(fontSize: 13, fontWeight: FontWeight.bold, color: AppTheme.onSurface),
              ),
              const SizedBox(height: 10),
              _buildFacultySelector(),
              const SizedBox(height: 20),

              // 4. Course Attendance Breakdown List
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text(
                    'Course Attendance Breakdown',
                    style: GoogleFonts.plusJakartaSans(fontSize: 13, fontWeight: FontWeight.bold, color: AppTheme.onSurface),
                  ),
                  Text(
                    '75% Required',
                    style: GoogleFonts.inter(fontSize: 11, fontWeight: FontWeight.w600, color: AppTheme.secondary),
                  ),
                ],
              ),
              const SizedBox(height: 12),
              _buildCourseBreakdownList(),
              const SizedBox(height: 24),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildStudentHeader() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: AppTheme.outlineVariant.withOpacity(0.3)),
      ),
      child: Row(
        children: [
          // Real Profile Picture or Initials
          _buildAvatar(widget.student.profilePictureUrl, widget.student.initials),
          const SizedBox(width: 14),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Flexible(
                      child: Text(
                        widget.student.fullName,
                        style: GoogleFonts.plusJakartaSans(fontSize: 16, fontWeight: FontWeight.bold, color: AppTheme.onSurface),
                        overflow: TextOverflow.ellipsis,
                      ),
                    ),
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                      decoration: BoxDecoration(
                        color: _stats.isGoodStanding ? AppTheme.successBg : AppTheme.errorBg,
                        borderRadius: BorderRadius.circular(12),
                      ),
                      child: Text(
                        _stats.isGoodStanding ? 'Good Standing' : 'Low Attendance',
                        style: GoogleFonts.inter(
                          fontSize: 10,
                          fontWeight: FontWeight.bold,
                          color: _stats.isGoodStanding ? AppTheme.success : AppTheme.error,
                        ),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 4),
                Text(
                  'Roll: ${widget.student.rollNumber ?? 'IT2026'} • ${widget.student.department}',
                  style: GoogleFonts.inter(fontSize: 11, color: AppTheme.secondary),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildAttendanceMetricCard() {
    final pct = _stats.percentage;
    final isGood = _stats.isGoodStanding;

    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: [
            AppTheme.primary,
            AppTheme.primaryContainer,
          ],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(24),
        boxShadow: [
          BoxShadow(
            color: AppTheme.primary.withOpacity(0.25),
            blurRadius: 20,
            offset: const Offset(0, 10),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                'Overall Verified Attendance',
                style: GoogleFonts.inter(color: Colors.white.withOpacity(0.9), fontSize: 12, fontWeight: FontWeight.w500),
              ),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                decoration: BoxDecoration(
                  color: Colors.white.withOpacity(0.2),
                  borderRadius: BorderRadius.circular(10),
                ),
                child: Text(
                  '128-D Biometric',
                  style: GoogleFonts.inter(color: Colors.white, fontSize: 10, fontWeight: FontWeight.bold),
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),

          // Big Percentage Number
          Row(
            crossAxisAlignment: CrossAxisAlignment.baseline,
            textBaseline: TextBaseline.alphabetic,
            children: [
              Text(
                '${pct.toStringAsFixed(1)}%',
                style: GoogleFonts.plusJakartaSans(
                  fontSize: 42,
                  fontWeight: FontWeight.bold,
                  color: Colors.white,
                  letterSpacing: -1,
                ),
              ),
              const SizedBox(width: 10),
              Text(
                '${_stats.presentDays} of ${_stats.totalDays} Sessions Attended',
                style: GoogleFonts.inter(
                  fontSize: 12,
                  color: Colors.white.withOpacity(0.85),
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),

          // 75% Safety Margin Progress Bar
          ClipRRect(
            borderRadius: BorderRadius.circular(8),
            child: LinearProgressIndicator(
              value: (pct / 100.0).clamp(0.0, 1.0),
              minHeight: 8,
              backgroundColor: Colors.white.withOpacity(0.25),
              valueColor: AlwaysStoppedAnimation<Color>(
                isGood ? const Color(0xFF34D399) : const Color(0xFFFBBF24),
              ),
            ),
          ),
          const SizedBox(height: 8),

          // Safety margin text
          Text(
            isGood
                ? '+${_stats.safetyMargin.toStringAsFixed(1)}% Above 75% Safety Margin'
                : '-${_stats.safetyMargin.toStringAsFixed(1)}% Short of 75% Criteria',
            style: GoogleFonts.inter(
              fontSize: 11,
              fontWeight: FontWeight.bold,
              color: isGood ? const Color(0xFF6EE7B7) : const Color(0xFFFDE68A),
            ),
          ),
          const SizedBox(height: 16),
          const Divider(color: Colors.white24, height: 1),
          const SizedBox(height: 14),

          // 3 Metric Counters
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceAround,
            children: [
              _buildCounter('Total Held', '${_stats.totalDays}'),
              _buildCounter('Attended', '${_stats.presentDays}'),
              _buildCounter('Missed', '${_stats.absentDays}'),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildCounter(String label, String value) {
    return Column(
      children: [
        Text(value, style: GoogleFonts.plusJakartaSans(fontSize: 18, fontWeight: FontWeight.bold, color: Colors.white)),
        const SizedBox(height: 2),
        Text(label, style: GoogleFonts.inter(fontSize: 10, color: Colors.white70)),
      ],
    );
  }

  Widget _buildFacultySelector() {
    return SizedBox(
      height: 42,
      child: ListView.separated(
        scrollDirection: Axis.horizontal,
        itemCount: _faculties.length,
        separatorBuilder: (_, __) => const SizedBox(width: 8),
        itemBuilder: (context, index) {
          final f = _faculties[index];
          final isSelected = _selectedFacultyCode == f['code'];
          return GestureDetector(
            onTap: () {
              setState(() {
                _selectedFacultyCode = f['code']!;
                _selectedFacultyName = f['name']!;
              });
            },
            child: AnimatedContainer(
              duration: const Duration(milliseconds: 200),
              padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 8),
              decoration: BoxDecoration(
                color: isSelected ? AppTheme.primary : Colors.white,
                borderRadius: BorderRadius.circular(14),
                border: Border.all(
                  color: isSelected ? AppTheme.primary : AppTheme.outlineVariant.withOpacity(0.3),
                  width: 1.5,
                ),
                boxShadow: isSelected
                    ? [BoxShadow(color: AppTheme.primary.withOpacity(0.25), blurRadius: 8, offset: const Offset(0, 3))]
                    : null,
              ),
              child: Row(
                children: [
                  if (isSelected) const Icon(Icons.star, color: Colors.white, size: 14),
                  if (isSelected) const SizedBox(width: 4),
                  Text(
                    f['name']!,
                    style: GoogleFonts.plusJakartaSans(
                      fontSize: 11,
                      fontWeight: isSelected ? FontWeight.bold : FontWeight.w600,
                      color: isSelected ? Colors.white : AppTheme.onSurface,
                    ),
                  ),
                ],
              ),
            ),
          );
        },
      ),
    );
  }

  Widget _buildCourseBreakdownList() {
    final allSubjects = _stats.bySubject.values.toList();

    // Sort: Selected Professor's subject is ALWAYS pinned at index 0 (top)!
    final selectedSubj = allSubjects.where((s) => s.code == _selectedFacultyCode).firstOrNull;
    final otherSubjs = allSubjects.where((s) => s.code != _selectedFacultyCode).toList();
    final sortedList = [if (selectedSubj != null) selectedSubj, ...otherSubjs];

    return ListView.separated(
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      itemCount: sortedList.length,
      separatorBuilder: (_, __) => const SizedBox(height: 10),
      itemBuilder: (context, index) {
        final s = sortedList[index];
        final isSelected = s.code == _selectedFacultyCode;
        final hasClasses = s.total > 0;
        final isSubjGood = hasClasses ? s.percentage >= 75.0 : true;

        return Container(
          padding: const EdgeInsets.all(14),
          decoration: BoxDecoration(
            color: isSelected ? AppTheme.primary.withOpacity(0.08) : Colors.white,
            borderRadius: BorderRadius.circular(18),
            border: Border.all(
              color: isSelected ? AppTheme.primary : AppTheme.outlineVariant.withOpacity(0.3),
              width: isSelected ? 2 : 1,
            ),
          ),
          child: Row(
            children: [
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    if (isSelected)
                      Container(
                        margin: const EdgeInsets.only(bottom: 6),
                        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                        decoration: BoxDecoration(
                          color: AppTheme.primary,
                          borderRadius: BorderRadius.circular(8),
                        ),
                        child: Row(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            const Icon(Icons.star, color: Colors.white, size: 10),
                            const SizedBox(width: 4),
                            Text(
                              'Selected Professor',
                              style: GoogleFonts.plusJakartaSans(color: Colors.white, fontSize: 9, fontWeight: FontWeight.bold),
                            ),
                          ],
                        ),
                      ),
                    Text(
                      '${s.name} (${s.code})',
                      style: GoogleFonts.plusJakartaSans(
                        fontSize: 12,
                        fontWeight: FontWeight.bold,
                        color: AppTheme.onSurface,
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      hasClasses
                          ? '${s.profName} • ${s.present}/${s.total} Classes Verified'
                          : '${s.profName} • 0/0 Classes Verified (0 Sessions)',
                      style: GoogleFonts.inter(fontSize: 10, color: AppTheme.secondary),
                    ),
                  ],
                ),
              ),
              const SizedBox(width: 12),
              Column(
                crossAxisAlignment: CrossAxisAlignment.end,
                children: [
                  Text(
                    hasClasses ? '${s.percentage.toStringAsFixed(1)}%' : '0.0%',
                    style: GoogleFonts.plusJakartaSans(
                      fontSize: 14,
                      fontWeight: FontWeight.bold,
                      color: isSubjGood ? AppTheme.success : AppTheme.error,
                    ),
                  ),
                  const SizedBox(height: 2),
                  Text(
                    hasClasses ? (isSubjGood ? 'Verified' : 'Low') : '0 Sessions',
                    style: GoogleFonts.inter(
                      fontSize: 9,
                      fontWeight: FontWeight.bold,
                      color: isSubjGood ? AppTheme.success : AppTheme.error,
                    ),
                  ),
                ],
              ),
            ],
          ),
        );
      },
    );
  }

  Widget _buildAvatar(String? url, String initials) {
    if (url != null && url.isNotEmpty) {
      return ClipRRect(
        borderRadius: BorderRadius.circular(22),
        child: CachedNetworkImage(
          imageUrl: url,
          width: 44,
          height: 44,
          fit: BoxFit.cover,
          placeholder: (_, __) => CircleAvatar(backgroundColor: AppTheme.primaryFixed, child: Text(initials, style: const TextStyle(color: AppTheme.primary))),
          errorWidget: (_, __, ___) => CircleAvatar(backgroundColor: AppTheme.primaryFixed, child: Text(initials, style: const TextStyle(color: AppTheme.primary))),
        ),
      );
    }
    return CircleAvatar(
      radius: 22,
      backgroundColor: AppTheme.primaryFixed,
      child: Text(initials, style: GoogleFonts.plusJakartaSans(fontSize: 14, fontWeight: FontWeight.bold, color: AppTheme.primary)),
    );
  }
}
