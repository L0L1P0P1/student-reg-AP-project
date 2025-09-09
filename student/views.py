from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from courses.models import Course, CourseStudentStatus, TimeSlots, Semester



def available_courses(request):
    student = request.user.student 
    
    available_courses = Course.objects.filter(
        unit__majors=student.major,
        active=True
    )

    return render(request, "student/available_courses.html", {
        "available_courses": available_courses
    })


def other_courses(request):
    student = request.user.student

    # IDs of courses the student has already taken
    taken_courses = CourseStudentStatus.objects.filter(
        student=student
    ).values_list("course_id", flat=True)

    # Courses in the student's major, excluding taken ones
    other_courses = Course.objects.filter(
        unit__majors=student.major
    ).exclude(id__in=taken_courses)

    return render(request, "student/other_courses.html", {
        "other_courses": other_courses
    })


def select_course(request, course_id):
    student = request.user.student  # assumes OneToOneField from User → Student
    course = get_object_or_404(Course, id=course_id)

    #  Check if already registered

    if CourseStudentStatus.objects.filter(student=student, course=course).exists():
        messages.error(request, "You are already registered in this course.")
        return redirect("available_courses")

     
    # Check if course is full
   
    current_enrolled = CourseStudentStatus.objects.filter(course=course).count()
    if current_enrolled >= course.slots:
        messages.error(request, "Course is full.")
        return redirect("available_courses")

     
    # Check if student already passed this course
     
    if CourseStudentStatus.objects.filter(student=student, course=course, passed=True).exists():
        messages.error(request, "You have already passed this course.")
        return redirect("available_courses")

     
    # Check for schedule conflicts
     
    # Get timeslots of the course student wants to register
    course_times = set(course.coursestudentstatus_set.first().time.all()) if course.coursestudentstatus_set.exists() else set(course.time.all())
    
    # Check all registered courses of the student
    for css in CourseStudentStatus.objects.filter(student=student):
        registered_times = set(css.time.all())
        if course_times & registered_times:
            messages.error(request, "Schedule conflict detected with another course.")
            return redirect("available_courses")

     
    #  Register student
     
    new_status = CourseStudentStatus.objects.create(
        student=student,
        course=course,
        grade=0,
        price=course.unit.unit_size * 1000,  # example calculation
        paid=False,
        passed=False
    )
    
    # If the course has timeslots, assign them (optional)
    if hasattr(course, "time"):
        new_status.time.set(course.time.all())
    
    messages.success(request, f"You have successfully registered for {course.unit.name}!")
    return redirect("student_program")

## Third task: Checking Semester's Class Program

def student_program(request):
    student = request.user.student
    current_semester = Semester.objects.filter(active=True).first()

    if not current_semester:
        messages.warning(request, "No active semester right now.")
        return redirect("available_courses")

    enrolled = CourseStudentStatus.objects.filter(
        student=student,
        course__semester=current_semester,
        canceled=False
    ).select_related("course__unit", "course__instructor").prefetch_related("course__time_slot")

    return render(request, "student/program.html", {
        "semester": current_semester,
        "enrolled": enrolled
    })
