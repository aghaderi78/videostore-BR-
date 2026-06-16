from rest_framework import serializers
from .models import Course, Lesson, Enrollment, Payment


class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = ['id', 'title', 'order', 'duration_minutes', 'is_preview', 'video_url', 'description']


class CourseListSerializer(serializers.ModelSerializer):
    lesson_count = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = [
            'id', 'title', 'slug', 'instructor', 'price', 'duration_hours',
            'level', 'thumbnail', 'published_at', 'lesson_count'
        ]

    def get_lesson_count(self, obj):
        return obj.lessons.count()


class CourseDetailSerializer(serializers.ModelSerializer):
    lessons = LessonSerializer(many=True, read_only=True)
    lesson_count = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = [
            'id', 'title', 'slug', 'description', 'instructor', 'price',
            'duration_hours', 'level', 'thumbnail', 'published_at',
            'lesson_count', 'lessons'
        ]

    def get_lesson_count(self, obj):
        return obj.lessons.count()


class EnrollmentSerializer(serializers.ModelSerializer):
    course = CourseListSerializer(read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Enrollment
        fields = ['id', 'course', 'status', 'status_display', 'enrolled_at', 'paid_at']
