from django.urls import path

from students import views

app_name = 'students'

urlpatterns = [
    path('register/', views.StudentRegistrationView.as_view(), name='registration'),
    path('enroll-course/', views.StudentEnrollCourseView.as_view(), name='enroll_course'),
    path('courses/', views.StudentCourseView.as_view(), name='course_list'),
    path('course/<pk>/', views.StudentCourseDetailView.as_view(), name='course_detail'),
    path('course/<pk>/<module_id>/', views.StudentCourseDetailView.as_view(), name='course_detail_module'),
]
