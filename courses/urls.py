from django.urls import path
from . import views

app_name = 'courses'

urlpatterns = [
    path('', views.home_view, name='home'),
    path('courses/', views.home_view, name='course_list'),
    path('course/<slug:slug>/', views.course_detail_view, name='detail'),
    path('course/<slug:slug>/enroll/', views.enroll_view, name='enroll'),
    path('course/<slug:slug>/add-to-cart/', views.cart_add_view, name='cart_add'),
    path('cart/', views.cart_view, name='cart'),
    path('cart/remove/<int:course_id>/', views.cart_remove_view, name='cart_remove'),
    path('cart/checkout/', views.cart_checkout_view, name='cart_checkout'),
    path('payment/<int:enrollment_id>/', views.payment_view, name='payment'),
    path('payment/success/<int:payment_id>/', views.payment_success_view, name='payment_success'),
    path('payment/callback/', views.payment_callback_view, name='payment_callback'),
]
