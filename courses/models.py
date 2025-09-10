from django.db import models
from users.models import Instructor, Student

class Unit(models.Model):
    name = models.CharField(max_length=50)
    description = models.CharField(255, blank=True)
    unit_size = models.PositiveSmallIntegerField()

    majors = models.ManyToManyField(
        'users.Major', 
        through='MajorUnit',
        related_name='units'
    )

class Semester(models.Model):
    code_name = models.PositiveSmallIntegerField(primary_key=True)
    start_date = models.DateField()
    end_date = models.DateField()
    active = models.BooleanField()

    def save(self, *args, **kwargs):
        if self.active:  
            Semester.objects.exclude(pk=self.pk).update(active=False)  # pyright: ignore
        super().save(*args, **kwargs)

class MajorUnit(models.Model):
    major = models.ForeignKey('users.Major', on_delete=models.CASCADE)
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE)
    class UnitMajorState(models.IntegerChoices):
        SPECIALITY = 1, "Speciality Units"
        PRIMARY = 2, 'Primary Units'
        OPTIONAL = 3, 'Optional Units'
        GENERAL = 4, 'General Units'

    state = models.PositiveSmallIntegerField(choices=UnitMajorState.choices) 

class TimeSlots(models.Model):
    id = models.PositiveSmallIntegerField(primary_key=True)
    time = models.CharField(255)

class Course(models.Model):
    unit = models.ForeignKey(Unit, null=True, on_delete=models.SET_NULL) 
    instructor = models.ForeignKey(Instructor, null=True, on_delete=models.SET_NULL)
    semester = models.ForeignKey(Semester, on_delete=models.SET_NULL, null=True)
    slots = models.PositiveSmallIntegerField() 
    time_slot = models.ManyToManyField(TimeSlots)
    price = models.PositiveIntegerField()

class CourseStudentStatus(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    grade = models.FloatField()
    paid = models.BooleanField()
    passed = models.BooleanField(default=False)
    canceled = models.BooleanField(default=False)
