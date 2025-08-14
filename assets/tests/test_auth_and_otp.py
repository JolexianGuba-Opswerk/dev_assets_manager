from unittest.mock import patch

from django.contrib.auth.models import User
from django.urls import reverse
from django.test import override_settings
from rest_framework import status
from rest_framework.test import APITestCase, APIClient


SQLITE_DB = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:'
    }
}


@override_settings(DATABASES=SQLITE_DB)
class AuthAndOtpTests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="jdoe",
            password="userpass",
            email="jdoe@example.com",
        )
        self.token_url = reverse("token_obtain_pair")
        self.refresh_url = reverse("token_refresh")
        self.otp_request_url = "/api/forget-password/"
        self.otp_verify_url = "/api/verify-otp/"
        self.reset_password_url = "/api/reset-password/"

    def test_jwt_obtain_and_refresh(self):
        res = self.client.post(self.token_url, {"username": "jdoe", "password": "userpass"}, format="json")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("access", res.data)
        self.assertIn("refresh", res.data)

        refresh = res.data["refresh"]
        res2 = self.client.post(self.refresh_url, {"refresh": refresh}, format="json")
        self.assertEqual(res2.status_code, status.HTTP_200_OK)
        self.assertIn("access", res2.data)

    @patch("assets.views.otp_views.store_otp", return_value="123456")
    @patch("assets.views.otp_views.send_otp_email")
    def test_request_otp_sends_email(self, mock_send_email, mock_store):
        res = self.client.post(self.otp_request_url, {"email": "jdoe@example.com"}, format="json")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        mock_store.assert_called_once_with("jdoe@example.com")
        mock_send_email.assert_called_once_with("jdoe@example.com", "123456")

    @patch("assets.views.otp_views.verify_otp", return_value=True)
    def test_verify_otp_returns_access_token(self, mock_verify):
        res = self.client.post(self.otp_verify_url, {"email": "jdoe@example.com", "otp": "123456"}, format="json")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("access", res.data)
        self.assertEqual(res.data.get("expires_in"), 900)

    @patch("assets.views.otp_views.verify_otp", return_value=True)
    def test_reset_password_requires_auth_then_changes_password(self, _):
        # First obtain JWT via verify-otp mocked route to simulate authentication
        res = self.client.post(self.otp_verify_url, {"email": "jdoe@example.com", "otp": "123456"}, format="json")
        access = res.data["access"]

        # Use the access token to call reset-password
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
        res2 = self.client.post(self.reset_password_url, {"new_password": "NewStrongPass!123"}, format="json")
        self.assertEqual(res2.status_code, status.HTTP_200_OK)

        # Verify new password works with JWT obtain
        self.client.credentials()  # clear
        token_res = self.client.post(self.token_url, {"username": "jdoe", "password": "NewStrongPass!123"}, format="json")
        self.assertEqual(token_res.status_code, status.HTTP_200_OK)
        self.assertIn("access", token_res.data)