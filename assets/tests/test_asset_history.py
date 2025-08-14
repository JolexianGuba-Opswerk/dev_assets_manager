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
        self.assertIsInstance(response.data["results"], list)
        self.assertGreaterEqual(len(response.data["results"]), 1)