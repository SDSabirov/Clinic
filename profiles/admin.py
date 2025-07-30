from django.contrib import admin

# Register your models here.
from .models import DoctorProfile,ReceptionistProfile
# Register your models here.

class DoctorProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'main_specialty', 'phone_number')  # example fields

admin.site.register(DoctorProfile, DoctorProfileAdmin)
