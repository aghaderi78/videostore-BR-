from celery import shared_task
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_otp_sms(self, mobile: str, code: str):
    """ارسال کد تأیید از طریق پیامک"""
    try:
        api_key = settings.KAVENEGAR_API_KEY
        if not api_key:
            logger.warning(f'[SMS] کلید API کاوه‌نگار تنظیم نشده. کد برای {mobile}: {code}')
            return {'status': 'skipped', 'message': 'API key not configured'}

        from kavenegar import KavenegarAPI, APIException, HTTPException
        api = KavenegarAPI(api_key)
        params = {
            'sender': settings.KAVENEGAR_SENDER,
            'receptor': mobile,
            'message': f'کد تأیید برنس آکادمی: {code}\nاین کد تا ۵ دقیقه معتبر است.',
        }
        response = api.sms_send(params)
        logger.info(f'[SMS] پیامک به {mobile} ارسال شد. پاسخ: {response}')
        return {'status': 'sent', 'response': str(response)}

    except Exception as exc:
        logger.error(f'[SMS] خطا در ارسال پیامک به {mobile}: {exc}')
        raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_reminder_sms(self, mobile: str, course_title: str):
    """ارسال پیامک یادآوری برای تکمیل پرداخت"""
    try:
        api_key = settings.KAVENEGAR_API_KEY
        if not api_key:
            logger.warning(f'[SMS-Reminder] کلید API تنظیم نشده. یادآوری برای {mobile}: دوره {course_title}')
            return {'status': 'skipped', 'message': 'API key not configured'}

        from kavenegar import KavenegarAPI, APIException, HTTPException
        api = KavenegarAPI(api_key)
        params = {
            'sender': settings.KAVENEGAR_SENDER,
            'receptor': mobile,
            'message': (
                f'کاربر گرامی،\n'
                f'شما ثبت‌نام دوره «{course_title}» را آغاز کرده‌اید اما پرداخت شما تکمیل نشده است.\n'
                f'برای تکمیل ثبت‌نام به سایت برنس آکادمی مراجعه کنید.'
            ),
        }
        response = api.sms_send(params)
        logger.info(f'[SMS-Reminder] پیامک یادآوری به {mobile} ارسال شد.')
        return {'status': 'sent', 'response': str(response)}

    except Exception as exc:
        logger.error(f'[SMS-Reminder] خطا در ارسال پیامک به {mobile}: {exc}')
        raise self.retry(exc=exc)
