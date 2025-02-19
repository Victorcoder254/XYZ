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
    path('edit_faculty/<int:faculty_id>/', edit_faculty, name='edit_faculty'),
    path('send_email/', send_email, name='send_email'),
    path('job_listings_management/', job_listings_management, name='job_listings_management'),
    path('spam_jobs/', spam_job_listings, name='spam_job_listings'),
    path('applications/', manage_job_applications, name='manage_applications'),
    # ... other URL patterns ...
]
