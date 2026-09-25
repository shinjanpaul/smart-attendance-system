from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

class StudentClass(models.Model):
    name = models.CharField(max_length=50, unique=True, help_text="e.g. CSE-A, IT-3rd-Year")
    department = models.CharField(max_length=100, default='Information Technology')

    def __str__(self):
        return f"{self.name} ({self.department})"

    class Meta:
        verbose_name_plural = "Student Classes"


class Subject(models.Model):
    name = models.CharField(max_length=100, help_text="e.g. Data Structures")
    code = models.CharField(max_length=20, help_text="e.g. CS301")
    student_class = models.ForeignKey(StudentClass, on_delete=models.CASCADE, related_name='subjects')

    def __str__(self):
        return f"{self.code} - {self.name} ({self.student_class.name})"


class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('ADMIN', 'Admin'),
        ('TEACHER', 'Teacher'),
        ('STUDENT', 'Student'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='STUDENT')
    department = models.CharField(max_length=100, default='Information Technology')
    roll_number = models.CharField(max_length=50, blank=True, null=True, unique=True)
    student_class = models.ForeignKey(StudentClass, on_delete=models.SET_NULL, blank=True, null=True, related_name='students')
    face_embedding = models.JSONField(blank=True, null=True, help_text="128-D vector representation for FaceNet")
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"


class AttendanceLog(models.Model):
    STATUS_CHOICES = (
        ('PRESENT', 'Present'),
        ('ABSENT', 'Absent'),
        ('LATE', 'Late'),
    )
    VERIFICATION_CHOICES = (
        ('FACE_RECOGNITION', 'Face Recognition'),
        ('MANUAL', 'Manual'),
    )
    student = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='attendance_logs')
    student_class = models.ForeignKey(StudentClass, on_delete=models.CASCADE, related_name='attendance_logs', blank=True, null=True)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='attendance_logs', blank=True, null=True)
    date = models.DateField(default=timezone.now)
    timestamp = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PRESENT')
    verification_method = models.CharField(max_length=30, choices=VERIFICATION_CHOICES, default='FACE_RECOGNITION')
    confidence_score = models.FloatField(blank=True, null=True)
    snapshot = models.ImageField(upload_to='attendance_snapshots/', blank=True, null=True)

    class Meta:
        # Enforce unique attendance log per student + class + subject + date
        unique_together = ('student', 'student_class', 'subject', 'date')

    def __str__(self):
        subj_name = self.subject.name if self.subject else "General"
        return f"{self.student.username} - {subj_name} - {self.status} on {self.date}"


class Task(models.Model):
    PRIORITY_CHOICES = (
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High'),
    )
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('COMPLETED', 'Completed'),
        ('OVERDUE', 'Overdue'),
    )
    title = models.CharField(max_length=255)
    description = models.TextField()
    assigned_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='tasks_assigned')
    assigned_to = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='tasks_received', blank=True, null=True, help_text="Null means assigned to all students")
    deadline = models.DateTimeField()
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='MEDIUM')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Task: {self.title} (Due: {self.deadline.strftime('%Y-%m-%d')})"


class Submission(models.Model):
    STATUS_CHOICES = (
        ('PENDING', 'Pending Review'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    )
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='submissions')
    student = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='submissions')
    submission_file = models.FileField(upload_to='submissions/', blank=True, null=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    feedback = models.TextField(blank=True, null=True)
    score = models.FloatField(blank=True, null=True)

    def __str__(self):
        return f"Submission by {self.student.username} for '{self.task.title}'"
