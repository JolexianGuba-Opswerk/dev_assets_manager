from unittest.mock import patch

from django.urls import reverse
from django.test import override_settings
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth.models import User

from assets.models import Department, EmployeeProfile


SQLITE_DB = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:'
    }
}


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
        self.assertIsInstance(response.data["results"], list)

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