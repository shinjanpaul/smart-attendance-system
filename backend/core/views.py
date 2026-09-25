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
from .ai_engine import (
    detect_all_faces, crop_and_preprocess_face, generate_embedding,
    process_classroom_photos
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

    @action(detail=False, methods=['get'])
    def students(self, request):
        class_id = request.query_params.get('class_id')
        students = CustomUser.objects.filter(role='STUDENT')
        if class_id:
            students = students.filter(student_class_id=class_id)
        serializer = self.get_serializer(students, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def teachers(self, request):
        teachers = CustomUser.objects.filter(role='TEACHER')
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
            nparr = np.frombuffer(photo_bytes, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
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

        photo_bytes_list = [p.read() for p in photos]
        draft_result = process_classroom_photos(photo_bytes_list, class_students)

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

            log, created = AttendanceLog.objects.update_or_create(
                student_id=student_id,
                student_class_id=class_id,
                subject_id=subject_id,
                date=att_date,
                defaults={
                    'status': att_status,
                    'verification_method': 'FACE_RECOGNITION',
                    'confidence_score': confidence,
                }
            )

            if created:
                created_logs.append(log.id)
            else:
                updated_logs.append(log.id)

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
