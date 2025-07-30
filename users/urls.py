from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import UserViewSet, LoginView, UserDetailView

router = DefaultRouter()
router.register('users', UserViewSet, basename='user')

urlpatterns = [
    # JWT login
    path('login/', LoginView.as_view(), name='token_obtain_pair'),
    # current-user endpoint
    path('user/', UserDetailView.as_view(), name='current_user'),
    # admin user CRUD
    path('', include(router.urls)),
]