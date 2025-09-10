from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from users.models import Instructor, Student, User, Admin 
from courses.models import Unit, Course, CourseStudentStatus, Semester 

# student management 
@login_required(login_url="/login/")
def list_all_students(request):
    query = request.GET.get('q', '')
    enrollment_year = request.GET.get('year', '')
    funded = request.GET.get('funded', '')
    verified = request.GET.get('verified', '')

    students = Student.objects.all()

    if query:
        students = students.filter(
            Q(username__icontains=query) | #pyright: ignore
            Q(fist_name__icontains=query) |
            Q(last_name__icontains=query)
            )

    if enrollment_year:
        students = students.filter(enrollment_year=enrollment_year)

    if funded:
        students = students.filter(funded=funded)

    if verified:
        students = students.filter(verified=verified)

    # return render

@login_required(login_url="/login/")
def admin_student_modification(request, pk):
    student = get_object_or_404(Student, pk=pk)

    # needs a form to do stuff

#course and unit management
@login_required(login_url="/login/")
def list_all_units(request):
    pass

@login_required(login_url="/login/")
def unit_creation(request):
    #needs a form 
    pass

@login_required(login_url="/login/")
def unit_modification(request, pk):
    #needs a form
    pass

@login_required(login_url="/login/")
def list_all_courses(request):
    query = request.GET.get('q', '')
    active = request.GET.get('active', '')
    semester = request.GET.get('semester', '')
    
    courses = Course.objects.all() # pyright: ignore

    if query:
        courses = courses.filter(
                Q(unit__name__icontains=query) | # pyright: ignore
                Q(instructor__first_name__icontains=query) |
                Q(instructor__last_name__icontains=query) 
            )

    if active == "yes":
        courses = courses.filter(semester__active=True)
    elif active == "no":
        courses = courses.filter(semester__active=False)

    if semester:
        courses = courses.filter(semester__codename=semester)

@login_required(login_url="/login/")
def course_creation(request):
    #needs a form 
    pass

@login_required(login_url="/login/")
def course_modification(request, pk):
    # needs a form
    pass

#instructor management
@login_required(login_url="/login/")
def list_all_instructors(request):
    query = request.GET.get('q', '')
    verified = request.GET.get('verified', '')

    instructors = Instructor.objects.all()
    
    if query:
        instructors = instructors.filter(
                Q(username__icontaints = query) |  # pyright: ignore
                Q(first_name__icontaints = query) |
                Q(last_name__icontaints = query)
            )

    if verified == "yes":
        instructors = instructors.filter(verified=True)
    elif verified == "no":
        instructors = instructors.filter(verified=False)


@login_required(login_url="/login/")
def admin_instructor_modification(request, pk):
    #needs a form
    pass

#admin management
@login_required(login_url="/login/")
def admin_modification(request, pk):
    # needs a form
    pass
