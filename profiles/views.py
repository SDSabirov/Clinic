from rest_framework import generics, permissions, status, filters
from rest_framework.response import Response
from rest_framework.exceptions import NotFound
from django_filters.rest_framework import DjangoFilterBackend

from .models import DoctorProfile
from .serializers import (
    UserWithProfileCreateSerializer,
    ProfileUpdateSerializer,
    DoctorProfileSerializer,
)

# Register new user with profile
class RegisterUserWithProfileView(generics.CreateAPIView):
    serializer_class = UserWithProfileCreateSerializer
    permission_classes = [permissions.AllowAny]

# Authenticated user: get or update their profile
class ProfileMeUpdateView(generics.RetrieveUpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ProfileUpdateSerializer

    def get_object(self):
        user = self.request.user
        # Make sure related_name is 'doctor_profile' and 'receptionist_profile'
        if hasattr(user, 'doctor_profile'):
            return user.doctor_profile
        elif hasattr(user, 'receptionist_profile'):
            return user.receptionist_profile
        # Add logic for other profile types if needed
        else:
            raise NotFound("Profile not found.")

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

# Public view: list all doctor profiles (with filters)
class DoctorProfileListView(generics.ListAPIView):
    queryset = DoctorProfile.objects.filter(is_active=True)
    serializer_class = DoctorProfileSerializer
    permission_classes = [permissions.AllowAny]

    # Optional: add search/filtering by specialty, name, etc.
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]
    search_fields = [
        'user__first_name',
        'user__last_name',
        'main_specialty',
        'other_specialties__name',
        'qualifications',
    ]
    ordering_fields = ['years_of_experience', 'main_specialty']
    filterset_fields = ['main_specialty', 'is_active', 'other_specialties']