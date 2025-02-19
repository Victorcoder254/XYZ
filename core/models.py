from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.contrib.auth import get_user_model

# Create your models here.

class Visitor(models.Model):
    ip_address = models.GenericIPAddressField()
    location = models.CharField(max_length=255, blank=True, null=True)
    visit_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Visitor {self.ip_address} on {self.visit_date}"


class User(AbstractUser):
    ROLE_CHOICES = (
        ('business_admin', 'Business Admin'),
        ('cpc_admin', 'CPC Admin'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, blank=True, null=True)

    # Fix related_name conflicts
    groups = models.ManyToManyField(Group, related_name="custom_user_set", blank=True)
    user_permissions = models.ManyToManyField(Permission, related_name="custom_user_permissions_set", blank=True)



User = get_user_model()

class BusinessProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="business_profile", blank=True, null=True)
    business_name = models.CharField(max_length=255, blank=True, null=True)
    industry = models.CharField(max_length=100, choices=[
        ('tech', 'Technology'),
        ('finance', 'Finance'),
        ('health', 'Healthcare'),
        ('education', 'Education'),
        ('other', 'Other'),
    ], blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.business_name
    

class College(models.Model):
    name = models.CharField(max_length=255, unique=True, blank=True, null=True)
    email = models.EmailField(unique=True, blank=True, null=True)

    def __str__(self):
        return self.name



class CPCProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="cpc_profile", blank=True, null=True)
    college = models.OneToOneField(College, on_delete=models.SET_NULL, blank=True, null=True, related_name='cpc_profiles')
    location = models.CharField(max_length=255, blank=True, null=True)
    major_field = models.CharField(max_length=255, help_text="E.g. Tech, Engineering, Business, Medicine", blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
                return self.college.name if self.college else "No College Assigned"

class Faculty(models.Model):
    cpc_profile = models.ForeignKey(CPCProfile, on_delete=models.CASCADE, related_name='faculties', blank=True, null=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name    


class JobDescription(models.Model):
    EMPLOYMENT_TYPE_CHOICES = [
        ('full_time', 'Full Time'),
        ('part_time', 'Part Time'),
        ('contract', 'Contract'),
        ('internship', 'Internship'),
        ('hybrid', 'Hybrid'),
        ('remote', 'Remote'),
    ]

    PAY_GRADE_CHOICES = [
        ('entry', 'Entry Level (0-2 years)'),
        ('junior', 'Junior Level (2-4 years)'),
        ('mid', 'Mid Level (4-6 years)'),
        ('senior', 'Senior Level (6+ years)'),
    ]

    JOB_CATEGORY_CHOICES = [
        ('tech', 'Technology'),
        ('finance', 'Finance'),
        ('healthcare', 'Healthcare'),
        ('education', 'Education'),
        ('marketing', 'Marketing'),
        ('sales', 'Sales'),
        ('other', 'Other'),
    ]

    business = models.ForeignKey(BusinessProfile, on_delete=models.CASCADE, related_name="job_descriptions", blank=True, null=True)
    job_title = models.CharField(max_length=255, blank=True, null=True)
    job_description = models.TextField(blank=True, null=True)
    required_qualifications = models.TextField(blank=True, null=True)
    is_approved = models.BooleanField(default=False, blank=True, null=True)
    
    # Required fields
    employment_type = models.CharField(max_length=20, choices=EMPLOYMENT_TYPE_CHOICES, blank=True, null=True)
    job_category = models.CharField(max_length=100, help_text="Select from common categories or enter your own", blank=True, null=True)
    pay_grade = models.CharField(max_length=20, choices=PAY_GRADE_CHOICES, blank=True, null=True)
    # New salary fields
    minimum_pay = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        help_text="Minimum annual salary",
        blank=True, 
        null=True
    )
    maximum_pay = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        help_text="Maximum annual salary",
        blank=True, 
        null=True
    )
    location_type = models.CharField(
        max_length=20,
        choices=[('remote', 'Remote'), ('hybrid', 'Hybrid'), ('onsite', 'On-site')],
        default='onsite',
        blank=True,
        null=True
    )
    location_type = models.CharField(
        max_length=20,
        choices=[('remote', 'Remote'), ('hybrid', 'Hybrid'), ('onsite', 'On-site')],
        default='onsite', blank=True, null=True
    )
    work_location = models.CharField(max_length=255, help_text="City, Country or Remote", blank=True, null=True)
    department = models.CharField(max_length=100, blank=True, null=True)
    skills_required = models.TextField(help_text="List key skills required for this position", blank=True, null=True)
    benefits = models.TextField(help_text="List job benefits and perks", blank=True, null=True)
    
    application_deadline = models.DateField(blank=True, null=True)
    colleges = models.ManyToManyField(College, related_name="job_listings")
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    is_active = models.BooleanField(default=True, blank=True, null=True)

    def __str__(self):
        return f"{self.business.business_name} - {self.job_title} - {self.created_at}"
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Job Description"
        verbose_name_plural = "Job Descriptions"


