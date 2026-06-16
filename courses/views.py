from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db import IntegrityError
from .models import Course, Lesson, Enrollment, Payment
from .cart import Cart


def home_view(request):
    courses = Course.objects.filter(is_active=True).order_by('-published_at')
    cart = Cart(request)
    return render(request, 'courses/home.html', {
        'courses': courses,
        'cart': cart,
    })


def course_detail_view(request, slug):
    course = get_object_or_404(Course, slug=slug, is_active=True)
    lessons = course.lessons.all().order_by('order')
    enrollment = None
    in_cart = False
    if request.user.is_authenticated:
        enrollment = Enrollment.objects.filter(user=request.user, course=course).first()
    cart = Cart(request)
    in_cart = cart.contains(course.id)
    related_courses = Course.objects.filter(is_active=True, level=course.level).exclude(id=course.id)[:3]
    return render(request, 'courses/detail.html', {
        'course': course,
        'lessons': lessons,
        'enrollment': enrollment,
        'in_cart': in_cart,
        'related_courses': related_courses,
    })


# ─── Cart ──────────────────────────────────────────────────────────────────────

def cart_view(request):
    cart = Cart(request)
    items = list(cart)
    total_price = cart.total_price()
    return render(request, 'courses/cart.html', {
        'items': items,
        'total_price': total_price,
    })


def cart_add_view(request, slug):
    course = get_object_or_404(Course, slug=slug, is_active=True)
    cart = Cart(request)
    added = cart.add(course)
    if added:
        messages.success(request, f'«{course.title}» به سبد خرید اضافه شد.')
    else:
        messages.info(request, 'این دوره از قبل در سبد خرید شماست.')
    next_url = request.GET.get('next', request.META.get('HTTP_REFERER', '/'))
    return redirect(next_url)


def cart_remove_view(request, course_id):
    cart = Cart(request)
    cart.remove(course_id)
    messages.success(request, 'دوره از سبد خرید حذف شد.')
    return redirect('courses:cart')


@login_required
def cart_checkout_view(request):
    cart = Cart(request)
    if not cart:
        messages.warning(request, 'سبد خرید شما خالی است.')
        return redirect('courses:cart')

    items = list(cart)
    created_enrollments = []

    for item in items:
        course = item.get('course')
        if not course:
            continue
        existing = Enrollment.objects.filter(user=request.user, course=course).first()
        if existing and existing.is_paid:
            messages.info(request, f'«{course.title}» قبلاً خریداری شده.')
            continue
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
            messages.success(request, f'ثبت‌نام رایگان در «{course.title}» انجام شد.')
        else:
            created_enrollments.append(enrollment)

    cart.clear()

    if len(created_enrollments) == 1:
        return redirect('courses:payment', enrollment_id=created_enrollments[0].id)
    elif len(created_enrollments) > 1:
        messages.info(request, 'لطفاً هر دوره را جداگانه پرداخت کنید.')
        return redirect('accounts:profile')
    return redirect('accounts:profile')


# ─── Enrollment & Payment ──────────────────────────────────────────────────────

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
