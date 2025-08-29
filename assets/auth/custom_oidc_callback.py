import time

from django.contrib import auth
from django.http import HttpResponseRedirect
from mozilla_django_oidc.views import OIDCAuthenticationCallbackView
from rest_framework_simplejwt.tokens import RefreshToken


class CustomOIDCAuthenticationCallbackView(OIDCAuthenticationCallbackView):

    def login_success(self):
        """
        Custom login success:
        - Attach JWT access token in a cookie
        - Properly log in the user
        - Redirect based on user role
        """
        user = self.user

        # Generate JWT token for the user
        refresh = RefreshToken.for_user(user)

        # Make sure the user is logged in
        request_user = getattr(self.request, "user", None)
        if (
            not request_user
            or not request_user.is_authenticated
            or request_user != self.user
        ):
            auth.login(self.request, self.user)

        # Set expiration for id_token in session
        expiration_interval = self.get_settings(
            "OIDC_RENEW_ID_TOKEN_EXPIRY_SECONDS", 60 * 100
        )
        self.request.session["oidc_id_token_expiration"] = (
            time.time() + expiration_interval
        )

        # Clear any previous 'oidc_login_next' to prevent override
        self.request.session.pop("oidc_login_next", None)

        # Attach JWT access token as HttpOnly cookie
        response = HttpResponseRedirect("/")  # Placeholder, will override below
        response.set_cookie(
            "access_token",
            str(refresh.access_token),
            httponly=True,
            secure=False,
            samesite="Lax",
            path="/",
        )

        # Determine redirect URL based on user role
        if user.is_staff or user.is_superuser:
            redirect_url = "http://127.0.0.1:5173/admin/"
        else:
            redirect_url = "http://127.0.0.1:5173/dashboard/"

        print(f"[OIDC] Redirecting user '{user.username}' to: {redirect_url}")

        # Return response with cookie and redirect
        response["Location"] = redirect_url
        response.status_code = 302
        return response
