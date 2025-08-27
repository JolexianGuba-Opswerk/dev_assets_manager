from mozilla_django_oidc.views import OIDCAuthenticationCallbackView
from rest_framework_simplejwt.tokens import RefreshToken


class CustomOIDCAuthenticationCallbackView(OIDCAuthenticationCallbackView):

    def login_success(self):
        user = self.request.user
        refresh = RefreshToken.for_user(user)
        response = super().login_success()
        response.set_cookie(
            "access_token",
            str(refresh.access_token),
            httponly=True,
            secure=False,
            samesite="Lax",
            path="/",
        )
        return response
