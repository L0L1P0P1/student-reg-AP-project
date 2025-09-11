from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Prefetch, Count, Sum
from courses.models import Course, CourseStudentStatus, MajorUnit, Unit, TimeSlots
from django.core.exceptions import ObjectDoesNotExist

@login_required(login_url="login")
def available_courses(request):
    student = request.user.student
    major_units = Unit.objects.filter(majors=student.major) # pyright: ignore
    available_courses = Course.objects.filter(unit__in=major_units, semester__active=True) # pyright: ignore
    selected_course_ids = list(CourseStudentStatus.objects.filter( # pyright: ignore
        student=student,
    ).values_list('course_id', flat=True))
    passed_course_statuses = CourseStudentStatus.objects.filter(
        student=student,
        passed=True # pyright: ignore
    ).select_related('course__unit')

    passed_unit_ids = set()
    for status in passed_course_statuses:
        if status.course and status.course.unit:
             passed_unit_ids.add(status.course.unit.id)

    eligible_courses = []
    for course in available_courses:
        unit = course.unit
        if unit:
            prereq_unit_ids = set(unit.prerequisites.values_list('id', flat=True)) # pyright: ignore
            if prereq_unit_ids.issubset(passed_unit_ids):
                eligible_courses.append(course)

    return render(request, "student/available_courses.html", {
        "available_courses": eligible_courses, # Pass only eligible courses
        "selected_course_ids": selected_course_ids
    })

@login_required(login_url="login")
def other_courses(request):
    student = request.user.student
    taken_courses = CourseStudentStatus.objects.filter(student=student).values_list("course_id", flat=True) # pyright: ignore
    other_courses_queryset = Course.objects.filter( # pyright: ignore
        unit__majors=student.major,
        semester__active=True
    ).exclude(id__in=taken_courses)

    passed_course_statuses = CourseStudentStatus.objects.filter(   # pyright: ignore
        student=student,
        passed=True # pyright: ignore
    ).select_related('course__unit')

    passed_unit_ids = set()
    for status in passed_course_statuses:
        if status.course and status.course.unit:
             passed_unit_ids.add(status.course.unit.id)

    eligible_other_courses = []
    for course in other_courses_queryset:
        unit = course.unit
        if unit:
            prereq_unit_ids = set(unit.prerequisites.values_list('id', flat=True)) # pyright: ignore
            if prereq_unit_ids.issubset(passed_unit_ids):
                eligible_other_courses.append(course)

    selected_course_ids = list(taken_courses) 

    return render(request, "student/other_courses.html", {
        "other_courses": eligible_other_courses, # Pass only eligible courses
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


@login_required(login_url="login")
def payment_panel(request, css_id=None):
    try:
        student = request.user.student
    except ObjectDoesNotExist:
        messages.error(request, "⚠️ شما به عنوان دانشجو ثبت‌نام نشده‌اید. لطفاً ابتدا پروفایل دانشجویی خود را تکمیل کنید.")
        return redirect("hub")
    # --- Handle a checkout (if css_id provided) ---
    if css_id:
        course_status = get_object_or_404(CourseStudentStatus, id=css_id, student=student)
        if course_status.paid:
            messages.info(request, "You have already paid for this course.")
        else:
            # Simulate payment success (درگاه پرداخت)
            course_status.paid = True
            course_status.save()
            messages.success(request, f"پرداخت موفق برای {course_status.course.unit.name}.")
        return redirect("payment_panel")  # refresh the page

    # --- Prepare lists ---
    failed_transactions = CourseStudentStatus.objects.filter(
        student=student,
        paid=False,
        course__semester__active=True,
        canceled=False
    ).select_related("course__unit", "course__instructor__user_ptr", "course__semester")

    succeeded_transactions = CourseStudentStatus.objects.filter(
        student=student,
        paid=True,
        course__semester__active=True,
        canceled=False
    ).select_related("course__unit", "course__instructor__user_ptr", "course__semester")

    return render(request, "student/payment_panel.html", {
        "student": student,
        "failed_transactions": failed_transactions,
        "succeeded_transactions": succeeded_transactions,
    })



from django.utils import timezone

@login_required(login_url="login")
def payment_gateway(request, css_id):
    student = request.user.student
    course_status = get_object_or_404(CourseStudentStatus, id=css_id, student=student)

    if course_status.paid:
        messages.info(request, "این دوره قبلاً پرداخت شده است.")
        return redirect('payment_panel')

    course = course_status.course

    if request.method == "POST":
        payment_result = request.POST.get("payment_result")

        if payment_result == "success":
            enrolled_courses = CourseStudentStatus.objects.filter(
                student=student,
                course__semester__active=True,
                paid=True,
                canceled=False
            ).exclude(course=course).select_related('course')

            has_conflict = False
            current_times = set(course.time_slot.all())

            for css in enrolled_courses:
                other_times = set(css.course.time_slot.all())
                if current_times & other_times: 
                    has_conflict = True
                    break

            if has_conflict:
                messages.error(request, "❌ تداخل زمانی با یک یا چند درس ثبت‌نام شده دارید.")
                return redirect('payment_gateway', css_id=css_id)

    
            course_status.paid = True
            course_status.registered_at = timezone.now()
            course_status.save()

            messages.success(request, f"✅ پرداخت شما برای «{course.unit.name}» با موفقیت انجام شد.")
            return redirect('payment_panel')

        elif payment_result == "failure":
            messages.error(request, "❌ پرداخت ناموفق بود. لطفاً دوباره تلاش کنید.")
            return redirect('payment_gateway', css_id=css_id)

    return render(request, 'student/payment_gateway.html', {
        'course': course,
        'css_id': css_id,
    })
