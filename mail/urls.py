from django.contrib import admin
from django.urls import path
from rest_framework_simplejwt import views as jwt_views
from .views import RegisterAPI, ListUser, EmailVerificationAPI, PhoneVerificationAPI, SendOTP
urlpatterns = [
    path('user/', RegisterAPI.as_view(), name="register"),
    path('all-user/', ListUser.as_view(), name="list_users"),
    path('send-otp/', SendOTP.as_view(), name="send_otp"),
    path('email-verification/', EmailVerificationAPI.as_view(), name="emailـverification"),
    path('phone-verification/', PhoneVerificationAPI.as_view(), name="phoneـverification"),
    path('token/', jwt_views.TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh')
]
