from django.urls import path
from . import views

# app_name = 'instructor'

urlpatterns = [
    path('courses/', views.instructor_courses, name='instructor_courses'),
    path('courses/<int:pk>/manage/', views.instructor_course_management, name='instructor_course_management'),
    path('courses/attachments/', views.instructor_courses_attachments, name='instructor_courses_attachments'),
    path('courses/<int:course_pk>/attachments/', views.instructor_view_attachments, name='instructor_view_attachments'),
    path('courses/<int:course_pk>/attachments/create/', views.instructor_create_attachment, name='instructor_create_attachment'),
]
