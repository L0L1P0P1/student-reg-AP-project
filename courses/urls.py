from django.urls import path
from . import views

urlpatterns = [
    path('attachment/<int:attachment_id>/', views.view_attachment, name='view_attachment'),
]
