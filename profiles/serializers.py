from rest_framework import serializers
from users.serializers import UserCreateSerializer, UserUpdateSerializer
from .models import DoctorProfile, ReceptionistProfile, Specialty, Achievement

class SpecialtySerializer(serializers.ModelSerializer):
    class Meta:
        model = Specialty
        fields = ['id', 'name']

class AchievementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Achievement
        fields = ['id', 'type', 'name', 'institution', 'year', 'details']

class DoctorProfileSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()  # Swap for a user serializer if needed
    other_specialties = SpecialtySerializer(many=True, read_only=True)
    other_specialties_ids = serializers.PrimaryKeyRelatedField(
        source='other_specialties',
        many=True,
        queryset=Specialty.objects.all(),
        write_only=True,
        required=False
    )
    achievements = AchievementSerializer(many=True, required=False)
    average_rating = serializers.FloatField(read_only=True)

    class Meta:
        model = DoctorProfile
        fields = [
            'id',
            'user',
            'main_specialty',
            'other_specialties',
            'other_specialties_ids',  # Writable list of IDs
            'qualifications',
            'license_number',
            'years_of_experience',
            'is_active',
            'average_rating',
            'achievements',
        ]

    def create(self, validated_data):
        # Pop writable specialties and achievements
        specialties = validated_data.pop('other_specialties', [])
        achievements_data = validated_data.pop('achievements', [])
        instance = super().create(validated_data)
        # Set ManyToMany specialties
        if specialties:
            instance.other_specialties.set(specialties)
        # Create related achievements
        for ach_data in achievements_data:
            Achievement.objects.create(doctor=instance, **ach_data)
        return instance

    def update(self, instance, validated_data):
        specialties = validated_data.pop('other_specialties', None)
        achievements_data = validated_data.pop('achievements', None)
        instance = super().update(instance, validated_data)
        # Update specialties if provided
        if specialties is not None:
            instance.other_specialties.set(specialties)
        # Update achievements (replace all, or implement custom logic)
        if achievements_data is not None:
            instance.achievements.all().delete()
            for ach_data in achievements_data:
                Achievement.objects.create(doctor=instance, **ach_data)
        return instance

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
            # Pop nested data for DoctorProfile if present
            specialties = profile_data.pop('other_specialties_ids', [])
            achievements_data = profile_data.pop('achievements', [])
            if role == 'DOCTOR':
                profile = DoctorProfile.objects.create(user=user, **profile_data)
                # Set specialties
                if specialties:
                    profile.other_specialties.set(specialties)
                # Create achievements
                for ach_data in achievements_data:
                    Achievement.objects.create(doctor=profile, **ach_data)
            elif role == 'RECEPTIONIST':
                profile = ReceptionistProfile.objects.create(user=user, **profile_data)
            else:
                raise serializers.ValidationError('Invalid role.')
        return {
            'user': user,
            'profile': profile,
        }

    def to_representation(self, instance):
        user = instance['user']
        profile = instance['profile']
        # Choose appropriate profile serializer
        if isinstance(profile, DoctorProfile):
            profile_data = DoctorProfileSerializer(profile).data
        elif isinstance(profile, ReceptionistProfile):
            profile_data = ReceptionistProfileCreateSerializer(profile).data
        else:
            profile_data = str(profile)
        return {
            'user': UserCreateSerializer(user).data,
            'profile': profile_data,
        }

class DoctorProfileUpdateSerializer(serializers.ModelSerializer):
    other_specialties_ids = serializers.PrimaryKeyRelatedField(
        source='other_specialties',
        many=True,
        queryset=Specialty.objects.all(),
        write_only=True,
        required=False
    )
    achievements = AchievementSerializer(many=True, required=False)

    class Meta:
        model = DoctorProfile
        exclude = ['user', 'created_at', 'updated_at']

    def update(self, instance, validated_data):
        specialties = validated_data.pop('other_specialties', None)
        achievements_data = validated_data.pop('achievements', None)
        instance = super().update(instance, validated_data)
        if specialties is not None:
            instance.other_specialties.set(specialties)
        if achievements_data is not None:
            instance.achievements.all().delete()
            for ach_data in achievements_data:
                Achievement.objects.create(doctor=instance, **ach_data)
        return instance

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

        if profile_data:
            # Handle nested specialties and achievements if present
            specialties = profile_data.pop('other_specialties_ids', None)
            achievements_data = profile_data.pop('achievements', None)
            for attr, value in profile_data.items():
                setattr(instance, attr, value)
            instance.save()
            if specialties is not None:
                instance.other_specialties.set(specialties)
            if achievements_data is not None:
                instance.achievements.all().delete()
                for ach_data in achievements_data:
                    Achievement.objects.create(doctor=instance, **ach_data)
        return instance

    def to_representation(self, instance):
        user = instance.user
        data = UserUpdateSerializer(user).data
        data.update(self._profile_serializer(instance).data)
        return data

    def _profile_serializer(self, profile):
        if isinstance(profile, DoctorProfile):
            return DoctorProfileUpdateSerializer(profile)
        elif isinstance(profile, ReceptionistProfile):
            return ReceptionistProfileUpdateSerializer(profile)
        else:
            raise Exception("Unknown profile type")