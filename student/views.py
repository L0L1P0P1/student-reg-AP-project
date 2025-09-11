from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.db.models import Prefetch
from courses.models import Course, CourseStudentStatus, MajorUnit, Unit, TimeSlots


def available_courses(request):
    student = request.user.student  

    major_units = Unit.objects.filter(majors=student.major) # pyright: ignore

    # Only fetch courses from active semester(s)
    available_courses = Course.objects.filter(
        unit__in=major_units,
        semester__active=True
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

    # Courses in student's major but not yet taken
    other_courses = Course.objects.filter(
        unit__majors=student.major,
        semester__active=True
    ).exclude(id__in=taken_courses)

    return render(request, "student/other_courses.html", {
        "other_courses": other_courses
    })


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
            return redirect("available_courses")

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
def check_scores(request):
    student = request.user.student
    scores = CourseStudentStatus.objects.filter(student=student).select_related('course__unit', 'course__instructor')

    return render(request, 'student/scores.html', {
        'scores': scores
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
def pay_course(request, css_id):
    student = request.user.student
    course_status = get_object_or_404(CourseStudentStatus, id=css_id, student=student)

    if course_status.paid:
        messages.info(request, "You have already paid for this course.")
    else:
        course_status.paid = True
        course_status.save()
        messages.success(request, f"Payment successful for {course_status.course.unit.name}.")

    return redirect('available_courses')  # or program page
