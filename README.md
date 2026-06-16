# 📌 برنس آکادمی - یادآوری پروژه

## پروژه
فروشگاه دوره آموزشی آنلاین با جنگو ۵

## کاری که کردم

### اپلیکیشن accounts
- مدل User با شماره موبایل
- مدل OTP برای کد تأیید
- ورود با پیامک
- ارسال کد با Celery

### اپلیکیشن courses
- مدل Course (دوره)
- مدل Lesson (جلسه)
- مدل Enrollment (ثبت‌نام)
- مدل Payment (پرداخت)
- نمایش دوره‌ها
- ثبت‌نام و پرداخت
- API با DRF

### تسک‌های Celery
- ارسال OTP
- یادآوری پرداخت (هر ۱ دقیقه)
- انقضای ثبت‌نام (هر ۱۰ دقیقه)

### تنظیمات
- settings.py کامل
- celery.py تنظیم شده
- Dockerfile و docker-compose.yml

### قالب‌ها
- base.html (اصلی)
- login.html (ورود)
- verify.html (تأیید کد)
- list.html (لیست دوره‌ها)
- detail.html (جزئیات دوره)
- payment.html (پرداخت)

## راه‌اندازی

### با Docker
```bash
docker-compose up --build -d
docker-compose exec web python manage.py createsuperuser
