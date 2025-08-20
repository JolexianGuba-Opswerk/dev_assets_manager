from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from assets.models import Department, EmployeeProfile


class EmployeeAPITest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        # Admin User & Normal User Creation
        self.admin_user = User.objects.create_superuser(
            username="admin", email="admin@example.com", password="admin_pass"
        )

        self.normal_user = User.objects.create_user(
            username="user", email="user@example.com", password="user_pass"
        )

        # Department Creation
        self.it_department = Department.objects.create(
            name="IT", full_name="Information Technology", added_by=self.admin_user
        )
        self.hr_department = Department.objects.create(
            name="HR", full_name="Human Resource", added_by=self.admin_user
        )

        # Admin User Profile Creation
        EmployeeProfile.objects.create(
            user=self.admin_user,
            department=self.hr_department,
            position="Human Resource",
        )

        # Normal User Profile Creation
        EmployeeProfile.objects.create(
            user=self.normal_user,
            department=self.it_department,
            position="Software Engineer",
        )
        self.other_user = User.objects.create_user(
            username="user2", password="userpass", email="user2@example.com"
        )
        EmployeeProfile.objects.create(
            user=self.other_user, department=self.it_department, position="Tester"
        )

        self.token_url = reverse("token_obtain_pair")
        self.employee_list_create_api = reverse("employee_list_create")
        self.detail_url = lambda id: reverse("employee_details", args=[id])
        self.side_update_url = lambda id: reverse("employee_side_details", args=[id])

    def authenticate_as_admin(self):
        response = self.client.post(
            self.token_url, {"username": "admin", "password": "admin_pass"}
        )
        token = response.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    def authenticate_as_normal_user(self):
        response = self.client.post(
            self.token_url, {"username": "user", "password": "user_pass"}
        )
        token = response.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    # ----- CREATE SECTION ----- #

    # Creating employee without credentials
    def test_create_employee_without_credentials(self):
        payload = {
            "username": "test_username",
            "first_name": "test_first_name",
            "last_name": "test_last_name",
            "email": "test@example.com",
            "password": "test_pass",
            "department": self.it_department.id,
            "position": "Software Engineer",
        }
        response = self.client.post(
            self.employee_list_create_api, payload, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # Creating employee as a normal user
    def test_create_employee_as_normal_user(self):
        self.authenticate_as_normal_user()
        payload = {
            "username": "test_username",
            "first_name": "test_first_name",
            "last_name": "test_last_name",
            "email": "test@example.com",
            "password": "test_pass",
            "department": self.it_department.id,
            "position": "Software Engineer",
        }
        response = self.client.post(
            self.employee_list_create_api, payload, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # Creating employee as admin
    def test_create_employee_as_admin(self):
        self.authenticate_as_admin()
        payload = {
            "username": "test_username",
            "first_name": "test_first_name",
            "last_name": "test_last_name",
            "email": "test@example.com",
            "password": "test_pass",
            "department": self.it_department.id,
            "position": "Software Engineer",
        }
        response = self.client.post(
            self.employee_list_create_api, payload, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    # Missing Required Fields and Invalid Email
    def test_create_missing_required_fields_invalid_email(self):
        self.authenticate_as_admin()
        payload = {
            "username": "test_username",
            "first_name": "test_first_name",
            "last_name": "test_last_name",
            "email": "test@mail.com",
            "password": None,
            "department": self.it_department.id,
            "position": "Software Engineer",
        }
        response = self.client.post(
            self.employee_list_create_api, payload, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # Invalid Foreign Keys
    def test_create_invalid_foreign_keys(self):
        self.authenticate_as_admin()
        payload = {
            "username": "test_username",
            "first_name": "test_first_name",
            "last_name": "test_last_name",
            "email": "test@gmail.com",
            "password": "password",
            "department": 9999,
            "position": "Software Engineer",
        }
        response = self.client.post(
            self.employee_list_create_api, payload, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # Duplicate Username
    def test_create_duplicate_username(self):
        self.authenticate_as_admin()
        payload = {
            "username": "user",
            "first_name": "test_first_name",
            "last_name": "test_last_name",
            "email": "test@gmail.com",
            "password": "password",
            "department": self.it_department.id,
            "position": "Software Engineer",
        }
        response = self.client.post(
            self.employee_list_create_api, payload, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # ----- LIST SECTION ----- #

    # Listing employees as admin
    def test_list_employees_as_admin(self):
        self.authenticate_as_admin()
        response = self.client.get(self.employee_list_create_api)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data)

    # Listing employees as normal user
    def test_list_employees_as_normal_user(self):
        self.authenticate_as_normal_user()
        response = self.client.get(self.employee_list_create_api)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data)

    # Listing employees without credentials
    def test_list_employees_no_credentials(self):
        response = self.client.get(self.employee_list_create_api)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # Search existing user
    def test_search_existing_user(self):
        self.authenticate_as_normal_user()
        self.search_term = "user"
        response = self.client.get(
            f"{self.employee_list_create_api}?search={self.search_term}"
        )
        self.assertGreaterEqual(response.data["count"], 1)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # ----- UPDATE SECTION ----- #
    def test_admin_can_patch_employee(self):
        self.client.force_authenticate(user=self.admin_user)
        payload = {"first_name": "Updated"}
        response = self.client.patch(
            self.detail_url(self.normal_user.id), payload, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.normal_user.refresh_from_db()
        self.assertEqual(self.normal_user.first_name, "Updated")

    def test_non_admin_cannot_patch_employee(self):
        self.client.force_authenticate(user=self.normal_user)
        payload = {"first_name": "Hacker"}
        response = self.client.patch(
            self.detail_url(self.other_user.id), payload, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_owner_can_patch_own_details_via_side_update(self):
        self.client.force_authenticate(user=self.normal_user)
        payload = {"first_name": "SelfUpdated"}
        response = self.client.patch(
            self.side_update_url(self.normal_user.id), payload, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.normal_user.refresh_from_db()
        self.assertEqual(self.normal_user.first_name, "SelfUpdated")

    def test_owner_cannot_patch_other_user_via_side_update(self):
        self.client.force_authenticate(user=self.normal_user)
        payload = {"first_name": "ShouldNotWork"}
        response = self.client.patch(
            self.side_update_url(self.other_user.id), payload, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # ----- DELETE SECTION ----- #
    def test_admin_can_delete_employee(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.delete(self.detail_url(self.normal_user.id))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(User.objects.filter(id=self.normal_user.id).exists())

    def test_non_admin_cannot_delete_employee(self):
        self.client.force_authenticate(user=self.normal_user)
        response = self.client.delete(self.detail_url(self.other_user.id))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
