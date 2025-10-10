from rest_framework.decorators import api_view, permission_classes
from base.models import Program, Project, Constituency
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.contrib.auth.models import User



@api_view(['GET'])
@permission_classes([AllowAny])
def dashboard_summary(request):
    """Returns summary statistics for dashboard."""
    total_users = User.objects.count()
    total_constituencies = Constituency.objects.count()
    total_programs = Program.objects.count()
    total_pending_projects = Project.objects.filter(status='pending').count()
    total_active_projects = Project.objects.filter(is_active=True).count()

    data = {
        "total_users": total_users,
        "total_constituencies": total_constituencies,
        "total_programs": total_programs,
        "pending_projects": total_pending_projects,
        "active_projects": total_active_projects,
    }

    response = {
        "status": "success",
        "data": [data]
    }

    return Response(response)
