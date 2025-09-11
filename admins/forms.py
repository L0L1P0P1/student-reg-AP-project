from django import forms
from users.models import Student, Instructor, Admin
from courses.models import Unit, Course, Semester, CourseStudentStatus


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
    prerequisites = forms.ModelMultipleChoiceField(
        queryset=Unit.objects.all(),  # pyright: ignore
        required=False,
        widget=forms.SelectMultiple(attrs={'size': 10})
    )

    class Meta:
        model = Unit
        fields = ["name", "description", "unit_size", "majors", "prerequisites"]
        widgets = {
            'majors': forms.SelectMultiple(attrs={'size': 5}),
        }

class AdminUnitModificationForm(forms.ModelForm):
    prerequisites = forms.ModelMultipleChoiceField(
        queryset=Unit.objects.all(), # pyright: ignore
        required=False,
        widget=forms.SelectMultiple(attrs={'size': 10})
        )
    class Meta:
        model = Unit
        fields = ["name", "description", "unit_size", "majors", "prerequisites"]
        widgets = {
            'majors': forms.SelectMultiple(attrs={'size': 5}),
        }

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

class AdminCSSInlineForm(forms.ModelForm):
    class Meta:
        model = CourseStudentStatus
        fields = ['student', 'grade', 'paid', 'passed', 'canceled']
        widgets = {
            'grade': forms.NumberInput(attrs={'step': "0.25"}), # Example for decimal grades
        }

AdminCSSInlineFormSet = forms.inlineformset_factory(
    Course,                    
    CourseStudentStatus,       
    form=AdminCSSInlineForm, 
    extra=0,                   
    can_delete=True,          
)


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

class AdminSemesterCreationForm(forms.ModelForm):
    start_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}), # Explicitly set widget
        help_text="فرمت: YYYY-MM-DD (مثال: 2024-12-31)" # Optional help text
    )
    end_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        help_text="فرمت: YYYY-MM-DD (مثال: 2024-12-31)"
    )
    class Meta:
        model = Semester
        fields = [
            "codename",
            "start_date",
            "end_date",
            "active",
        ]

class AdminSemesterModificationForm(forms.ModelForm):
    start_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}), # Explicitly set widget
        help_text="فرمت: YYYY-MM-DD (مثال: 2024-12-31)" # Optional help text
    )
    end_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        help_text="فرمت: YYYY-MM-DD (مثال: 2024-12-31)"
    )
    class Meta:
        model = Semester
        fields = [
            "codename", # Usually, codename shouldn't be changed, but including it for completeness.
            "start_date",
            "end_date",
            "active",
        ]
