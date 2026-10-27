from rest_framework import serializers
from .models import CustomUser, AttendanceLog, Task, Submission, StudentClass, Subject

class StudentClassSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentClass
        fields = ['id', 'name', 'department']


class SubjectSerializer(serializers.ModelSerializer):
    student_class_name = serializers.ReadOnlyField(source='student_class.name')

    class Meta:
        model = Subject
        fields = ['id', 'name', 'code', 'student_class', 'student_class_name']


class UserSerializer(serializers.ModelSerializer):
    student_class_name = serializers.ReadOnlyField(source='student_class.name')
    has_registered_face = serializers.SerializerMethodField()
    attendance_stats = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 'role', 
            'department', 'roll_number', 'student_class', 'student_class_name', 
            'has_registered_face', 'profile_picture', 'attendance_stats'
        ]
        extra_kwargs = {'password': {'write_only': True}}

    def get_has_registered_face(self, obj):
        return bool(obj.face_embedding)

    def get_attendance_stats(self, obj):
        if obj.role != 'STUDENT':
            return None
        total_sessions = obj.attendance_logs.count()
        present_sessions = obj.attendance_logs.filter(status='PRESENT').count()
        absent_sessions = total_sessions - present_sessions
        percentage = round((present_sessions / total_sessions) * 100.0, 1) if total_sessions > 0 else 0.0

        # Subject-wise breakdown for each professor's course
        by_subject = {}
        if obj.student_class:
            for subj in obj.student_class.subjects.all():
                key = f"{subj.code} - {subj.name}"
                by_subject[key] = {
                    'code': subj.code,
                    'name': subj.name,
                    'total': 0,
                    'present': 0,
                    'percentage': 0.0
                }

        for log in obj.attendance_logs.select_related('subject').all():
            subj_name = log.subject.name if log.subject else 'General Lecture'
            subj_code = log.subject.code if log.subject else 'GEN'
            key = f"{subj_code} - {subj_name}"
            if key not in by_subject:
                by_subject[key] = {'code': subj_code, 'name': subj_name, 'total': 0, 'present': 0, 'percentage': 0.0}
            by_subject[key]['total'] += 1
            if log.status == 'PRESENT':
                by_subject[key]['present'] += 1
            by_subject[key]['percentage'] = round((by_subject[key]['present'] / by_subject[key]['total']) * 100.0, 1) if by_subject[key]['total'] > 0 else 0.0

        return {
            'total_days': total_sessions,
            'present_days': present_sessions,
            'absent_days': absent_sessions,
            'percentage': percentage,
            'by_subject': by_subject
        }

    def create(self, validated_data):
        user = CustomUser.objects.create_user(**validated_data)
        return user


class AttendanceLogSerializer(serializers.ModelSerializer):
    student_name = serializers.ReadOnlyField(source='student.username')
    student_full_name = serializers.SerializerMethodField()
    student_roll = serializers.ReadOnlyField(source='student.roll_number')
    class_name = serializers.ReadOnlyField(source='student_class.name')
    subject_name = serializers.ReadOnlyField(source='subject.name')
    subject_code = serializers.ReadOnlyField(source='subject.code')

    class Meta:
        model = AttendanceLog
        fields = [
            'id', 'student', 'student_name', 'student_full_name', 'student_roll', 
            'student_class', 'class_name', 'subject', 'subject_name', 'subject_code', 
            'date', 'timestamp', 'status', 'verification_method', 'confidence_score', 'snapshot'
        ]

    def get_student_full_name(self, obj):
        return f"{obj.student.first_name} {obj.student.last_name}".strip() or obj.student.username


class TaskSerializer(serializers.ModelSerializer):
    assigned_by_name = serializers.ReadOnlyField(source='assigned_by.username')
    assigned_to_name = serializers.ReadOnlyField(source='assigned_to.username', default="All Students")

    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'assigned_by', 'assigned_by_name', 'assigned_to', 'assigned_to_name', 'deadline', 'priority', 'status', 'created_at']


class SubmissionSerializer(serializers.ModelSerializer):
    student_name = serializers.ReadOnlyField(source='student.username')
    task_title = serializers.ReadOnlyField(source='task.title')

    class Meta:
        model = Submission
        fields = ['id', 'task', 'task_title', 'student', 'student_name', 'submission_file', 'submitted_at', 'status', 'feedback', 'score']
