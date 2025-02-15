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
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

    # Fix related_name conflicts
    groups = models.ManyToManyField(Group, related_name="custom_user_set", blank=True)
    user_permissions = models.ManyToManyField(Permission, related_name="custom_user_permissions_set", blank=True)



User = get_user_model()

class BusinessProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="business_profile")
    business_name = models.CharField(max_length=255)
    industry = models.CharField(max_length=100, choices=[
        ('tech', 'Technology'),
        ('finance', 'Finance'),
        ('health', 'Healthcare'),
        ('education', 'Education'),
        ('other', 'Other'),
    ])
    location = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.business_name
    

class College(models.Model):
    name = models.CharField(max_length=255, unique=True)
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.name


class JobDescription(models.Model):
    business = models.ForeignKey(BusinessProfile, on_delete=models.CASCADE, related_name="job_descriptions")
    job_title = models.CharField(max_length=255)
    job_description = models.TextField()
    required_qualifications = models.TextField()
    application_deadline = models.DateField()
    colleges = models.ManyToManyField(College, related_name="job_listings")  # Stores selected colleges

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.job_title   


class CPCProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="cpc_profile")
    college_name = models.CharField(max_length=255, unique=True)
    location = models.CharField(max_length=255)
    major_field = models.CharField(max_length=255, help_text="E.g. Tech, Engineering, Business, Medicine")

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.college_name