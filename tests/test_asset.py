from datetime import date

from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from assets.models import Asset, AssetHistory, Category, Department, EmployeeProfile


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
            name="HR", full_name="Human Resource", added_by=self.admin_user
        )

        # Admin, Normal User, Other User Profile
        EmployeeProfile.objects.create(
            user=self.admin_user,
            department=self.hr_department,
            position="Human Resource",
        )
        EmployeeProfile.objects.create(
            user=self.normal_user, department=self.hr_department, position="IT"
        )
        EmployeeProfile.objects.create(
            user=self.other_user,
            department=self.hr_department,
            position="Soft Engineer",
        )

        self.asset = Asset.objects.create(
            name="Dell Laptop",
            serial_number="SN9929",
            category=self.category,
            purchase_date=date.today(),
            status="available",
        )
        self.id = None
        # URLS
        self.asset_list_url = reverse("asset_list_create")
        self.user_asset_list_url = reverse("employee_assets")

    def asset_detail_url(self, asset_id):
        return reverse("asset_list_detail", kwargs={"id": asset_id})

    def user_own_assets_url(self, asset_id):
        return reverse("employee_assets_details", kwargs={"id": asset_id})

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
            "notes": "Initial purchase",
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
            "description": "Work laptop",
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
            description="New Asset",
        )
        update_payload = {"assigned_to": self.normal_user.id, "notes": ""}
        response = self.client.patch(
            self.asset_detail_url(asset.id), update_payload, format="json"
        )
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
