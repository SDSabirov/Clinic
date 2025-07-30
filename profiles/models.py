from django.db import models
from django.conf import settings
from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _


class BaseProfile(models.Model):
    """
    Abstract base for common profile attributes and metadata.
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="%(class)ss"
    )
    avatar = models.ImageField(
        upload_to="profiles/avatars/",
        blank=True,
        null=True,
        help_text=_("Profile picture")
    )
    phone_number = models.CharField(
        max_length=20,
        blank=True,
        validators=[
            RegexValidator(
                regex=r"^\+?1?\d{9,15}$",
                message=_("Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
            )
        ],
        help_text=_("Contact phone number")
    )
    address = models.TextField(
        blank=True,
        help_text=_("Full mailing address")
    )
    bio = models.TextField(
        blank=True,
        help_text=_("Short bio or profile summary")
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ['-updated_at']

    def __str__(self):
        return getattr(self.user, 'get_full_name', lambda: str(self.user))()

class Specialty(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class DoctorProfile(BaseProfile):
    """
    Profile for doctor users with clinical credentials and availability.
    """
   
    main_specialty = models.CharField(
        max_length=100,
        help_text=_("Medical specialty, e.g., 'Cardiology'")
    )
    other_specialties = models.ManyToManyField(
        Specialty,
        related_name='doctors',
        blank=True,
        help_text=_("Other specialties for the doctor")
    )
    qualifications = models.CharField(
        max_length=255,
        blank=True,
        help_text=_("Comma-separated qualifications/degrees")
    )
    license_number = models.CharField(
        max_length=50,
        unique=True,
        null=True,
        blank=True,
        help_text=_("Medical license or registration number")
    )
    years_of_experience = models.PositiveSmallIntegerField(
        default=0,
        help_text=_("Total years in clinical practice")
    )
    is_active = models.BooleanField(
        default=True,
        help_text=_("Toggle if the doctor is currently active")
    )

    class Meta:
        verbose_name = _("Doctor Profile")
        verbose_name_plural = _("Doctor Profiles")
        indexes = [
            models.Index(fields=['main_specialty']),
            models.Index(fields=['license_number']),
        ]

    @property
    def average_rating(self):
        """Compute average rating from associated reviews."""
        return self.reviews.aggregate(models.Avg('rating'))['rating__avg'] or 0

    def __str__(self):
        name = self.user.get_full_name() or self.user.username
        return f"Dr. {name} ({self.main_specialty})"

#achievments for doctor that will be educations certification internship etc     
class Achievement(models.Model):
    EDUCATION = 'education'
    INTERNSHIP = 'internship'
    CERTIFICATION = 'certification'
    ACHIEVEMENT_TYPES = [
        (EDUCATION, 'Education'),
        (INTERNSHIP, 'Internship'),
        (CERTIFICATION, 'Certification'),
    ]

    doctor = models.ForeignKey(
        'DoctorProfile',
        related_name='achievements',
        on_delete=models.CASCADE
    )
    type = models.CharField(
        max_length=20,
        choices=ACHIEVEMENT_TYPES
    )
    name = models.CharField(max_length=255, help_text="Degree, Certification, or Internship Name")
    institution = models.CharField(max_length=255, blank=True, help_text="Where it was earned")
    year = models.PositiveSmallIntegerField(blank=True, null=True)
    details = models.TextField(blank=True, help_text="Additional info (optional)")

    class Meta:
        verbose_name = "Achievement"
        verbose_name_plural = "Achievements"

    def __str__(self):
        return f"{self.get_type_display()}: {self.name} ({self.institution})"


class ReceptionistProfile(BaseProfile):
    """
    Profile for receptionist users with shift details.
    """
 
    phone_extension = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        help_text=_("Internal phone extension")
    )
    shift_start = models.TimeField(
        help_text=_("Daily shift start time"),
        blank=True,
        null=True,
        
    )
    shift_end = models.TimeField(
        help_text=_("Daily shift end time"),
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = _("Receptionist Profile")
        verbose_name_plural = _("Receptionist Profiles")
        indexes = [
            models.Index(fields=['shift_start', 'shift_end']),
        ]

    def __str__(self):
        name = self.user.get_full_name() or self.user.username
        return f"Receptionist {name} ({self.shift_start.strftime('%H:%M')}-{self.shift_end.strftime('%H:%M')})"


class DoctorReview(models.Model):
    """
    Patient reviews and ratings for doctors.
    """
    doctor = models.ForeignKey(
        DoctorProfile,
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    reviewer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text=_("User who submitted the review")
    )
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text=_("Rating from 1 (worst) to 5 (best)")
    )
    comment = models.TextField(
        blank=True,
        help_text=_("Optional review comments")
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['doctor']),
        ]

    def __str__(self):
        return f"Review for {self.doctor} — {self.rating} stars"


class TimetableEntry(models.Model):
    """
    Weekly availability slots for doctors.
    """
    class WeekDay(models.IntegerChoices):
        MONDAY = 0, _('Monday')
        TUESDAY = 1, _('Tuesday')
        WEDNESDAY = 2, _('Wednesday')
        THURSDAY = 3, _('Thursday')
        FRIDAY = 4, _('Friday')
        SATURDAY = 5, _('Saturday')
        SUNDAY = 6, _('Sunday')

    doctor = models.ForeignKey(
        DoctorProfile,
        on_delete=models.CASCADE,
        related_name='timetable_entries'
    )
    day_of_week = models.IntegerField(
        choices=WeekDay.choices,
        help_text=_("Day of the week")
    )
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_active = models.BooleanField(
        default=True,
        help_text=_("Whether this time slot is active")
    )

    class Meta:
        verbose_name = _("Timetable Entry")
        verbose_name_plural = _("Timetable Entries")
        ordering = ['doctor', 'day_of_week', 'start_time']
        unique_together = [('doctor', 'day_of_week', 'start_time', 'end_time')]

    def __str__(self):
        return f"{self.doctor} — {self.get_day_of_week_display()} {self.start_time.strftime('%H:%M')}-{self.end_time.strftime('%H:%M')}"
