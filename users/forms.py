from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Major

class SignUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    email = forms.EmailField(max_length=254, required=True)
    phone_number = forms.CharField(max_length=15, required=False)
    national_id = forms.CharField(max_length=20, required=True)
    
    class Meta:  # pyright: ignore
        model = User
        fields = ('first_name', 'last_name', 'email', 'phone_number', 'national_id', 'password1', 'password2')

class StudentSignUpForm(SignUpForm):
    major = forms.ModelChoiceField(queryset=Major.objects.all(), required=True)  # pyright: ignore
    funded = forms.BooleanField(required=False, initial=False)
    
    class Meta(SignUpForm.Meta):
        fields = SignUpForm.Meta.fields + ('major', 'funded')
