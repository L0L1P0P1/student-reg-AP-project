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
    paid = models.BooleanField(blank=True)
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

class CourseAttachment(models.Model):

    ATTACHMENT_TYPE_CHOICES = [
            ('file', 'File'),
            ('text', 'Text'),
            ('both', 'File and Text')
            ]

    course = models.ForeignKey(
            'courses.Course',
            on_delete=models.CASCADE,
            related_name='attachments'
            )
    name = models.CharField(
            max_length=255,
            help_text="",
            )
    file = models.FileField(
        upload_to='course_attachments/%Y/%m/%d/', 
        blank=True, 
        null=True,
        help_text="Upload a file (PDF, DOC, etc.)"
    )
    text_content = models.TextField(
        blank=True, 
        null=True,
        help_text="Enter text content directly (e.g., announcements, instructions)"
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)
    description = models.TextField(
        blank=True, 
        help_text="Optional description of the attachment's content."
    )
    class Meta:
        ordering = ['-uploaded_at'] # Show newest attachments first
        verbose_name = "Course Attachment"
        verbose_name_plural = "Course Attachments"

    def __str__(self):
        content_type = "File" if self.file else "Text" if self.text_content else "Empty"
        return f"{self.name} ({content_type} - {self.course.unit.name if self.course and self.course.unit else 'Unknown Course'})"  # pyright: ignore

    def get_file_name(self):
        """Helper to get just the filename from the full path."""
        if self.file:
            return self.file.name.split('/')[-1]  # pyright: ignore
        return None

    def get_primary_content_type(self):
        """
        Determines the primary content type based on which field has data.
        Prioritizes 'file' if both are present.
        """
        if self.file:
            return 'file'
        elif self.text_content:
            return 'text'
        else:
            return 'none'
