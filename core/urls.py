from django.urls import path
from .views import *

urlpatterns = [
    path("", home_view, name="home"),
    path("signup/", signup_view, name="signup"),
    path("login/", login_user, name="login_user"),
    path("business/", business_dashboard, name="business_dashboard"),
    path("cpc/", cpc_dashboard, name="cpc_dashboard"),
    path("submit-student-profile/<str:e_mail>/<int:college_id>/", submit_student_profile, name="submit_student_profile"),    
    path('submit-job-application/<int:job_id>/<str:email>/', submit_job_application, name='submit_job_application'),
    path("success/", success_page, name="success_page"),
    path("student_Management/", student_management, name="student_management"),
]
