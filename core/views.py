from django.shortcuts import redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render
from .models import User
from .decorators import role_required
from django.shortcuts import render, redirect
from django.contrib.auth import login
from core.models import *  # Import your custom User model
from django.contrib import messages
import datetime
from django.core.mail import send_mail
from django.conf import settings



def home_view(request):
    return render(request, "home.html")

def signup_view(request):
    if request.method == "POST":
        username = request.POST.get("username").strip()
        email = request.POST.get("email").strip()
        password = request.POST.get("password")
        role = request.POST.get("role")  # Capturing role from the form

        # Validate role
        if role not in ["business_admin", "cpc_admin"]:
            messages.error(request, "Invalid role selected.")
            return render(request, "files/signup.html")

        # Check if user already exists
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists. Choose another one.")
            return render(request, "files/signup.html")

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already in use. Use another email.")
            return render(request, "files/signup.html")

        # Create user without role first
        user = User.objects.create_user(username=username, email=email, password=password)
        user.role = role  # Assign role manually
        user.save()

        # Log in user
        login(request, user)

        # Redirect based on role
        if role == "business_admin":
            return redirect("business_dashboard")
        else:
            return redirect("cpc_dashboard")

    return render(request, "files/signup.html")


def login_user(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            if user.role == "business_admin":
                return redirect("business_dashboard")
            elif user.role == "cpc_admin":
                return redirect("cpc_dashboard")
        else:
            return HttpResponse("Invalid credentials")
    return render(request, "files/login.html")


@login_required
@role_required("business_admin")  # Ensure only business admins can access
def business_dashboard(request):
    profile_complete = False
    jobs = None
    colleges = College.objects.all()  # Fetch all colleges for selection

    # Check if the business profile exists
    if hasattr(request.user, "business_profile"):
        profile_complete = True
        business = request.user.business_profile
        jobs = JobDescription.objects.filter(business=business)  # Fetch jobs for display

    if request.method == "POST":
        form_type = request.POST.get("form_type")  # Check which form is submitted

        if form_type == "profile":
            # Handle business profile creation
            business_name = request.POST.get("business_name")
            industry = request.POST.get("industry")
            location = request.POST.get("location")
            description = request.POST.get("description")
            phone_number = request.POST.get("phone_number")
            website = request.POST.get("website")

            if business_name and industry and location:
                BusinessProfile.objects.create(
                    user=request.user,
                    business_name=business_name,
                    industry=industry,
                    location=location,
                    description=description,
                    phone_number=phone_number,
                    website=website
                )
                return redirect("business_dashboard")  # Refresh page after saving

        elif form_type == "job":  
            # Handle job description submission
            job_title = request.POST.get("job_title")
            job_description = request.POST.get("job_description")
            required_qualifications = request.POST.get("required_qualifications")
            application_deadline = request.POST.get("application_deadline")
            selected_colleges = request.POST.getlist("selected_colleges")  # Get selected colleges

            if job_title and job_description and required_qualifications and application_deadline:
                job = JobDescription.objects.create(
                    business=request.user.business_profile,
                    job_title=job_title,
                    job_description=job_description,
                    required_qualifications=required_qualifications,
                    application_deadline=application_deadline
                )
                job.colleges.set(selected_colleges)  # Assign selected colleges to job

                # **Send Emails to Selected Colleges**
                colleges = College.objects.filter(id__in=selected_colleges)  # Fetch college details
                recipient_emails = [college.email for college in colleges if college.email]

                if recipient_emails:
                    subject = f"New Job Opportunity: {job_title}"
                    message = f"""
                    Hello,

                    A new job opportunity has been posted for your college:

                    Job Title: {job_title}
                    Description: {job_description}
                    Required Qualifications: {required_qualifications}
                    Application Deadline: {application_deadline}

                    Please inform interested students to apply.

                    Best regards,
                    {request.user.business_profile.business_name}
                    """
                    
                    send_mail(
                        subject,
                        message,
                        settings.EMAIL_HOST_USER,  # Sender (your email)
                        recipient_emails,  # List of college emails
                        fail_silently=False,
                    )
                return redirect("business_dashboard")  # Refresh after submission

    return render(request, "files/business_dashboard.html", {
        "profile_complete": profile_complete,
        "jobs": jobs,
        "colleges": colleges,  # Send colleges to template
    })

@login_required
@role_required("cpc_admin")
def cpc_dashboard(request):
    # Check if the CPC profile exists for the logged-in user
    cpc_profile = CPCProfile.objects.filter(user=request.user).first()

    if request.method == "POST":
        form_type = request.POST.get("form_type")

        if form_type == "cpc_profile":
            college_name = request.POST.get("college_name")
            location = request.POST.get("location")
            major_field = request.POST.get("major_field")

            if college_name and location and major_field:
                if cpc_profile:
                    # Update existing profile
                    cpc_profile.college_name = college_name
                    cpc_profile.location = location
                    cpc_profile.major_field = major_field
                    cpc_profile.save()
                else:
                    # Create new profile
                    CPCProfile.objects.create(
                        user=request.user,
                        college_name=college_name,
                        location=location,
                        major_field=major_field
                    )

                return redirect("cpc_dashboard")  # Refresh dashboard

    return render(request, "files/cpc_dashboard.html", {"cpc_profile": cpc_profile})
