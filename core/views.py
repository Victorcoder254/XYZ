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
from django.http import JsonResponse
from django.urls import reverse
import json

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
@role_required("business_admin")
def business_dashboard(request):
    profile_complete = False
    jobs = None
    colleges = College.objects.all()

    if hasattr(request.user, "business_profile"):
        profile_complete = True
        business = request.user.business_profile
        jobs = JobDescription.objects.filter(business=business)

    if request.method == "POST":
        form_type = request.POST.get("form_type")
        current_step = request.POST.get("current_step", "1")

        print(f"Processing POST request - Step {current_step}")
        print(f"POST data: {request.POST}")
        print(f"Current session data: {dict(request.session)}")

        if form_type == "job":
            if current_step == "1":
                try:
                    print("Processing step 1")
                    
                    # Store job details in session
                    job_data = {
                        'job_title': request.POST.get('job_title', '').strip(),
                        'department': request.POST.get('department', '').strip(),
                        'job_description': request.POST.get('job_description', '').strip(),
                        'required_qualifications': request.POST.get('required_qualifications', '').strip(),
                        'employment_type': request.POST.get('employment_type', '').strip(),
                        'job_category': request.POST.get('job_category', '').strip(),
                        'pay_grade': request.POST.get('pay_grade', '').strip(),
                        'minimum_pay': request.POST.get('minimum_pay', '').strip(),
                        'maximum_pay': request.POST.get('maximum_pay', '').strip(),
                        'location_type': request.POST.get('location_type', '').strip(),
                        'work_location': request.POST.get('work_location', '').strip(),
                        'skills_required': request.POST.get('skills_required', '').strip(),
                        'benefits': request.POST.get('benefits', '').strip(),
                        'application_deadline': request.POST.get('application_deadline', '').strip(),
                        'is_active': request.POST.get('is_active') == 'on'
                    }

                    # Validate required fields
                    missing_fields = [field for field, value in job_data.items() 
                                    if not value and field not in ['benefits', 'is_active']]
                    
                    if missing_fields:
                        return JsonResponse({
                            'status': 'error',
                            'message': f'Missing required fields: {", ".join(missing_fields)}'
                        })

                    # Validate pay range
                    try:
                        min_pay = float(job_data['minimum_pay'])
                        max_pay = float(job_data['maximum_pay'])
                        if min_pay >= max_pay:
                            return JsonResponse({
                                'status': 'error',
                                'message': 'Maximum pay must be greater than minimum pay'
                            })
                    except ValueError:
                        return JsonResponse({
                            'status': 'error',
                            'message': 'Invalid pay values provided'
                        })

                    # Store in session
                    request.session['job_data'] = job_data
                    request.session.modified = True
                    request.session.save()
                    
                    print(f"Step 1 session data saved: {request.session.get('job_data')}")
                    return JsonResponse({'status': 'success', 'step': 2})

                except Exception as e:
                    print(f"Error in step 1: {str(e)}")
                    return JsonResponse({'status': 'error', 'message': str(e)})

            elif current_step == "2":
                try:
                    print("Processing step 2")
                    
                    # Retrieve job_data from session
                    job_data = request.session.get('job_data')
                    if not job_data:
                        return JsonResponse({
                            'status': 'error',
                            'message': 'Job details not found. Please fill out step 1 first.'
                        })
                    print(f"Job data from session: {job_data}")

                    # Retrieve questions_data from POST
                    questions_data_json = request.POST.get('questions_data')
                    if questions_data_json:
                        questions_data = json.loads(questions_data_json)
                        print(f"Questions data from POST: {questions_data}")
                    else:
                        questions_data = []
                        print("No questions data found in POST")

                    # Store questions_data in session
                    request.session['questions_data'] = questions_data
                    request.session.modified = True
                    request.session.save()
                    print(f"Step 2 session data saved: {questions_data}")

                    return JsonResponse({'status': 'success', 'step': 3})

                except Exception as e:
                    print(f"Error in step 2: {str(e)}")
                    return JsonResponse({'status': 'error', 'message': str(e)})

            elif current_step == "3":
                try:
                    print("Processing step 3")
                    print(f"Current session state: {dict(request.session)}")
                    
                    job_data = request.session.get('job_data')
                    questions_data = request.session.get('questions_data', [])
                    selected_colleges = request.POST.getlist('selected_colleges')

                    print(f"Job data from session: {job_data}")
                    print(f"Questions data from session: {questions_data}")
                    print(f"Selected colleges: {selected_colleges}")

                    if not job_data:
                        return JsonResponse({
                            'status': 'error',
                            'message': 'Job details not found. Please fill out step 1 first.'
                        })

                    if not selected_colleges:
                        return JsonResponse({
                            'status': 'error',
                            'message': 'Please select at least one college'
                        })

                    # Create job
                    job = JobDescription.objects.create(
                        business=request.user.business_profile,
                        **job_data
                    )
                    
                    # Add colleges
                    job.colleges.set(selected_colleges)

                    # Create custom questions
                    for question in questions_data:
                        CustomQuestion.objects.create(
                            job=job,
                            question_text=question['question_text'],
                            question_type=question['question_type'],
                            is_required=question['is_required'],
                            options=question['options'],
                            order=question['order']
                        )

                    # Send email notifications to CPC admins of selected colleges
                    for college_id in selected_colleges:
                        try:
                            cpc_profile = CPCProfile.objects.get(college_id=college_id)
                            if cpc_profile and cpc_profile.user.email:
                                send_job_notification_email(job, cpc_profile.user.email)
                        except CPCProfile.DoesNotExist:
                            continue

                    # Clear session data
                    request.session.pop('job_data', None)
                    request.session.pop('questions_data', None)

                    messages.success(request, "Job posted successfully!")
                    return JsonResponse({'status': 'success', 'redirect': reverse('business_dashboard')})

                except Exception as e:
                    print(f"Error in step 3: {str(e)}")
                    return JsonResponse({'status': 'error', 'message': str(e)})

    context = {
        "profile_complete": profile_complete,
        "jobs": jobs,
        "colleges": colleges,
        "employment_types": JobDescription.EMPLOYMENT_TYPE_CHOICES,
        "job_categories": JobDescription.JOB_CATEGORY_CHOICES,
        "pay_grades": JobDescription.PAY_GRADE_CHOICES,
        "location_types": [('remote', 'Remote'), ('hybrid', 'Hybrid'), ('onsite', 'On-site')]
    }

    return render(request, "files/business_dashboard.html", context)



def send_job_notification_email(job, email):
    try:
        # Convert salary values to float for formatting
        min_pay = float(job.minimum_pay) if job.minimum_pay else 0
        max_pay = float(job.maximum_pay) if job.maximum_pay else 0
        
        subject = f"New Job Opportunity: {job.job_title}"
        message = f"""
Hello CPC Admin,

A new job opportunity has been posted:

Job Title: {job.job_title}
Department: {job.department}
Category: {job.job_category}
Employment Type: {job.employment_type}
Pay Grade: {job.pay_grade}
Salary Range: ${min_pay:,.2f} - ${max_pay:,.2f}
Location: {job.work_location} ({job.location_type})

Application Deadline: {job.application_deadline}

You can view the full details in your CPC dashboard.

Best regards,
{job.business.business_name}
        """
        
        send_mail(
            subject,
            message,
            settings.EMAIL_HOST_USER,
            [email],
            fail_silently=False,
        )
        print(f"Email sent successfully to {email}")
        return True
    except Exception as e:
        print(f"Error sending email notification: {str(e)}")
        return False



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
