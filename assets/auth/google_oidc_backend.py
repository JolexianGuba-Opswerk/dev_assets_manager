from django.contrib.auth.models import User
from mozilla_django_oidc.auth import OIDCAuthenticationBackend

from assets.models import EmployeeProfile


class GoogleOIDCBackend(OIDCAuthenticationBackend):
    def filter_users_by_claims(self, claims):
        email = claims.get("email")
        if not email:
            return self.UserModel.objects.none()
        try:
            user = User.objects.get(email=email)
            return [user]

        except User.DoesNotExist:
            return self.UserModel.objects.none()

    def create_user(self, claims):
        user = super().create_user(claims)
        user.email = claims.get("email")
        user.first_name = claims.get("given_name", "")
        user.last_name = claims.get("family_name", "")
        user.save()

        EmployeeProfile.objects.create(
            user=user,
            avatar_url=claims.get("picture", ""),
        )

        return user

    def update_user(self, user, claims):
        user.email = claims.get("email", user.email)
        user.first_name = claims.get("given_name", user.first_name)
        user.last_name = claims.get("family_name", user.last_name)
        user.save()

        # Update or create profile avatar
        profile, created = EmployeeProfile.objects.get_or_create(user=user)
        profile.avatar_url = claims.get("picture", profile.avatar_url)
        profile.save()

        return user
