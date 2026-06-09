from django.urls import path,include
from rest_framework.routers import DefaultRouter
from .views import (
    CourseView_set,
    SubjectViewSet,
    ChapterViewSet,
    # contentViewSet,
    TopicViewSet,
    courseShow_all,
    EnrollmentView_Set,
    FileViewSet,
    BuyCourseAPIView,
    VerifyPaymentAPIView,
    GenerateCertificateAPIView
    )

router = DefaultRouter()
router.register(r'course',CourseView_set, basename='course')
router.register(r'course_all',courseShow_all, basename='course_all')
router.register(r'subject',SubjectViewSet, basename='subject')
router.register(r'chapter',ChapterViewSet, basename='chapter')
router.register(r'topics',TopicViewSet, basename='topics')
router.register(r'enrol',EnrollmentView_Set, basename='enrol')
router.register(r'files',FileViewSet, basename='files')
# router.register(r'task',TaskTrackViewSet, basename='task')


urlpatterns = [
  path('',include(router.urls))  ,
  path(
    "buy-course/<int:course_id>/",
    BuyCourseAPIView.as_view()
    ),
    path(
        "verify-payment/",
        VerifyPaymentAPIView.as_view(),
        name="verify-payment"
    ),
    path(
        "certificate/<int:pk>/",
        GenerateCertificateAPIView.as_view(),
        name='generate-certificate'
    ),
]   