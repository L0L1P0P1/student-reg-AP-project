from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from users.models import Instructor, Student, User
from courses.models import Unit, Course, CourseStudentStatus 

@login_required(login_url="/login/")
def instructor_classes(request):
    user = request.user

    if user.role != User.role.INSTRUCTOR:
        return HttpResponse('401 Unauthorized: You are likely not permitted to see this page with your current authorization.', status=401) # pyright: ignore 
    
    current_classes = Course.objects.filter(semester__active=True, instructor=user) # I'll add a logic in the template to filter by active/not active

    return HttpResponse(current_classes[0], status=200)

@login_required(login_url='/login/')
def class_management(request, pk):
    course = get_object_or_404(Course, pk=pk)
    students = CourseStudentStatus.objects.filter(course=course).select_related("student")
    # need to create someshi like ModelFormSet 
    # for now
    pass 


