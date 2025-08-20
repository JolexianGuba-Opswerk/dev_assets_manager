import logging
import time

from django.contrib.auth.models import User
from django.db.models import Prefetch
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics
from rest_framework.permissions import IsAdminUser, IsAuthenticated

from assets.filters import AssetFilter
from assets.models import Asset
from assets.permissions import IsOwnerAssetsOrReadOnly
from assets.serializers.asset_serializer import (
    AssetCreateSerializer,
    AssetDetailSerializer,
    AssetListSerializer,
    UserAssetListSerializer,
    UserAssetSerializer,
)

logger = logging.getLogger("assets")


# CREATE/GET view for Asset
class AssetListCreateAPIView(generics.ListCreateAPIView):
    queryset = Asset.objects.select_related("category", "assigned_to").order_by("-id")
    serializer_class = AssetListSerializer
    permission_classes = [IsAuthenticated]

    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_class = AssetFilter

    ordering_fields = ["purchased_date", "name"]
    search_fields = ["name", "serial_number", "description"]

    # 15 MINUTES OF CACHING
    @method_decorator(cache_page(60 * 15, key_prefix="asset_list"))
    def list(self, request, *args, **kwargs):
        return super().list(request, request, *args, **kwargs)

    def get_queryset(self):
        time.sleep(2)
        return super().get_queryset()

    def get_serializer_class(self):
        if self.request.method == "POST":
            return AssetCreateSerializer
        return super().get_serializer_class()

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAdminUser()]
        return [IsAuthenticated()]


# GET/UPDATE/DELETE view for Asset Details
class AssetDetailsView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Asset.objects.select_related("assigned_to", "category")
    serializer_class = AssetCreateSerializer
    lookup_field = "id"

    def get_serializer_class(self):
        if self.request.method == "GET":
            return AssetDetailSerializer
        return super().get_serializer_class()

    def get_permissions(self):
        if self.request.method == "GET":
            return [IsAuthenticated()]
        return [IsAdminUser()]


# Getting User's Asset with Details
class UserAssetDetailsView(generics.ListAPIView):
    queryset = (
        User.objects.select_related("employee_profile__department").prefetch_related(
            "assets__category"
        )
    ).order_by("-id")
    serializer_class = UserAssetListSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]

    filter_backends = [filters.SearchFilter]
    search_fields = ["username", "email"]


# Getting Own Assets of User
class UserOwnAssetDetailsAPIView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated, IsOwnerAssetsOrReadOnly]
    queryset = User.objects.prefetch_related(
        Prefetch(
            "assets",
            Asset.objects.select_related("category").order_by("-purchase_date"),
        )
    )
    serializer_class = UserAssetSerializer
    lookup_field = "id"
