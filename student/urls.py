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
    path('pay-course/<int:css_id>/', views.pay_course, name='pay_course'),
]
