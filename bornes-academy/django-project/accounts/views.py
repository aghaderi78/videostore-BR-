from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import User, OTP
from .forms import SendOTPForm, VerifyOTPForm, ProfileForm
from .tasks import send_otp_sms


def send_otp_view(request):
    if request.user.is_authenticated:
        return redirect('courses:home')

    if request.method == 'POST':
        form = SendOTPForm(request.POST)
        if form.is_valid():
            mobile = form.cleaned_data['mobile']
            OTP.objects.filter(mobile=mobile, is_used=False).update(is_used=True)
            code = OTP.generate_code()
            OTP.objects.create(mobile=mobile, code=code)
            send_otp_sms.delay(mobile, code)
            messages.success(request, f'کد تأیید به شماره {mobile} ارسال شد.')
            request.session['otp_mobile'] = mobile
            return redirect('accounts:verify_otp')
    else:
        form = SendOTPForm()

    return render(request, 'accounts/send_otp.html', {'form': form})


def verify_otp_view(request):
    if request.user.is_authenticated:
        return redirect('courses:home')

    mobile = request.session.get('otp_mobile')
    if not mobile:
        messages.error(request, 'لطفاً ابتدا شماره موبایل خود را وارد کنید.')
        return redirect('accounts:send_otp')

    if request.method == 'POST':
        form = VerifyOTPForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data['code']
            try:
                otp = OTP.objects.filter(
                    mobile=mobile,
                    code=code,
                    is_used=False
                ).latest('created_at')

                if otp.is_valid():
                    otp.is_used = True
                    otp.save()
                    user, created = User.objects.get_or_create(mobile=mobile)
                    if not user.is_active:
                        messages.error(request, 'حساب کاربری شما غیرفعال است.')
                        return redirect('accounts:send_otp')
                    login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                    if 'otp_mobile' in request.session:
                        del request.session['otp_mobile']
                    if created:
                        messages.success(request, 'ثبت‌نام شما با موفقیت انجام شد.')
                    else:
                        messages.success(request, 'ورود با موفقیت انجام شد.')
                    return redirect(request.GET.get('next', 'courses:home'))
                else:
                    messages.error(request, 'کد تأیید منقضی شده است. لطفاً مجدداً درخواست کنید.')
            except OTP.DoesNotExist:
                messages.error(request, 'کد تأیید اشتباه است.')
    else:
        form = VerifyOTPForm(initial={'mobile': mobile})

    return render(request, 'accounts/verify_otp.html', {'form': form, 'mobile': mobile})


def resend_otp_view(request):
    mobile = request.session.get('otp_mobile')
    if not mobile:
        return redirect('accounts:send_otp')

    last_otp = OTP.objects.filter(mobile=mobile).order_by('-created_at').first()
    if last_otp:
        diff = timezone.now() - last_otp.created_at
        if diff.total_seconds() < 60:
            remaining = int(60 - diff.total_seconds())
            messages.warning(request, f'لطفاً {remaining} ثانیه دیگر تلاش کنید.')
            return redirect('accounts:verify_otp')

    OTP.objects.filter(mobile=mobile, is_used=False).update(is_used=True)
    code = OTP.generate_code()
    OTP.objects.create(mobile=mobile, code=code)
    send_otp_sms.delay(mobile, code)
    messages.success(request, 'کد جدید ارسال شد.')
    return redirect('accounts:verify_otp')


@login_required
def profile_view(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'اطلاعات پروفایل با موفقیت به‌روز شد.')
            return redirect('accounts:profile')
    else:
        form = ProfileForm(instance=request.user)

    from courses.models import Enrollment
    enrollments = Enrollment.objects.filter(
        user=request.user
    ).select_related('course').order_by('-enrolled_at')

    return render(request, 'accounts/profile.html', {
        'form': form,
        'enrollments': enrollments,
    })


def logout_view(request):
    logout(request)
    messages.success(request, 'با موفقیت خارج شدید.')
    return redirect('courses:home')
