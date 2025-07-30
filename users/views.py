from django.contrib.auth import get_user_model
from rest_framework import viewsets, permissions
from rest_framework.views import APIView
from rest_framework.response import Response

from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .serializers import UserCreateSerializer

User = get_user_model()

class UserViewSet(viewsets.ModelViewSet):
    """
    Admin-only CRUD for users.
    """
    queryset = User.objects.all()
    serializer_class = UserCreateSerializer
    permission_classes = [permissions.IsAdminUser]


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['role'] = getattr(user, 'role', '')
        token['username'] = user.username
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        
        # Get user profile based on role
        profile_data = None
        if hasattr(self.user, 'doctorprofiles'):
            from profiles.serializers import DoctorProfileSerializer
            profile_data = DoctorProfileSerializer(self.user.doctorprofiles).data
        elif hasattr(self.user, 'receptionistprofiles'):
            from profiles.serializers import ReceptionistProfileUpdateSerializer
            profile_data = ReceptionistProfileUpdateSerializer(self.user.receptionistprofiles).data
        
        data['user'] = {
            'id': self.user.id,
            'username': self.user.username,
            'email': self.user.email,
            'role': getattr(self.user, 'role', ''),
            'profile': profile_data
        }
        return data


class LoginView(TokenObtainPairView):
    """
    POST /api/login/  →  { access, refresh, user: { … } }
    """
    serializer_class = CustomTokenObtainPairSerializer


class UserDetailView(APIView):
    """
    GET /api/user/  →  current user info
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        return Response({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'role': getattr(user, 'role', '')
        })
