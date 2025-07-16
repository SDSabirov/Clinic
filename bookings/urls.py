from rest_framework.routers import DefaultRouter
from .views import BookingViewSet, PatientViewSet

router = DefaultRouter()
router.register(r'patients', PatientViewSet)
router.register(r'bookings', BookingViewSet)

urlpatterns = router.urls
