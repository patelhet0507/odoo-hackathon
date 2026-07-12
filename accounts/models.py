from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        FLEET_MANAGER = 'fleet_manager', 'Fleet Manager'
        DRIVER = 'driver', 'Driver'
        SAFETY_OFFICER = 'safety_officer', 'Safety Officer'
        FINANCIAL_ANALYST = 'financial_analyst', 'Financial Analyst'

    role = models.CharField(max_length=20, choices=Role.choices, default=Role.FLEET_MANAGER)
    phone = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.get_role_display()})"
