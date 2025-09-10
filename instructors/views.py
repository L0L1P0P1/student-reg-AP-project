from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from django.http import HttpResponse
from users.models import Instructor, Student, User
from courses.models import Unit, Course, CourseStudentStatus 

@login_required(login_url="/login/")
def instructor_courses(request):
    user = request.user

    if user.role != User.Role.INSTRUCTOR:
        return HttpResponse('401 Unauthorized: You are likely not permitted to see this page with your current authorization.', status=401) # pyright: ignore 

    query = request.GET.get('q', '')
    active = request.GET.get('active', '')
    
    current_courses = Course.objects.filter(instructor=user)  # pyright: ignore

    # for now no id matching
    if query:
        current_courses = current_courses.filter(
                # Q(course__id__icontains=query) |
                Q(unit__name__icontains=query)      
            )
    
    if active=="yes":
        current_courses = current_courses.filter(semester__active=True)
    elif active=="no":
        current_courses = current_courses.filter(semester__active=False)
    
    # render template

@login_required(login_url='/login/')
def course_management(request, pk):
    course = get_object_or_404(Course, pk=pk)
    students = CourseStudentStatus.objects.filter(course=course).select_related("student")

    # need to create someshi like ModelFormSet 
    # for now
    pass 


