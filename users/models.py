from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.

class User(AbstractUser):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone_number = models.CharField(max_length=11, unique=True)
    national_id = models.CharField(max_length=10, unique=True)
    email = models.CharField(max_length=254, unique=True, blank=True)
    
    class Role(models.IntegerChoices):
        ADMIN = 1, 'Admin'
        INSTRUCTOR = 2, 'Instructor'
        STUDENT = 3, 'Student'

    role = models.PositiveSmallIntegerField(choices=Role.choices, default=Role.STUDENT)

class 
