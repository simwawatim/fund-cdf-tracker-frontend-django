import requests
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from api.serializers.forget_password_serializers import PasswordResetRequestSerializer, PasswordResetConfirmSerializer

User = get_user_model()


class PasswordResetRequestView(APIView):
    permission_classes = []
    authentication_classes = []

    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]
        users = User.objects.filter(email__iexact=email, is_active=True)

        email_sent = False 

        for user in users:
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            reset_path = f"/new-password/{uid}/{token}/"
            reset_url = getattr(settings, "FRONTEND_URL", "") + reset_path

            payload = {
                "subject": "Password Reset Request",
                "message": "Click the button below to reset your password.",
                "recipient": user.email,
                "header": "Reset Your Password",
                "action_url": reset_url,
                "action_text": "Reset Password",
                "system_name": "YourApp",
                "support_email": "help@yourapp.com"
            }

            try:
                response = requests.post(
                    "https://timmails.pythonanywhere.com/api/send-email/",
                    json=payload,
                    timeout=10
                )
                res_json = response.json()
                if res_json.get("status") == "success" and res_json.get("status_code") == 200:
                    email_sent = True
                else:
                    print(f"Email API failed: {res_json}")
            except Exception as e:
                print("Email sending exception:", e)

        if email_sent:
            return Response(
                {"detail": "Password reset email sent successfully."},
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                {"detail": "Failed to send password reset email."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class PasswordResetConfirmView(APIView):
    permission_classes = []
    authentication_classes = []

    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {"detail": "Password has been reset successfully."},
            status=status.HTTP_200_OK
        )
