from utils.send_mail import send_welcome_email
from rest_framework import serializers
from django.contrib.auth.models import User
from base.models import UserProfile, Constituency
from django.conf import settings
import random
import string


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']
        extra_kwargs = {
            'username': {'required': True},
            'email': {'required': True}
        }

    def update(self, instance, validated_data):
        username = validated_data.get('username', instance.username)
        email = validated_data.get('email', instance.email)

        if User.objects.exclude(pk=instance.pk).filter(username=username).exists():
            raise serializers.ValidationError({"username": "A user with that username already exists."})
        if User.objects.exclude(pk=instance.pk).filter(email=email).exists():
            raise serializers.ValidationError({"email": "A user with that email already exists."})


        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    constituency = serializers.PrimaryKeyRelatedField(
        queryset=Constituency.objects.filter(is_active=True),
        required=False,
        allow_null=True
    )
    profile_picture = serializers.ImageField(required=False, allow_null=True)
    cover_picture = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = UserProfile
        fields = [
            'id', 'user', 'role', 'phone', 'constituency',
            'profile_picture', 'cover_picture',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        request = self.context.get('request')
        if instance.profile_picture and hasattr(instance.profile_picture, 'url'):
            data['profile_picture'] = (
                request.build_absolute_uri(instance.profile_picture.url)
                if request else instance.profile_picture.url
            )
        else:
            data['profile_picture'] = settings.MEDIA_URL + 'profiles/default_profile.jpg'
        if instance.cover_picture and hasattr(instance.cover_picture, 'url'):
            data['cover_picture'] = (
                request.build_absolute_uri(instance.cover_picture.url)
                if request else instance.cover_picture.url
            )
        else:
            data['cover_picture'] = settings.MEDIA_URL + 'covers/default_cover.jpg'

        return data

    def validate_role(self, value):
        if value not in ['admin', 'officer', 'viewer']:
            raise serializers.ValidationError("Invalid role selected.")
        return value

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        if User.objects.filter(username=user_data['username']).exists():
            raise serializers.ValidationError({"user": {"username": "Username already exists."}})

        if User.objects.filter(email=user_data['email']).exists():
            raise serializers.ValidationError({"user": {"email": "Email already exists."}})

        password = self.generate_password()
        email_sent = send_welcome_email(
            recipient=user_data['email'],
            username=user_data['username'],
            password=password
        )

        if not email_sent:
            raise serializers.ValidationError({"email": "Failed to send login details. User not created."})


        user = User.objects.create(**user_data)
        user.set_password(password)
        user.save()

        profile = UserProfile.objects.create(user=user, **validated_data)

        return profile


    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', None)
        if user_data:
            user_serializer = UserSerializer(instance.user, data=user_data, partial=True)
            user_serializer.is_valid(raise_exception=True)
            user_serializer.save()

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance

    def generate_password(self, length=8):
        return ''.join(random.choices(string.ascii_letters + string.digits, k=length))
