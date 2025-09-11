from django.urls import path
from . import views

# app_name = 'student'

urlpatterns = [
    # Course selection
    path('available-courses/', views.available_courses, name='available_courses'),
    path('other-courses/', views.other_courses, name='other_courses'),
    path('select-course/<int:course_id>/', views.select_course, name='select_course'),
    
    # Scores
    path('scores/', views.check_scores, name='check_scores'),
    
    # Payment
    path("payments/", views.payment_panel, name="payment_panel"),
    path("payments/<int:css_id>/", views.payment_panel, name="payment_checkout"),

    #weekly-program
    path('weekly-program/', views.student_weekly_program, name='student_weekly_program'),
]
