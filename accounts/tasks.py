"""
وظایف Celery برای ارسال پیامک
─────────────────────────────
پشتیبانی از دو سرویس:
  1. کاوه‌نگار  (KAVENEGAR_API_KEY)
  2. SMS.ir     (SMSIR_API_KEY + SMSIR_LINE_NUMBER)
اگر هیچ‌کدام تنظیم نشده باشند، کد در لاگ نمایش داده می‌شود.
"""
from celery import shared_task
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


def _send_via_kavenegar(mobile: str, message: str) -> dict:
    from kavenegar import KavenegarAPI, APIException, HTTPException
    api = KavenegarAPI(settings.KAVENEGAR_API_KEY)
    params = {
        'sender': settings.KAVENEGAR_SENDER or '10004346',
        'receptor': mobile,
        'message': message,
    }
    response = api.sms_send(params)
    return {'provider': 'kavenegar', 'response': str(response)}


def _send_via_smsir(mobile: str, message: str) -> dict:
    import urllib.request, json
    url = 'https://api.sms.ir/v1/send/plain'
    payload = json.dumps({
        'lineNumber': settings.SMSIR_LINE_NUMBER,
        'receptor': mobile,
        'messageText': message,
    }).encode('utf-8')
    req = urllib.request.Request(
        url,
        data=payload,
        headers={
            'Content-Type': 'application/json',
            'X-API-KEY': settings.SMSIR_API_KEY,
        },
        method='POST',
    )
    with urllib.request.urlopen(req, timeout=10) as resp:
        data = json.loads(resp.read())
    return {'provider': 'sms.ir', 'response': str(data)}


def _dispatch_sms(mobile: str, message: str) -> dict:
    """ارسال پیامک از طریق سرویس فعال"""
    if getattr(settings, 'KAVENEGAR_API_KEY', ''):
        return _send_via_kavenegar(mobile, message)
    if getattr(settings, 'SMSIR_API_KEY', ''):
        return _send_via_smsir(mobile, message)
    # حالت توسعه — فقط لاگ
    logger.warning(f'[SMS-DEV] {mobile} → {message}')
    return {'provider': 'dev', 'message': message}


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_otp_sms(self, mobile: str, code: str):
    """ارسال کد تأیید"""
    message = (
        f'کد تأیید برنس آکادمی:\n'
        f'{code}\n'
        f'این کد ۵ دقیقه معتبر است.'
    )
    try:
        result = _dispatch_sms(mobile, message)
        logger.info(f'[OTP-SMS] {mobile} — {result}')
        return result
    except Exception as exc:
        logger.error(f'[OTP-SMS] خطا برای {mobile}: {exc}')
        raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_reminder_sms(self, mobile: str, course_title: str):
    """یادآوری پرداخت ناقص"""
    message = (
        f'کاربر گرامی،\n'
        f'ثبت‌نام دوره «{course_title}» شما تکمیل نشده.\n'
        f'برای تکمیل پرداخت به برنس آکادمی مراجعه کنید.'
    )
    try:
        result = _dispatch_sms(mobile, message)
        logger.info(f'[Reminder-SMS] {mobile} — {result}')
        return result
    except Exception as exc:
        logger.error(f'[Reminder-SMS] خطا برای {mobile}: {exc}')
        raise self.retry(exc=exc)


def send_otp_sms_sync(mobile: str, code: str):
    """ارسال همزمان (بدون Celery) — برای استفاده مستقیم در ویو"""
    message = (
        f'کد تأیید برنس آکادمی:\n'
        f'{code}\n'
        f'این کد ۵ دقیقه معتبر است.'
    )
    try:
        result = _dispatch_sms(mobile, message)
        logger.info(f'[OTP-Sync] {mobile} — {result["provider"]}')
        return True, result
    except Exception as exc:
        logger.error(f'[OTP-Sync] خطا: {exc}')
        return False, str(exc)
