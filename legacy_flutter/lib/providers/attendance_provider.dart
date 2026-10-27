import 'dart:convert';
import 'dart:io';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;

class ClassModel {
  final int id;
  final String name;
  final String department;

  ClassModel({required this.id, required this.name, required this.department});

  factory ClassModel.fromJson(Map<String, dynamic> json) {
    return ClassModel(
      id: json['id'],
      name: json['name'],
      department: json['department'] ?? 'General',
    );
  }
}

class SubjectModel {
  final int id;
  final String name;
  final String code;

  SubjectModel({required this.id, required this.name, required this.code});

  factory SubjectModel.fromJson(Map<String, dynamic> json) {
    return SubjectModel(
      id: json['id'],
      name: json['name'],
      code: json['code'],
    );
  }
}

class StudentAttendanceItem {
  final int id;
  final String username;
  final String name;
  final String? rollNumber;
  bool isPresent;
  final bool hasRegisteredFace;

  StudentAttendanceItem({
    required this.id,
    required this.username,
    required this.name,
    this.rollNumber,
    required this.isPresent,
    required this.hasRegisteredFace,
  });

  factory StudentAttendanceItem.fromJson(Map<String, dynamic> json, bool isPresent) {
    return StudentAttendanceItem(
      id: json['id'],
      username: json['username'],
      name: json['name'] ?? json['username'],
      rollNumber: json['roll_number'],
      isPresent: isPresent,
      hasRegisteredFace: json['has_registered_face'] ?? false,
    );
  }
}

class AttendanceProvider extends ChangeNotifier {
  // Configurable Django Backend Base URL (Laptop IP for physical Android phone, 10.0.2.2 for emulator)
  String baseUrl = "http://10.0.2.2:8000";

  List<ClassModel> _classes = [];
  List<SubjectModel> _subjects = [];
  ClassModel? _selectedClass;
  SubjectModel? _selectedSubject;

  bool _isProcessing = false;
  String? _errorMessage;

  // Draft Attendance Results
  List<StudentAttendanceItem> _studentsList = [];
  int _totalPhotosProcessed = 0;
  int _totalFacesDetected = 0;
  int _unmatchedFacesCount = 0;

  List<ClassModel> get classes => _classes;
  List<SubjectModel> get subjects => _subjects;
  ClassModel? get selectedClass => _selectedClass;
  SubjectModel? get selectedSubject => _selectedSubject;
  bool get isProcessing => _isProcessing;
  String? get errorMessage => _errorMessage;

  List<StudentAttendanceItem> get presentStudents =>
      _studentsList.where((s) => s.isPresent).toList();
  List<StudentAttendanceItem> get absentStudents =>
      _studentsList.where((s) => !s.isPresent).toList();

  int get totalPhotosProcessed => _totalPhotosProcessed;
  int get totalFacesDetected => _totalFacesDetected;
  int get unmatchedFacesCount => _unmatchedFacesCount;

  void setBaseUrl(String url) {
    baseUrl = url;
    notifyListeners();
  }

  void setSelectedClass(ClassModel? cls) {
    _selectedClass = cls;
    _selectedSubject = null;
    _subjects = [];
    notifyListeners();
    if (cls != null) {
      fetchSubjectsForClass(cls.id);
    }
  }

  void setSelectedSubject(SubjectModel? subj) {
    _selectedSubject = subj;
    notifyListeners();
  }

  Future<void> fetchClasses() async {
    try {
      final response = await http.get(Uri.parse('$baseUrl/api/classes/'));
      if (response.statusCode == 200) {
        final List data = json.decode(response.body);
        _classes = data.map((item) => ClassModel.fromJson(item)).toList();
        if (_classes.isNotEmpty && _selectedClass == null) {
          setSelectedClass(_classes.first);
        }
        notifyListeners();
      }
    } catch (e) {
      _errorMessage = "Failed to load classes from Django: $e";
      notifyListeners();
    }
  }

