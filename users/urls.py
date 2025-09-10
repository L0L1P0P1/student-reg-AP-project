from django.urls import path, include
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.hub, name='hub'),
    path('login/', auth_views.LoginView.as_view(template_name='users/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('signup/', views.signup, name='signup'),
    path('signup/student/', views.student_signup, name='student_signup'),
    path('signup/instructor/', views.instructor_signup, name='instructor_signup'),
    # path('signup/admin/', views.admin_signup, name='admin_signup'),
    path('admin-panel/', include('admins.urls', namespace='admin')),
    path('instructor/', include('instructors.urls', namespace='instructor')),
    path('student/', include('student.urls', namespace='student')),
]
