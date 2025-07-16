from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    ROLE_RECEPTIONIST = 'RECEPTIONIST'
    ROLE_DOCTOR      = 'DOCTOR'

    ROLE_CHOICES = [
        (ROLE_RECEPTIONIST, 'Receptionist'),
        (ROLE_DOCTOR,      'Doctor'),
    ]

    # blank so superusers can omit role
    role = models.CharField(
        max_length=15,
        choices=ROLE_CHOICES,
        blank=True,
        help_text="Receptionist or Doctor; superusers leave blank."
    )

    def is_receptionist(self):
        return self.role == self.ROLE_RECEPTIONIST

    def is_doctor(self):
        return self.role == self.ROLE_DOCTOR