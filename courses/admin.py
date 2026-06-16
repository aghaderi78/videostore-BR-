from django.contrib import admin
from django.utils.html import format_html
from .models import Course, Lesson, Enrollment, Payment


class LessonInline(admin.TabularInline):
    model = Lesson
    extra = 1
    fields = ('order', 'title', 'duration_minutes', 'is_preview', 'video_url')
    ordering = ('order',)


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'instructor', 'price_display', 'duration_hours', 'level', 'lesson_count', 'is_active', 'published_at')
    list_filter = ('is_active', 'level', 'published_at')
    search_fields = ('title', 'instructor', 'description')
    prepopulated_fields = {'slug': ('title',)}
    inlines = [LessonInline]
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-published_at',)

    fieldsets = (
        ('اطلاعات اصلی', {'fields': ('title', 'slug', 'description', 'instructor', 'thumbnail')}),
        ('قیمت و مشخصات', {'fields': ('price', 'duration_hours', 'level')}),
        ('وضعیت', {'fields': ('is_active', 'published_at')}),
        ('تاریخ‌ها', {'fields': ('created_at', 'updated_at')}),
    )

    def price_display(self, obj):
        return f'{obj.price:,} تومان'
    price_display.short_description = 'قیمت'

    def lesson_count(self, obj):
        return obj.lessons.count()
    lesson_count.short_description = 'تعداد جلسات'


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('course', 'order', 'title', 'duration_minutes', 'is_preview')
    list_filter = ('course', 'is_preview')
    search_fields = ('title', 'course__title')
    ordering = ('course', 'order')


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('user', 'course', 'status_colored', 'enrolled_at', 'paid_at', 'reminder_sent')
    list_filter = ('status', 'enrolled_at', 'reminder_sent')
    search_fields = ('user__mobile', 'course__title')
    ordering = ('-enrolled_at',)
    readonly_fields = ('enrolled_at', 'paid_at', 'expired_at')
    actions = ['mark_as_paid', 'mark_as_expired']

    def status_colored(self, obj):
        colors = {
            'pending': '#ffc107',
            'paid': '#28a745',
            'expired': '#dc3545',
            'refunded': '#6c757d',
        }
        color = colors.get(obj.status, '#000')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_colored.short_description = 'وضعیت'

    def mark_as_paid(self, request, queryset):
        for enrollment in queryset:
            enrollment.mark_paid()
        self.message_user(request, f'{queryset.count()} ثبت‌نام به عنوان پرداخت شده تعیین شد.')
    mark_as_paid.short_description = 'علامت‌گذاری به عنوان پرداخت شده'

    def mark_as_expired(self, request, queryset):
        for enrollment in queryset:
            enrollment.mark_expired()
        self.message_user(request, f'{queryset.count()} ثبت‌نام منقضی شد.')
    mark_as_expired.short_description = 'منقضی کردن ثبت‌نام‌ها'


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('enrollment', 'amount_display', 'status', 'authority', 'ref_id', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('enrollment__user__mobile', 'authority', 'ref_id')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')

    def amount_display(self, obj):
        return f'{obj.amount:,} تومان'
    amount_display.short_description = 'مبلغ'
