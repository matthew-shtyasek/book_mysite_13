from django.urls import path
from django.views.decorators.cache import cache_page

from students import views

app_name = 'students'

urlpatterns = [
    path('register/', views.StudentRegistrationView.as_view(), name='registration'),
    path('enroll-course/', views.StudentEnrollCourseView.as_view(), name='enroll_course'),
    path('courses/', views.StudentCourseView.as_view(), name='course_list'),
    path('course/<pk>/', cache_page(60*15)(views.StudentCourseDetailView.as_view()), name='course_detail'),
    path('course/<pk>/<module_id>/', cache_page(60*15)(views.StudentCourseDetailView.as_view()), name='course_detail_module'),
]
