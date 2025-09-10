from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import HttpResponse
from .users import Instructor, Student, User

@login_required(login_url="/login/")
def active_classes(request):
    user = request.user

    if user.role != User.role.INSTRUCTOR:
        return HttpResponse('401 Unauthorized: You are likely not permitted to see this page with your current authorization.', status=401) # pyright: ignore 
    else:
        pass


