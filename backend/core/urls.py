from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UserViewSet, AttendanceLogViewSet, TaskViewSet,
    SubmissionViewSet, StudentClassViewSet, SubjectViewSet
)

router = DefaultRouter()
router.register(r'classes', StudentClassViewSet, basename='class')
router.register(r'subjects', SubjectViewSet, basename='subject')
router.register(r'users', UserViewSet, basename='user')
router.register(r'attendance', AttendanceLogViewSet, basename='attendance')
router.register(r'tasks', TaskViewSet, basename='task')
router.register(r'submissions', SubmissionViewSet, basename='submission')

urlpatterns = [
    path('', include(router.urls)),
]
