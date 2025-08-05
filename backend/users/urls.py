from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('verify-otp/', views.verify_otp, name='verifyotp'),
    path('login/', views.login_view, name='login'),
     # ✅ Forgot/Reset password
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('reset-password/', views.reset_password, name='reset_password'),
    path('api/dashboard/', views.dashboard_view, name='dashboard'),

]
