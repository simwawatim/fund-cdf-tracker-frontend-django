from django.conf import settings
from rest_framework import serializers
from django.contrib.auth.models import User
from base.models import UserProfile, Constituency
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
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
        """
        Custom update that ignores duplicate username/email errors
        for the same user.
        """
        username = validated_data.get('username', instance.username)
        email = validated_data.get('email', instance.email)

        # Skip duplicate check for the same user
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

    class Meta:
        model = UserProfile
        fields = ['id', 'user', 'role', 'phone', 'constituency', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

    def validate_role(self, value):
        if value not in ['admin', 'officer', 'viewer']:
            raise serializers.ValidationError("Invalid role selected.")
        return value

    def generate_password(self, length=8):
        return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

    def create(self, validated_data):
        user_data = validated_data.pop('user')

        # Check unique username/email
        if User.objects.filter(username=user_data['username']).exists():
            raise serializers.ValidationError({"user": {"username": "Username already exists."}})
        if User.objects.filter(email=user_data['email']).exists():
            raise serializers.ValidationError({"user": {"email": "Email already exists."}})

        # Create user and password
        password = self.generate_password()
        user = User.objects.create(**user_data)
        user.set_password(password)
        user.save()

        # Create profile
        profile = UserProfile.objects.create(user=user, **validated_data)

        # Send email
        subject = "Your CDF Portal Account"
        from_email = settings.DEFAULT_FROM_EMAIL
        to_email = user.email
        login_url = "http://127.0.0.1:8000/login/"

        html_content = render_to_string(
            "emails/new_user.html",
            {
                "first_name": user.first_name,
                "last_name": user.last_name,
                "username": user.username,
                "password": password,
                "login_url": login_url
            }
        )

        msg = EmailMultiAlternatives(subject, html_content, from_email, [to_email])
        msg.attach_alternative(html_content, "text/html")
        msg.send()

        return profile

    def update(self, instance, validated_data):
        """
        Update user profile and nested user safely.
        """
        user_data = validated_data.pop('user', None)
        if user_data:
            user_serializer = UserSerializer(instance.user, data=user_data, partial=True)
            user_serializer.is_valid(raise_exception=True)
            user_serializer.save()

        # Update profile fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
