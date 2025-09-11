from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from users.models import Instructor, Student, User, Admin 
from courses.models import Unit, Course, Semester
from .forms import (
    AdminStudentModificationForm,
    AdminUnitCreationForm,
    AdminUnitModificationForm,
    AdminCourseCreationForm,
    AdminCourseModificationForm,
    AdminInstructorModificationForm,
    AdminModificationForm,
    AdminSemesterCreationForm,
    AdminSemesterModificationForm
)
from django.contrib import messages
from functools import wraps


def admin_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect("login")  # only for not-logged-in users
        if not hasattr(request.user, "admin"):
            messages.error(request, "Access denied: Admins only.")
            return redirect("home")  # safe page for logged-in non-admins
        return view_func(request, *args, **kwargs)
    return _wrapped_view

# Student management 
@admin_required
def list_all_students(request):
    query = request.GET.get('q', '')
    first_semester = request.GET.get('year', '')
    funded = request.GET.get('funded', '')
    verified = request.GET.get('verified', '')

    students = Student.objects.all()

    if query:
        students = students.filter(
            Q(username__icontains=query) |  # pyright: ignore
            Q(first_name__icontains=query) | 
            Q(last_name__icontains=query)
        )

    if first_semester:
        students = students.filter(first_semester__codename=first_semester)

    if funded in ["yes", "no"]:
        students = students.filter(funded=(funded == "yes"))

    if verified in ["yes", "no"]:
        students = students.filter(verified=(verified == "yes"))

    return render(request, "admin/students/list.html", {"students": students})

@admin_required
def admin_student_modification(request, pk):
    student = get_object_or_404(Student, pk=pk)

    if request.method == "POST":
        form = AdminStudentModificationForm(request.POST, instance=student)
        if form.is_valid():
            form.save()
            return redirect("list_all_students")
    else:
        form = AdminStudentModificationForm(instance=student)

    return render(request, "admin/students/edit.html", {"form": form, "student": student})


# Unit management 
@admin_required
def admin_list_all_units(request):
    units = Unit.objects.all() # pyright: ignore
    return render(request, "admin/units/list.html", {"units": units})


@admin_required
def admin_unit_creation(request):
    if request.method == "POST":
        form = AdminUnitCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("admin_list_all_units")
    else:
        form = AdminUnitCreationForm()

    return render(request, "admin/units/create.html", {"form": form})


@admin_required
def admin_unit_modification(request, pk):
    unit = get_object_or_404(Unit, pk=pk)

    if request.method == "POST":
        form = AdminUnitModificationForm(request.POST, instance=unit)
        if form.is_valid():
            form.save()
            return redirect("admin_list_all_units")
    else:
        form = AdminUnitModificationForm(instance=unit)

    return render(request, "admin/units/edit.html", {"form": form, "unit": unit})


# Course management 
@admin_required
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

    return render(request, "admin/courses/list.html", {"courses": courses})

@admin_required
def admin_course_creation(request):
    if request.method == "POST":
        form = AdminCourseCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("list_all_courses")
    else:
        form = AdminCourseCreationForm()

    return render(request, "admin/courses/create.html", {"form": form})

@admin_required
def admin_course_modification(request, pk):
    course = get_object_or_404(Course, pk=pk)

    if request.method == "POST":
        form = AdminCourseModificationForm(request.POST, instance=course)
        if form.is_valid():
            form.save()
            return redirect("list_all_courses")
    else:
        form = AdminCourseModificationForm(instance=course)

    return render(request, "admin/courses/edit.html", {"form": form, "course": course})


# Instructor management 
@admin_required
def list_all_instructors(request):
    query = request.GET.get('q', '')
    verified = request.GET.get('verified', '')

    instructors = Instructor.objects.all()
    
    if query:
        instructors = instructors.filter(
            Q(username__icontains=query) |  # pyright: ignore
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query)
        )

    if verified == "yes":
        instructors = instructors.filter(verified=True)
    elif verified == "no":
        instructors = instructors.filter(verified=False)

    return render(request, "admin/instructors/list.html", {"instructors": instructors})


@admin_required
def admin_instructor_modification(request, pk):
    instructor = get_object_or_404(Instructor, pk=pk)

    if request.method == "POST":
        form = AdminInstructorModificationForm(request.POST, instance=instructor)
        if form.is_valid():
            form.save()
            return redirect("list_all_instructors")
    else:
        form = AdminInstructorModificationForm(instance=instructor)

    return render(request, "admin/instructors/edit.html", {"form": form, "instructor": instructor})


# Admin management 
@admin_required
def admin_modification(request, pk):
    admin = get_object_or_404(Admin, pk=pk)

    if request.method == "POST":
        form = AdminModificationForm(request.POST, instance=admin)
        if form.is_valid():
            form.save()
            return redirect("admin_list")
    else:
        form = AdminStudentModificationForm(instance=admin)

    return render(request, "admin/admins/edit.html", {"form": form, "admin": admin})

# Semester management
@admin_required
def admin_list_all_semesters(request):
    semesters = Semester.objects.all().order_by('-codename') # pyright: ignore
    return render(request, "admin/semesters/list.html", {"semesters": semesters})

@admin_required
def admin_semester_creation(request):
    if request.method == "POST":
        form = AdminSemesterCreationForm(request.POST)
        if form.is_valid():
            try:
                form.save()
                return redirect("admin_list_all_semesters")
            except Exception as e:
                pass
    else:
        form = AdminSemesterCreationForm()
    return render(request, "admin/semesters/create.html", {"form": form})

@admin_required
def admin_semester_modification(request, codename):
    semester = get_object_or_404(Semester, codename=codename)
    if request.method == "POST":
        form = AdminSemesterModificationForm(request.POST, instance=semester)
        if form.is_valid():
            try:
                form.save()
                return redirect("admin_list_all_semesters")
            except Exception as e:
                pass
    else:
        form = AdminSemesterModificationForm(instance=semester)
    return render(request, "admin/semesters/edit.html", {"form": form, "semester": semester})
