from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from django.contrib import messages
from django.http import HttpResponse, HttpResponseForbidden 
from django.forms import modelformset_factory
from users.models import User
from courses.models import Course, CourseStudentStatus, CourseAttachment
from .forms import InstructorCSSForm


@login_required(login_url="login")
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

@login_required(login_url='login')
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

@login_required(login_url="login")
def instructor_courses_attachments(request):
    """
    Displays a list of courses taught by the logged-in instructor,
    allowing them to manage attachments for each.
    """
    user = request.user
    if user.role != User.Role.INSTRUCTOR:
        return HttpResponseForbidden("You do not have permission to access this page.")

    courses = Course.objects.filter(
        instructor=user,
        semester__active=True # pyright: ignore
    ).select_related('unit', 'semester') # Optimize queries

    return render(request, 'instructors/instructor_courses_attachments.html', {'courses': courses})


@login_required(login_url="login")
def instructor_create_attachment(request, course_pk):
    """
    Handles creating a new attachment for a specific course.
    """
    user = request.user
    if user.role != User.Role.INSTRUCTOR:
        return HttpResponseForbidden("You do not have permission to access this page.")

    course = get_object_or_404(
        Course,
        pk=course_pk,
        instructor=user 
    )

    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        description = request.POST.get('description', '').strip()
        text_content = request.POST.get('text_content', '').strip()
        uploaded_file = request.FILES.get('file')

        if not name:
            messages.error(request, "Attachment name is required.")
            return render(request, 'instructors/instructor_create_attachment.html', {
                'course': course,
                'submitted_name': name,
                'submitted_description': description,
                'submitted_text_content': text_content,
            })

        if not uploaded_file and not text_content:
            messages.error(request, "You must provide either a file or text content.")
            return render(request, 'instructors/instructor_create_attachment.html', {
                'course': course,
                'submitted_name': name,
                'submitted_description': description,
                'submitted_text_content': text_content,
            })

        try:
            attachment = CourseAttachment.objects.create(
                course=course,
                name=name,
                description=description,
                text_content=text_content if text_content else None,
                file=uploaded_file if uploaded_file else None,
            )
            messages.success(request, f"Attachment '{attachment.name}' created successfully for '{course.unit.name}'.")
            return redirect('instructor_courses_attachments') # Or a view showing attachments for this specific course
        except Exception as e:
            messages.error(request, f"An error occurred while creating the attachment: {e}")
            return render(request, 'instructors/instructor_create_attachment.html', {
                'course': course,
                'submitted_name': name,
                'submitted_description': description,
                'submitted_text_content': text_content,
            })

    else: # GET request - display the form
        return render(request, 'instructors/instructor_create_attachment.html', {'course': course})

@login_required(login_url="login")
def instructor_view_attachments(request, course_pk):
    """
    Displays a list of attachments for a specific course.
    Only accessible by the course instructor.
    """
    user = request.user
    if user.role != User.Role.INSTRUCTOR:
        return HttpResponseForbidden("You do not have permission to access this page.")

    # Get the course, ensuring it belongs to the logged-in instructor
    course = get_object_or_404(
        Course,
        pk=course_pk,
        instructor=user # Security check: instructor can only see their own courses
    )

    # Get all attachments for this course, ordered by upload date (newest first)
    attachments = course.attachments.all() # Uses the related_name='attachments' from the ForeignKey

    return render(request, 'instructors/instructor_view_attachments.html', {
        'course': course,
        'attachments': attachments
    })
