from celery import shared_task
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)


@shared_task
def check_pending_enrollments():
    """
    هر دقیقه اجرا می‌شود.
    برای کاربرانی که ۱ ساعت از ثبت‌نامشان گذشته و پرداخت نکرده‌اند،
    یک پیامک یادآوری ارسال می‌کند.
    """
    from .models import Enrollment
    from accounts.tasks import send_reminder_sms

    one_hour_ago = timezone.now() - timezone.timedelta(hours=1)
    two_hours_ago = timezone.now() - timezone.timedelta(hours=2)

    pending_enrollments = Enrollment.objects.filter(
        status='pending',
        reminder_sent=False,
        enrolled_at__lte=one_hour_ago,
        enrolled_at__gte=two_hours_ago,
    ).select_related('user', 'course')

    count = 0
    for enrollment in pending_enrollments:
        try:
            send_reminder_sms.delay(enrollment.user.mobile, enrollment.course.title)
            enrollment.reminder_sent = True
            enrollment.save(update_fields=['reminder_sent'])
            count += 1
            logger.info(f'[Reminder] پیامک به {enrollment.user.mobile} برای دوره {enrollment.course.title} ارسال شد.')
        except Exception as exc:
            logger.error(f'[Reminder] خطا برای {enrollment.user.mobile}: {exc}')

    logger.info(f'[check_pending_enrollments] {count} پیامک یادآوری ارسال شد.')
    return f'{count} reminder(s) sent'


@shared_task
def expire_old_enrollments():
    """
    ثبت‌نام‌هایی که ۲۴ ساعت از زمانشان گذشته و پرداخت نشده را منقضی می‌کند.
    """
    from .models import Enrollment

    cutoff = timezone.now() - timezone.timedelta(hours=24)
    expired_count = Enrollment.objects.filter(
        status='pending',
        enrolled_at__lte=cutoff,
    ).update(status='expired', expired_at=timezone.now())

    logger.info(f'[expire_old_enrollments] {expired_count} ثبت‌نام منقضی شد.')
    return f'{expired_count} enrollment(s) expired'


@shared_task(bind=True, max_retries=3)
def process_payment_verification(self, enrollment_id: int, authority: str, status: str):
    """تأیید پرداخت از طریق درگاه"""
    from .models import Enrollment, Payment

    try:
        enrollment = Enrollment.objects.get(id=enrollment_id)
        payment = Payment.objects.filter(
            enrollment=enrollment,
            authority=authority,
        ).first()

        if not payment:
            logger.error(f'[Payment] پرداختی با authority={authority} یافت نشد.')
            return

        if status == 'OK':
            payment.status = 'success'
            payment.save()
            enrollment.mark_paid()
            logger.info(f'[Payment] پرداخت {enrollment_id} موفق بود.')
        else:
            payment.status = 'failed'
            payment.save()
            logger.warning(f'[Payment] پرداخت {enrollment_id} ناموفق بود.')

    except Enrollment.DoesNotExist:
        logger.error(f'[Payment] ثبت‌نام {enrollment_id} یافت نشد.')
    except Exception as exc:
        raise self.retry(exc=exc)
