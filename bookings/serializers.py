from rest_framework import serializers
from .models import Patient, Booking

class PatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = ['id', 'first_name', 'last_name', 'date_of_birth', 'email', 'created_at', 'updated_at']

class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = ['id', 'patient', 'doctor', 'scheduled_at', 'notes', 'created_at', 'updated_at','total']


class PublicBookingSerializer(serializers.ModelSerializer):
    patient = serializers.DictField(write_only=True)
    
    class Meta:
        model = Booking
        fields = ['id', 'patient', 'doctor', 'scheduled_at', 'notes', 'total', 'created_at', 'updated_at']
        
    def create(self, validated_data):
        patient_data = validated_data.pop('patient')
        
        # Create or get patient
        patient, created = Patient.objects.get_or_create(
            email=patient_data.get('email'),
            defaults={
                'first_name': patient_data.get('first_name'),
                'last_name': patient_data.get('last_name'),
                'date_of_birth': patient_data.get('date_of_birth', '1990-01-01'),
            }
        )
        
        # Create booking with patient
        booking = Booking.objects.create(patient=patient, **validated_data)
        return booking