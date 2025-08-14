from datetime import timedelta

from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status
from assets.services.otp_services import store_otp, verify_otp
from assets.tasks import send_otp_email


class RequestOTPView(APIView):
    def post(self, request):
        email = request.data.get('email')

        if not email:
            return Response({"error": "Email required"}, status=status.HTTP_400_BAD_REQUEST)

        email_exist = User.objects.filter(email=email).exists()
        if not email_exist:
            return Response({"error": "Invalid email"}, status=status.HTTP_400_BAD_REQUEST)

        otp = store_otp(email)
        send_otp_email(email, otp)

        return Response({"message": "OTP sent to your email"}, status=status.HTTP_200_OK)


class VerifyOTPView(APIView):
    def post(self, request):
        email = request.data.get('email')
        otp = request.data.get('otp')

        if not email or not otp:
            return Response({"error": "Email and OTP required"}, status=status.HTTP_400_BAD_REQUEST)

        if verify_otp(email, otp):
            user = User.objects.get(email=email)
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            refresh.set_exp(lifetime=timedelta(minutes=15))

            return Response({
                "message": "OTP verified successfully",
                "access": access_token,
                "expires_in": 900
            }, status=200)

        return Response({"error": "Invalid or expired OTP"}, status=status.HTTP_400_BAD_REQUEST)


class ResetPasswordView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        new_password = request.data.get("new_password")
        if not new_password:
            return Response({"error": "New password is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            validate_password(new_password, user=request.user)
        except ValidationError as e:
            return Response({"error": e.messages}, status=status.HTTP_400_BAD_REQUEST)

        request.user.set_password(new_password)
        request.user.save()
        return Response({"message": "Password changed successfully"}, status=status.HTTP_200_OK)
