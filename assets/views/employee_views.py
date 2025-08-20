import logging
import time

from django.contrib.auth.models import User
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics
from rest_framework.permissions import IsAdminUser, IsAuthenticated

from assets.filters import EmployeeFilter
from assets.permissions import IsOwnerOrReadOnly
from assets.serializers.employee_serializer import (
    EmployeeCreateSerializer,
    EmployeeListSerializer,
    EmployeeSideUpdateSerializer,
    EmployeeUpdateSerializer,
)

logger = logging.getLogger("assets")


class EmployeeListCreateAPIView(generics.ListCreateAPIView):
    queryset = User.objects.select_related(
        "employee_profile", "employee_profile__department"
    ).order_by("-id")
    serializer_class = EmployeeListSerializer
    permission_classes = [IsAdminUser, IsAuthenticated]

    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_class = EmployeeFilter
    search_fields = ["username", "=email"]

    @method_decorator(cache_page(60 * 15, key_prefix="employee_list"))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def get_queryset(self):
        time.sleep(2)
        return super().get_queryset()

    def get_serializer_class(self):
        if self.request.method == "POST":
            return EmployeeCreateSerializer
        return super().get_serializer_class()

    def get_permissions(self):
        if self.request.method == "GET":
            return [IsAuthenticated()]
        return [IsAdminUser()]


class EmployeeDetailsView(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.select_related(
        "employee_profile", "employee_profile__department"
    ).order_by("-id")
    serializer_class = EmployeeUpdateSerializer
    permission_classes = [IsAdminUser, IsAuthenticated]
    lookup_field = "id"

    def get_serializer_class(self):
        if self.request.method == "GET":
            return EmployeeListSerializer
        return super().get_serializer_class()

    def get_permissions(self):
        if self.request.method == "GET":
            return [IsAuthenticated()]
        return [IsAdminUser()]


# User side, updating own credentials only
class EmployeeSideDetailsUpdate(generics.RetrieveUpdateAPIView):
    queryset = User.objects.select_related(
        "employee_profile", "employee_profile__department"
    )
    permission_classes = [IsOwnerOrReadOnly, IsAuthenticated]
    serializer_class = EmployeeSideUpdateSerializer
    lookup_field = "id"
