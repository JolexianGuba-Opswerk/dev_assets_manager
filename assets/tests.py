from datetime import date
from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from assets.models import (
    Category,
    Asset,
    AssetHistory,
    Department,
    EmployeeProfile,
)


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
    def test_verify_otp_returns_access_token(self, _):
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


@override_settings(DATABASES=SQLITE_DB)
class AssetEndpointsTests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin_user = User.objects.create_user(
            username="admin",
            password="adminpass",
            is_staff=True,
            is_superuser=True,
            email="admin@example.com",
        )
        self.normal_user = User.objects.create_user(
            username="jdoe",
            password="userpass",
            email="jdoe@example.com",
        )
        self.another_user = User.objects.create_user(
            username="asmith",
            password="userpass",
            email="asmith@example.com",
        )
        self.category = Category.objects.create(name="Laptops")
        self.asset_list_url = reverse("asset_list_create")

    def _asset_detail_url(self, asset_id: int) -> str:
        return reverse("asset_list_detail", kwargs={"id": asset_id})

    def test_asset_create_requires_authentication(self):
        payload = {
            "name": "MacBook Pro 14",
            "serial_number": "SN-A-100",
            "category": self.category.id,
            "assigned_to": self.normal_user.id,
            "purchase_date": "2024-01-01",
            "status": "IN_USE",
            "description": "Dev laptop",
        }
        response = self.client.post(self.asset_list_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_asset_create_requires_admin(self):
        self.client.force_authenticate(user=self.normal_user)
        payload = {
            "name": "MacBook Pro 14",
            "serial_number": "SN-A-101",
            "category": self.category.id,
            "assigned_to": self.normal_user.id,
            "purchase_date": "2024-01-02",
            "status": "IN_USE",
            "description": "Dev laptop",
        }
        response = self.client.post(self.asset_list_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_asset_create_success_by_admin_creates_history_if_assigned(self):
        self.client.force_authenticate(user=self.admin_user)
        payload = {
            "name": "MacBook Pro 14",
            "serial_number": "SN-A-102",
            "category": self.category.id,
            "assigned_to": self.normal_user.id,
            "purchase_date": "2024-01-03",
            "status": "IN_USE",
            "description": "Dev laptop",
            "notes": "Initial assignment",
        }
        response = self.client.post(self.asset_list_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Asset.objects.filter(serial_number="SN-A-102").exists())
        asset = Asset.objects.get(serial_number="SN-A-102")
        self.assertEqual(asset.assigned_to, self.normal_user)
        self.assertEqual(AssetHistory.objects.filter(asset=asset).count(), 1)

    def test_asset_retrieve_requires_authentication(self):
        asset = Asset.objects.create(
            name="Dell XPS 13",
            serial_number="SN-B-200",
            category=self.category,
            assigned_to=self.normal_user,
            purchase_date=date(2024, 2, 1),
            status="IN_USE",
            description="",
        )
        url = self._asset_detail_url(asset.id)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_asset_retrieve_authenticated(self):
        asset = Asset.objects.create(
            name="Dell XPS 13",
            serial_number="SN-B-201",
            category=self.category,
            assigned_to=self.normal_user,
            purchase_date=date(2024, 2, 2),
            status="IN_USE",
            description="",
        )
        url = self._asset_detail_url(asset.id)
        self.client.force_authenticate(user=self.normal_user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("serial_number", response.data)
        self.assertEqual(response.data["serial_number"], "SN-B-201")

    def test_asset_update_admin_creates_history_on_reassignment_and_updates_notes(self):
        asset = Asset.objects.create(
            name="Dell XPS 13",
            serial_number="SN-B-300",
            category=self.category,
            assigned_to=self.normal_user,
            purchase_date=date(2024, 3, 1),
            status="IN_USE",
            description="",
        )
        self.client.force_authenticate(user=self.admin_user)
        url = self._asset_detail_url(asset.id)
        payload = {
            "assigned_to": self.another_user.id,
            "notes": "Reassigned to asmith",
        }
        response = self.client.patch(url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        asset.refresh_from_db()
        self.assertEqual(asset.assigned_to, self.another_user)
        history_entries = AssetHistory.objects.filter(asset=asset).order_by("-change_date")
        self.assertGreaterEqual(history_entries.count(), 1)
        self.assertEqual(history_entries.first().notes, "Reassigned to asmith")

    def test_user_own_assets_access(self):
        # Create assets for normal_user
        Asset.objects.create(
            name="Lenovo T14",
            serial_number="SN-C-400",
            category=self.category,
            assigned_to=self.normal_user,
            purchase_date=date(2024, 4, 1),
            status="IN_USE",
            description="",
        )
        Asset.objects.create(
            name="Lenovo T14 Gen2",
            serial_number="SN-C-401",
            category=self.category,
            assigned_to=self.normal_user,
            purchase_date=date(2024, 4, 2),
            status="IN_USE",
            description="",
        )

        # Owner can view
        self.client.force_authenticate(user=self.normal_user)
        owner_url = reverse("employee_assets_details", kwargs={"id": self.normal_user.id})
        res_owner = self.client.get(owner_url)
        self.assertEqual(res_owner.status_code, status.HTTP_200_OK)
        self.assertIn("assets", res_owner.data)
        self.assertEqual(len(res_owner.data["assets"]), 2)

        # Another user cannot view
        self.client.force_authenticate(user=self.another_user)
        other_url = reverse("employee_assets_details", kwargs={"id": self.normal_user.id})
        res_other = self.client.get(other_url)
        self.assertEqual(res_other.status_code, status.HTTP_403_FORBIDDEN)


@override_settings(DATABASES=SQLITE_DB)
class EmployeeEndpointsTests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin_user = User.objects.create_user(
            username="admin",
            password="adminpass",
            is_staff=True,
            is_superuser=True,
            email="admin@example.com",
        )
        self.normal_user = User.objects.create_user(
            username="jdoe",
            password="userpass",
            email="jdoe@example.com",
        )
        self.department = Department.objects.create(name="ENG", full_name="Engineering")
        self.department2 = Department.objects.create(name="HR", full_name="Human Resources")
        # Create profile for normal user
        EmployeeProfile.objects.create(user=self.normal_user, department=self.department, position="Engineer")

    def _employee_list_url(self) -> str:
        # Choose the list endpoint, not the detail or side endpoints
        return reverse("employee_details")

    def _employee_detail_url(self, user_id: int) -> str:
        return reverse("employee_details", kwargs={"id": user_id})

    def _employee_side_update_url(self, user_id: int) -> str:
        return reverse("employee_details", kwargs={"id": user_id}).replace("employees/", "employees-side/")

    def test_employees_list_requires_authentication(self):
        url = self._employee_list_url()
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_employees_list_authenticated(self):
        self.client.force_authenticate(user=self.normal_user)
        url = self._employee_list_url()
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data.get("results"), list)

    @patch("assets.serializers.employee_serializers.send_welcome_email.delay")
    def test_employees_create_requires_admin(self, mock_delay):
        self.client.force_authenticate(user=self.normal_user)
        url = self._employee_list_url()
        payload = {
            "username": "asmith",
            "first_name": "Alice",
            "last_name": "Smith",
            "email": "asmith@example.com",
            "password": "StrongPass123!",
            "department": self.department.id,
            "position": "Recruiter",
        }
        response = self.client.post(url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        mock_delay.assert_not_called()

    @patch("assets.serializers.employee_serializers.send_welcome_email.delay")
    def test_employees_create_success_admin(self, mock_delay):
        self.client.force_authenticate(user=self.admin_user)
        url = self._employee_list_url()
        payload = {
            "username": "asmith",
            "first_name": "Alice",
            "last_name": "Smith",
            "email": "asmith@example.com",
            "password": "StrongPass123!",
            "department": self.department.id,
            "position": "Recruiter",
        }
        response = self.client.post(url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        mock_delay.assert_called_once()
        self.assertTrue(User.objects.filter(username="asmith").exists())
        new_user = User.objects.get(username="asmith")
        self.assertTrue(EmployeeProfile.objects.filter(user=new_user, department__name="ENG").exists())

    def test_employee_detail_get_authenticated(self):
        self.client.force_authenticate(user=self.normal_user)
        url = self._employee_detail_url(self.normal_user.id)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["username"], "jdoe")

    def test_employee_update_admin(self):
        self.client.force_authenticate(user=self.admin_user)
        url = self._employee_detail_url(self.normal_user.id)
        payload = {
            "first_name": "John",
            "last_name": "Doe",
            "email": "new-jdoe@example.com",
            "department": self.department2.id,
            "position": "Senior Engineer",
            "password": "NewStrongPass123!",
        }
        response = self.client.patch(url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.normal_user.refresh_from_db()
        self.assertEqual(self.normal_user.email, "new-jdoe@example.com")
        self.assertEqual(self.normal_user.employee_profile.department.name, "HR")
        self.assertEqual(self.normal_user.employee_profile.position, "Senior Engineer")

    def test_employee_side_update_only_owner(self):
        # Owner can update
        owner_url = self._employee_side_update_url(self.normal_user.id)
        self.client.force_authenticate(user=self.normal_user)
        response = self.client.patch(owner_url, {"email": "owner-update@example.com"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.normal_user.refresh_from_db()
        self.assertEqual(self.normal_user.email, "owner-update@example.com")

        # Another user cannot update
        self.client.force_authenticate(user=self.admin_user)
        response2 = self.client.patch(owner_url, {"email": "hijack@example.com"}, format="json")
        self.assertEqual(response2.status_code, status.HTTP_403_FORBIDDEN)


@override_settings(DATABASES=SQLITE_DB)
class AssetHistoryEndpointsTests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="user",
            password="userpass",
            email="user@example.com",
        )
        self.category = Category.objects.create(name="Monitors")
        self.asset = Asset.objects.create(
            name="Dell U2720Q",
            serial_number="SN-H-500",
            category=self.category,
            assigned_to=self.user,
            purchase_date=date(2024, 5, 1),
            status="IN_USE",
            description="",
        )
        AssetHistory.objects.create(asset=self.asset, previous_user=None, new_user=self.user, notes="Assigned")
        self.url = "/api/assets/history/"

    def test_asset_history_requires_authentication(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_asset_history_authenticated(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data.get("results"), list)
        self.assertGreaterEqual(len(response.data.get("results")), 1)