  Future<void> fetchSubjectsForClass(int classId) async {
    try {
      final response = await http.get(Uri.parse('$baseUrl/api/subjects/?class_id=$classId'));
      if (response.statusCode == 200) {
        final List data = json.decode(response.body);
        _subjects = data.map((item) => SubjectModel.fromJson(item)).toList();
        if (_subjects.isNotEmpty) {
          _selectedSubject = _subjects.first;
        }
        notifyListeners();
      }
    } catch (e) {
      _errorMessage = "Failed to load subjects: $e";
      notifyListeners();
    }
  }

  // Upload multiple classroom photos to Django AI engine
  Future<bool> processClassroomPhotos(List<File> photoFiles) async {
    if (_selectedClass == null) {
      _errorMessage = "Please select a class first.";
      notifyListeners();
      return false;
    }

    _isProcessing = true;
    _errorMessage = null;
    notifyListeners();

    try {
      final request = http.MultipartRequest(
        'POST',
        Uri.parse('$baseUrl/api/attendance/process-photos/'),
      );

      request.fields['class_id'] = _selectedClass!.id.toString();
      if (_selectedSubject != null) {
        request.fields['subject_id'] = _selectedSubject!.id.toString();
      }

      for (var file in photoFiles) {
        request.files.add(await http.MultipartFile.fromPath('photos', file.path));
      }

      final streamedResponse = await request.send();
      final response = await http.Response.fromStream(streamedResponse);

      if (response.statusCode == 200) {
        final data = json.decode(response.body);

        _totalPhotosProcessed = data['total_photos_processed'] ?? photoFiles.length;
        _totalFacesDetected = data['total_faces_detected'] ?? 0;
        _unmatchedFacesCount = data['unmatched_faces_count'] ?? 0;

        _studentsList = [];
        final presentList = data['present_students'] as List? ?? [];
        final absentList = data['absent_students'] as List? ?? [];

        for (var item in presentList) {
          _studentsList.add(StudentAttendanceItem.fromJson(item, true));
        }
        for (var item in absentList) {
          _studentsList.add(StudentAttendanceItem.fromJson(item, false));
        }

        _isProcessing = false;
        notifyListeners();
        return true;
      } else {
        _errorMessage = "Server error (${response.statusCode}): ${response.body}";
        _isProcessing = false;
        notifyListeners();
        return false;
      }
    } catch (e) {
      _errorMessage = "Error processing photos on Django: $e";
      _isProcessing = false;
      notifyListeners();
      return false;
    }
  }

  void toggleStudentStatus(int studentId) {
    final idx = _studentsList.indexWhere((s) => s.id == studentId);
    if (idx != -1) {
      _studentsList[idx].isPresent = !_studentsList[idx].isPresent;
      notifyListeners();
    }
  }

  // Teacher confirms attendance -> save to database
  Future<bool> confirmAttendance() async {
    if (_selectedClass == null) return false;

    _isProcessing = true;
    notifyListeners();

    try {
      final recordsPayload = _studentsList.map((s) => {
        'student_id': s.id,
        'status': s.isPresent ? 'PRESENT' : 'ABSENT',
        'confidence': s.isPresent ? 0.95 : 0.0,
      }).toList();

      final body = json.encode({
        'class_id': _selectedClass!.id,
        'subject_id': _selectedSubject?.id,
        'date': DateTime.now().toIso8601String().substring(0, 10),
        'records': recordsPayload,
      });

      final response = await http.post(
        Uri.parse('$baseUrl/api/attendance/confirm/'),
        headers: {'Content-Type': 'application/json'},
        body: body,
      );

      _isProcessing = false;
      if (response.statusCode == 200) {
        notifyListeners();
        return true;
      } else {
        _errorMessage = "Failed to confirm attendance: ${response.body}";
        notifyListeners();
        return false;
      }
    } catch (e) {
      _isProcessing = false;
      _errorMessage = "Connection error: $e";
      notifyListeners();
      return false;
    }
  }
}
