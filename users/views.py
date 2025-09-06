# users/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import login as auth_login
from django.contrib import messages
from .forms import SignUpForm, StudentSignUpForm
from .models import User, Student, Major, Instructor, Admin

def signup(request):
    """General signup page - user chooses role"""
    return render(request, 'users/signup_choice.html')

def student_signup(request):
    """Student signup form"""
    if request.method == 'POST':
        form = StudentSignUpForm(request.POST)
        if form.is_valid():
            try:
                user = form.save(commit=False)
                user.role = User.Role.STUDENT
                user.save()
                
                student = Student(
                    user_ptr=user,
                    enrollment_year=request.POST.get('enrollment_year', 2024),
                    gpa=0.0,
                    major_id=request.POST.get('major'),
                    funded=request.POST.get('funded', False) == 'on',
                    verified=False
                )
                student.__dict__.update(user.__dict__)
                student.save()
                
                auth_login(request, user)
                messages.success(request, 'ثبت نام شما با موفقیت انجام شد!')
                return redirect('home')
            except Exception as e:
                messages.error(request, f'خطا در ثبت نام: {str(e)}')
    else:
        form = StudentSignUpForm()
    
    majors = Major.objects.all() # pyright: ignore
    
    return render(request, 'users/signup_student.html', {
        'form': form,
        'majors': majors
    })

def instructor_signup(request):
    """Instructor signup form"""
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            try:
                user = form.save(commit=False)
                user.role = User.Role.INSTRUCTOR
                user.save()
                
                instructor = Instructor(
                    user_ptr=user,
                    specialty=request.POST.get('specialty', ''),
                    academic_title=request.POST.get('academic_title', 4)
                )
                instructor.__dict__.update(user.__dict__)
                instructor.save()
                
                auth_login(request, user)
                messages.success(request, 'ثبت نام استاد با موفقیت انجام شد!')
                return redirect('home')
            except Exception as e:
                messages.error(request, f'خطا در ثبت نام: {str(e)}')
    else:
        form = SignUpForm()
    
    return render(request, 'users/signup_instructor.html', {'form': form})

def admin_signup(request):
    """Admin signup form"""
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            try:
                user = form.save(commit=False)
                user.role = User.Role.ADMIN
                user.save()
                
                admin_user = Admin(
                    user_ptr=user,
                    title=request.POST.get('title', '')
                )
                admin_user.__dict__.update(user.__dict__)
                admin_user.save()
                
                auth_login(request, user)
                messages.success(request, 'ثبت نام مدیر با موفقیت انجام شد!')
                return redirect('home')
            except Exception as e:
                messages.error(request, f'خطا در ثبت نام: {str(e)}')
    else:
        form = SignUpForm()
    
    return render(request, 'users/signup_admin.html', {'form': form})
