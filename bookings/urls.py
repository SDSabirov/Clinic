from rest_framework.routers import DefaultRouter
from django.urls import path
from .views import BookingViewSet, PatientViewSet, PublicBookingCreateAPIView

router = DefaultRouter()
router.register(r'patients', PatientViewSet)
router.register(r'bookings', BookingViewSet)

urlpatterns = router.urls + [
    path('public-create/', PublicBookingCreateAPIView.as_view(), name='public_booking_create'),
]