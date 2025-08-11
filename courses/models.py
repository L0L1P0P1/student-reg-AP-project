from django.db import models
from users.models import Major, Instructor, Student

class Unit(models.Model):
    name = models.CharField(max_size=50)
    description = models.CharField(255, blank=True)
    unit_size = models.PositiveSmallIntegerField()

    majors = models.ManyToManyField(
        'Major', 
        through='MajorUnit',
        related_name='units'
    )

class MajorUnit(models.Model):
    major = models.ForeignKey(Major, on_delete=models.CASCADE)
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE)
    class UnitMajorState(models.IntegerChoices):
        SPECIALITY = 1, "Speciality Units"
        PRIMARY = 2, 'Primary Units'
        OPTIONAL = 3, 'Optional Units'
        GENERAL = 4, 'General Units'

    state = models.PositiveSmallIntegerField(choices=UnitMajorState.choices) 

class Course(models.Model):
    unit = models.ForeignKey(Unit, on_delete=models.SET_NULL) 
    instructor = models.ForeignKey(Instructor, on_delete=models.SET_NULL)
    term = models.PositiveSmallIntegerField()
    slots = models.PositiveSmallIntegerField() 
    active = models.BooleanField()

class TimeSlots(models.Model):
    time = models.CharField(255)

class CourseStudentStatus(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    grade = models.FloatField()
    price = models.PositiveIntegerField()
    paid = models.BooleanField()
    passed = models.BooleanField()
    time = models.ManyToManyField(TimeSlots)
