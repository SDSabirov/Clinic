from django.urls import path, include
from django.contrib import admin

urlpatterns = [
    path('admin/', admin.site.urls), 
    path('api/', include('users.urls')),
    path('api/', include('bookings.urls')),
    path('api/profiles/', include('profiles.urls')),
]