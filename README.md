# برنس آکادمی — سایت فروش دوره آموزشی

پروژه کامل جنگو ۵ برای فروش دوره‌های آموزشی آنلاین با قابلیت‌های:
- احراز هویت با شماره موبایل و کد پیامکی
- مدیریت دوره‌ها، جلسات و ثبت‌نام‌ها
- پرداخت آنلاین (با شبیه‌سازی sandbox)
- وظایف Celery برای ارسال یادآوری خودکار
- Django REST Framework برای API
- پنل ادمین زیبا با Jazzmin

---

## ساختار پروژه

```
django-project/
├── bornes/               # تنظیمات اصلی پروژه
│   ├── settings.py
│   ├── urls.py
│   ├── celery.py
│   ├── wsgi.py
│   └── asgi.py
├── accounts/             # اپ کاربران و احراز هویت
│   ├── models.py         # User سفارشی + OTP
│   ├── views.py          # ورود با پیامک
│   ├── forms.py
│   ├── admin.py
│   ├── tasks.py          # وظیفه ارسال پیامک
│   └── urls.py
├── courses/              # اپ دوره‌ها
│   ├── models.py         # Course, Lesson, Enrollment, Payment
│   ├── views.py
│   ├── admin.py
│   ├── tasks.py          # وظایف Celery یادآوری
│   ├── serializers.py    # DRF serializers
│   ├── api_views.py      # API endpoints
│   └── urls.py
├── templates/            # قالب‌های HTML (Bootstrap 5 RTL)
├── static/               # فایل‌های استاتیک
├── manage.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── .env.example
```

---

## پیش‌نیازها

- Python 3.11 یا بالاتر
- Docker و Docker Compose (روش توصیه‌شده)
- **یا** PostgreSQL + Redis به صورت محلی

---

## روش اول: اجرا با Docker Compose (توصیه‌شده)

### ۱. کلون کردن و آماده‌سازی

```bash
cd django-project
cp .env.example .env
```

### ۲. ویرایش فایل `.env`

```
SECRET_KEY=یک-کلید-امن-و-تصادفی-بسازید
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

DB_NAME=bornes_db
DB_USER=bornes_user
DB_PASSWORD=bornes_pass
DB_HOST=db
DB_PORT=5432

REDIS_URL=redis://redis:6379/0
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0

# اختیاری — اگر دارید
KAVENEGAR_API_KEY=your-api-key
KAVENEGAR_SENDER=your-sender
```

### ۳. ساختن و اجرا

```bash
docker-compose up --build -d
```

### ۴. ساختن superuser

```bash
docker-compose exec web python manage.py createsuperuser
```

> فقط شماره موبایل و رمز عبور بخواهد.

### ۵. بارگذاری داده‌های نمونه

```bash
docker-compose exec web python manage.py loaddata initial_data.json
```

### ۶. آدرس‌ها

| سرویس | آدرس |
|---|---|
| سایت | http://localhost:8000 |
| پنل ادمین | http://localhost:8000/admin |
| API | http://localhost:8000/api/courses/ |
| Flower (مانیتور Celery) | http://localhost:5555 |

---

## روش دوم: اجرا محلی (بدون Docker)

### ۱. ایجاد محیط مجازی

```bash
cd django-project
python -m venv venv
source venv/bin/activate          # Linux/Mac
# یا
venv\Scripts\activate             # Windows
```

### ۲. نصب وابستگی‌ها

```bash
pip install -r requirements.txt
```

### ۳. راه‌اندازی PostgreSQL

```sql
CREATE DATABASE bornes_db;
CREATE USER bornes_user WITH PASSWORD 'bornes_pass';
GRANT ALL PRIVILEGES ON DATABASE bornes_db TO bornes_user;
```

### ۴. راه‌اندازی Redis

```bash
# Ubuntu/Debian
sudo apt-get install redis-server
sudo systemctl start redis

# Mac با Homebrew
brew install redis
brew services start redis
```

### ۵. آماده‌سازی فایل `.env`

```bash
cp .env.example .env
# DB_HOST را به localhost تغییر دهید
```

### ۶. اجرای Migrations

```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py collectstatic
```

### ۷. اجرای سرور Django

```bash
python manage.py runserver
```

### ۸. اجرای Celery Worker (در ترمینال جدید)

```bash
celery -A bornes worker --loglevel=info
```

### ۹. اجرای Celery Beat (در ترمینال جدید)

```bash
celery -A bornes beat --loglevel=info --scheduler django_celery_beat.schedulers:DatabaseScheduler
```

---

## تنظیم پیامک کاوه‌نگار

۱. در سایت [kavenegar.com](https://kavenegar.com) ثبت‌نام کنید
۲. از داشبورد کاوه‌نگار، API Key دریافت کنید
۳. در فایل `.env` مقادیر را وارد کنید:
   ```
   KAVENEGAR_API_KEY=your-actual-api-key
   KAVENEGAR_SENDER=your-sender-number
   ```

> **نکته:** اگر API Key تنظیم نشده باشد، پروژه باز هم کار می‌کند — کد تأیید در لاگ‌های سرور نمایش داده می‌شود (برای تست محلی).

---

## API Endpoints

```
GET  /api/courses/           → لیست تمام دوره‌ها
GET  /api/courses/{id}/      → جزئیات یک دوره
GET  /api/courses/featured/  → دوره‌های ویژه
GET  /api/enrollments/       → ثبت‌نام‌های کاربر جاری (نیاز به احراز هویت)
```

---

## وظایف Celery

| وظیفه | زمان‌بندی | توضیح |
|---|---|---|
| `check_pending_enrollments` | هر ۱ دقیقه | ارسال پیامک یادآوری به کاربران با پرداخت معلق بیش از ۱ ساعت |
| `expire_old_enrollments` | هر ۱۰ دقیقه | منقضی کردن ثبت‌نام‌های بیش از ۲۴ ساعت |
| `send_otp_sms` | فوری | ارسال کد تأیید هنگام ورود |
| `send_reminder_sms` | فوری | ارسال پیامک یادآوری پرداخت |

---

## دستورات مفید

```bash
# مشاهده لاگ‌های تمام سرویس‌ها
docker-compose logs -f

# مشاهده لاگ Celery
docker-compose logs -f celery_worker

# اجرای shell جنگو
docker-compose exec web python manage.py shell

# ریست کردن DB
docker-compose down -v
docker-compose up --build -d

# نصب وابستگی جدید
pip install package-name
echo "package-name==x.x.x" >> requirements.txt
```

---

## امنیت در محیط Production

قبل از استقرار، در فایل `.env`:

```
DEBUG=False
SECRET_KEY=یک-کلید-۵۰-کاراکتری-تصادفی
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
```

و حتماً از HTTPS استفاده کنید.
