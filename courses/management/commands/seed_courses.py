"""
دستور مدیریتی برای بارگذاری داده‌های نمونه
اجرا: python manage.py seed_courses
"""
from django.core.management.base import BaseCommand
from courses.models import Course, Lesson


SAMPLE_COURSES = [
    {
        "title": "آموزش جامع پایتون از صفر تا صد",
        "slug": "python-complete",
        "description": (
            "در این دوره جامع، از اصول پایه پایتون شروع کرده و تا مباحث پیشرفته مثل "
            "برنامه‌نویسی شی‌گرا، کار با فایل‌ها، API‌ها و پروژه‌های واقعی پیش می‌رویم. "
            "مناسب برای تمام سطوح، حتی اگر هیچ تجربه برنامه‌نویسی ندارید."
        ),
        "price": 350000,
        "duration_hours": 40,
        "level": "beginner",
        "instructor": "دکتر سعید کریمی",
        "lessons": [
            {"title": "معرفی پایتون و نصب محیط", "order": 1, "duration_minutes": 25, "is_preview": True},
            {"title": "متغیرها و انواع داده", "order": 2, "duration_minutes": 35},
            {"title": "ساختارهای کنترلی (if, for, while)", "order": 3, "duration_minutes": 45},
            {"title": "توابع و ماژول‌ها", "order": 4, "duration_minutes": 50},
            {"title": "برنامه‌نویسی شی‌گرا", "order": 5, "duration_minutes": 60},
            {"title": "کار با فایل و استثناها", "order": 6, "duration_minutes": 40},
            {"title": "پروژه نهایی: ساخت ربات تلگرام", "order": 7, "duration_minutes": 90},
        ]
    },
    {
        "title": "Django 5 — ساخت وب‌اپلیکیشن حرفه‌ای",
        "slug": "django-5-pro",
        "description": (
            "آموزش کامل فریم‌ورک Django 5 برای ساخت وب‌سایت‌های حرفه‌ای. "
            "شامل مدل‌سازی پایگاه داده، احراز هویت، REST API، Celery، "
            "آپلود فایل و استقرار روی سرور."
        ),
        "price": 490000,
        "duration_hours": 55,
        "level": "intermediate",
        "instructor": "مهندس نیلوفر رضایی",
        "lessons": [
            {"title": "معرفی جنگو و ساختار پروژه", "order": 1, "duration_minutes": 30, "is_preview": True},
            {"title": "مدل‌ها و migrations", "order": 2, "duration_minutes": 45},
            {"title": "ویوها و URL routing", "order": 3, "duration_minutes": 50},
            {"title": "قالب‌بندی با Django Templates", "order": 4, "duration_minutes": 40},
            {"title": "احراز هویت سفارشی", "order": 5, "duration_minutes": 55},
            {"title": "Django REST Framework", "order": 6, "duration_minutes": 70},
            {"title": "Celery و Redis", "order": 7, "duration_minutes": 60},
            {"title": "استقرار با Docker", "order": 8, "duration_minutes": 80},
        ]
    },
    {
        "title": "React.js برای مبتدیان",
        "slug": "react-beginner",
        "description": (
            "یادگیری React.js از پایه — کامپوننت‌ها، State، Props، Hooks و "
            "ساخت اپلیکیشن‌های تک‌صفحه‌ای. در پایان دوره یک پروژه کامل E-Commerce می‌سازیم."
        ),
        "price": 420000,
        "duration_hours": 38,
        "level": "beginner",
        "instructor": "دکتر سعید کریمی",
        "lessons": [
            {"title": "معرفی React و JSX", "order": 1, "duration_minutes": 20, "is_preview": True},
            {"title": "کامپوننت‌ها و Props", "order": 2, "duration_minutes": 40},
            {"title": "State و مدیریت حالت", "order": 3, "duration_minutes": 45},
            {"title": "React Hooks", "order": 4, "duration_minutes": 55},
            {"title": "مسیریابی با React Router", "order": 5, "duration_minutes": 35},
            {"title": "پروژه: فروشگاه آنلاین", "order": 6, "duration_minutes": 120},
        ]
    },
    {
        "title": "مقدمه Docker و DevOps",
        "slug": "docker-devops-intro",
        "description": (
            "آشنایی با Docker، Docker Compose و اصول DevOps. "
            "این دوره برای توسعه‌دهندگانی مناسب است که می‌خواهند اپلیکیشن‌هایشان را "
            "به روش حرفه‌ای مدیریت و مستقر کنند."
        ),
        "price": 0,
        "duration_hours": 12,
        "level": "intermediate",
        "instructor": "مهندس علی محمدی",
        "lessons": [
            {"title": "Docker چیست؟", "order": 1, "duration_minutes": 20, "is_preview": True},
            {"title": "ساخت Image و Container", "order": 2, "duration_minutes": 35, "is_preview": True},
            {"title": "Docker Compose", "order": 3, "duration_minutes": 40},
            {"title": "استقرار Django با Docker", "order": 4, "duration_minutes": 50},
        ]
    },
]


class Command(BaseCommand):
    help = 'بارگذاری داده‌های نمونه دوره‌ها'

    def handle(self, *args, **options):
        created_count = 0
        for data in SAMPLE_COURSES:
            lessons_data = data.pop('lessons', [])
            course, created = Course.objects.get_or_create(
                slug=data['slug'],
                defaults=data
            )
            if created:
                for lesson_data in lessons_data:
                    Lesson.objects.create(
                        course=course,
                        description='',
                        **lesson_data
                    )
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f'✓ دوره ساخته شد: {course.title}'))
            else:
                self.stdout.write(f'— دوره موجود است: {course.title}')

        self.stdout.write(self.style.SUCCESS(f'\n{created_count} دوره جدید اضافه شد.'))
