from datetime import date
from django.urls import reverse
from django.test import override_settings
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth.models import User

from assets.models import Category, Asset, AssetHistory


SQLITE_DB = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:'
    }
}


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
        a1 = Asset.objects.create(
            name="Lenovo T14",
            serial_number="SN-C-400",
            category=self.category,
            assigned_to=self.normal_user,
            purchase_date=date(2024, 4, 1),
            status="IN_USE",
            description="",
        )
        a2 = Asset.objects.create(
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