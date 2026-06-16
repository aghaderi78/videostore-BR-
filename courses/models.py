from django.db import models
from django.conf import settings
from django.utils import timezone


class Course(models.Model):
    LEVEL_CHOICES = [
        ('beginner', 'مبتدی'),
        ('intermediate', 'متوسط'),
        ('advanced', 'پیشرفته'),
    ]

    title = models.CharField(max_length=255, verbose_name='عنوان دوره')
    slug = models.SlugField(max_length=255, unique=True, allow_unicode=True, verbose_name='اسلاگ')
    description = models.TextField(verbose_name='توضیحات')
    instructor = models.CharField(max_length=100, default='دکتر سعید کریمی', verbose_name='مدرس')
    price = models.PositiveIntegerField(verbose_name='قیمت (تومان)')
    duration_hours = models.PositiveIntegerField(verbose_name='مدت زمان (ساعت)')
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, default='beginner', verbose_name='سطح')
    thumbnail = models.ImageField(upload_to='courses/thumbnails/', blank=True, null=True, verbose_name='تصویر شاخص')
    is_active = models.BooleanField(default=True, verbose_name='فعال')
    published_at = models.DateTimeField(default=timezone.now, verbose_name='تاریخ انتشار')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='تاریخ به‌روزرسانی')

    class Meta:
        verbose_name = 'دوره'
        verbose_name_plural = 'دوره‌ها'
        ordering = ['-published_at']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('courses:detail', kwargs={'slug': self.slug})

    @property
    def lesson_count(self):
        return self.lessons.count()

    @property
    def formatted_price(self):
        return f'{self.price:,}'

    @property
    def is_free(self):
        return self.price == 0


class Lesson(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='lessons', verbose_name='دوره')
    title = models.CharField(max_length=255, verbose_name='عنوان جلسه')
    order = models.PositiveIntegerField(default=1, verbose_name='ترتیب')
    video_url = models.URLField(blank=True, verbose_name='لینک ویدیو')
    video_file = models.FileField(upload_to='courses/videos/', blank=True, null=True, verbose_name='فایل ویدیو')
    description = models.TextField(blank=True, verbose_name='توضیحات جلسه')
    duration_minutes = models.PositiveIntegerField(default=0, verbose_name='مدت زمان (دقیقه)')
    is_preview = models.BooleanField(default=False, verbose_name='پیش‌نمایش رایگان')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')

    class Meta:
        verbose_name = 'جلسه'
        verbose_name_plural = 'جلسات'
        ordering = ['order']

    def __str__(self):
        return f'{self.course.title} - جلسه {self.order}: {self.title}'


class Enrollment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'در انتظار پرداخت'),
        ('paid', 'پرداخت شده'),
        ('expired', 'منقضی شده'),
        ('refunded', 'بازگشت وجه'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='enrollments', verbose_name='کاربر')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments', verbose_name='دوره')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='وضعیت')
    enrolled_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ثبت‌نام')
    paid_at = models.DateTimeField(null=True, blank=True, verbose_name='تاریخ پرداخت')
    expired_at = models.DateTimeField(null=True, blank=True, verbose_name='تاریخ انقضا')
    reminder_sent = models.BooleanField(default=False, verbose_name='یادآوری ارسال شد')

    class Meta:
        verbose_name = 'ثبت‌نام'
        verbose_name_plural = 'ثبت‌نام‌ها'
        ordering = ['-enrolled_at']
        unique_together = ('user', 'course')

    def __str__(self):
        return f'{self.user.mobile} - {self.course.title} ({self.get_status_display()})'

    def mark_paid(self):
        self.status = 'paid'
        self.paid_at = timezone.now()
        self.save()

    def mark_expired(self):
        self.status = 'expired'
        self.expired_at = timezone.now()
        self.save()

    @property
    def is_paid(self):
        return self.status == 'paid'

    @property
    def is_pending(self):
        return self.status == 'pending'

    @property
    def is_expired(self):
        return self.status == 'expired'

    @property
    def hours_since_enrollment(self):
        delta = timezone.now() - self.enrolled_at
        return delta.total_seconds() / 3600


class Payment(models.Model):
    STATUS_CHOICES = [
        ('initiated', 'آغاز شده'),
        ('pending', 'در انتظار'),
        ('success', 'موفق'),
        ('failed', 'ناموفق'),
        ('cancelled', 'لغو شده'),
    ]

    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE, related_name='payments', verbose_name='ثبت‌نام')
    amount = models.PositiveIntegerField(verbose_name='مبلغ (تومان)')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='initiated', verbose_name='وضعیت')
    authority = models.CharField(max_length=255, blank=True, verbose_name='کد مرجع درگاه')
    ref_id = models.CharField(max_length=255, blank=True, verbose_name='شماره مرجع')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='تاریخ به‌روزرسانی')

    class Meta:
        verbose_name = 'پرداخت'
        verbose_name_plural = 'پرداخت‌ها'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.enrollment.user.mobile} - {self.amount:,} تومان - {self.get_status_display()}'
