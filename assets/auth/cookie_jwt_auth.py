# myapp/authentication.py
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken


class CookieJWTAuthentication(JWTAuthentication):
    """
    Custom JWT authentication class to read JWT from HttpOnly cookies..
    """

    def authenticate(self, request):

        raw_token = request.COOKIES.get("access_token")
        if raw_token is None:
            print("No access_token cookie found")
            return None

        try:
            validated_token = self.get_validated_token(raw_token)
            user = self.get_user(validated_token)
            print("Authentication successful for user:", user.username)
            return (user, validated_token)
        except InvalidToken as e:
            print("Token validation failed:", str(e))
            return None
