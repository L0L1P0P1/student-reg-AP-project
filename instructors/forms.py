from django import forms
from courses.models import CourseStudentStatus

class InstructorCSSForm(forms.ModelForm):
    class Meta:
        model = CourseStudentStatus 
        fields = ['score', 'canceled']
