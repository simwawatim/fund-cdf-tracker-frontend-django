from django.urls import path
from api.views.change_password import change_password
from api.views.comment_views import project_comment_detail, project_comments_list_create
from api.views.contractor_views import contractor_detail, contractor_list_create
from api.views.forget_password_views import PasswordResetConfirmView, PasswordResetRequestView
from api.views.graph_view import stats_overview
from api.views.project_views import financial_report_detail, financial_report_list, project_detail, project_document_detail, project_document_list, project_list, project_update_detail, project_update_list
from api.views.stats_view import dashboard_summary
from api.views.user_views import get_profile_picture, get_profile_picture_by_profile_id, userprofile_list, userprofile_detail,  update_user_profile
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
    path('api/change-password/v1', change_password, name='change-password'),
    path('api/users/update-profile/v1/<int:id>/',  update_user_profile),
    path('api/user-profiles/picture/<int:user_id>/', get_profile_picture, name='get-profile-picture'),
    path('api/user-profiles-by-profile-id/picture/<int:id>/', get_profile_picture_by_profile_id, name='get-profile-picture'),
    

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


    #Password RestEnpoints
    path("api/password-reset/", PasswordResetRequestView.as_view(), name="api-password-reset"),
    path("api/password-reset-confirm/", PasswordResetConfirmView.as_view(), name="api-password-reset-confirm"),

    #Contractor Endpoints
    path("api/contractors/v1", contractor_list_create, name="contractor_list_create"),
    path("api/contractors/v1/<int:pk>/", contractor_detail, name="contractor_detail"),

]