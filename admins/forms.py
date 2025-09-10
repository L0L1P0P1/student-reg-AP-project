from django import forms
from users.models import Student, Instructor, Admin
from courses.models import Unit, Course


class AdminStudentModificationForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = [
            "username",
            "first_name",
            "last_name",
            "email",
            "phone_number",
            "first_semester",
            "gpa",
            "major",
            "funded",
            "verified",
        ]

class AdminUnitCreationForm(forms.ModelForm):
    class Meta:
        model = Unit
        fields = [
            "name",
            "description",
            "unit_size",
            "majors",
        ]

class AdminUnitModificationForm(forms.ModelForm):
    class Meta:
        model = Unit
        fields = [
            "name",
            "description",
            "unit_size",
            "majors",
        ]

class AdminCourseCreationForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = [
            "unit",
            "instructor",
            "semester",
            "slots",
            "time_slot",
            "price",
        ]

class AdminCourseModificationForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = [
            "unit",
            "instructor",
            "semester",
            "slots",
            "time_slot",
            "price",
        ]

class AdminInstructorModificationForm(forms.ModelForm):
    class Meta:
        model = Instructor
        fields = [
            "username",
            "first_name",
            "last_name",
            "email",
            "phone_number",
            "specialty",
            "bio",
            "academic_title",
            "verified",
        ]

class AdminModificationForm(forms.ModelForm):
    class Meta:
        model = Admin
        fields = [
            "username",
            "first_name",
            "last_name",
            "email",
            "phone_number",
            "title",
        ]
