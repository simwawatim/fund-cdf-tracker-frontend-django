from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from base.models import UserProfile
from api.serializers.user_serializer import UserProfileSerializer
from django.db import IntegrityError
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

@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def userprofile_list(request):
    if request.method == 'GET':
        profiles = UserProfile.objects.all()
        serializer = UserProfileSerializer(profiles, many=True)
        return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)

    elif request.method == 'POST':
        serializer = UserProfileSerializer(data=request.data)
        if serializer.is_valid():
            try:
                profile = serializer.save()
                return Response({"status": "success", "data": UserProfileSerializer(profile).data},
                                status=status.HTTP_201_CREATED)
            except IntegrityError:
                return Response({"status": "error", "message": "Username or email already exists."},
                                status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                return Response({"status": "error", "message": str(e)},
                                status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"status": "error", "message": format_serializer_errors(serializer.errors)},
                            status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([AllowAny])
def userprofile_detail(request, pk):
    try:
        profile = UserProfile.objects.get(pk=pk)
    except UserProfile.DoesNotExist:
        return Response({"status": "error", "message": "UserProfile not found."},
                        status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = UserProfileSerializer(profile)
        return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)

    elif request.method in ['PUT', 'PATCH']:
        serializer = UserProfileSerializer(profile, data=request.data, partial=(request.method=='PATCH'))
        if serializer.is_valid():
            try:
                profile = serializer.save()
                return Response({"status": "success", "data": UserProfileSerializer(profile).data},
                                status=status.HTTP_200_OK)
            except IntegrityError:
                return Response({"status": "error", "message": "Username or email already exists."},
                                status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                return Response({"status": "error", "message": str(e)},
                                status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"status": "error", "message": format_serializer_errors(serializer.errors)},
                            status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        profile.user.delete()
        profile.delete()
        return Response({"status": "success", "message": "UserProfile deleted successfully."},
                        status=status.HTTP_200_OK)
