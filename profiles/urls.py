from django.urls import path
from .views import RegisterUserWithProfileView, ProfileMeUpdateView, DoctorProfileListView

urlpatterns = [
    path('register/', RegisterUserWithProfileView.as_view(), name='register'),
    path('me/', ProfileMeUpdateView.as_view(), name='profile-me'),
    path('doctors/', DoctorProfileListView.as_view(), name='doctor-list'),
]