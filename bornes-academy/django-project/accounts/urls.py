from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.send_otp_view, name='send_otp'),
    path('verify/', views.verify_otp_view, name='verify_otp'),
    path('resend/', views.resend_otp_view, name='resend_otp'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
]
