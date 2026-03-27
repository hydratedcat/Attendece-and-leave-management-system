from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    EMPLOYEE = 'EMPLOYEE'
    MANAGER = 'MANAGER'
    HR_ADMIN = 'HR_ADMIN'

    ROLE_CHOICES = [
        (EMPLOYEE, 'Employee'),
        (MANAGER, 'Manager'),
        (HR_ADMIN, 'HR Admin'),
    ]

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=EMPLOYEE)

    def __str__(self):
        return f"{self.username} ({self.role})"
