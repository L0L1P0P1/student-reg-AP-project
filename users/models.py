from django.contrib.auth.models import AbstractUser
from django.db import models
from datetime import datetime

class Major(models.Model):
    name = models.CharField(max_length=255)
    codename = models.CharField(max_length=5, null=True)
    
    def __str__(self): # type: ignore 
        return self.name

class User(AbstractUser):
    national_id = models.CharField(max_length=20, unique=True, null=False)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    email = models.EmailField(max_length=254, unique=True)
    
    class Role(models.IntegerChoices):
        ADMIN = 1, 'Admin'
        INSTRUCTOR = 2, 'Instructor'
        STUDENT = 3, 'Student'

    role = models.PositiveSmallIntegerField(choices=Role.choices, default=Role.STUDENT) # type: ignore

    USERNAME_FIELD = 'national_id'
    REQUIRED_FIELDS = ['username']

    def save(self, *args, **kwargs):
        if not self.username:
            self.username = self.national_id
        super().save(*args, **kwargs)

class Admin(User):
    title = models.CharField(max_length=50)
    
    class Meta: # type: ignore 
        verbose_name = "Admin"
        verbose_name_plural = "Admins"

    def save(self, *args, **kwargs):
        self.role = User.Role.ADMIN
        super().save(*args, **kwargs)

class Instructor(User):
    specialty = models.CharField(max_length=50)
    bio = models.TextField(max_length=500, blank=True)
    verified = models.BooleanField(default=False)  # pyright: ignore
    
    class AcademicTitle(models.IntegerChoices):
        HEAD_OF_DEPARTMENT = 1, "Head Of Department"
        PROFESSOR = 2, 'Professor'
        ASSOCIATE_PROFESSOR = 3, 'Associate Professor'
        ASSISTANT_PROFESSOR = 4, 'Assistant Professor'
        POST_DOC = 5, "PostDoc"

    academic_title = models.PositiveSmallIntegerField(choices=AcademicTitle.choices)
    
    class Meta: # type: ignore 
        verbose_name = "Instructor"
        verbose_name_plural = "Instructors"

    def save(self, *args, **kwargs):
        self.role = User.Role.INSTRUCTOR
        super().save(*args, **kwargs)

class Student(User):
    first_semester = models.ForeignKey("courses.Semester", on_delete=models.SET_NULL, null=True)
    student_id = models.CharField(max_length=15, unique=True, blank=True)
    gpa = models.FloatField()
    major = models.ForeignKey(Major, null=True, blank=True, on_delete=models.SET_NULL)
    funded = models.BooleanField(default=False) # type: ignore
    verified = models.BooleanField(default=False) # type: ignore
    
    class Meta: # type: ignore 
        verbose_name = "Student"
        verbose_name_plural = "Students"
    
    def generate_student_id(self):
        if self.major:
            major_code = self.major.codename  # pyright: ignore

        year = str(self.first_semester.codename)[-3:-1] # pyright: ignore
        
        prefix = f"{major_code}{year}" # pyright: ignore
        last_student = Student.objects.filter(
            student_id__startswith=prefix
        ).order_by('-student_id').first()
        
        if last_student:
            try:
                last_sequence = int(last_student.student_id[len(prefix):])
                sequence = last_sequence + 1
            except (ValueError, IndexError):
                sequence = 1
        else:
            sequence = 1
        sequence_str = f"{sequence:04d}"
        student_id = f"{prefix}{sequence_str}"
        
        return student_id

    def calculate_gpa(self):
        try:
            from courses.models import CourseStudentStatus
            passed_courses_grades = CourseStudentStatus.objects.filter(         # pyright: ignore
                student=self,
                passed=True,
                grade__isnull=False,
                canceled=False
            ).select_related('course__unit')

            total_weighted_points = 0
            total_units_attempted = 0

            for status in passed_courses_grades:
                unit_size = status.course.unit.unit_size if status.course and status.course.unit else 0
                if unit_size > 0 and status.grade is not None:
                    total_weighted_points += status.grade * unit_size
                    total_units_attempted += unit_size

            if total_units_attempted > 0:
                new_gpa = total_weighted_points / total_units_attempted
            else:
                new_gpa = 0.0

            if self.gpa != new_gpa:
                self.gpa = new_gpa
                self.save(update_fields=['gpa'])

        except Exception as e:
            print(f"Error calculating GPA for student {self.student_id if hasattr(self, 'student_id') else 'ID_NA'}: {e}")

    def save(self, *args, **kwargs):
        self.role = User.Role.STUDENT
        if not self.first_semester:
            from courses.models import Semester
            self.first_semester = Semester.objects.filter(active=True).first() # pyright: ignore
        if not self.student_id:
            self.student_id = self.generate_student_id()
        super().save(*args, **kwargs)
