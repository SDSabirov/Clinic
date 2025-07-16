from django.db import models
from django.conf import settings
from profiles.models import DoctorProfile

class Patient(models.Model):
    """
    Represents a patient in the clinic.
    """
    first_name    = models.CharField(max_length=100)
    last_name     = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    email         = models.EmailField(unique=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['last_name', 'first_name']
        verbose_name = 'Patient'
        verbose_name_plural = 'Patients'

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Booking(models.Model):
    """
    Represents an appointment booking between a patient and a doctor.
    """
    patient      = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name='bookings'
    )
    doctor       = models.ForeignKey(
        DoctorProfile,
        on_delete=models.CASCADE,
        related_name='bookings'
    )
    scheduled_at = models.DateTimeField()
    notes        = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-scheduled_at']
        verbose_name = 'Booking'
        verbose_name_plural = 'Bookings'

    def __str__(self):
        return f"Booking: {self.patient} with {self.doctor} at {self.scheduled_at}"