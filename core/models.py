from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractUser, Group, Permission

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