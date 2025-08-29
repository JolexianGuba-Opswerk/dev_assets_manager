import django_filters
from django.contrib.auth.models import User

from assets.models import Asset


class AssetFilter(django_filters.FilterSet):

    category = django_filters.CharFilter(
        field_name="category__name", lookup_expr="iexact"
    )

    class Meta:
        model = Asset
        fields = ["category", "status"]


class EmployeeFilter(django_filters.FilterSet):
    department = django_filters.CharFilter(
        field_name="employee_profile__department__name", lookup_expr="iexact"
    )
    position = django_filters.CharFilter(
        field_name="employee_profile__position", lookup_expr="icontains"
    )
    is_verified = django_filters.BooleanFilter(
        field_name="employee_profile__is_verified",
    )

    class Meta:
        model = User
        fields = ["department", "position", "is_verified"]
