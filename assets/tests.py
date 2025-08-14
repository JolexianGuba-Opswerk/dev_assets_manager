from datetime import date

from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from assets.models import Department, EmployeeProfile, Asset, AssetHistory, Category


# Create your tests here.
class EmployeeListCreateAPITest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        # Admin User & Normal User Creation
        self.admin_user = User.objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="admin_pass"
        )

        self.normal_user = User.objects.create_user(
            username="user",
            email="user@example.com",
            password="user_pass"
        )

        # Department Creation
        self.it_department = Department.objects.create(
            name="IT",
            full_name="Information Technology",
            added_by=self.admin_user
        )
        self.hr_department = Department.objects.create(
            name="HR",
            full_name="Human Resource",
            added_by=self.admin_user
        )

        # Admin User Profile Creation
        EmployeeProfile.objects.create(
            user=self.admin_user,
            department=self.hr_department,
            position="Human Resource"
        )

        # Normal User Profile Creation
        EmployeeProfile.objects.create(
            user=self.normal_user,
            department=self.it_department,
            position="Software Engineer"
        )
        self.other_user = User.objects.create_user(
            username="user2", password="userpass", email="user2@example.com"
        )
        EmployeeProfile.objects.create(
            user=self.other_user,
            department=self.it_department,
            position="Tester")

        self.token_url = reverse('token_obtain_pair')
        self.employee_list_create_api = reverse('employee_list_create')
        self.detail_url = lambda id: reverse("employee_details", args=[id])
        self.side_update_url = lambda id: reverse("employee_side_details", args=[id])

    def authenticate_as_admin(self):
        response = self.client.post(self.token_url, {
            "username": "admin",
            "password": "admin_pass"
        })
        token = response.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    def authenticate_as_normal_user(self):
        response = self.client.post(self.token_url, {
            "username": "user",
            "password": "user_pass"
        })
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
            "position": "Software Engineer"
        }
        response = self.client.post(self.employee_list_create_api, payload, format="json")
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
            "position": "Software Engineer"
        }
        response = self.client.post(self.employee_list_create_api, payload, format="json")
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
            "position": "Software Engineer"
        }
        response = self.client.post(self.employee_list_create_api, payload, format="json")
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
            "position": "Software Engineer"
        }
        response = self.client.post(self.employee_list_create_api, payload, format="json")
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
            "position": "Software Engineer"
        }
        response = self.client.post(self.employee_list_create_api, payload, format="json")
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
            "position": "Software Engineer"
        }
        response = self.client.post(self.employee_list_create_api, payload, format="json")
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
        response = self.client.get(f"{self.employee_list_create_api}?search={self.search_term}")
        self.assertGreaterEqual(response.data["count"],1)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # ----- UPDATE SECTION ----- #
    def test_admin_can_patch_employee(self):
        self.client.force_authenticate(user=self.admin_user)
        payload = {"first_name": "Updated"}
        response = self.client.patch(self.detail_url(self.normal_user.id), payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.normal_user.refresh_from_db()
        self.assertEqual(self.normal_user.first_name, "Updated")

    def test_non_admin_cannot_patch_employee(self):
        self.client.force_authenticate(user=self.normal_user)
        payload = {"first_name": "Hacker"}
        response = self.client.patch(self.detail_url(self.other_user.id), payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_owner_can_patch_own_details_via_side_update(self):
        self.client.force_authenticate(user=self.normal_user)
        payload = {"first_name": "SelfUpdated"}
        response = self.client.patch(self.side_update_url(self.normal_user.id), payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.normal_user.refresh_from_db()
        self.assertEqual(self.normal_user.first_name, "SelfUpdated")

    def test_owner_cannot_patch_other_user_via_side_update(self):
        self.client.force_authenticate(user=self.normal_user)
        payload = {"first_name": "ShouldNotWork"}
        response = self.client.patch(self.side_update_url(self.other_user.id), payload, format="json")
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

class AssetAPITest(APITestCase):
    def setUp(self):
        self.admin_user = User.objects.create_superuser(
            username="admin", password="adminpass", email="admin@example.com"
        )
        self.normal_user = User.objects.create_user(
            username="user", password="userpass", email="user@example.com"
        )
        self.other_user = User.objects.create_user(
            username="other", password="otherpass", email="other@example.com"
        )
        self.category = Category.objects.create(name="Laptop")

        self.hr_department = Department.objects.create(
            name="HR",
            full_name="Human Resource",
            added_by=self.admin_user
        )

        # Admin, Normal User, Other User Profile
        EmployeeProfile.objects.create(
            user=self.admin_user,
            department=self.hr_department,
            position="Human Resource"
        )
        EmployeeProfile.objects.create(
            user=self.normal_user,
            department=self.hr_department,
            position="IT"
        )
        EmployeeProfile.objects.create(
            user=self.other_user,
            department=self.hr_department,
            position="Soft Engineer"
        )

        self.asset = Asset.objects.create(
            name="Dell Laptop",
            serial_number="SN9929",
            category=self.category,
            purchase_date=date.today(),
            status="available"
        )
        self.id = None
        # URLS
        self.asset_list_url = reverse("asset_list_create")
        self.user_asset_list_url = reverse("employee_assets")

    def asset_detail_url(self, asset_id):
        return reverse("asset_list_detail", kwargs={"id": asset_id})

    def user_own_assets_url(self, asset_id):
        return reverse("employee_assets_details", kwargs={"id":asset_id})

    def authenticate_as_admin(self):
        self.client.force_authenticate(user=self.admin_user)

    def authenticate_as_user(self):
        self.client.force_authenticate(user=self.normal_user)

    def test_list_assets_requires_auth(self):
        response = self.client.get(self.asset_list_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # ----- CREATE, UPDATE SECTION ----- #
    # Admin Create Asset
    def test_admin_can_create_asset(self):
        self.authenticate_as_admin()
        payload = {
            "name": "Macbook Pro",
            "serial_number": "SN12345",
            "category": self.category.id,
            "purchase_date": date.today(),
            "status": "IN_USE",
            "description": "Work laptop",
            "notes": "Initial purchase"
        }
        response = self.client.post(self.asset_list_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Asset.objects.filter(name="Macbook Pro").exists())

    # Normal User Create Asset
    def test_normal_user_cannot_create_asset(self):
        self.authenticate_as_user()
        payload = {
            "name": "Macbook Pro",
            "serial_number": "SN12345",
            "category": self.category.id,
            "purchase_date": date.today(),
            "status": "available",
            "description": "Work laptop"
        }
        response = self.client.post(self.asset_list_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # Creating Asset and Asset History
    def test_update_asset_creates_history_when_user_changes(self):
        self.authenticate_as_admin()
        asset = Asset.objects.create(
            name="Dell Laptop",
            serial_number="SN999",
            category=self.category,
            purchase_date=date.today(),
            status="IN_USE",
            description="New Asset"
        )
        update_payload = {
            "assigned_to": self.normal_user.id,
            "notes": ""
        }
        response = self.client.patch(self.asset_detail_url(asset.id), update_payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(AssetHistory.objects.filter(asset=asset).exists())

    # ----- LIST SECTION ----- #

    def test_admin_can_view_all_user_assets(self):
        self.authenticate_as_admin()
        response = self.client.get(self.user_asset_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_non_admin_cannot_view_all_user_assets(self):
        self.authenticate_as_user()
        response = self.client.get(self.user_asset_list_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_cant_view_others_asset(self):
        self.asset.assigned_to = self.normal_user
        self.asset.save()
        self.authenticate_as_user()
        response = self.client.get(self.user_own_assets_url(self.other_user.id))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_cannot_view_others_assets(self):
        self.authenticate_as_user()
        response = self.client.get(self.user_own_assets_url(self.other_user.id))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_nonexistent_user_assets(self):
        self.authenticate_as_user()
        response = self.client.get(self.user_own_assets_url(999))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)