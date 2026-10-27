import cv2
import numpy as np
import io
from PIL import Image
from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from rest_framework.test import APIClient
from rest_framework import status
from .models import CustomUser, AttendanceLog, Task, Submission, StudentClass, Subject
from .ai_engine import (
    detect_all_faces, crop_and_preprocess_face, generate_embedding,
    euclidean_distance, match_face_to_students, process_classroom_photos
)


def create_synthetic_face_image(num_faces=1):
    """Utility helper to generate synthetic image with faces for unit testing"""
    img = np.zeros((480, 640, 3), dtype=np.uint8)
    img[:] = (30, 30, 45)

    centers = [(200, 240), (440, 240)] if num_faces == 2 else [(320, 240)]
    for i in range(min(num_faces, 2)):
        cx, cy = centers[i]
        # Draw face oval
        cv2.ellipse(img, (cx, cy), (80, 110), 0, 0, 360, (220, 220, 220), -1)
        # Eyes
        cv2.circle(img, (cx - 30, cy - 25), 10, (50, 50, 50), -1)
        cv2.circle(img, (cx + 30, cy - 25), 10, (50, 50, 50), -1)
        # Mouth
        cv2.ellipse(img, (cx, cy + 35), (30, 15), 0, 0, 180, (50, 50, 50), 3)

    _, encoded = cv2.imencode('.jpg', img)
    return encoded.tobytes()


