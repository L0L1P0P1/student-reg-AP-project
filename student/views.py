from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Prefetch, Count, Sum
from courses.models import Course, CourseStudentStatus, MajorUnit, Unit, TimeSlots

@login_required(login_url="login")
def available_courses(request):
    student = request.user.student
    major_units = Unit.objects.filter(majors=student.major) # pyright: ignore
    available_courses = Course.objects.filter(unit__in=major_units, semester__active=True) # pyright: ignore
    selected_course_ids = list(CourseStudentStatus.objects.filter( # pyright: ignore 
        student=student,
    ).values_list('course_id', flat=True))

    return render(request, "student/available_courses.html", {
        "available_courses": available_courses,
        "selected_course_ids": selected_course_ids # Pass the list
    })

@login_required(login_url="login")
def other_courses(request):
    student = request.user.student
    taken_courses = CourseStudentStatus.objects.filter(student=student).values_list("course_id", flat=True) # pyright: ignore
    other_courses = Course.objects.filter(   # pyright: ignore
        unit__majors=student.major,
        semester__active=True
    ).exclude(id__in=taken_courses)

    selected_course_ids = list(taken_courses) 
    return render(request, "student/other_courses.html", {
        "other_courses": other_courses,
        "selected_course_ids": selected_course_ids
        })

@login_required(login_url="login")
def select_course(request, course_id):
    student = request.user.student
    course = get_object_or_404(Course, id=course_id)

    # 1. Already registered
    if CourseStudentStatus.objects.filter(student=student, course=course).exists():
        messages.error(request, "You are already registered in this course.")
        return redirect("available_courses")

    # 2. Course full
    current_enrolled = CourseStudentStatus.objects.filter(course=course).count()
    if current_enrolled >= course.slots:
        messages.error(request, "Course is full.")
        return redirect("available_courses")

    # 3. Already passed this course
    if CourseStudentStatus.objects.filter(student=student, course__unit=course.unit, passed=True).exists():
        messages.error(request, "You have already passed this course.")
        return redirect("available_courses")

    # 4. Check for schedule conflicts
    course_times = set(course.time_slot.all())  # Course has ManyToMany with TimeSlots

    for css in CourseStudentStatus.objects.filter(student=student, course__semester__active=True):
        registered_times = set(css.course.time_slot.all())
        if course_times & registered_times:
            messages.error(request, "Schedule conflict with another course.")
            return redirect("student_weekly_program")

    # 5. Register student
    CourseStudentStatus.objects.create(
        student=student,
        course=course,
        paid=False,
        canceled=False
    )

    messages.success(request, f"You have successfully registered for {course.unit.name}!")
    return redirect("available_courses")

## Checking Scores
@login_required(login_url="login")
def check_scores(request):
    student = request.user.student
    
    scores = CourseStudentStatus.objects.filter(student=student).select_related('course__unit', 'course__instructor')

    passed_units_size = CourseStudentStatus.objects.filter(
        student=student,
        passed=True
    ).aggregate(total_size=Sum('course__unit__unit_size'))['total_size'] or 0

    return render(request, 'student/scores.html', {
        'scores': scores,
        'passed_units_size': passed_units_size,
    })

## Canceling Courses     !LATER!
'''
def cancel_course(request, css_id):
    student = request.user.student
    course_status = get_object_or_404(CourseStudentStatus, id=css_id, student=student)

    if course_status.canceled:
        messages.info(request, "This course is already canceled.")
    else:
        course_status.canceled = True
        course_status.save()
        messages.success(request, f"{course_status.course.unit.name} has been canceled.")

    return redirect('student_program')

'''
@login_required(login_url="login")
def unpaid_courses(request):
    """
    Displays a list of courses the logged-in student has enrolled in
    but has not yet paid for.
    """
    student_profile = request.user.student

    # Get CourseStudentStatus records for this student where paid=False
    # and the course is in the active semester.
    unpaid_course_statuses = CourseStudentStatus.objects.filter(
        student=student_profile,
        paid=student_profile.funded,
        course__semester__active=True,
        canceled=False # Exclude canceled enrollments
    ).select_related(
        'course__unit',        # Get unit info (name)
        'course__instructor__user_ptr', # Get instructor info (name)
        'course__semester'     # Get semester info
    )

    return render(request, 'student/unpaid_courses.html', {
        'student': student_profile,
        'unpaid_course_statuses': unpaid_course_statuses,
    })

## Weekly Program
@login_required(login_url="login")
def student_weekly_program(request):

    student_profile = request.user.student

    enrolled_courses = CourseStudentStatus.objects.filter(
        student=student_profile,
        course__semester__active=True, # Get courses from the active semester
        canceled=False
    ).select_related(
        'course__unit',
        'course__instructor__user_ptr'
    ).prefetch_related(
        Prefetch('course__time_slot', queryset=TimeSlots.objects.all())
    )

    return render(request, 'student/weekly_program.html', {
        'student': student_profile,
        'enrolled_courses': enrolled_courses,
    })

## Paying for Courses
@login_required(login_url="login")
def pay_course(request, css_id):
    student = request.user.student
    course_status = get_object_or_404(CourseStudentStatus, id=css_id, student=student)

    if course_status.paid:
        messages.info(request, "You have already paid for this course.")
    else:
        course_status.paid = True
        course_status.save()
        messages.success(request, f"Payment successful for {course_status.course.unit.name}.")

    return redirect('unpaid_courses')  # or program page
