from rest_framework import status
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView


class CookieTokenObtainPairView(TokenObtainPairView):

    def post(self, request, *args, **kwargs):

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data
        user = serializer.user

        res = Response(
            {
                "message": "Login successful",
                "username": user.username,
                "is_superuser": user.is_superuser,
            },
            status=status.HTTP_200_OK,
        )
        res.set_cookie(
            "access_token",
            data["access"],
            httponly=True,
            samesite="Lax",
            path="/",
        )
        res.set_cookie(
            "refresh_token",
            data["refresh"],
            httponly=True,
            samesite="Lax",
            path="/",
        )
        return res


class CookieTokenRefreshView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            access = response.data.get("access")
            res = Response({"message": "Token refreshed"})
            res.set_cookie(
                "access_token",
                access,
                httponly=True,
                samesite="Lax",
                path="/",
            )
            return res
        return response
