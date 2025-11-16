from rest_framework import serializers
from base.models import Contractor

class ContractorSerializer(serializers.ModelSerializer):

    class Meta:
        model = Contractor
        fields = "__all__"

    def validate_name(self, value):
        name = value.strip()
        contractor_id = self.instance.id if self.instance else None

        if Contractor.objects.exclude(id=contractor_id).filter(name__iexact=name).exists():
            raise serializers.ValidationError("A contractor with this name already exists.")

        return name
