from django.db import models
from django.utils import timezone


class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name='نام')
    slug = models.SlugField(max_length=100, unique=True, allow_unicode=True)
    icon = models.CharField(max_length=50, default='fas fa-tag', verbose_name='آیکون')

    class Meta:
        verbose_name = 'دسته‌بندی'
        verbose_name_plural = 'دسته‌بندی‌ها'

    def __str__(self):
        return self.name


class Post(models.Model):
    title = models.CharField(max_length=255, verbose_name='عنوان')
    slug = models.SlugField(max_length=255, unique=True, allow_unicode=True, verbose_name='اسلاگ')
    excerpt = models.TextField(max_length=500, verbose_name='خلاصه')
    content = models.TextField(verbose_name='محتوا')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='posts', verbose_name='دسته‌بندی')
    author = models.CharField(max_length=100, default='دکتر سعید کریمی', verbose_name='نویسنده')
    cover_image = models.ImageField(upload_to='blog/', blank=True, null=True, verbose_name='تصویر')
    is_published = models.BooleanField(default=True, verbose_name='منتشر شده')
    views_count = models.PositiveIntegerField(default=0, verbose_name='بازدید')
    published_at = models.DateTimeField(default=timezone.now, verbose_name='تاریخ انتشار')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'مقاله'
        verbose_name_plural = 'مقالات'
        ordering = ['-published_at']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('blog:detail', kwargs={'slug': self.slug})

    def reading_time(self):
        words = len(self.content.split())
        minutes = max(1, words // 200)
        return minutes
