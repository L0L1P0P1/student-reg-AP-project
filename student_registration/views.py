from django.shortcuts import render
from django.http import HttpResponse

def home(request):
    """Home page view"""
    return render(request, 'home.html')

def about(request):
    """About page"""
    return render(request, 'about.html')
