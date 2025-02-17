from django.contrib import admin
from .models import *
# Register your models here.


class VisitorAdmin(admin.ModelAdmin):
    list_display = ("visit_date", "location")


admin.site.register(Visitor, VisitorAdmin)

class UserAdmin(admin.ModelAdmin):
    list_display = ("username", "role")

admin.site.register(User, UserAdmin)    


class BusinessProfileAdmin(admin.ModelAdmin):
    list_display = ("business_name", "industry", "location", "created_at")

admin.site.register(BusinessProfile, BusinessProfileAdmin)    

class JobDescriptionAdmin(admin.ModelAdmin):
    list_display = ("job_title", "business", "created_at")

admin.site.register(JobDescription, JobDescriptionAdmin)

class CollegeAdmin(admin.ModelAdmin):
    list_display = ("name", "email")

admin.site.register(College, CollegeAdmin)

admin.site.register(CPCProfile)
class CpcAdmin(admin.ModelAdmin):
    list_display = ("college", "location", "created_at")

class StudentAdmin(admin.ModelAdmin):
    list_display = ("cpc_profile", "name", "email")    

admin.site.register(StudentProfile, StudentAdmin)

class JobApplicationAdmin(admin.ModelAdmin):
    list_display = ("job", "student_profile", "submitted_at")

admin.site.register(JobApplication, JobApplicationAdmin)


