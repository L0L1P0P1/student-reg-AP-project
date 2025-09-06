from django.contrib.auth.models import AbstractUser
from django.db import models

class Major(models.Model):
    name = models.CharField(max_length=255)
    
    def __str__(self): # type: ignore 
        return self.name

class User(AbstractUser):
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    national_id = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(max_length=254, unique=True)
    
    class Role(models.IntegerChoices):
        ADMIN = 1, 'Admin'
        INSTRUCTOR = 2, 'Instructor'
        STUDENT = 3, 'Student'

    role = models.PositiveSmallIntegerField(choices=Role.choices, default=Role.STUDENT) # type: ignore

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

class Admin(User):
    title = models.CharField(max_length=50)
    
    def save(self, *args, **kwargs):
        self.role = User.Role.ADMIN
        super().save(*args, **kwargs)

class Instructor(User):
    specialty = models.CharField(max_length=50)
    bio = models.TextField(max_length=500, blank=True)
    
    class AcademicTitle(models.IntegerChoices):
        HEAD_OF_DEPARTMENT = 1, "Head Of Department"
        PROFESSOR = 2, 'Professor'
        ASSOCIATE_PROFESSOR = 3, 'Associate Professor'
        ASSISTANT_PROFESSOR = 4, 'Assistant Professor'
        POST_DOC = 5, "PostDoc"

    academic_title = models.PositiveSmallIntegerField(choices=AcademicTitle.choices)
    
    def save(self, *args, **kwargs):
        self.role = User.Role.INSTRUCTOR
        super().save(*args, **kwargs)

class Student(User):
    enrollment_year = models.PositiveSmallIntegerField()
    gpa = models.FloatField()
    major = models.ForeignKey(Major, null=True, blank=True, on_delete=models.SET_NULL)
    funded = models.BooleanField(default=False) # type: ignore
    verified = models.BooleanField(default=False) # type: ignore
    
    class Meta: # type: ignore 
        ordering = ['enrollment_year']
    
    def save(self, *args, **kwargs):
        self.role = User.Role.STUDENT
        super().save(*args, **kwargs)
