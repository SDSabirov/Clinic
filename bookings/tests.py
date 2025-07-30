from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from decimal import Decimal
from datetime import timedelta

from .models import Patient, Booking
from profiles.models import DoctorProfile, Specialty

User = get_user_model()


class PatientModelTest(TestCase):
    def setUp(self):
        self.patient_data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'date_of_birth': '1990-01-01',
            'email': 'john.doe@example.com'
        }

    def test_patient_creation(self):
        patient = Patient.objects.create(**self.patient_data)
        self.assertEqual(patient.first_name, 'John')
        self.assertEqual(patient.last_name, 'Doe')
        self.assertEqual(patient.email, 'john.doe@example.com')
        self.assertEqual(str(patient), 'John Doe')

    def test_patient_email_unique(self):
        Patient.objects.create(**self.patient_data)
        with self.assertRaises(Exception):
            Patient.objects.create(**self.patient_data)

    def test_patient_ordering(self):
        patient1 = Patient.objects.create(
            first_name='Alice', last_name='Smith',
            date_of_birth='1985-01-01', email='alice@example.com'
        )
        patient2 = Patient.objects.create(
            first_name='Bob', last_name='Johnson', 
            date_of_birth='1990-01-01', email='bob@example.com'
        )
        patients = list(Patient.objects.all())
        self.assertEqual(patients[0], patient2)  # Johnson comes before Smith
        self.assertEqual(patients[1], patient1)


class BookingModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='doctor1',
            email='doctor1@example.com',
            password='testpass123',
            role=User.ROLE_DOCTOR
        )
        self.doctor = DoctorProfile.objects.create(
            user=self.user,
            main_specialty='Cardiology',
            years_of_experience=5
        )
        self.patient = Patient.objects.create(
            first_name='Jane',
            last_name='Smith',
            date_of_birth='1985-05-15',
            email='jane@example.com'
        )

    def test_booking_creation(self):
        scheduled_time = timezone.now() + timedelta(days=1)
        booking = Booking.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            scheduled_at=scheduled_time,
            notes='Regular checkup',
            total=Decimal('100.00')
        )
        self.assertEqual(booking.patient, self.patient)
        self.assertEqual(booking.doctor, self.doctor)
        self.assertEqual(booking.total, Decimal('100.00'))
        self.assertEqual(booking.notes, 'Regular checkup')

    def test_booking_str_representation(self):
        scheduled_time = timezone.now() + timedelta(days=1)
        booking = Booking.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            scheduled_at=scheduled_time
        )
        expected_str = f"Booking: {self.patient} with {self.doctor} at {scheduled_time}"
        self.assertEqual(str(booking), expected_str)

    def test_booking_default_total(self):
        booking = Booking.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            scheduled_at=timezone.now() + timedelta(days=1)
        )
        self.assertEqual(booking.total, Decimal('0'))


