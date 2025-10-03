from rest_framework import serializers
from base.models import Project, ProjectUpdate, FinancialReport, ProjectDocument, Constituency
from django.contrib.auth.models import User

# ---------------------------
# Project Serializer
# ---------------------------
class ProjectSerializer(serializers.ModelSerializer):
    constituency = serializers.PrimaryKeyRelatedField(queryset=Constituency.objects.filter(is_active=True))
    created_by = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=False, allow_null=True)
    updated_by = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=False, allow_null=True)

    class Meta:
        model = Project
        fields = [
            'id', 'name', 'constituency', 'project_type', 'description',
            'allocated_budget', 'actual_expenditure', 'status',
            'start_date', 'end_date', 'completion_percentage', 'beneficiaries_count',
            'project_manager', 'funding_source', 'location', 'remarks',
            'created_by', 'updated_by', 'created_at', 'updated_at', 'is_active'
        ]
        read_only_fields = ['created_at', 'updated_at', 'actual_expenditure', 'completion_percentage']

    def validate_name(self, value):
        if self.instance:
            qs = Project.objects.exclude(pk=self.instance.pk)
        else:
            qs = Project.objects.all()
        if qs.filter(name=value).exists():
            raise serializers.ValidationError("Project name must be unique.")
        return value


# ---------------------------
# ProjectUpdate Serializer
# ---------------------------
class ProjectUpdateSerializer(serializers.ModelSerializer):
    updated_by = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=False, allow_null=True)

    class Meta:
        model = ProjectUpdate
        fields = ['id', 'project', 'update_type', 'date', 'progress_percentage', 'remarks', 'updated_by', 'is_active']
        read_only_fields = ['date']

    def validate_progress_percentage(self, value):
        if value < 0 or value > 100:
            raise serializers.ValidationError("Progress must be between 0 and 100.")
        return value


# ---------------------------
# FinancialReport Serializer
# ---------------------------
class FinancialReportSerializer(serializers.ModelSerializer):
    reported_by = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=False, allow_null=True)

    class Meta:
        model = FinancialReport
        fields = ['id', 'project', 'date', 'description', 'category', 'amount_spent', 'reported_by', 'is_active']
        read_only_fields = ['date']

    def validate_amount_spent(self, value):
        if value < 0:
            raise serializers.ValidationError("Amount spent cannot be negative.")
        return value


# ---------------------------
# ProjectDocument Serializer
# ---------------------------

# serializers.py
from rest_framework import serializers
from base.models import ProjectDocument
from django.core.files.base import ContentFile
import requests, os

class ProjectDocumentSerializer(serializers.ModelSerializer):
    file_url = serializers.URLField(write_only=True, required=False)

    class Meta:
        model = ProjectDocument
        fields = ['id', 'project', 'title', 'doc_type', 'file', 'file_url', 'uploaded_by', 'uploaded_at']

    def create(self, validated_data):
        file_url = validated_data.pop('file_url', None)
        if file_url:
            resp = requests.get(file_url)
            if resp.status_code == 200:
                filename = os.path.basename(file_url)
                validated_data['file'] = ContentFile(resp.content, name=filename)
            else:
                raise serializers.ValidationError({"file_url": "Could not download the file."})

        return super().create(validated_data)

