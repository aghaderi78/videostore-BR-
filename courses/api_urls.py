from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import api_views

app_name = 'api'

router = DefaultRouter()
router.register(r'courses', api_views.CourseViewSet, basename='course')

urlpatterns = [
    path('', include(router.urls)),
    path('enrollments/', api_views.EnrollmentListAPIView.as_view(), name='enrollments'),
]
