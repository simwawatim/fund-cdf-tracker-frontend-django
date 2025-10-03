from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate, get_user_model
from rest_framework_simplejwt.tokens import AccessToken
from django.core.exceptions import ObjectDoesNotExist

User = get_user_model()

@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    email = request.data.get('email')
    password = request.data.get('password')

    # Validate input
    if not email or not password:
        return Response(
            {"status": "error", "message": "Email and password are required."},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Try to find user by email
    user = User.objects.filter(email=email).first()
    if not user:
        return Response(
            {"status": "error", "message": "Invalid credentials."},
            status=status.HTTP_401_UNAUTHORIZED
        )

    # Authenticate with username and password
    user = authenticate(username=user.username, password=password)
    if not user:
        return Response(
            {"status": "error", "message": "Invalid credentials."},
            status=status.HTTP_401_UNAUTHORIZED
        )

    # Create JWT token
    access_token = AccessToken.for_user(user)

    # Add custom claims
    try:
        profile = user.profile
        access_token['role'] = profile.role
        access_token['constituency'] = profile.constituency.id if profile.constituency else None
    except ObjectDoesNotExist:
        access_token['role'] = None
        access_token['constituency'] = None

    return Response({
        "status": "success",
        "token_type": "access",
        "access": str(access_token),
        "user_id": user.id,
        "role": access_token['role'],
        "constituency": access_token['constituency'],
    }, status=status.HTTP_200_OK)
