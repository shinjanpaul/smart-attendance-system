import cv2
import numpy as np
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.utils import timezone
from .models import CustomUser, AttendanceLog, Task, Submission, StudentClass, Subject
from .serializers import (
    UserSerializer, AttendanceLogSerializer, TaskSerializer,
    SubmissionSerializer, StudentClassSerializer, SubjectSerializer
)
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from .ai_engine import (
    detect_all_faces, crop_and_preprocess_face, generate_embedding,
    process_classroom_photos, decode_image_with_exif
)


class StudentClassViewSet(viewsets.ModelViewSet):
    queryset = StudentClass.objects.all()
    serializer_class = StudentClassSerializer


class SubjectViewSet(viewsets.ModelViewSet):
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer

    def get_queryset(self):
        queryset = Subject.objects.all()
        class_id = self.request.query_params.get('class_id')
        if class_id:
            queryset = queryset.filter(student_class_id=class_id)
        return queryset


class UserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer

    @action(detail=False, methods=['post'])
    def login(self, request):
        username = request.data.get('username', '').strip()
        password = request.data.get('password', '')

        if not username:
            return Response({'error': 'Username is required.'}, status=status.HTTP_400_BAD_REQUEST)

        # Ensure realistic past attendance sessions exist in database
        if AttendanceLog.objects.filter(student__username='shinjan_paul').count() != 18:
            try:
                from .attendance_seeder import seed_realistic_attendance
                seed_realistic_attendance()
            except Exception:
                pass

        # Ensure all curriculum subjects (IT801, IT802, IT803) exist for B.Tech IT class
        try:
            target_class = StudentClass.objects.filter(name__icontains='B.Tech IT').first()
            if target_class:
                Subject.objects.get_or_create(code='IT801', defaults={'name': 'Cloud Computing & Distributed Systems', 'student_class': target_class})
                subj_802, created = Subject.objects.get_or_create(code='IT802', defaults={'name': 'Software Engineering & AI Systems', 'student_class': target_class})
                if subj_802.student_class_id != target_class.id:
                    subj_802.student_class = target_class
                    subj_802.save()
                Subject.objects.get_or_create(code='IT803', defaults={'name': 'Cyber & Information Security', 'student_class': target_class})
        except Exception:
            pass

        user = CustomUser.objects.filter(username__iexact=username).first()
        if not user:
            # Auto-seed database if user not found (e.g. freshly booted cloud container)
            try:
                from .attendance_seeder import seed_database_complete
                seed_database_complete()
                user = CustomUser.objects.filter(username__iexact=username).first()
            except Exception as e:
                print(f"[ERROR] Auto-seed on login: {e}")

        if not user:
            return Response({'error': f"User '{username}' was not found in the database."}, status=status.HTTP_404_NOT_FOUND)

        # Teachers MUST provide their admin-assigned password
        if user.role == 'TEACHER':
            if not password:
                return Response({'error': 'Faculty password is required. Please enter the password set in Django Admin.'}, status=status.HTTP_400_BAD_REQUEST)
            if not user.check_password(password):
                return Response({'error': 'Incorrect faculty password. Please verify your password with the department admin.'}, status=status.HTTP_401_UNAUTHORIZED)

        # Students do not require passwords for viewing their attendance score
        serializer = self.get_serializer(user)
        return Response({
            'message': 'Login successful',
            'user': serializer.data,
            'role': user.role
        }, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def students(self, request):
        class_id = request.query_params.get('class_id')
        students = CustomUser.objects.filter(role='STUDENT')
        if not students.exists():
            try:
                from .attendance_seeder import seed_database_complete
                seed_database_complete()
                students = CustomUser.objects.filter(role='STUDENT')
            except Exception as e:
                print(f"[ERROR] Auto-seed students: {e}")
        if class_id:
            students = students.filter(student_class_id=class_id)
        serializer = self.get_serializer(students, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def teachers(self, request):
        teachers = CustomUser.objects.filter(role='TEACHER')
        if not teachers.exists():
            try:
                from .attendance_seeder import seed_database_complete
                seed_database_complete()
                teachers = CustomUser.objects.filter(role='TEACHER')
            except Exception as e:
                print(f"[ERROR] Auto-seed teachers: {e}")
        serializer = self.get_serializer(teachers, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], url_path='register-face')
    def register_face(self, request, pk=None):
        student = self.get_object()
        photos = request.FILES.getlist('photos') or request.FILES.getlist('photo')
        if not photos:
            return Response({'error': 'No photo uploaded. Please provide photo file(s).'}, status=status.HTTP_400_BAD_REQUEST)

        valid_embeddings = []
        last_photo_file = photos[-1]

        for p_file in photos:
            photo_bytes = p_file.read()
            img = decode_image_with_exif(photo_bytes)
            if img is None:
                continue

            bboxes = detect_all_faces(img)
            if len(bboxes) == 0:
                continue

            # Automatically select the largest face in the photo (the primary student subject)
            primary_bbox = max(bboxes, key=lambda b: b[2] * b[3])
            face_crop = crop_and_preprocess_face(img, primary_bbox)
            emb = generate_embedding(face_crop)
            valid_embeddings.append(emb)

        if not valid_embeddings:
            return Response({'error': 'No valid face detected in any of the uploaded registration photos.'}, status=status.HTTP_400_BAD_REQUEST)

        # Compute L2-normalized master centroid embedding across all registration photos
        avg_emb = np.mean(np.array(valid_embeddings, dtype=np.float32), axis=0)
        norm = np.linalg.norm(avg_emb)
        if norm > 0:
            avg_emb = avg_emb / norm

        final_embedding = avg_emb.tolist()
        student.face_embedding = final_embedding
        student.profile_picture = last_photo_file
        student.save()

        return Response({
            'message': f'Face embedding successfully registered for {student.username} using {len(valid_embeddings)} photo(s)!',
            'student_id': student.id,
            'photos_processed': len(valid_embeddings),
            'embedding_length': len(final_embedding)
        }, status=status.HTTP_200_OK)


class AttendanceLogViewSet(viewsets.ModelViewSet):
    queryset = AttendanceLog.objects.all().order_by('-timestamp')
    serializer_class = AttendanceLogSerializer

    @action(detail=False, methods=['post'], url_path='process-photos')
    def process_photos(self, request):
        class_id = request.data.get('class_id')
        subject_id = request.data.get('subject_id')
        photos = request.FILES.getlist('photos')

        if not class_id:
            return Response({'error': 'class_id is required.'}, status=status.HTTP_400_BAD_REQUEST)
        if not photos:
            return Response({'error': 'At least one photo file is required.'}, status=status.HTTP_400_BAD_REQUEST)

        # Scoped matching: query students belonging strictly to the selected class
        class_students = list(CustomUser.objects.filter(role='STUDENT', student_class_id=class_id))
        total_photos = len(photos)

        # Broadcast live photo-by-photo progress via WebSockets
        channel_layer = get_channel_layer()
        def ws_progress_callback(curr_idx, total_count, faces_in_frame):
            if channel_layer:
                pct = int((curr_idx / total_count) * 100)
                try:
                    async_to_sync(channel_layer.group_send)(
                        'attendance_updates',
                        {
                            'type': 'scan_progress',
                            'current': curr_idx,
                            'total': total_count,
                            'percentage': pct,
                            'faces_detected': faces_in_frame,
                            'message': f"Scanning Photo {curr_idx}/{total_count} ({pct}% complete) — {faces_in_frame} face(s) analyzed"
                        }
                    )
                except Exception:
                    pass
                import time
                time.sleep(0.4)

        photo_bytes_list = [p.read() for p in photos]
        draft_result = process_classroom_photos(
            photo_bytes_list,
            class_students,
            progress_callback=ws_progress_callback
        )

        # Broadcast scan completion event
        if channel_layer:
            try:
                async_to_sync(channel_layer.group_send)(
                    'attendance_updates',
                    {
                        'type': 'scan_progress',
                        'current': total_photos,
                        'total': total_photos,
                        'percentage': 100,
                        'faces_detected': draft_result.get('total_faces_detected', 0),
                        'message': f"Scan Complete! All {total_photos} photos processed successfully ({draft_result.get('present_count', 0)} present)."
                    }
                )
            except Exception:
                pass

        draft_result['class_id'] = int(class_id)
        draft_result['subject_id'] = int(subject_id) if subject_id else None
        draft_result['date'] = str(timezone.now().date())

        return Response(draft_result, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], url_path='confirm')
    def confirm_attendance(self, request):
        class_id = request.data.get('class_id')
        subject_id = request.data.get('subject_id')
        att_date = request.data.get('date', str(timezone.now().date()))
        records = request.data.get('records', [])

        if not class_id or not records:
            return Response({'error': 'class_id and records are required.'}, status=status.HTTP_400_BAD_REQUEST)

        created_logs = []
        updated_logs = []

        for rec in records:
            student_id = rec.get('student_id')
            att_status = rec.get('status', 'PRESENT')
            confidence = rec.get('confidence', 1.0)

            # Strict guard: Only record attendance for verified STUDENT accounts
            student_user = CustomUser.objects.filter(id=student_id, role='STUDENT').first()
            if not student_user:
                continue

            # Check if an attendance record already exists for this student + subject + class on this date
            filter_kwargs = {
                'student_id': student_id,
                'date': att_date
            }
            if subject_id:
                filter_kwargs['subject_id'] = subject_id
            if class_id:
                filter_kwargs['student_class_id'] = class_id

            existing_log = AttendanceLog.objects.filter(**filter_kwargs).first()
            if existing_log:
                existing_log.status = att_status
                existing_log.student_class_id = class_id
                if subject_id:
                    existing_log.subject_id = subject_id
                existing_log.verification_method = 'FACE_RECOGNITION'
                existing_log.confidence_score = confidence
                existing_log.save()
                updated_logs.append(existing_log.id)
            else:
                log = AttendanceLog.objects.create(
                    student=student_user,
                    student_class_id=class_id,
                    subject_id=subject_id,
                    date=att_date,
                    status=att_status,
                    verification_method='FACE_RECOGNITION',
                    confidence_score=confidence
                )
                created_logs.append(log.id)

        # Broadcast real-time confirmation to connected students and faculty via WebSockets
        channel_layer = get_channel_layer()
        if channel_layer:
            subject = Subject.objects.filter(id=subject_id).first() if subject_id else None
            subject_name = subject.name if subject else "Class Session"
            subject_code = subject.code if subject else ""
            teacher_name = request.user.get_full_name() or request.user.username if request.user.is_authenticated else "Faculty"

            try:
                async_to_sync(channel_layer.group_send)(
                    'attendance_updates',
                    {
                        'type': 'attendance_confirmed',
                        'class_id': int(class_id),
                        'subject_name': subject_name,
                        'subject_code': subject_code,
                        'teacher_name': teacher_name,
                        'date': att_date,
                        'records': records
                    }
                )
            except Exception:
                pass

        return Response({
            'message': 'Attendance confirmed and saved successfully to database!',
            'created_records_count': len(created_logs),
            'updated_records_count': len(updated_logs),
            'date': att_date
        }, status=status.HTTP_200_OK)


class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all().order_by('-created_at')
    serializer_class = TaskSerializer


class SubmissionViewSet(viewsets.ModelViewSet):
    queryset = Submission.objects.all().order_by('-submitted_at')
    serializer_class = SubmissionSerializer


from django.http import HttpResponse

def frontend_view(request):
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    frontend_path = os.path.join(base_dir, '..', 'frontend', 'app.html')
    if not os.path.exists(frontend_path):
        frontend_path = os.path.join(base_dir, '..', 'index.html')
    if os.path.exists(frontend_path):
        with open(frontend_path, 'r', encoding='utf-8') as f:
            return HttpResponse(f.read(), content_type='text/html')
    return HttpResponse("VeriFace AI Frontend app.html not found.", status=404)

