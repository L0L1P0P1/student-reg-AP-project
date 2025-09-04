from django.contrib.auth.models import AbstractUser
from django.db import models

class Major(models.Model):
    name = models.CharField(max_length=255)
    
    def __str__(self):
        return self.name

class User(AbstractUser):
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    national_id = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(max_length=254, unique=True)
    
    class Role(models.IntegerChoices):
        ADMIN = 1, 'Admin'
        INSTRUCTOR = 2, 'Instructor'
        STUDENT = 3, 'Student'

    role = models.PositiveSmallIntegerField(choices=Role.choices, default=Role.STUDENT)

class AdminProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='admin_profile')
    title = models.CharField(max_length=50)

class InstructorProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='instructor_profile')
    specialty = models.CharField(max_length=50)
    bio = models.TextField(max_length=500, blank=True)
    
    class AcademicTitle(models.IntegerChoices):
        HEAD_OF_DEPARTMENT = 1, "Head Of Department"
        PROFESSOR = 2, 'Professor'
        ASSOCIATE_PROFESSOR = 3, 'Associate Professor'
        ASSISTANT_PROFESSOR = 4, 'Assistant Professor'
        POST_DOC = 5, "PostDoc"

    academic_title = models.PositiveSmallIntegerField(choices=AcademicTitle.choices)

class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    enrollment_year = models.PositiveSmallIntegerField()
    gpa = models.FloatField()
    major = models.ForeignKey(Major, null=True, blank=True, on_delete=models.SET_NULL)
    funded = models.BooleanField(default=False)

    class Meta:
        ordering = ['enrollment_year']
