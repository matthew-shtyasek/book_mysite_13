from django.urls import path, include
from rest_framework.routers import DefaultRouter

from courses.api import views

app_name = 'courses'

router = DefaultRouter()
router.register('courses', views.CourseViewSet)

urlpatterns = [
    path('subjects/', views.SubjectListView.as_view(), name='subject_list'),
    path('subjects/<pk>/', views.SubjectDetailView.as_view(), name='subject_detail'),
    path('', include(router.urls)),
]
