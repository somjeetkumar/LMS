from django.urls import path,include
from rest_framework.routers import DefaultRouter
from .views import RegisterViewSet,LoginViewSet,Teacher_register_ViesSet,LoginUserDetails,VerifyOTPView,ForgotPasswordView,ResetPasswordView,reSendOtpView,TeacherListView,RefreshAccessTokenView,HeadTeacherListView

router = DefaultRouter()
router.register(r'register',RegisterViewSet, basename='register')
router.register(r'login',LoginViewSet, basename='login')
router.register(r'teacherRegister',Teacher_register_ViesSet, basename='teacherRegister')
router.register(r'LoginUserDetails',LoginUserDetails, basename='loginUser')

# 
urlpatterns = [
  path('refreshAccessToken/',RefreshAccessTokenView.as_view()),
  path('verify_mail/',VerifyOTPView.as_view()),
  path('forgot_password/',ForgotPasswordView.as_view()),
  path('reset_password/',ResetPasswordView.as_view()),
  path('reSendOtp/',reSendOtpView.as_view()),
  path('teacherList/',TeacherListView.as_view()),
  path('headTeacherListView/',HeadTeacherListView.as_view()),
  path('',include(router.urls)),
] 

# 