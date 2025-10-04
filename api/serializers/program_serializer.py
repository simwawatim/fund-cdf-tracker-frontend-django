from rest_framework import serializers
from base.models import Program


class ProgramSerializer(serializers.ModelSerializer):
    class Meta:
        model = Program
        fields = [
            'id',
            'name',
            'description',
        ]
        extra_kwargs = {
            'name': {'required': True},
            'description': {'required': True}
        }