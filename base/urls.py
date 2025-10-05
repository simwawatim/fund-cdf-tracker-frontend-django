from django.urls import path
from api.views.project_views import financial_report_detail, financial_report_list, project_detail, project_document_detail, project_document_list, project_list, project_update_detail, project_update_list
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

    # JWT auth endpoints
    path('api/login/v1', login, name='custom-login'),
]
