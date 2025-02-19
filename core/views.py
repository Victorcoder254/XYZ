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
import urllib.parse
from django.core.mail import send_mail
from django.conf import settings#
from django.http import JsonResponse
from django.urls import reverse
import json
import openpyxl
from django.db import IntegrityError
from django.core.paginator import Paginator
from django.db.models import Q


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
    cpc_job_filters = CPCJobFilter.objects.all()

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
                        'is_active': request.POST.get('is_active') == 'no'
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
                    
                    # Set is_active to True
                    job_data['is_active'] = True



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
        "location_types": [('remote', 'Remote'), ('hybrid', 'Hybrid'), ('onsite', 'On-site')],
        "cpc_job_filters": cpc_job_filters,
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
    cpc_job_filter = CPCJobFilter.objects.filter(cpc_profile=cpc_profile).first()

    
    # Initialize metrics
    metrics = {
        'students_count': 0,
        'faculties_count': 0,
        'applications_count': 0,
        'spam_jobs_count': 0
    }

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
            existing_cpc = CPCProfile.objects.filter(college=college).exclude(
                user=request.user).first()
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
                cpc_profile = CPCProfile.objects.create(
                    user=request.user,
                    college=college,
                    location=location,
                    major_field=major_field
                )
                messages.success(request, "Profile created successfully!")

            return redirect("cpc_dashboard")

        elif form_type == "cpc_job_filter":
            minimum_salary = request.POST.get("minimum_salary")
            allowed_employment_types = request.POST.getlist("allowed_employment_types")
            allowed_job_categories = request.POST.getlist("allowed_job_categories")
            custom_job_categories = request.POST.getlist("custom_job_categories")

            if cpc_job_filter:
                # Update existing filter
                cpc_job_filter.minimum_salary = minimum_salary
                cpc_job_filter.allowed_employment_types = allowed_employment_types
                cpc_job_filter.allowed_job_categories = allowed_job_categories
                cpc_job_filter.custom_job_categories = custom_job_categories
                cpc_job_filter.save()
                messages.success(request, "Job filter updated successfully!")
            else:
                # Create new filter
                CPCJobFilter.objects.create(
                    cpc_profile=cpc_profile,
                    minimum_salary=minimum_salary,
                    allowed_employment_types=allowed_employment_types,
                    allowed_job_categories=allowed_job_categories,
                    custom_job_categories=custom_job_categories
                )
                messages.success(request, "Job filter created successfully!")

            return redirect("cpc_dashboard")
        
        
    if cpc_profile and cpc_profile.college:
    # Get base querysets
        students = StudentProfile.objects.filter(cpc_profile=cpc_profile)
        faculties = Faculty.objects.filter(cpc_profile=cpc_profile)
        applications = JobApplication.objects.filter(job__colleges=cpc_profile.college)
        jobs = JobDescription.objects.filter(colleges=cpc_profile.college)

    # Calculate spam jobs using existing logic
    if cpc_job_filter:
        valid_jobs = jobs
        if cpc_job_filter.minimum_salary:
            valid_jobs = valid_jobs.filter(minimum_pay__gte=cpc_job_filter.minimum_salary)
        if cpc_job_filter.allowed_employment_types:
            try:
                allowed_types = json.loads(cpc_job_filter.allowed_employment_types)
                valid_jobs = valid_jobs.filter(employment_type__in=allowed_types)
            except (TypeError, json.JSONDecodeError):
                pass
        spam_jobs = jobs.exclude(id__in=valid_jobs.values_list('id', flat=True))
    else:
        spam_jobs = jobs.none()

    # Update metrics
    metrics.update({
        'students_count': students.count(),
        'faculties_count': faculties.count(),
        'applications_count': applications.count(),
        'spam_jobs_count': spam_jobs.count()
    })


    context = {
        "cpc_profile": cpc_profile,
        "colleges": colleges,
        "selected_college": cpc_profile.college if cpc_profile else None,
        "cpc_job_filter": cpc_job_filter,
        "employment_type_choices": CPCJobFilter.EMPLOYMENT_TYPE_CHOICES,
        "job_category_choices": CPCJobFilter.JOB_CATEGORY_CHOICES,
        **metrics
    }
    return render(request, "files/cpc_dashboard.html", context)



