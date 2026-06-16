from django.apps import AppConfig


class CoursesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'courses'
    verbose_name = 'دوره‌ها'

    def ready(self):
        from django_celery_beat.models import PeriodicTask, IntervalSchedule
        import json
        try:
            schedule_1min, _ = IntervalSchedule.objects.get_or_create(
                every=1, period=IntervalSchedule.MINUTES
            )
            PeriodicTask.objects.get_or_create(
                name='بررسی پرداخت‌های معلق',
                defaults={
                    'task': 'courses.tasks.check_pending_enrollments',
                    'interval': schedule_1min,
                    'args': json.dumps([]),
                }
            )
            schedule_10min, _ = IntervalSchedule.objects.get_or_create(
                every=10, period=IntervalSchedule.MINUTES
            )
            PeriodicTask.objects.get_or_create(
                name='منقضی کردن ثبت‌نام‌های قدیمی',
                defaults={
                    'task': 'courses.tasks.expire_old_enrollments',
                    'interval': schedule_10min,
                    'args': json.dumps([]),
                }
            )
        except Exception:
            pass
