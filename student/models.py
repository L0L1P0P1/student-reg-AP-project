from django.db import models
from django.shortcuts import render
from courses.models import Course, CourseStudentStatus

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

