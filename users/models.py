from django.contrib.auth.models import AbstractUser
from django.db import models

class Major(models.Model):
    name = models.CharField(max_length="255")

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

class Admin(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, limit_choices_to={'role': User.Role.ADMIN})
    title = models.CharField(max_length="50")

class Instructor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, limit_choices_to={'role': User.Role.INSTRUCTOR})
    specialty = models.CharField(max_length="50")
    bio = models.CharField(max_length="255")

    class AcademicTitle(models.IntegerChoices):
        HEAD_OF_DEPARTMENT = 1, "Head Of Department"
        PROFESSOR = 2, 'Professor'
        ASSOCIATE_PROFESSOR = 3, 'Associate Professor'
        ASSISTANT_PROFESSOR = 4, 'Assistant Professor'
        POST_DOC = 5, "PostDoc"

    academic_title = models.PositiveSmallIntegerField(choices=AcademicTitle.choices)

class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, limit_choices_to={'role': User.Role.STUDENT})
    enrollment_year = models.PositiveSmallIntegerField()
    gpa = models.FloatField()
    major = models.ForeignKey(Major, on_delete=models.SET_NULL)
    funded = models.BooleanField()
