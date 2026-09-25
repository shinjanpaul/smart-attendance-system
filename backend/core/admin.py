from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, AttendanceLog, Task, Submission, StudentClass, Subject

@admin.register(StudentClass)
class StudentClassAdmin(admin.ModelAdmin):
    list_display = ('name', 'department')
    search_fields = ('name', 'department')


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'student_class')
    list_filter = ('student_class',)
    search_fields = ('name', 'code')


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Smart Attendance Profile', {'fields': ('role', 'department', 'roll_number', 'student_class', 'face_embedding', 'profile_picture')}),
    )
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'department', 'roll_number', 'student_class', 'is_staff')
    list_filter = ('role', 'department', 'student_class', 'is_staff', 'is_active')
    search_fields = ('username', 'email', 'roll_number', 'first_name', 'last_name')


@admin.register(AttendanceLog)
class AttendanceLogAdmin(admin.ModelAdmin):
    list_display = ('student', 'student_class', 'subject', 'status', 'verification_method', 'confidence_score', 'date', 'timestamp')
    list_filter = ('status', 'verification_method', 'student_class', 'subject', 'date')
    search_fields = ('student__username', 'student__roll_number')


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'assigned_by', 'assigned_to', 'priority', 'status', 'deadline', 'created_at')
    list_filter = ('priority', 'status', 'deadline')
    search_fields = ('title', 'description', 'assigned_by__username', 'assigned_to__username')


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ('task', 'student', 'status', 'score', 'submitted_at')
    list_filter = ('status', 'submitted_at')
    search_fields = ('task__title', 'student__username', 'feedback')