class CustomQuestion(models.Model):
    QUESTION_TYPE_CHOICES = [
        ('text', 'Text Answer'),
        ('multiple_choice', 'Multiple Choice'),
        ('yes_no', 'Yes/No'),
        ('file_upload', 'File Upload'),
    ]

    job = models.ForeignKey(JobDescription, on_delete=models.CASCADE, related_name='custom_questions', blank=True, null=True)
    question_text = models.TextField(blank=True, null=True)
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPE_CHOICES, blank=True, null=True)
    is_required = models.BooleanField(default=True, blank=True, null=True)
    options = models.JSONField(
        null=True, 
        blank=True, 
        help_text="For multiple choice questions, provide options as a JSON array"
    )
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    order = models.IntegerField(default=0, help_text="Order in which questions should appear", blank=True, null=True)

    class Meta:
        ordering = ['-order']

    def __str__(self):
        return f"{self.job.job_title} - {self.question_text[:50]}"



# Replace the Student model with StudentProfile
class StudentProfile(models.Model):
    cpc_profile = models.ForeignKey(CPCProfile, on_delete=models.CASCADE, blank=True, null=True)
    faculty = models.ForeignKey(Faculty, on_delete=models.SET_NULL, blank=True, null=True, related_name='student_profile')
    name = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField(unique=True, blank=True, null=True)
    
    academic_year = models.CharField(max_length=10, blank=True, null=True)
    # New profile fields
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    education_level = models.CharField(
        max_length=50,
        choices=[
            ('undergraduate', 'Undergraduate'),
            ('graduate', 'Graduate'),
            ('postgraduate', 'Post Graduate'),
        ],
        blank=True, 
        null=True
    )
    course = models.CharField(max_length=255, blank=True, null=True)
    graduation_year = models.IntegerField(blank=True, null=True)
    skills = models.TextField(help_text="List your key skills", blank=True, null=True)
    bio = models.TextField(blank=True)
    linkedin_profile = models.URLField(blank=True)
    github_profile = models.URLField(blank=True)
    portfolio_website = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.course}"

    class Meta:
        verbose_name = "Student Profile"
        verbose_name_plural = "Student Profiles"



class JobApplication(models.Model):
    job = models.ForeignKey(JobDescription, on_delete=models.CASCADE, related_name='applications', blank=True, null=True)
    student_profile = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='applications', blank=True, null=True)
    submitted_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    resume = models.FileField(upload_to='resumes/', blank=True, null=True)
    cover_letter = models.FileField(upload_to='cover_letters/', blank=True, null=True)

    def __str__(self):
        return f"{self.student_profile.name} - {self.job.job_title}"

        
class QuestionResponse(models.Model):
    job_application = models.ForeignKey(JobApplication, on_delete=models.CASCADE, related_name='question_responses', blank=True, null=True)
    question = models.ForeignKey(CustomQuestion, on_delete=models.CASCADE, blank=True, null=True)
    response = models.TextField(blank=True, null=True)
    file_response = models.FileField(upload_to='question_responses/', null=True, blank=True)

    def __str__(self):
        return f"Response to {self.question.question_text[:30]} - {self.job_application}"


class CPCJobFilter(models.Model):
    cpc_profile = models.OneToOneField(CPCProfile, on_delete=models.CASCADE, related_name="job_filter", blank=True, null=True)
    minimum_salary = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        help_text="Minimum salary for job listings",
        blank=True,
        null=True
    )

    EMPLOYMENT_TYPE_CHOICES = [
        ('full_time', 'Full Time'),
        ('part_time', 'Part Time'),
        ('contract', 'Contract'),
        ('internship', 'Internship'),
        ('hybrid', 'Hybrid'),
        ('remote', 'Remote'),
    ]
    allowed_employment_types = models.JSONField(
        blank=True,
        null=True,
        help_text="Specific employment types allowed (JSON array)"
    )

    JOB_CATEGORY_CHOICES = [
        ('tech', 'Technology'),
        ('finance', 'Finance'),
        ('healthcare', 'Healthcare'),
        ('education', 'Education'),
        ('marketing', 'Marketing'),
        ('sales', 'Sales'),
        ('other', 'Other'),
        ('engineering', 'Engineering'),
        ('accounting', 'Accounting'),
        ('human_resources', 'Human Resources'),
        ('customer_service', 'Customer Service'),
        ('research', 'Research'),
        ('art_design', 'Art & Design'),
        ('writing_editing', 'Writing & Editing'),
        ('legal', 'Legal'),
        ('manufacturing', 'Manufacturing'),
        ('transportation', 'Transportation'),
        ('construction', 'Construction'),
        ('hospitality', 'Hospitality'),
        ('retail', 'Retail'),
        ('government', 'Government'),
        ('nonprofit', 'Nonprofit'),
    ]
    allowed_job_categories = models.JSONField(
        blank=True,
        null=True,
        help_text="Specific job categories allowed (JSON array)"
    )
    custom_job_categories = models.JSONField(
        blank=True,
        null=True,
        help_text="Enter custom job categories (JSON array)"
    )
    # Add other filter criteria as needed (e.g., skills, experience level)
    
    def __str__(self):
        return f"Job Filter for {self.cpc_profile.college.name if self.cpc_profile.college else 'No College'}"



class ExcelSheetUpload(models.Model):
    cpc_profile = models.ForeignKey(CPCProfile, on_delete=models.CASCADE, related_name='excel_uploads', blank=True, null=True)
    upload_date = models.DateTimeField(auto_now_add=True)
    excel_file = models.FileField(upload_to='excel_sheets/')

    def __str__(self):
        return f"Excel Sheet Uploaded on {self.upload_date} for {self.cpc_profile}"


class StudentEmail(models.Model):
    excel_sheet = models.ForeignKey(ExcelSheetUpload, on_delete=models.CASCADE, related_name='student_emails', blank=True, null=True)
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.email


