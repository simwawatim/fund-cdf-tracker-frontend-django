from rest_framework import serializers
from base.models import Constituency

class ConstituencySerializer(serializers.ModelSerializer):
    class Meta:
        model = Constituency
        fields = ['id', 'name', 'district', 'constituency_code',
                  'is_active', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at', 'constituency_code']

    def validate_name(self, value):
        qs = Constituency.objects.filter(name=value)
        if self.instance:
            qs = qs.exclude(id=self.instance.id)
        if qs.exists():
            raise serializers.ValidationError("Constituency with this name already exists.")
        return value