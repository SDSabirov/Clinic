
from rest_framework import generics, permissions
from .serializers import UserWithProfileCreateSerializer,ProfileUpdateSerializer
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .models import DoctorProfile, ReceptionistProfile
from .serializers import ProfileUpdateSerializer
from rest_framework.exceptions import NotFound

class RegisterUserWithProfileView(generics.CreateAPIView):
    serializer_class = UserWithProfileCreateSerializer
    permission_classes = [permissions.AllowAny]


class ProfileMeUpdateView(generics.RetrieveUpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ProfileUpdateSerializer

    def get_object(self):
        # Detect which profile this user has
        user = self.request.user
        if hasattr(user, 'doctor_profile'):
            return user.doctor_profile
        elif hasattr(user, 'receptionist_profile'):
            return user.receptionist_profile
        # Add other roles...
        else:
            raise NotFound("Profile not found.")

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)