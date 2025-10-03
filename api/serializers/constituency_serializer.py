from rest_framework import serializers
from base.models import Constituency

# ---------------------------
# Constituency Serializer
# ---------------------------
class ConstituencySerializer(serializers.ModelSerializer):
    class Meta:
        model = Constituency
        fields = ['id', 'name', 'county', 'constituency_code',
                  'is_active', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at', 'constituency_code']

    def validate_name(self, value):
        if Constituency.objects.filter(name=value).exists():
            raise serializers.ValidationError("Constituency with this name already exists.")
        return value