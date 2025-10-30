from rest_framework import serializers
from django.contrib.auth.models import User
from base.models import UserProfile, Constituency
from django.conf import settings

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
    profile_picture = serializers.SerializerMethodField()
    cover_picture = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = [
            'id', 'user', 'role', 'phone', 'constituency',
            'profile_picture', 'cover_picture',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def get_profile_picture(self, obj):
        if obj.profile_picture and hasattr(obj.profile_picture, 'url'):
            return obj.profile_picture.url
        return settings.MEDIA_URL + 'profiles/default_profile.jpg'

    def get_cover_picture(self, obj):
        if obj.cover_picture and hasattr(obj.cover_picture, 'url'):
            return obj.cover_picture.url
        return settings.MEDIA_URL + 'covers/default_cover.jpg'

    def validate_role(self, value):
        if value not in ['admin', 'officer', 'viewer']:
            raise serializers.ValidationError("Invalid role selected.")
        return value

    def create(self, validated_data):
        user_data = validated_data.pop('user')

        # Check unique username/email
        if User.objects.filter(username=user_data['username']).exists():
            raise serializers.ValidationError({"user": {"username": "Username already exists."}})
        if User.objects.filter(email=user_data['email']).exists():
            raise serializers.ValidationError({"user": {"email": "Email already exists."}})

        # Create user
        password = self.generate_password()
        user = User.objects.create(**user_data)
        user.set_password(password)
        user.save()

        # Create profile
        profile = UserProfile.objects.create(user=user, **validated_data)

        # Send email logic here...

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
        import random, string
        password = ''.join(random.choices(string.ascii_letters + string.digits, k=length))
        return password
