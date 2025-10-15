from rest_framework import serializers
from base.models import ProjectComment, UserProfile


class UserProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = UserProfile
        fields = ['id', 'username', 'role', 'phone', 'constituency']


class ProjectCommentSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.user.username', read_only=True)
    user_profile = UserProfileSerializer(source='user', read_only=True)

    class Meta:
        model = ProjectComment
        fields = [
            'id',
            'project',
            'user',
            'user_name',
            'user_profile',
            'message',
            'parent',
            'created_at',
            'updated_at',
            'is_active',
        ]
        read_only_fields = ['created_at', 'updated_at', 'user_name', 'user_profile']
