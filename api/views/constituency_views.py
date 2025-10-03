from django.db import IntegrityError
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from base.models import Constituency
from api.serializers.constituency_serializer import ConstituencySerializer
from rest_framework.permissions import AllowAny
from rest_framework.decorators import api_view, permission_classes

def format_serializer_errors(errors):
    """Convert DRF errors to simple dict"""
    formatted = {}
    for field, value in errors.items():
        if isinstance(value, list):
            formatted[field] = [str(v) for v in value]
        else:
            formatted[field] = str(value)
    return formatted

# ---------------------------
# Constituency CRUD
# ---------------------------
@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def constituency_list(request):
    if request.method == 'GET':
        items = Constituency.objects.all()
        serializer = ConstituencySerializer(items, many=True)
        return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)

    elif request.method == 'POST':
        serializer = ConstituencySerializer(data=request.data)
        if serializer.is_valid():
            try:
                instance = serializer.save()
                return Response({"status": "success", "data": ConstituencySerializer(instance).data},
                                status=status.HTTP_201_CREATED)
            except IntegrityError as e:
                return Response({"status": "error", "message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"status": "error", "message": format_serializer_errors(serializer.errors)},
                            status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([AllowAny])
def constituency_detail(request, pk):
    try:
        item = Constituency.objects.get(pk=pk)
    except Constituency.DoesNotExist:
        return Response({"status": "error", "message": "Constituency not found."},
                        status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = ConstituencySerializer(item)
        return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)

    elif request.method in ['PUT', 'PATCH']:
        serializer = ConstituencySerializer(item, data=request.data, partial=(request.method=='PATCH'))
        if serializer.is_valid():
            try:
                instance = serializer.save()
                return Response({"status": "success", "data": ConstituencySerializer(instance).data},
                                status=status.HTTP_200_OK)
            except IntegrityError as e:
                return Response({"status": "error", "message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"status": "error", "message": format_serializer_errors(serializer.errors)},
                            status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        item.delete()
        return Response({"status": "success", "message": "Constituency soft-deleted successfully."},
                        status=status.HTTP_200_OK)