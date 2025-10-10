from rest_framework import serializers
from base.models import ProjectComment

class ProjectCommentSerializer(serializers.ModelSerializer):
    user_name = serializers.ReadOnlyField(source='user.username')

    class Meta:
        model = ProjectComment
        fields = [
            'id',
            'project',
            'user',
            'user_name',
            'message',
            'parent',
            'created_at',
            'updated_at',
            'is_active',
        ]
        read_only_fields = ['created_at', 'updated_at', 'user_name']
