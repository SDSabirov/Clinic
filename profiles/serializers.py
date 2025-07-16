from rest_framework import serializers
from users.serializers import UserCreateSerializer,UserUpdateSerializer
from .models import DoctorProfile, ReceptionistProfile

class DoctorProfileCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = DoctorProfile
        exclude = ['user', 'created_at', 'updated_at']

class ReceptionistProfileCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReceptionistProfile
        exclude = ['user', 'created_at', 'updated_at']


class UserWithProfileCreateSerializer(serializers.Serializer):
    user = UserCreateSerializer()
    profile = serializers.DictField(write_only=True)

    def create(self, validated_data):
        from django.db import transaction

        user_data = validated_data.pop('user')
        profile_data = validated_data.pop('profile')
        role = user_data.get('role')
        with transaction.atomic():
            user = UserCreateSerializer().create(user_data)
            if role == 'DOCTOR':
                profile = DoctorProfile.objects.create(user=user, **profile_data)
            elif role == 'RECEPTIONIST':
                profile = ReceptionistProfile.objects.create(user=user, **profile_data)
            else:
                # handle more roles or raise error
                raise serializers.ValidationError('Invalid role.')
        return {
            'user': user,
            'profile': profile,
        }

    def to_representation(self, instance):
        user = instance['user']
        profile = instance['profile']
        return {
            'user': UserCreateSerializer(user).data,
            'profile': str(profile)
        }

class DoctorProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = DoctorProfile
        exclude = ['user', 'created_at', 'updated_at']

class ReceptionistProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReceptionistProfile
        exclude = ['user', 'created_at', 'updated_at']

class ProfileUpdateSerializer(serializers.Serializer):
    user = UserUpdateSerializer(required=False)
    profile = serializers.DictField(required=False)

    def update(self, instance, validated_data):
        user_data = validated_data.get('user')
        profile_data = validated_data.get('profile')

        if user_data:
            for attr, value in user_data.items():
                setattr(instance.user, attr, value)
            instance.user.save()

        # instance = the profile (DoctorProfile, ReceptionistProfile, ...)
        if profile_data:
            for attr, value in profile_data.items():
                setattr(instance, attr, value)
            instance.save()
        return instance

    def to_representation(self, instance):
        # You could return all profile fields + user fields if you want
        user = instance.user
        data = UserUpdateSerializer(user).data
        data.update(self._profile_serializer(instance).data)
        return data

    def _profile_serializer(self, profile):
        if isinstance(profile, DoctorProfile):
            return DoctorProfileUpdateSerializer(profile)
        elif isinstance(profile, ReceptionistProfile):
            return ReceptionistProfileUpdateSerializer(profile)
        # ... Add more as needed
        else:
            raise Exception("Unknown profile type")
