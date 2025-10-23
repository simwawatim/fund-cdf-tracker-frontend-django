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



from django.urls import path
from api.views.comment_views import project_comment_detail, project_comments_list_create
from api.views.graph_view import stats_overview
from api.views.project_views import financial_report_detail, financial_report_list, project_detail, project_document_detail, project_document_list, project_list, project_update_detail, project_update_list
from api.views.stats_view import dashboard_summary
from api.views.user_views import userprofile_list, userprofile_detail
from api.views.constituency_views import constituency_list, constituency_detail
from api.views.program_view import program_detail, program_list

from api.views.auth_views import (
    login,
)


urlpatterns = [
    path('api/users/v1/', userprofile_list, name='userprofile-list'),
    path('api/users/v1/<int:pk>/', userprofile_detail, name='userprofile-detail'),
    path('api/constituencies/v1/', constituency_list, name='constituency-list'),
    path('api/constituencies/v1/<int:pk>/', constituency_detail, name='constituency-detail'),
    path('api/projects/v1/', project_list, name='project-list'),
    path('api/projects/v1/<int:pk>/', project_detail, name='project-detail'),

    # ---------------------------
    # Project URLs
    # ---------------------------
    path('api/projects/v1/', project_list, name='project-list'),
    path('api/projects/v1/<int:pk>/', project_detail, name='project-detail'),

    # ---------------------------
    # Project Update URLs
    # ---------------------------
    path('api/project-updates/v1/', project_update_list, name='project-update-list'),
    path('api/project-updates/v1/<int:pk>/', project_update_detail, name='project-update-detail'),

    # ---------------------------
    # Financial Report URLs
    # ---------------------------
    path('api/financial-reports/v1/', financial_report_list, name='financial-report-list'),
    path('api/financial-reports/v1/<int:pk>/', financial_report_detail, name='financial-report-detail'),

    # ---------------------------
    # Project Document URLs
    # ---------------------------
    path('api/project-documents/v1/', project_document_list, name='project-document-list'),
    path('api/project-documents/v1/<int:pk>/', project_document_detail, name='project-document-detail'),

    # ---------------------------
    # Program URLs
    # ---------------------------

    path('api/programs/v1', program_list),
    path('api/programs/v1/<int:pk>', program_detail),

    # ---------------------------
    # Comment URLs
    # ---------------------------

    path('api/comments/', project_comments_list_create, name='comments-list-create'),
    path('api/comments/<int:pk>/', project_comment_detail, name='comment-detail'),

    # ---------------------------
    # Stats URLs
    # ---------------------------
    path('api/dashboard-summary/', dashboard_summary, name='dashboard-summary'),
    path('api/stats/', stats_overview, name='stats_overview'),

    # JWT auth endpoints
    path('api/login/v1', login, name='custom-login'),
]