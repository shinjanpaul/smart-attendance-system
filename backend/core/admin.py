from django.contrib import admin, messages
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserCreationForm
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


from django import forms
from django.contrib.auth.forms import UserChangeForm

class MultipleFileInput(forms.FileInput):
    allow_multiple_selected = True

class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_clean = super().clean
        if isinstance(data, (list, tuple)):
            return [single_clean(d, initial) for d in data]
        return single_clean(data, initial)

class CustomUserCreationForm(UserCreationForm):
    face_photos = MultipleFileField(
        required=False,
        label="Multi-Angle Face Photos (1-5 photos)",
        help_text="Optional: Upload 1 to 5 photos from different angles (front, left, right). AI will compute the optimal 128-D centroid vector."
    )

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = (
            'username', 'first_name', 'last_name', 'email', 
            'role', 'department', 'roll_number', 'student_class', 'profile_picture'
        )

class CustomUserChangeForm(UserChangeForm):
    face_photos = MultipleFileField(
        required=False,
        label="Multi-Angle Face Photos (1-5 photos)",
        help_text="Upload 1 to 5 photos from different angles. AI will calculate the optimal 128-D centroid vector."
    )

    class Meta(UserChangeForm.Meta):
        model = CustomUser
        fields = '__all__'

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    form = CustomUserChangeForm
    add_form = CustomUserCreationForm
    add_fieldsets = (
        ('Account Credentials', {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2'),
        }),
        ('Personal Info', {
            'classes': ('wide',),
            'fields': ('first_name', 'last_name', 'email'),
        }),
        ('Smart Attendance Profile', {
            'classes': ('wide',),
            'fields': ('role', 'department', 'roll_number', 'student_class', 'profile_picture', 'face_photos'),
        }),
    )
    fieldsets = UserAdmin.fieldsets + (
        ('Smart Attendance Profile', {'fields': ('role', 'department', 'roll_number', 'student_class', 'profile_picture', 'face_photos', 'face_embedding')}),
    )
    readonly_fields = ('face_embedding',)
    list_display = ('username', 'first_name', 'last_name', 'role', 'department', 'roll_number', 'student_class', 'has_face_indexed', 'is_staff')
    list_filter = ('role', 'department', 'student_class', 'is_staff', 'is_active')
    search_fields = ('username', 'email', 'roll_number', 'first_name', 'last_name')

    @admin.display(boolean=True, description='Face 128-D Indexed')
    def has_face_indexed(self, obj):
        return bool(obj.face_embedding)

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

        # 1. Process multiple face photos if uploaded
        uploaded_face_photos = request.FILES.getlist('face_photos')
        if uploaded_face_photos:
            try:
                import numpy as np
                from .ai_engine import decode_image_with_exif, generate_image_encodings
                valid_embeddings = []
                for p_file in uploaded_face_photos:
                    img = decode_image_with_exif(p_file.read())
                    if img is not None:
                        encs = generate_image_encodings(img)
                        if encs:
                            valid_embeddings.append(encs[0][1])

                if valid_embeddings:
                    centroid = np.mean(valid_embeddings, axis=0)
                    obj.face_embedding = centroid.tolist()
                    if not obj.profile_picture:
                        obj.profile_picture = uploaded_face_photos[0]
                        obj.save()
                    else:
                        CustomUser.objects.filter(pk=obj.pk).update(face_embedding=obj.face_embedding)
                    self.message_user(
                        request,
                        f"✓ Successfully extracted and indexed 128-D centroid face biometrics from {len(valid_embeddings)} photos for {obj.username}!"
                    )
                else:
                    self.message_user(
                        request,
                        "⚠️ Note: No clear face detected in the uploaded face photos.",
                        level=messages.WARNING
                    )
            except Exception as e:
                self.message_user(request, f"Face biometric processing notice: {e}", level=messages.WARNING)

        # 2. Or fallback to single profile_picture if no multi-photos uploaded
        elif obj.profile_picture and not obj.face_embedding:
            try:
                from .ai_engine import decode_image_with_exif, generate_image_encodings
                import os
                if os.path.exists(obj.profile_picture.path):
                    with open(obj.profile_picture.path, 'rb') as f:
                        img = decode_image_with_exif(f.read())
                    if img is not None:
                        encs = generate_image_encodings(img)
                        if encs:
                            obj.face_embedding = encs[0][1]
                            CustomUser.objects.filter(pk=obj.pk).update(face_embedding=obj.face_embedding)
                            self.message_user(request, f"✓ Successfully extracted 128-D face biometrics from {obj.username}'s profile photo!")
                        else:
                            self.message_user(request, f"⚠️ Note: No clear face detected in {obj.username}'s profile photo. Face biometrics not indexed.", level=messages.WARNING)
            except Exception as e:
                self.message_user(request, f"Biometric processing notice: {e}", level=messages.WARNING)



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
