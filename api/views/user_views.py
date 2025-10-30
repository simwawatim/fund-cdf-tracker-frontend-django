from api.serializers.user_serializer import UserProfileSerializer
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.contrib.auth.models import User
from django.db import IntegrityError
from base.models import UserProfile
from rest_framework import status
from django.conf import settings
import json



def format_serializer_errors(errors):
    formatted = {}
    for field, value in errors.items():
        if isinstance(value, list):
            formatted[field] = [str(v) for v in value]
        else:
            formatted[field] = str(value)
    return formatted

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
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
@permission_classes([IsAuthenticated])
def userprofile_detail(request, pk):
    try:
        profile = UserProfile.objects.get(pk=pk)
    except UserProfile.DoesNotExist:
        return Response(
            {"status": "error", "message": "UserProfile not found."},
            status=status.HTTP_404_NOT_FOUND
        )

    if request.method == 'GET':
        serializer = UserProfileSerializer(profile)
        return Response(
            {"status": "success", "data": serializer.data},
            status=status.HTTP_200_OK
        )

    elif request.method in ['PUT', 'PATCH']:
        serializer = UserProfileSerializer(profile, data=request.data, partial=(request.method == 'PATCH'))
        if serializer.is_valid():
            try:
                updated_profile = serializer.save()
                return Response(
                    {"status": "success", "data": UserProfileSerializer(updated_profile).data},
                    status=status.HTTP_200_OK
                )
            except IntegrityError:
                return Response(
                    {"status": "error", "message": "Username or email already exists."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            except Exception as e:
                return Response(
                    {"status": "error", "message": str(e)},
                    status=status.HTTP_400_BAD_REQUEST
                )
        else:
            return Response(
                {"status": "error", "message": format_serializer_errors(serializer.errors)},
                status=status.HTTP_400_BAD_REQUEST
            )

    elif request.method == 'DELETE':
        profile.user.delete()
        profile.delete()
        return Response(
            {"status": "success", "message": "UserProfile deleted successfully."},
            status=status.HTTP_200_OK
        )

@api_view(['PATCH'])
@permission_classes([AllowAny])
def update_user_profile(request, id):
    try:
        profile = UserProfile.objects.get(user__id=id)
    except UserProfile.DoesNotExist:
        return Response(
            {"status": "error", "message": "User profile not found."},
            status=status.HTTP_404_NOT_FOUND
        )

    serializer = UserProfileSerializer(profile, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(
            {"status": "success", "message": "User profile updated successfully.", "data": serializer.data},
            status=status.HTTP_200_OK
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




@api_view(['GET'])
@permission_classes([AllowAny])
def get_profile_picture(request, user_id):
    try:
        profile = UserProfile.objects.get(user__id=user_id)
        CURRENT_DOMAIN = settings.CURRENT_DOMAIN  
        pic_url = f"{CURRENT_DOMAIN}media/{profile.profile_picture}"


        
        return Response({"status": "success", "profile_pic": pic_url}, status=status.HTTP_200_OK)
    except UserProfile.DoesNotExist:
        return Response({"status": "error", "message": "User profile not found."},
                        status=status.HTTP_404_NOT_FOUND)
