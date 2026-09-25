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

    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'role', 'department', 'roll_number', 'student_class', 'student_class_name', 'has_registered_face', 'profile_picture']
        extra_kwargs = {'password': {'write_only': True}}

    def get_has_registered_face(self, obj):
        return bool(obj.face_embedding)

    def create(self, validated_data):
        user = CustomUser.objects.create_user(**validated_data)
        return user


class AttendanceLogSerializer(serializers.ModelSerializer):
    student_name = serializers.ReadOnlyField(source='student.username')
    student_roll = serializers.ReadOnlyField(source='student.roll_number')
    class_name = serializers.ReadOnlyField(source='student_class.name')
    subject_name = serializers.ReadOnlyField(source='subject.name')

    class Meta:
        model = AttendanceLog
        fields = ['id', 'student', 'student_name', 'student_roll', 'student_class', 'class_name', 'subject', 'subject_name', 'date', 'timestamp', 'status', 'verification_method', 'confidence_score', 'snapshot']


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
