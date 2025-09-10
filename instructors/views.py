from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from django.http import HttpResponse
from django.forms import modelformset_factory
from users.models import User
from courses.models import Course, CourseStudentStatus 
from .forms import InstructorCSSForm


@login_required(login_url="/login/")
def instructor_courses(request):
    user = request.user

    if user.role != User.Role.INSTRUCTOR:
        return HttpResponse('401 Unauthorized: You are likely not permitted to see this page with your current authorization.', status=401) # pyright: ignore

    query = request.GET.get('q', '')
    active = request.GET.get('active', '')
    
    current_courses = Course.objects.filter(instructor=user) # pyright: ignore

    if query:
        current_courses = current_courses.filter(
            Q(unit__name__icontains=query)      
        )
    
    if active == "yes":
        current_courses = current_courses.filter(semester__active=True)
    elif active == "no":
        current_courses = current_courses.filter(semester__active=False)
    
    return render(request, 'instructors/instructor_courses.html', {
        'current_courses': current_courses
    })

@login_required(login_url='/login/')
def instructor_course_management(request, pk):
    course = get_object_or_404(Course, pk=pk, instructor=request.user)
    students = CourseStudentStatus.objects.filter(course=course).select_related("student") # pyright: ignore

    CourseStudentStatusFormSet = modelformset_factory(
        CourseStudentStatus,
        form=InstructorCSSForm,
        extra=0
    )

    if request.method == 'POST':
        formset = CourseStudentStatusFormSet(request.POST, queryset=students)
        if formset.is_valid():
            formset.save()
            return redirect('instructor_course_management', pk=course.pk)
    else:
        formset = CourseStudentStatusFormSet(queryset=students)

    return render(request, 'instructors/instructors_course_management.html', {
        'course': course,
        'formset': formset,
        'students': students
    })
