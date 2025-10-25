from rest_framework.decorators import permission_classes, api_view
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.http import JsonResponse
from django.db.models.functions import TruncMonth
from django.db.models import Count
from django.contrib.auth.models import User
from base.models import Project
import calendar

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def stats_overview(request):
    user_stats = (
        User.objects.annotate(month=TruncMonth('date_joined'))
        .values('month')
        .annotate(total=Count('id'))
        .order_by('month')
    )
    project_stats = (
        Project.objects.annotate(month=TruncMonth('created_at'))
        .values('month')
        .annotate(total=Count('id'))
        .order_by('month')
    )

    user_dict = {u['month'].strftime("%b"): u['total'] for u in user_stats if u['month']}
    project_dict = {p['month'].strftime("%b"): p['total'] for p in project_stats if p['month']}


    months = list(calendar.month_abbr)[1:] 
    data = [
        {
            "name": month,
            "Users": user_dict.get(month, 0),
            "Projects": project_dict.get(month, 0)
        }
        for month in months
    ]

    return JsonResponse({
        "status": "success",
        "data": data
    })