class BookingAPITest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        
        # Create doctor user and profile
        self.doctor_user = User.objects.create_user(
            username='doctor1',
            email='doctor1@example.com',
            password='testpass123',
            role=User.ROLE_DOCTOR
        )
        self.doctor_profile = DoctorProfile.objects.create(
            user=self.doctor_user,
            main_specialty='Cardiology',
            years_of_experience=5
        )
        
        # Create receptionist user
        self.receptionist_user = User.objects.create_user(
            username='receptionist1',
            email='receptionist1@example.com',
            password='testpass123',
            role=User.ROLE_RECEPTIONIST
        )
        
        # Create patient
        self.patient = Patient.objects.create(
            first_name='John',
            last_name='Doe',
            date_of_birth='1990-01-01',
            email='john@example.com'
        )
        
        # Create booking
        self.booking = Booking.objects.create(
            patient=self.patient,
            doctor=self.doctor_profile,
            scheduled_at=timezone.now() + timedelta(days=1),
            notes='Test booking',
            total=Decimal('150.00')
        )

    def test_unauthenticated_access_denied(self):
        url = reverse('booking-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_doctor_can_view_own_bookings(self):
        self.client.force_authenticate(user=self.doctor_user)
        url = reverse('booking-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], self.booking.id)

    def test_doctor_cannot_view_other_doctor_bookings(self):
        # Create another doctor and booking
        other_doctor_user = User.objects.create_user(
            username='doctor2',
            email='doctor2@example.com',
            password='testpass123',
            role=User.ROLE_DOCTOR
        )
        other_doctor_profile = DoctorProfile.objects.create(
            user=other_doctor_user,
            main_specialty='Neurology',
            years_of_experience=3
        )
        Booking.objects.create(
            patient=self.patient,
            doctor=other_doctor_profile,
            scheduled_at=timezone.now() + timedelta(days=2)
        )
        
        self.client.force_authenticate(user=self.doctor_user)
        url = reverse('booking-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)  # Only own booking

    def test_receptionist_can_view_all_bookings(self):
        self.client.force_authenticate(user=self.receptionist_user)
        url = reverse('booking-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_create_booking_authenticated(self):
        self.client.force_authenticate(user=self.receptionist_user)
        url = reverse('booking-list')
        data = {
            'patient': self.patient.id,
            'doctor': self.doctor_profile.id,
            'scheduled_at': (timezone.now() + timedelta(days=3)).isoformat(),
            'notes': 'New appointment',
            'total': '200.00'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Booking.objects.count(), 2)

    def test_update_booking(self):
        self.client.force_authenticate(user=self.receptionist_user)
        url = reverse('booking-detail', kwargs={'pk': self.booking.id})
        data = {
            'notes': 'Updated notes',
            'total': '175.00'
        }
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.booking.refresh_from_db()
        self.assertEqual(self.booking.notes, 'Updated notes')
        self.assertEqual(self.booking.total, Decimal('175.00'))

    def test_delete_booking(self):
        self.client.force_authenticate(user=self.receptionist_user)
        url = reverse('booking-detail', kwargs={'pk': self.booking.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Booking.objects.count(), 0)


class PublicBookingAPITest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.doctor_user = User.objects.create_user(
            username='doctor1',
            email='doctor1@example.com',
            password='testpass123',
            role=User.ROLE_DOCTOR
        )
        self.doctor_profile = DoctorProfile.objects.create(
            user=self.doctor_user,
            main_specialty='Cardiology',
            years_of_experience=5
        )

    def test_public_booking_creation_new_patient(self):
        url = reverse('public_booking_create')
        data = {
            'doctor': self.doctor_profile.id,
            'scheduled_at': (timezone.now() + timedelta(days=1)).isoformat(),
            'notes': 'Public booking',
            'total': '100.00',
            'patient': {
                'first_name': 'Alice',
                'last_name': 'Johnson',
                'email': 'alice.johnson@example.com',
                'date_of_birth': '1990-05-15'
            }
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Patient.objects.count(), 1)
        self.assertEqual(Booking.objects.count(), 1)
        
        patient = Patient.objects.first()
        self.assertEqual(patient.email, 'alice.johnson@example.com')

    def test_public_booking_creation_existing_patient(self):
        # Create existing patient
        existing_patient = Patient.objects.create(
            first_name='Bob',
            last_name='Smith',
            date_of_birth='1980-01-01',
            email='bob@example.com'
        )
        
        url = reverse('public_booking_create')
        data = {
            'doctor': self.doctor_profile.id,
            'scheduled_at': (timezone.now() + timedelta(days=1)).isoformat(),
            'notes': 'Public booking',
            'patient': {
                'first_name': 'Bob',
                'last_name': 'Smith',
                'email': 'bob@example.com',
                'date_of_birth': '1980-01-01'
            }
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Patient.objects.count(), 1)  # No new patient created
        self.assertEqual(Booking.objects.count(), 1)

    def test_public_booking_missing_patient_data(self):
        url = reverse('public_booking_create')
        data = {
            'doctor': self.doctor_profile.id,
            'scheduled_at': (timezone.now() + timedelta(days=1)).isoformat(),
            'notes': 'Public booking'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('patient', response.data)


class PatientAPITest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='receptionist1',
            email='receptionist1@example.com',
            password='testpass123',
            role=User.ROLE_RECEPTIONIST
        )
        self.patient = Patient.objects.create(
            first_name='John',
            last_name='Doe',
            date_of_birth='1990-01-01',
            email='john@example.com'
        )

    def test_patient_list_requires_authentication(self):
        url = reverse('patient-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authenticated_user_can_list_patients(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('patient-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_create_patient(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('patient-list')
        data = {
            'first_name': 'Jane',
            'last_name': 'Smith',
            'date_of_birth': '1985-05-15',
            'email': 'jane@example.com'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Patient.objects.count(), 2)