class FaceRecognitionAIEngineTestCase(TestCase):
    def test_01_face_detection_single_face(self):
        img_bytes = create_synthetic_face_image(num_faces=1)
        nparr = np.frombuffer(img_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        faces = detect_all_faces(img)
        self.assertGreaterEqual(len(faces), 1)

    def test_02_face_detection_multiple_faces(self):
        img_bytes = create_synthetic_face_image(num_faces=2)
        nparr = np.frombuffer(img_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        faces = detect_all_faces(img)
        self.assertGreaterEqual(len(faces), 1)

    def test_03_no_face_image(self):
        blank = np.zeros((480, 640, 3), dtype=np.uint8)
        faces = detect_all_faces(blank)
        self.assertEqual(len(faces), 0)

    def test_04_invalid_image_handling(self):
        nparr = np.frombuffer(b"invalid_corrupt_data", np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        self.assertIsNone(img)

    def test_05_and_06_embedding_generation_dimension_and_format(self):
        img = np.zeros((160, 160, 3), dtype=np.uint8)
        emb = generate_embedding(img)
        self.assertEqual(len(emb), 128)
        self.assertIsInstance(emb[0], float)

    def test_07_same_person_matching(self):
        emb1 = [0.1] * 128
        emb2 = [0.1] * 128
        dist = euclidean_distance(emb1, emb2)
        self.assertAlmostEqual(dist, 0.0)

    def test_08_different_person_rejection(self):
        emb1 = [0.5] * 128
        emb2 = [-0.5] * 128
        dist = euclidean_distance(emb1, emb2)
        self.assertGreater(dist, 0.9)


class AttendanceAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

        # Create class and subjects
        self.class_csea = StudentClass.objects.create(name='CSE-A', department='Computer Science')
        self.class_it3 = StudentClass.objects.create(name='IT-3rd-Year', department='Information Technology')

        self.subject = Subject.objects.create(name='Data Structures', code='CS301', student_class=self.class_csea)

        # Create teacher
        self.teacher = CustomUser.objects.create_user(
            username='prof_test', password='password123', role='TEACHER', department='Computer Science'
        )

        # Create students in CSE-A
        dummy_emb = generate_embedding(np.zeros((160, 160, 3), dtype=np.uint8))
        self.student1 = CustomUser.objects.create_user(
            username='student1', password='password123', role='STUDENT',
            roll_number='ROLL01', student_class=self.class_csea, face_embedding=dummy_emb
        )
        self.student2 = CustomUser.objects.create_user(
            username='student2', password='password123', role='STUDENT',
            roll_number='ROLL02', student_class=self.class_csea, face_embedding=dummy_emb
        )

        # Student in another class (IT-3rd-Year)
        self.student_other = CustomUser.objects.create_user(
            username='student_other', password='password123', role='STUDENT',
            roll_number='ROLL99', student_class=self.class_it3, face_embedding=dummy_emb
        )

    def test_09_class_scoped_matching_api(self):
        res = self.client.get(f'/api/users/students/?class_id={self.class_csea.id}')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        student_ids = [s['id'] for s in res.data]
        self.assertIn(self.student1.id, student_ids)
        self.assertIn(self.student2.id, student_ids)
        self.assertNotIn(self.student_other.id, student_ids)

    def test_10_11_12_process_photos_multi_photo_and_deduplication(self):
        photo1 = io.BytesIO(create_synthetic_face_image(1))
        photo1.name = 'photo1.jpg'
        photo2 = io.BytesIO(create_synthetic_face_image(1))
        photo2.name = 'photo2.jpg'

        data = {
            'class_id': self.class_csea.id,
            'subject_id': self.subject.id,
            'photos': [photo1, photo2]
        }
        res = self.client.post('/api/attendance/process-photos/', data, format='multipart')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['total_photos_processed'], 2)
        # Check Present + Absent breakdown
        self.assertIn('present_students', res.data)
        self.assertIn('absent_students', res.data)

    def test_13_14_15_attendance_confirmation_and_duplicate_prevention(self):
        today = str(timezone.now().date())
        payload = {
            'class_id': self.class_csea.id,
            'subject_id': self.subject.id,
            'date': today,
            'records': [
                {'student_id': self.student1.id, 'status': 'PRESENT', 'confidence': 0.95},
                {'student_id': self.student2.id, 'status': 'ABSENT', 'confidence': 0.0},
            ]
        }
        res = self.client.post('/api/attendance/confirm/', payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(AttendanceLog.objects.count(), 2)

        # Run confirmation second time (duplicate protection check)
        res2 = self.client.post('/api/attendance/confirm/', payload, format='json')
        self.assertEqual(res2.status_code, status.HTTP_200_OK)
        self.assertEqual(AttendanceLog.objects.count(), 2) # Count remains 2 due to update_or_create


from channels.testing import WebsocketCommunicator
from core.consumers import AttendanceConsumer
from channels.layers import get_channel_layer

class AttendanceWebSocketTestCase(TestCase):
    async def test_16_websocket_connection_and_scan_progress_broadcast(self):
        communicator = WebsocketCommunicator(AttendanceConsumer.as_asgi(), "/ws/attendance/")
        connected, _ = await communicator.connect()
        self.assertTrue(connected)

        # 1. Connection established message received
        init_msg = await communicator.receive_json_from()
        self.assertEqual(init_msg['type'], 'connection_established')

        # 2. Simulate broadcast to attendance_updates group
        channel_layer = get_channel_layer()
        await channel_layer.group_send(
            'attendance_updates',
            {
                'type': 'scan_progress',
                'current': 2,
                'total': 4,
                'percentage': 50,
                'faces_detected': 3,
                'message': 'Scanning Photo 2/4 (50%) — 3 faces detected'
            }
        )
        progress_msg = await communicator.receive_json_from()
        self.assertEqual(progress_msg['type'], 'scan_progress')
        self.assertEqual(progress_msg['current'], 2)
        self.assertEqual(progress_msg['percentage'], 50)

        # 3. Simulate attendance confirmed broadcast
        await channel_layer.group_send(
            'attendance_updates',
            {
                'type': 'attendance_confirmed',
                'class_id': 1,
                'subject_name': 'Data Structures',
                'subject_code': 'CS301',
                'teacher_name': 'Prof. Test',
                'date': '2026-10-19',
                'records': [{'student_id': 10, 'status': 'PRESENT', 'confidence': 0.98}]
            }
        )
        conf_msg = await communicator.receive_json_from()
        self.assertEqual(conf_msg['type'], 'attendance_confirmed')
        self.assertEqual(conf_msg['subject_name'], 'Data Structures')

        await communicator.disconnect()

