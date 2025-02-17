from django.shortcuts import redirect, get_object_or_404
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
from django.conf import settings#


def home_view(request):
    return render(request, "files/home.html")

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

                # Only fetch CPC Admin emails
                colleges = College.objects.filter(id__in=selected_colleges)
                cpc_profiles = CPCProfile.objects.filter(college__in=colleges)
                cpc_admin_emails = [cpc.user.email for cpc in cpc_profiles if cpc.user.email]

                if cpc_admin_emails:
                    for cpc_email in cpc_admin_emails:
                        subject = f"New Job Opportunity: {job_title}"
                        message = f"""
                        Hello CPC Admin,

                        A new job opportunity has been posted for your college. Please review and share with eligible students:

                        Job Title: {job_title}
                        Description: {job_description}
                        Required Qualifications: {required_qualifications}
                        Application Deadline: {application_deadline}

                        You can view this job posting in your CPC dashboard.

                        Best regards,
                        {request.user.business_profile.business_name}
                        """

                        send_mail(
                            subject,
                            message,
                            settings.EMAIL_HOST_USER,
                            [cpc_email],
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
    cpc_profile = CPCProfile.objects.filter(user=request.user).first()
    colleges = College.objects.all()

    if request.method == "POST":
        form_type = request.POST.get("form_type")

        if form_type == "cpc_profile":
            college_id = request.POST.get("college_id")  
            location = request.POST.get("location")
            major_field = request.POST.get("major_field")

            # Add debug messages
            print(f"College ID received: {college_id}")
            print(f"Location received: {location}")
            print(f"Major field received: {major_field}")

            try:
                college = College.objects.get(id=college_id)
            except College.DoesNotExist:
                messages.error(request, f"College with ID {college_id} not found.")
                return redirect("cpc_dashboard")

            # Check if this college is already assigned to a CPC admin
            existing_cpc = CPCProfile.objects.filter(college=college).exclude(user=request.user).first()
            if existing_cpc:
                messages.error(request, "This college already has a CPC admin.")
                return redirect("cpc_dashboard")

            if cpc_profile:
                # Update existing profile
                cpc_profile.college = college
                cpc_profile.location = location
                cpc_profile.major_field = major_field
                cpc_profile.save()
                messages.success(request, "Profile updated successfully!")
            else:
                # Create new profile
                CPCProfile.objects.create(
                    user=request.user,
                    college=college,
                    location=location,
                    major_field=major_field
                )
                messages.success(request, "Profile created successfully!")

            return redirect("cpc_dashboard")

    context = {
        "cpc_profile": cpc_profile, 
        "colleges": colleges,
        "selected_college": cpc_profile.college if cpc_profile else None
    }
    return render(request, "files/cpc_dashboard.html", context)


# Student Email Submission View
def submit_student_profile(request):
    colleges = College.objects.all()

    if request.method == "POST":
        # Basic Information
        name = request.POST.get("name")
        email = request.POST.get("email")
        college_id = request.POST.get("college_id")
        phone_number = request.POST.get("phone_number")
        
        # Educational Information
        education_level = request.POST.get("education_level")
        course = request.POST.get("course")
        graduation_year = request.POST.get("graduation_year")
        
        # Professional Information
        skills = request.POST.get("skills")
        bio = request.POST.get("bio")
        linkedin_profile = request.POST.get("linkedin_profile")
        github_profile = request.POST.get("github_profile")
        portfolio_website = request.POST.get("portfolio_website")

        if not all([name, email, college_id, phone_number, education_level, course, graduation_year]):
            messages.error(request, "Please fill in all required fields.")
            return redirect("student_email_submission")

        # Validate college and CPC profile
        college = get_object_or_404(College, id=college_id)
        cpc_profile = get_object_or_404(CPCProfile, college=college)

        # Check if student profile already exists
        if StudentProfile.objects.filter(email=email).exists():
            messages.warning(request, "A profile with this email already exists.")
            return redirect("student_email_submission")

        # Create student profile
        try:
            StudentProfile.objects.create(
                cpc_profile=cpc_profile,
                name=name,
                email=email,
                phone_number=phone_number,
                education_level=education_level,
                course=course,
                graduation_year=int(graduation_year),
                skills=skills,
                bio=bio or "",
                linkedin_profile=linkedin_profile or "",
                github_profile=github_profile or "",
                portfolio_website=portfolio_website or ""
            )
            messages.success(request, "Student profile created successfully!")
            return redirect("success_page")
        except Exception as e:
            messages.error(request, f"Error creating profile: {str(e)}")
            return redirect("student_email_submission")

    return render(request, "files/student_email.html", {"colleges": colleges})

# Job Application Submission View
def submit_job_application(request, job_id=None, email=None):
    # Get the job and validate student profile
    job = get_object_or_404(JobDescription, id=job_id)
    student_profile = get_object_or_404(StudentProfile, email=email)
    
    if request.method == "POST":
        cover_letter = request.FILES.get("cover_letter")
        resume = request.FILES.get("resume")

        # Validate required fields
        if not resume:
            messages.error(request, "Please upload your resume.")
            return render(request, "files/job_application.html", {
                "job": job,
                "student_profile": student_profile,
                "email": email
            })

        try:
            # Create job application record
            application = JobApplication.objects.create(
                job=job,
                student_profile=student_profile,
                resume=resume,
                cover_letter=cover_letter
            )

            # Handle custom questions if any
            for key, value in request.POST.items():
                if key.startswith('question_'):
                    question_id = key.split('_')[1]
                    question = get_object_or_404(CustomQuestion, id=question_id)
                    
                    # Handle file upload questions separately
                    if question.question_type == 'file_upload':
                        file_response = request.FILES.get(key)
                        if file_response:
                            QuestionResponse.objects.create(
                                job_application=application,
                                question=question,
                                file_response=file_response
                            )
                    else:
                        QuestionResponse.objects.create(
                            job_application=application,
                            question=question,
                            response=value
                        )

            messages.success(request, "Job application submitted successfully!")
            return redirect("success_page")
            
        except Exception as e:
            messages.error(request, f"Error submitting application: {str(e)}")
            return redirect("job_application", job_id=job_id, email=email)
    
    # Get custom questions for this job
    custom_questions = CustomQuestion.objects.filter(job=job).order_by('order')
    
    context = {
        "job": job,
        "student_profile": student_profile,
        "email": email,
        "custom_questions": custom_questions
    }
    return render(request, "files/job_application.html", context)

# Success Page View
def success_page(request):
    return render(request, "files/success.html")
