from django.contrib import admin
from .models import Major, User, Admin, Student, Instructor 

admin.site.register(Major)
admin.site.register(Admin)
admin.site.register(Student)
admin.site.register(Instructor)
