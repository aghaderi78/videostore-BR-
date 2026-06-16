from django.core.management.base import BaseCommand
from blog.models import Post, Category

CATEGORIES = [
    {'name': 'پایتون', 'slug': 'python', 'icon': 'fab fa-python'},
    {'name': 'وب', 'slug': 'web', 'icon': 'fas fa-globe'},
    {'name': 'دیتابیس', 'slug': 'database', 'icon': 'fas fa-database'},
    {'name': 'DevOps', 'slug': 'devops', 'icon': 'fas fa-server'},
]

POSTS = [
    {
        'title': 'راهنمای کامل شروع برنامه‌نویسی پایتون در ۲۰۲۴',
        'slug': 'python-beginner-guide-2024',
        'category_slug': 'python',
        'author': 'دکتر سعید کریمی',
        'excerpt': 'اگر می‌خواهید برنامه‌نویسی را با پایتون شروع کنید، این مقاله راهنمای جامعی است که همه چیز را از نصب تا نوشتن اولین برنامه به شما نشان می‌دهد.',
        'content': '''پایتون یکی از محبوب‌ترین زبان‌های برنامه‌نویسی در جهان است. ساده، خوانا و قدرتمند.

## چرا پایتون؟

پایتون دارای مزایای زیادی است:
- **سادگی**: سینتکس پایتون بسیار ساده و شبیه به زبان انگلیسی است
- **تطبیق‌پذیری**: از وب‌سایت‌سازی تا هوش مصنوعی
- **جامعه بزرگ**: میلیون‌ها توسعه‌دهنده و کتابخانه

## نصب پایتون

ابتدا به سایت python.org بروید و آخرین نسخه را دانلود کنید.

```bash
python --version
```

## اولین برنامه

```python
print("سلام دنیا!")
name = input("نامت چیست؟ ")
print(f"خوش آمدی {name}!")
```

## ادامه مسیر

پس از یادگیری مبانی، می‌توانید به یادگیری Django، Flask یا علم داده با pandas و numpy بپردازید.''',
    },
    {
        'title': 'آشنایی با Django REST Framework برای ساخت API',
        'slug': 'django-rest-framework-intro',
        'category_slug': 'web',
        'author': 'مهندس نیلوفر رضایی',
        'excerpt': 'Django REST Framework قوی‌ترین ابزار برای ساخت APIهای RESTful با Django است. در این مقاله یاد می‌گیریم چطور یک API کامل بسازیم.',
        'content': '''Django REST Framework (DRF) یکی از محبوب‌ترین کتابخانه‌های پایتون برای ساخت API است.

## نصب

```bash
pip install djangorestframework
```

در settings.py اضافه کنید:

```python
INSTALLED_APPS = [
    ...
    'rest_framework',
]
```

## ساخت یک Serializer

```python
from rest_framework import serializers
from .models import Course

class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ['id', 'title', 'price', 'instructor']
```

## ساخت ViewSet

```python
from rest_framework import viewsets
from .serializers import CourseSerializer

class CourseViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Course.objects.filter(is_active=True)
    serializer_class = CourseSerializer
```

## تست API

بعد از راه‌اندازی، به آدرس `/api/courses/` بروید و خروجی JSON را ببینید.''',
    },
    {
        'title': 'بهینه‌سازی کوئری‌های Django با select_related و prefetch_related',
        'slug': 'django-query-optimization',
        'category_slug': 'database',
        'author': 'دکتر سعید کریمی',
        'excerpt': 'یکی از رایج‌ترین مشکلات عملکردی در Django، مشکل N+1 query است. در این مقاله یاد می‌گیریم چطور با select_related و prefetch_related این مشکل را حل کنیم.',
        'content': '''مشکل N+1 Query یکی از رایج‌ترین مشکلات عملکردی در برنامه‌های Django است.

## مشکل N+1 چیست؟

فرض کنید ۱۰۰ دوره دارید و می‌خواهید نام مدرس هر دوره را نمایش دهید:

```python
# این کد N+1 کوئری اجرا می‌کند!
courses = Course.objects.all()
for course in courses:
    print(course.enrollment_set.count())  # N کوئری اضافی!
```

## راه‌حل: select_related

برای روابط ForeignKey:

```python
# فقط ۱ کوئری!
enrollments = Enrollment.objects.select_related('user', 'course').all()
```

## راه‌حل: prefetch_related

برای روابط Many-to-Many و reverse ForeignKey:

```python
courses = Course.objects.prefetch_related('lessons').all()
for course in courses:
    print(course.lessons.count())  # بدون کوئری اضافی
```

## استفاده از Django Debug Toolbar

برای پیدا کردن مشکلات عملکردی، Django Debug Toolbar را نصب کنید:

```bash
pip install django-debug-toolbar
```

این ابزار تعداد کوئری‌های هر صفحه را نشان می‌دهد.''',
    },
    {
        'title': 'آموزش Docker برای توسعه‌دهندگان Django',
        'slug': 'docker-for-django-developers',
        'category_slug': 'devops',
        'author': 'مهندس علی محمدی',
        'excerpt': 'با Docker می‌توانید محیط توسعه یکسانی برای تمام تیم داشته باشید. در این مقاله یاد می‌گیریم چطور یک پروژه Django را با Docker کانتینرایز کنیم.',
        'content': '''Docker یکی از ابزارهای ضروری برای توسعه‌دهندگان مدرن است.

## Dockerfile برای Django

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
```

## docker-compose.yml

```yaml
version: '3.9'
services:
  web:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - .:/app
    depends_on:
      - db
      - redis

  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: mydb
      POSTGRES_USER: myuser
      POSTGRES_PASSWORD: mypassword

  redis:
    image: redis:7-alpine
```

## اجرا

```bash
docker-compose up --build
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
```

## مزایا

۱. محیط یکسان برای همه اعضای تیم
۲. استقرار آسان
۳. جداسازی سرویس‌ها
۴. مقیاس‌پذیری راحت''',
    },
]


class Command(BaseCommand):
    help = 'بارگذاری مقالات نمونه'

    def handle(self, *args, **options):
        for cat_data in CATEGORIES:
            Category.objects.get_or_create(slug=cat_data['slug'], defaults=cat_data)

        created = 0
        for post_data in POSTS:
            cat_slug = post_data.pop('category_slug')
            category = Category.objects.filter(slug=cat_slug).first()
            post, c = Post.objects.get_or_create(
                slug=post_data['slug'],
                defaults={**post_data, 'category': category}
            )
            if c:
                created += 1
                self.stdout.write(self.style.SUCCESS(f'✓ مقاله: {post.title}'))
        self.stdout.write(self.style.SUCCESS(f'\n{created} مقاله اضافه شد.'))
