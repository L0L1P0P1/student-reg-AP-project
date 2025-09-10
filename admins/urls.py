from django.urls import path
from . import views

app_name = 'admin'

urlpatterns = [
    # Student management
    path('students/', views.list_all_students, name='list_all_students'),
    path('students/<int:pk>/edit/', views.admin_student_modification, name='admin_student_modification'),
    
    # Unit management
    path('units/', views.admin_list_all_units, name='admin_list_all_units'),
    path('units/create/', views.admin_unit_creation, name='admin_unit_creation'),
    path('units/<int:pk>/edit/', views.admin_unit_modification, name='admin_unit_modification'),
    
    # Course management
    path('courses/', views.list_all_courses, name='list_all_courses'),
    path('courses/create/', views.admin_course_creation, name='admin_course_creation'),
    path('courses/<int:pk>/edit/', views.admin_course_modification, name='admin_course_modification'),
    
    # Instructor management
    path('instructors/', views.list_all_instructors, name='list_all_instructors'),
    path('instructors/<int:pk>/edit/', views.admin_instructor_modification, name='admin_instructor_modification'),
    
    # Admin management
    path('admins/<int:pk>/edit/', views.admin_modification, name='admin_modification'),

    # Semester management
    path('semesters/', views.admin_list_all_semesters, name='admin_list_all_semesters'),
    path('semesters/create/', views.admin_semester_creation, name='admin_semester_creation'),
    path('semesters/<int:codename>/edit/', views.admin_semester_modification, name='admin_semester_modification'),
]
