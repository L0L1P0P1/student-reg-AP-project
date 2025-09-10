from django.urls import path
from . import views

# app_name = 'instructor'

urlpatterns = [
    path('courses/', views.instructor_courses, name='instructor_courses'),
    path('courses/<int:pk>/manage/', views.instructor_course_management, name='instructor_course_management'),
]
