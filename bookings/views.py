from rest_framework import viewsets, permissions,generics,serializers
from .models import Patient, Booking
from .serializers import PatientSerializer, BookingSerializer, PublicBookingSerializer

class PatientViewSet(viewsets.ModelViewSet):
    """
    CRUD API for Patients.
    """
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer
    permission_classes = [permissions.IsAuthenticated]

class BookingViewSet(viewsets.ModelViewSet):
    """
    CRUD API for Booking.
    """
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        # If doctor, only their bookings
        if hasattr(user, 'doctor_profile'):
            return self.queryset.filter(doctor__user=user)
        # If receptionist or superuser, see all bookings
        return self.queryset
    
class PublicBookingCreateAPIView(generics.CreateAPIView):
    queryset = Booking.objects.all()
    serializer_class = PublicBookingSerializer
    permission_classes = [permissions.AllowAny]  # Anyone can create