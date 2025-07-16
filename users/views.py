from rest_framework import viewsets, permissions
from django.contrib.auth import get_user_model
from .serializers import UserCreateSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
User = get_user_model()

class UserViewSet(viewsets.ModelViewSet):
    queryset         = User.objects.all()
    serializer_class = UserCreateSerializer
    permission_classes = [permissions.IsAdminUser]  

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # You can add custom claims here, for example:
        token['role'] = user.role
        token['username'] = user.username
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        # Optionally include more user info in the response
        data['user'] = {
            'id': self.user.id,
            'username': self.user.username,
            'email': self.user.email,
            'role': self.user.role,
        }
        return data

class LoginView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer