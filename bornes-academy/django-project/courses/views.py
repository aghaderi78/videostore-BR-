from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db import IntegrityError
from .models import Course, Lesson, Enrollment, Payment


def home_view(request):
    courses = Course.objects.filter(is_active=True).order_by('-published_at')
    return render(request, 'courses/home.html', {'courses': courses})


def course_detail_view(request, slug):
    course = get_object_or_404(Course, slug=slug, is_active=True)
    lessons = course.lessons.all().order_by('order')
    enrollment = None
    if request.user.is_authenticated:
        enrollment = Enrollment.objects.filter(user=request.user, course=course).first()
    return render(request, 'courses/detail.html', {
        'course': course,
        'lessons': lessons,
        'enrollment': enrollment,
    })


@login_required
def enroll_view(request, slug):
    course = get_object_or_404(Course, slug=slug, is_active=True)
    existing = Enrollment.objects.filter(user=request.user, course=course).first()

    if existing and existing.is_paid:
        messages.info(request, 'شما قبلاً این دوره را خریداری کرده‌اید.')
        return redirect('courses:detail', slug=slug)

    if existing and existing.is_expired:
        existing.delete()
        existing = None

    if not existing:
        try:
            enrollment = Enrollment.objects.create(user=request.user, course=course)
        except IntegrityError:
            enrollment = Enrollment.objects.get(user=request.user, course=course)
    else:
        enrollment = existing

    if course.is_free:
        enrollment.mark_paid()
        messages.success(request, f'ثبت‌نام رایگان در دوره «{course.title}» انجام شد.')
        return redirect('courses:detail', slug=slug)

    return redirect('courses:payment', enrollment_id=enrollment.id)


@login_required
def payment_view(request, enrollment_id):
    enrollment = get_object_or_404(Enrollment, id=enrollment_id, user=request.user)

    if enrollment.is_paid:
        messages.info(request, 'این دوره قبلاً پرداخت شده است.')
        return redirect('courses:detail', slug=enrollment.course.slug)

    if enrollment.is_expired:
        messages.error(request, 'مهلت پرداخت این ثبت‌نام منقضی شده است.')
        return redirect('courses:detail', slug=enrollment.course.slug)

    if request.method == 'POST':
        payment = Payment.objects.create(
            enrollment=enrollment,
            amount=enrollment.course.price,
            status='pending',
        )

        sandbox = True
        if sandbox:
            payment.authority = f'SANDBOX-{payment.id}-{timezone.now().timestamp():.0f}'
            payment.status = 'success'
            payment.ref_id = f'REF{payment.id:08d}'
            payment.save()
            enrollment.mark_paid()
            messages.success(request, f'پرداخت با موفقیت انجام شد. شماره مرجع: {payment.ref_id}')
            return redirect('courses:payment_success', payment_id=payment.id)

    return render(request, 'courses/payment.html', {'enrollment': enrollment})


@login_required
def payment_success_view(request, payment_id):
    payment = get_object_or_404(Payment, id=payment_id, enrollment__user=request.user)
    return render(request, 'courses/payment_success.html', {'payment': payment})


@login_required
def payment_callback_view(request):
    authority = request.GET.get('Authority', '')
    status = request.GET.get('Status', '')
    payment = get_object_or_404(Payment, authority=authority)
    enrollment = payment.enrollment

    if enrollment.user != request.user:
        messages.error(request, 'دسترسی غیرمجاز.')
        return redirect('courses:home')

    if status == 'OK':
        payment.status = 'success'
        ref_id = f'REF{payment.id:08d}'
        payment.ref_id = ref_id
        payment.save()
        enrollment.mark_paid()
        messages.success(request, f'پرداخت موفق. شماره مرجع: {ref_id}')
        return redirect('courses:payment_success', payment_id=payment.id)
    else:
        payment.status = 'failed'
        payment.save()
        messages.error(request, 'پرداخت ناموفق بود. لطفاً مجدداً تلاش کنید.')
        return redirect('courses:payment', enrollment_id=enrollment.id)
