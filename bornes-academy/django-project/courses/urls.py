from django.urls import path
from . import views

app_name = 'courses'

urlpatterns = [
    path('', views.home_view, name='home'),
    path('course/<slug:slug>/', views.course_detail_view, name='detail'),
    path('course/<slug:slug>/enroll/', views.enroll_view, name='enroll'),
    path('payment/<int:enrollment_id>/', views.payment_view, name='payment'),
    path('payment/success/<int:payment_id>/', views.payment_success_view, name='payment_success'),
    path('payment/callback/', views.payment_callback_view, name='payment_callback'),
]