from django.db.models import Count

@login_required
@role_required("cpc_admin")
def student_management(request):
    cpc_profile = CPCProfile.objects.filter(user=request.user).first()
    if not cpc_profile:
        messages.error(request, "CPC profile not found. Please create one first.")
        return redirect("cpc_dashboard")

    faculties = Faculty.objects.filter(cpc_profile=cpc_profile).annotate(num_students=Count('student_profile'))
    student_profiles = StudentProfile.objects.filter(cpc_profile=cpc_profile)
    excel_uploads = ExcelSheetUpload.objects.filter(cpc_profile=cpc_profile)
    job_applications = []

    q = request.GET.get("q", "").strip()
    faculty_filter = request.GET.get("faculty_id", "").strip()
    if q:
        student_profiles = student_profiles.filter(
            Q(name__icontains=q) |
            Q(email__icontains=q) |
            Q(course__icontains=q)
        )
    if faculty_filter:
        student_profiles = student_profiles.filter(faculty__id=faculty_filter)

    paginator = Paginator(student_profiles.order_by('-created_at'), 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    if request.method == "POST":
        form_type = request.POST.get("form_type")

        if form_type == "create_faculty":
            name = request.POST.get("name")
            description = request.POST.get("description")

            if not name or not description:
                messages.error(request, "Name and description are required for faculty creation.")
                return redirect("student_management")

            Faculty.objects.create(cpc_profile=cpc_profile, name=name, description=description)
            messages.success(request, "Faculty created successfully!")
            return redirect("student_management")

        elif form_type == "import_emails":
            excel_file = request.FILES.get('excel_file')

            if not excel_file:
                messages.error(request, 'Please upload a valid Excel file.')
                return redirect("student_management")

            if not excel_file.name.endswith('.xlsx'):
                messages.error(request, 'Please upload a valid Excel file.')
                return redirect("student_management")

            try:
                workbook = openpyxl.load_workbook(excel_file)
                sheet = workbook.active

                excel_upload = ExcelSheetUpload.objects.create(cpc_profile=cpc_profile, excel_file=excel_file)

                for row_num, row in enumerate(sheet.iter_rows(min_row=2, values_only=True), start=2):
                    email = row[0]
                    if not email:
                        print(f"Row {row_num}: Skipping row with empty email.")
                        continue
                    email = email.strip()
                    if StudentEmail.objects.filter(email=email).exists():
                        print(f"Row {row_num}: Student with email {email} already exists.")
                        continue
                    try:
                        student_email = StudentEmail.objects.create(excel_sheet=excel_upload, email=email)
                        encoded_email = urllib.parse.quote(email)
                        college_id = cpc_profile.college.id
                        invitation_link = request.build_absolute_uri(
                            reverse('submit_student_profile', args=[encoded_email, college_id])
                        )
                        subject = "Invitation to Create Your Student Profile"
                        message = (
                            f"Dear Student,\n\n"
                            f"You are invited to create your student profile. Please click on the following link to proceed:\n\n"
                            f"{invitation_link}\n\n"
                            f"Note: If a profile associated with this email already exists, you will not be able to create a new one.\n\n"
                            f"Best regards,\nYour CPC Admin"
                        )
                        send_mail(subject, message, settings.EMAIL_HOST_USER, [email], fail_silently=False)
                        print(f"Row {row_num}: Invitation email sent successfully to {email}")
                    except IntegrityError as e:
                        print(f"Row {row_num}: IntegrityError - Email {email} already exists: {e}")
                        continue
                    except Exception as e:
                        print(f"Row {row_num}: Error sending email to {email}: {e}")
                        continue

                messages.success(request, 'Student emails imported and invitations sent successfully!')
                return redirect("student_management")

            except Exception as e:
                messages.error(request, f'Error importing emails: {str(e)}')
                return redirect("student_management")

    context = {
        "cpc_profile": cpc_profile,
        "faculties": faculties,
        "student_profiles_count": student_profiles.count(),
        "faculties_count": faculties.count(),
        "job_applications_count": len(job_applications),
        "page_obj": page_obj,
        "q": q,
        "faculty_filter": faculty_filter,
        "excel_uploads": excel_uploads,
    }
    return render(request, "files/student_management.html", context)


from django.shortcuts import get_object_or_404, redirect

@login_required
@role_required("cpc_admin")
def edit_faculty(request, faculty_id):
    faculty = get_object_or_404(Faculty, id=faculty_id, cpc_profile__user=request.user)

    if request.method == "POST":
        name = request.POST.get("name")
        description = request.POST.get("description")

        if not name or not description:
            messages.error(request, "Name and description are required.")
            return redirect("student_management")

        faculty.name = name
        faculty.description = description
        faculty.save()
        messages.success(request, "Faculty updated successfully!")
        return redirect("student_management")

    messages.error(request, "Invalid request.")
    return redirect("student_management")

@login_required
@role_required("cpc_admin")
def send_email(request):
    if request.method == "POST":
        recipient_email = request.POST.get("recipient_email")
        subject = request.POST.get("subject")
        message = request.POST.get("message")

        if not recipient_email or not subject or not message:
            messages.error(request, "Recipient email, subject, and message are required.")
            return redirect("student_management")

        try:
            send_mail(subject, message, settings.EMAIL_HOST_USER, [recipient_email], fail_silently=False)
            messages.success(request, "Email sent successfully!")
            return redirect("student_management")
        except Exception as e:
            messages.error(request, f"Error sending email: {str(e)}")
            return redirect("student_management")

    messages.error(request, "Invalid request.")
    return redirect("student_management")


def submit_student_profile(request, e_mail, college_id):
    # Decode the email passed in the URL
    decoded_email = urllib.parse.unquote(e_mail)
    # Retrieve the specific college based on the college_id from the CPC admin invitation
    college = get_object_or_404(College, id=college_id)
    # Retrieve the associated CPC profile (assumes one CPCProfile per college)
    cpc_profile = get_object_or_404(CPCProfile, college=college)
    # Filter faculties belonging to that CPC profile
    faculties = Faculty.objects.filter(cpc_profile=cpc_profile)
    
    # Check if a StudentProfile already exists for this email
    if StudentProfile.objects.filter(email=decoded_email).exists():
        messages.error(request, "A profile with this email already exists. You cannot create another.")
        return redirect("login")  # or another appropriate view

    if request.method == "POST":
        name = request.POST.get("name")
        email = decoded_email
        # Notice: no need to retrieve college_id from POST now.
        phone_number = request.POST.get("phone_number")
        academic_year = request.POST.get("academic_year")
        
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
        
        # Faculty selection remains (student must select a faculty)
        faculty_id = request.POST.get("faculty_id")
        if not all([name, email, phone_number, academic_year, education_level, course, graduation_year, faculty_id]):
            messages.error(request, "Please fill in all required fields, including the faculty selection.")
            return redirect("student_email_submission")  # Adjust redirect if needed
        
        # Retrieve the selected faculty and ensure it belongs to the same CPC profile.
        faculty = get_object_or_404(Faculty, id=faculty_id, cpc_profile=cpc_profile)
        
        # Final check
        if StudentProfile.objects.filter(email=email).exists():
            messages.warning(request, "A profile with this email already exists.")
            return redirect("student_email_submission")
        
        try:
            StudentProfile.objects.create(
                cpc_profile=cpc_profile,
                faculty=faculty,
                name=name,
                email=email,
                phone_number=phone_number,
                academic_year=academic_year,
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
    
    # For GET requests, pass in the decoded email, the college (admin’s college) and the faculties
    context = {
        "decoded_email": decoded_email,
        "college": college,
        "faculties": faculties,
    }
    return render(request, "files/student_email.html", context)


# Job listings/opportunities for a college management By cpc admin

@login_required
@role_required("cpc_admin")
def job_listings_management(request):
    cpc_profile = CPCProfile.objects.filter(user=request.user).first()
    if not cpc_profile:
        messages.error(request, "CPC profile not found. Please create one first.")
        return redirect("cpc_dashboard")

    jobs = JobDescription.objects.filter(colleges=cpc_profile.college).prefetch_related('custom_questions')
    newest_job_id = jobs.order_by('-created_at').values_list('id', flat=True).first()
    faculties = Faculty.objects.filter(cpc_profile=cpc_profile)

    if request.method == "POST":
        job_id = request.POST.get("job_id")
        job = get_object_or_404(JobDescription, id=job_id)

        faculty_id = request.POST.get("faculty")
        graduation_year = request.POST.get("graduation_year")

        students = StudentProfile.objects.filter(cpc_profile=cpc_profile, faculty_id=faculty_id, graduation_year=graduation_year)

        if students.exists():
            subject = f"New Job Opportunity: {job.job_title}"
            from_email = request.user.email
            success_count = 0
            errors = []

            for student in students:
                try:
                    # Generate application URL
                    application_url = request.build_absolute_uri(
                        reverse('submit_job_application', kwargs={
                            'job_id': job.id,
                            'email': student.email
                        })
                    )

                    # Build email message
                    message = f"""
                    Dear {student.name},

                    We're excited to share a job opportunity that matches your profile:

                    Position: {job.job_title}
                    Company: {job.business.business_name}
                    Location: {job.work_location}
                    Employment Type: {job.employment_type}
                    Salary Range: ${job.minimum_pay:,.2f} - ${job.maximum_pay:,.2f}
                    Application Deadline: {job.application_deadline.strftime('%B %d, %Y')}

                    Key Responsibilities:
                    {job.job_description}

                    Skills Required:
                    {job.skills_required}

                    To apply, please visit:
                    {application_url}

                    Application Requirements:
                    - Updated Resume (required)
                    - Cover Letter (optional)
                    - Complete all required questions in the application form

                    Custom Application Questions:
                    {'\n'.join([f'• {q.question_text}' for q in job.custom_questions.all() if q.is_required])}

                    Please submit your application at least 3 days before the deadline.

                    Best regards,
                    {request.user.get_full_name()}
                    {cpc_profile.college.name} Career Services
                    """

                    send_mail(
                        subject,
                        message.strip(),  # Remove leading whitespace
                        from_email,
                        [student.email],
                        fail_silently=False
                    )
                    success_count += 1

                except Exception as e:
                    errors.append(f"{student.email}: {str(e)}")

            if success_count > 0:
                job.is_approved = True
                job.save()
                messages.success(request, 
                    f"Sent {success_count} invitations for '{job.job_title}'. "
                    f"{len(errors)} failed deliveries."
                )

            if errors:
                messages.error(request, "Failed to send to: " + ", ".join(errors))
                print(errors)

        else:
            messages.info(request, "No students found matching the criteria.")

    q = request.GET.get("q", "").strip()
    if q:
        jobs = jobs.filter(
            Q(job_title__icontains=q) |
            Q(department__icontains=q) |
            Q(employment_type__icontains=q)
        )

    paginator = Paginator(jobs.order_by('-created_at'), 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)


    context = {
        "page_obj": page_obj,
        "q": q,
        "newest_job_id": newest_job_id,
        "faculties": faculties,
    }
    return render(request, "files/job_listings_management.html", context)


@login_required
@role_required("cpc_admin")
def spam_job_listings(request):
    cpc_profile = CPCProfile.objects.filter(user=request.user).first()
    if not cpc_profile:
        messages.error(request, "CPC profile not found. Please create one first.")
        return redirect("cpc_dashboard")

    cpc_job_filter = CPCJobFilter.objects.filter(cpc_profile=cpc_profile).first()
    
    # Get all jobs for the college
    spam_jobs = JobDescription.objects.filter(colleges=cpc_profile.college)
    
    # Exclude jobs that match CPC filters
    if cpc_job_filter:
        valid_jobs = JobDescription.objects.filter(colleges=cpc_profile.college)
        
        if cpc_job_filter.minimum_salary:
            valid_jobs = valid_jobs.filter(minimum_pay__gte=cpc_job_filter.minimum_salary)
        
        if cpc_job_filter.allowed_employment_types:
            try:
                allowed_employment_types = json.loads(cpc_job_filter.allowed_employment_types)
                valid_jobs = valid_jobs.filter(
                    employment_type__in=[et.lower().replace(" ", "") for et in allowed_employment_types]
                )
            except (TypeError, json.JSONDecodeError):
                pass
        
        if cpc_job_filter.allowed_job_categories:
            try:
                allowed_job_categories = json.loads(cpc_job_filter.allowed_job_categories)
                valid_jobs = valid_jobs.filter(
                    job_category__in=[jc.lower().replace(" ", "") for jc in allowed_job_categories]
                )
            except (TypeError, json.JSONDecodeError):
                pass
        
        # Get spam jobs by excluding valid ones
        spam_jobs = spam_jobs.exclude(id__in=valid_jobs.values_list('id', flat=True))

    q = request.GET.get("q", "").strip()
    if q:
        spam_jobs = spam_jobs.filter(
            Q(job_title__icontains=q) |
            Q(department__icontains=q) |
            Q(employment_type__icontains=q)
        )

    paginator = Paginator(spam_jobs.order_by('-created_at'), 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        "page_obj": page_obj,
        "q": q,
    }
    return render(request, "files/spam_job_listings.html", context)

from django.core.exceptions import ValidationError

def submit_job_application(request, job_id=None, email=None):
    job = get_object_or_404(JobDescription, id=job_id)
    student_profile = get_object_or_404(StudentProfile, email=email)
    
    if request.method == "POST":
        cover_letter = request.FILES.get("cover_letter")
        resume = request.FILES.get("resume")
        custom_questions = CustomQuestion.objects.filter(job=job).order_by('order')

        # Validate required fields
        errors = []
        if not resume:
            errors.append("Resume is required")
            
        # Validate custom questions
        question_responses = {}
        for question in custom_questions:
            key = f'question_{question.id}'
            
            if question.question_type == 'file_upload':
                response = request.FILES.get(key)
            else:
                response = request.POST.get(key)
            
            if question.is_required and not response:
                errors.append(f"Required question missing: {question.question_text}")
            elif response:
                question_responses[question.id] = {
                    'question': question,
                    'response': response,
                    'is_file': question.question_type == 'file_upload'
                }

        if errors:
            for error in errors:
                messages.error(request, error)
            return render(request, "files/job_application.html", {
                "job": job,
                "student_profile": student_profile,
                "custom_questions": custom_questions,
                "email": email
            })

        try:
            # Create job application
            application = JobApplication.objects.create(
                job=job,
                student_profile=student_profile,
                resume=resume,
                cover_letter=cover_letter
            )

            # Save question responses
            for qid, response_data in question_responses.items():
                question = response_data['question']
                response_value = response_data['response']
                
                if response_data['is_file']:
                    QuestionResponse.objects.create(
                        job_application=application,
                        question=question,
                        file_response=response_value
                    )
                else:
                    # Handle multiple choice options
                    if question.question_type == 'multiple_choice' and question.options:
                        options = json.loads(question.options)
                        if response_value not in options:
                            raise ValidationError("Invalid choice for question")
                    
                    QuestionResponse.objects.create(
                        job_application=application,
                        question=question,
                        response=response_value
                    )

            messages.success(request, "Application submitted successfully!")
            return redirect("success_page")
            
        except Exception as e:
            messages.error(request, f"Error submitting application: {str(e)}")
            return redirect("job_application", job_id=job_id, email=email)
    
    # GET request handling remains the same
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


@login_required
@role_required("cpc_admin")
def manage_job_applications(request):
    cpc_profile = CPCProfile.objects.filter(user=request.user).first()
    if not cpc_profile:
        messages.error(request, "CPC profile not found.")
        return redirect("cpc_dashboard")

    applications = JobApplication.objects.filter(
        job__colleges=cpc_profile.college
    ).select_related('job', 'student_profile').prefetch_related('question_responses')

    # Filters
    job_id = request.GET.get('job_id')
    status = request.GET.get('status')
    student_email = request.GET.get('student_email')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')

    if job_id:
        applications = applications.filter(job__id=job_id)
    if status:
        applications = applications.filter(status=status)
    if student_email:
        applications = applications.filter(student_profile__email__icontains=student_email)
    if date_from and date_to:
        applications = applications.filter(submitted_at__date__range=[date_from, date_to])

    # Pagination
    paginator = Paginator(applications.order_by('-submitted_at'), 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'total_applications': applications.count(),
        'jobs': JobDescription.objects.filter(colleges=cpc_profile.college),
        'filter_params': {
            'job_id': job_id,
            'status': status,
            'student_email': student_email,
            'date_from': date_from,
            'date_to': date_to
        }
    }
    return render(request, 'files/manage_applications.html', context)
