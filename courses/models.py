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

    prerequisites = models.ManyToManyField(
            'self',
            symmetrical=False,
            blank=True,
            related_name='is_prerequisite_for'
            )

    def __str__(self): # pyright: ignore
        return self.name

    def get_prerequisites_display(self):
        prereq = self.prerequisites.all()  # pyright: ignore
        if prereq:
            return '، '.join([p.name for p in prereq]) 
        else:
            return "بدون پیش نیاز"

class Semester(models.Model):
    codename = models.PositiveSmallIntegerField(primary_key=True)
    start_date = models.DateField()
    end_date = models.DateField()
    active = models.BooleanField()

    def save(self, *args, **kwargs):
        if self.active:  
            Semester.objects.exclude(pk=self.pk).update(active=False)  # pyright: ignore
        super().save(*args, **kwargs)

    def __str__(self):
        return str(self.codename)

class MajorUnit(models.Model):
    major = models.ForeignKey('users.Major', on_delete=models.CASCADE)
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE)
    class UnitMajorState(models.IntegerChoices):
        SPECIALITY = 1, "Speciality Units"
        PRIMARY = 2, 'Primary Units'
        OPTIONAL = 3, 'Optional Units'
        GENERAL = 4, 'General Units'

    state = models.PositiveSmallIntegerField(choices=UnitMajorState.choices, null=True) 

class TimeSlots(models.Model):
    id = models.PositiveSmallIntegerField(primary_key=True)
    time = models.CharField(255)

    def __str__(self):
        return str(self.time)

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
    grade = models.FloatField(null=True, blank=True)
    paid = models.BooleanField()
    passed = models.BooleanField(blank=True, null=True)  # pyright: ignore
    canceled = models.BooleanField(default=False) # pyright: ignore

    def save(self, *args, **kwargs):
        if self.grade is not None:
            if self.grade > 20:
                self.grade = 20
            if self.grade >= 10:
                self.passed = True 
            else:
                self.passed=False
        super().save(*args, **kwargs)

        self.student.calculate_gpa()  # pyright: ignore

