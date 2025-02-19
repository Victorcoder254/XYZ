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

@admin.register(JobDescription)
class JobDescriptionAdmin(admin.ModelAdmin):
    list_display = ('job_title', 'business', 'employment_type', 'job_category', 'location_type', 'created_at', 'is_active')
    list_filter = ('employment_type', 'job_category', 'location_type', 'is_active', 'created_at')
    search_fields = ('job_title', 'job_description', 'department', 'work_location')
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at',)

class CollegeAdmin(admin.ModelAdmin):
    list_display = ("name", "email")

admin.site.register(College, CollegeAdmin)

admin.site.register(CPCProfile)
class CpcAdmin(admin.ModelAdmin):
    list_display = ("college", "location", "created_at")

class StudentAdmin(admin.ModelAdmin):
    list_display = ("cpc_profile", "name", "email")    

admin.site.register(StudentProfile, StudentAdmin)

class CustomQuestionAdmin(admin.ModelAdmin):
    list_display = ("job", "created_at")

admin.site.register(CustomQuestion, CustomQuestionAdmin)

@admin.register(CPCJobFilter)
class CPCJobFilterAdmin(admin.ModelAdmin):
    list_display = ("cpc_profile", "minimum_salary")


class ExcelSheetUploadAdmin(admin.ModelAdmin):
    list_display = ("cpc_profile", "upload_date", "excel_file")

admin.site.register(ExcelSheetUpload, ExcelSheetUploadAdmin)

class StudentEmailAdmin(admin.ModelAdmin):
    list_display = ("excel_sheet", "email")

admin.site.register(StudentEmail, StudentEmailAdmin)


class FacultyAdmin(admin.ModelAdmin):
    list_display = ("name", "description", "cpc_profile")

admin.site.register(Faculty, FacultyAdmin)

class JobApplicationAdmin(admin.ModelAdmin):
    list_display = ("submitted_at", "student_profile", "job")


admin.site.register(JobApplication, JobApplicationAdmin)