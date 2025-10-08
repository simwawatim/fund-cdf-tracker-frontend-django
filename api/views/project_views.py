from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db import IntegrityError
from base.models import Project, ProjectUpdate, FinancialReport, ProjectDocument
from api.serializers.project_serializers import (
   ProjectSerializer, ProjectUpdateSerializer, FinancialReportSerializer, ProjectDocumentSerializer
)


from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from base.models import ProjectUpdate, FinancialReport, ProjectDocument
from api.serializers.project_serializers import FinancialReportSerializer, ProjectDocumentSerializer, ProjectUpdateSerializer
from rest_framework.permissions import AllowAny
from rest_framework.decorators import api_view, permission_classes

def format_serializer_errors(errors):
    formatted = {}
    for field, value in errors.items():
        if isinstance(value, list):
            formatted[field] = [str(v) for v in value]
        else:
            formatted[field] = str(value)
    return formatted


# ---------------------------
# Project Views
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
                return Response({"status": "success", "data": ProjectSerializer(project).data},
                                status=status.HTTP_201_CREATED)
            except IntegrityError:
                return Response({"status": "error", "message": "Project with this name already exists."},
                                status=status.HTTP_400_BAD_REQUEST)
        return Response({"status": "error", "message": format_serializer_errors(serializer.errors)},
                        status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([AllowAny])
def project_detail(request, pk):
    try:
        project = Project.objects.get(pk=pk, is_active=True)
    except Project.DoesNotExist:
        return Response({"status": "error", "message": "Project not found."}, status=status.HTTP_404_NOT_FOUND)

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
                return Response({"status": "error", "message": "Project with this name already exists."},
                                status=status.HTTP_400_BAD_REQUEST)
        return Response({"status": "error", "message": format_serializer_errors(serializer.errors)},
                        status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        project.is_active = False
        project.save()
        return Response({"status": "success", "message": "Project archived (soft deleted)."})


def format_serializer_errors(errors):
    formatted = {}
    for field, value in errors.items():
        if isinstance(value, list):
            formatted[field] = [str(v) for v in value]
        else:
            formatted[field] = str(value)
    return formatted

# ---------------------------
# Project Update CRUD
# ---------------------------
@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def project_update_list(request):
    if request.method == 'GET':
        updates = ProjectUpdate.objects.filter(is_active=True)
        serializer = ProjectUpdateSerializer(updates, many=True)
        return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)

    elif request.method == 'POST':
        serializer = ProjectUpdateSerializer(data=request.data)
        if serializer.is_valid():
            update = serializer.save()
            # auto-update project completion
            update.project.update_completion()
            return Response({"status": "success", "data": ProjectUpdateSerializer(update).data},
                            status=status.HTTP_201_CREATED)
        else:
            return Response({"status": "error", "message": format_serializer_errors(serializer.errors)},
                            status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([AllowAny])
def project_update_detail(request, pk):
    try:
        update = ProjectUpdate.objects.filter(project=pk, is_active=True)
    except ProjectUpdate.DoesNotExist:
        return Response({"status": "error", "message": "Project update not found."}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = ProjectUpdateSerializer(update, many=True)
        return Response({"status": "success", "data": serializer.data})

    elif request.method in ['PUT', 'PATCH']:
        serializer = ProjectUpdateSerializer(update, data=request.data, partial=(request.method=='PATCH'))
        if serializer.is_valid():
            update = serializer.save()
            update.project.update_completion()
            return Response({"status": "success", "data": ProjectUpdateSerializer(update).data})
        else:
            return Response({"status": "error", "message": format_serializer_errors(serializer.errors)},
                            status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        update.is_active = False
        update.save()
        update.project.update_completion()
        return Response({"status": "success", "message": "Project update soft-deleted."})


# ---------------------------
# Financial Report CRUD
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
            return Response({"status": "success", "data": FinancialReportSerializer(report).data},
                            status=status.HTTP_201_CREATED)
        else:
            return Response({"status": "error", "message": format_serializer_errors(serializer.errors)},
                            status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([AllowAny])
def financial_report_detail(request, pk):
    try:
        report = FinancialReport.objects.get(pk=pk, is_active=True)
    except FinancialReport.DoesNotExist:
        return Response({"status": "error", "message": "Financial report not found."}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = FinancialReportSerializer(report)
        return Response({"status": "success", "data": serializer.data})

    elif request.method in ['PUT', 'PATCH']:
        serializer = FinancialReportSerializer(report, data=request.data, partial=(request.method=='PATCH'))
        if serializer.is_valid():
            report = serializer.save()
            report.project.update_expenditure()
            return Response({"status": "success", "data": FinancialReportSerializer(report).data})
        else:
            return Response({"status": "error", "message": format_serializer_errors(serializer.errors)},
                            status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        report.is_active = False
        report.save()
        report.project.update_expenditure()
        return Response({"status": "success", "message": "Financial report soft-deleted."})


# ---------------------------
# Project Document CRUD
# ---------------------------
@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def project_document_list(request):
    if request.method == 'GET':
        docs = ProjectDocument.objects.filter(is_active=True)
        serializer = ProjectDocumentSerializer(docs, many=True)
        return Response({"status": "success", "data": serializer.data})

    elif request.method == 'POST':
        serializer = ProjectDocumentSerializer(data=request.data)
        if serializer.is_valid():
            doc = serializer.save()
            return Response({"status": "success", "data": ProjectDocumentSerializer(doc).data},
                            status=status.HTTP_201_CREATED)
        else:
            return Response({"status": "error", "message": format_serializer_errors(serializer.errors)},
                            status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([AllowAny])
def project_document_detail(request, pk):
    try:
        doc = ProjectDocument.objects.get(pk=pk, is_active=True)
    except ProjectDocument.DoesNotExist:
        return Response({"status": "error", "message": "Project document not found."}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = ProjectDocumentSerializer(doc)
        return Response({"status": "success", "data": serializer.data})

    elif request.method in ['PUT', 'PATCH']:
        serializer = ProjectDocumentSerializer(doc, data=request.data, partial=(request.method=='PATCH'))
        if serializer.is_valid():
            doc = serializer.save()
            return Response({"status": "success", "data": ProjectDocumentSerializer(doc).data})
        else:
            return Response({"status": "error", "message": format_serializer_errors(serializer.errors)},
                            status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        doc.is_active = False
        doc.save()
        return Response({"status": "success", "message": "Project document soft-deleted."})