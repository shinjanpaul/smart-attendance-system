from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UserViewSet, AttendanceLogViewSet, TaskViewSet,
    SubmissionViewSet, StudentClassViewSet, SubjectViewSet,
    frontend_view, debug_engine, debug_face_trace, re_enroll_students_view
)

router = DefaultRouter()
router.register(r'classes', StudentClassViewSet, basename='class')
router.register(r'subjects', SubjectViewSet, basename='subject')
router.register(r'users', UserViewSet, basename='user')
router.register(r'attendance', AttendanceLogViewSet, basename='attendance')
router.register(r'tasks', TaskViewSet, basename='task')
router.register(r'submissions', SubmissionViewSet, basename='submission')

urlpatterns = [
    path('debug/engine/', debug_engine, name='debug-engine'),
    path('debug/face-trace/', debug_face_trace, name='debug-face-trace'),
    path('debug/re-enroll/', re_enroll_students_view, name='debug-re-enroll'),
    path('app/', frontend_view, name='frontend-app'),
    path('portal/', frontend_view, name='frontend-portal'),
    path('', include(router.urls)),
]
