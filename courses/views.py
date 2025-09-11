from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, Http404, HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from users.models import User
from .models import CourseAttachment
import mimetypes
import os


@login_required
def view_attachment(request, attachment_id):
    attachment = get_object_or_404(CourseAttachment, id=attachment_id)

    user = request.user
    if user.role not in [User.Role.STUDENT, User.Role.ADMIN, User.Role.INSTRUCTOR]:
         return HttpResponseForbidden("You do not have permission to view this attachment.")

    context = {
        'attachment': attachment,
        'file_content': None,  
        'is_text_file': False, 
        'file_display_error': None
    }

    content_type = attachment.get_primary_content_type()

    if content_type == 'text':
        context['file_content'] = attachment.text_content
        context['is_text_file'] = True 

    elif content_type == 'file' and attachment.file:
        file_path = attachment.file.path

        mime_type, _ = mimetypes.guess_type(file_path)
        
        if mime_type and mime_type.startswith('text/'):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read(10000)
                    context['file_content'] = content
                    context['is_text_file'] = True
                    if len(content) >= 10000:
                         context['file_truncated'] = True
                    else:
                         context['file_truncated'] = False
            except UnicodeDecodeError:
                try:
                    with open(file_path, 'r', encoding='latin-1') as f:
                        content = f.read(10000)
                        context['file_content'] = content
                        context['is_text_file'] = True
                        context['file_encoding'] = 'latin-1' 
                        if len(content) >= 10000:
                             context['file_truncated'] = True
                        else:
                             context['file_truncated'] = False
                except Exception as e:
                    context['file_display_error'] = f"Could not decode file content: {e}"
            except Exception as e:
                context['file_display_error'] = f"Error reading file: {e}"
        else:
            context['is_text_file'] = False
            context['file_mime_type'] = mime_type

    else:
        context['file_display_error'] = "This attachment has no content."

    return render(request, 'courses/view_attachment.html', context)
