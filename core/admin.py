from django.contrib import admin
from .models import *
# Register your models here.


class VisitorAdmin(admin.ModelAdmin):
    list_display = ("visit_date", "location")


admin.site.register(Visitor, VisitorAdmin)

class UserAdmin(admin.ModelAdmin):
    list_display = ("username", "role")

admin.site.register(User, UserAdmin)    

