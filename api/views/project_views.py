from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.permissions import AllowAny
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from django.db import IntegrityError

from base.models import Project, ProjectUpdate, FinancialReport, ProjectDocument
from api.serializers.project_serializers import (
    ProjectSerializer, ProjectUpdateSerializer, FinancialReportSerializer, ProjectDocumentSerializer
)

# ---------------------------
# Helpers
# ---------------------------
def format_serializer_errors(errors):
    formatted = {}
    for field, value in errors.items():
        if isinstance(value, list):
            formatted[field] = [str(v) for v in value]
        else:
            formatted[field] = str(value)
    return formatted


# ---------------------------
# Projects CRUD
# ---------------------------
@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def project_list(request):
    if request.method == 'GET':
        projects = Project.objects.filter(is_active=True)
        serializer = ProjectSerializer(projects, many=True)
        return Response({"status": "success", "data": serializer.data})

    elif request.method == 'POST':
        serializer = ProjectSerializer(data=request.data)
        if serializer.is_valid():
            try:
                project = serializer.save()
                return Response({"status": "success", "data": ProjectSerializer(project).data}, status=status.HTTP_201_CREATED)
            except IntegrityError:
                return Response({"status": "error", "message": "Project with this name already exists."}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"status": "error", "message": format_serializer_errors(serializer.errors)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([AllowAny])
def project_detail(request, pk):
    project = get_object_or_404(Project, pk=pk, is_active=True)

    if request.method == 'GET':
        serializer = ProjectSerializer(project)
        return Response({"status": "success", "data": serializer.data})

    elif request.method in ['PUT', 'PATCH']:
        serializer = ProjectSerializer(project, data=request.data, partial=(request.method=='PATCH'))
        if serializer.is_valid():
            try:
                project = serializer.save()
                return Response({"status": "success", "data": ProjectSerializer(project).data})
            except IntegrityError:
                return Response({"status": "error", "message": "Project with this name already exists."}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"status": "error", "message": format_serializer_errors(serializer.errors)}, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        project.is_active = False
        project.save()
        return Response({"status": "success", "message": "Project archived (soft deleted)."})


# ---------------------------
# Project Updates CRUD
# ---------------------------
@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
@parser_classes([MultiPartParser, FormParser])
def project_update_list(request):
    if request.method == 'GET':
        updates = ProjectUpdate.objects.filter(is_active=True)
        serializer = ProjectUpdateSerializer(updates, many=True)
        return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)

    elif request.method == 'POST':
        serializer = ProjectUpdateSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            update = serializer.save()
            update.project.update_completion()
            return Response({"status": "success", "data": ProjectUpdateSerializer(update).data}, status=status.HTTP_201_CREATED)
        return Response({"status": "error", "message": format_serializer_errors(serializer.errors)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([AllowAny])
@parser_classes([MultiPartParser, FormParser])
def project_update_detail(request, pk):
    update = get_object_or_404(ProjectUpdate, pk=pk, is_active=True)

    if request.method == 'GET':
        serializer = ProjectUpdateSerializer(update)
        return Response({"status": "success", "data": serializer.data})

    elif request.method in ['PUT', 'PATCH']:
        serializer = ProjectUpdateSerializer(update, data=request.data, partial=(request.method=='PATCH'))
        if serializer.is_valid():
            update = serializer.save()
            update.project.update_completion()
            return Response({"status": "success", "data": ProjectUpdateSerializer(update).data})
        return Response({"status": "error", "message": format_serializer_errors(serializer.errors)}, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        update.is_active = False
        update.save()
        update.project.update_completion()
        return Response({"status": "success", "message": "Project update soft-deleted."})


# ---------------------------
# Financial Reports CRUD
# ---------------------------
@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def financial_report_list(request):
    if request.method == 'GET':
        reports = FinancialReport.objects.filter(is_active=True)
        serializer = FinancialReportSerializer(reports, many=True)
        return Response({"status": "success", "data": serializer.data})

    elif request.method == 'POST':
        serializer = FinancialReportSerializer(data=request.data)
        if serializer.is_valid():
            report = serializer.save()
            report.project.update_expenditure()
            return Response({"status": "success", "data": FinancialReportSerializer(report).data}, status=status.HTTP_201_CREATED)
        return Response({"status": "error", "message": format_serializer_errors(serializer.errors)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([AllowAny])
def financial_report_detail(request, pk):
    report = get_object_or_404(FinancialReport, pk=pk, is_active=True)

    if request.method == 'GET':
        serializer = FinancialReportSerializer(report)
        return Response({"status": "success", "data": serializer.data})

    elif request.method in ['PUT', 'PATCH']:
        serializer = FinancialReportSerializer(report, data=request.data, partial=(request.method=='PATCH'))
        if serializer.is_valid():
            report = serializer.save()
            report.project.update_expenditure()
            return Response({"status": "success", "data": FinancialReportSerializer(report).data})
        return Response({"status": "error", "message": format_serializer_errors(serializer.errors)}, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        report.is_active = False
        report.save()
        report.project.update_expenditure()
        return Response({"status": "success", "message": "Financial report soft-deleted."})


# ---------------------------
# Project Documents CRUD
# ---------------------------
@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
@parser_classes([MultiPartParser, FormParser])
def project_document_list(request):
    if request.method == 'GET':
        docs = ProjectDocument.objects.filter(is_active=True)
        serializer = ProjectDocumentSerializer(docs, many=True)
        return Response({"status": "success", "data": serializer.data})

    elif request.method == 'POST':
        serializer = ProjectDocumentSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            doc = serializer.save()
            return Response({"status": "success", "data": ProjectDocumentSerializer(doc).data}, status=status.HTTP_201_CREATED)
        return Response({"status": "error", "message": format_serializer_errors(serializer.errors)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([AllowAny])
def project_documents_by_project(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    documents = ProjectDocument.objects.filter(project=project, is_active=True)
    serializer = ProjectDocumentSerializer(documents, many=True)
    return Response({"status": "success", "data": serializer.data})
