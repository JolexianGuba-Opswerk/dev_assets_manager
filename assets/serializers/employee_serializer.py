from django.contrib.auth.models import User
from rest_framework import serializers

from assets.models import Category, Department, EmployeeProfile
from assets.tasks import send_welcome_email


class EmployeeListSerializer(serializers.ModelSerializer):
    employee_profile = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "employee_profile",
            "is_superuser",
        ]

    def get_employee_profile(self, obj):
        profile = getattr(obj, "employee_profile", None)
        if not profile:
            return None

        department_name = getattr(profile.department, "full_name", None)
        department_id = getattr(profile.department, "id", None)
        position = getattr(profile, "position", None)
        return {
            "is_verified": profile.is_verified,
            "department": department_name,
            "department_id": department_id,
            "position": position,
        }


class EmployeeDetailsSerializer(serializers.ModelSerializer):
    employee_profile = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "date_joined",
            "employee_profile",
        ]

    def get_employee_profile(self, obj):
        profile = getattr(obj, "employee_profile", None)
        if not profile:
            return None

        department_name = getattr(profile.department, "full_name", None)
        id = getattr(profile.department, "id", None)
        position = getattr(profile, "position", None)

        return {
            "department": {"name": department_name, "id": id},
            "is_verified": profile.is_verified,
            "position": position,
            "avatar_url": profile.avatar_url,
        }


class EmployeeCreateSerializer(serializers.ModelSerializer):
    position = serializers.CharField(write_only=True, required=True, allow_blank=False)
    department = serializers.PrimaryKeyRelatedField(
        required=True, queryset=Department.objects.all(), write_only=True
    )
    is_verified = serializers.BooleanField(write_only=True, required=True)

    class Meta:
        model = User
        fields = [
            "username",
            "first_name",
            "last_name",
            "email",
            "password",
            "department",
            "position",
            "is_verified",
        ]

        extra_kwargs = {"password": {"write_only": True}}

    def create(
        self,
        validated_data,
    ):
        department = validated_data.pop("department")
        is_verified = validated_data.pop("is_verified")
        position = validated_data.pop("position", "").title()
        password = validated_data.pop("password")

        first_name = validated_data.get("first_name", "").strip().title()
        last_name = validated_data.get("last_name", "").strip().title()
        full_name = f"{first_name} {last_name}".strip()

        user = User(**validated_data)
        user.set_password(password)
        user.save()

        employee_profile = EmployeeProfile.objects.create(
            user=user,
            department=Department.objects.get(name=department),
            position=position,
            is_verified=is_verified,
        )
        department_name = employee_profile.department.full_name.title()
        send_welcome_email.delay(user.email, full_name, department_name, position)

        return user


class EmployeeUpdateSerializer(serializers.ModelSerializer):
    position = serializers.CharField(source="employee_profile.position", required=True)

    department = serializers.PrimaryKeyRelatedField(
        source="employee_profile.department",
        queryset=Department.objects.all(),
        required=True,
    )
    is_verified = serializers.BooleanField(source="employee_profile.is_verified")

    class Meta:
        model = User
        fields = [
            "username",
            "first_name",
            "last_name",
            "email",
            "department",
            "position",
            "is_verified",
        ]

        extra_kwargs = {"password": {"write_only": True}}

    def update(self, instance, validated_data):
        print("This is updated data:", validated_data)
        profile_data = validated_data.pop("employee_profile", {})
        department = profile_data.get("department", None)
        position = profile_data.get("position", None)
        is_verified = profile_data.get("is_verified", None)
        password = validated_data.pop("password", None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if password:
            instance.set_password(password)
        instance.save()

        if department:
            instance.employee_profile.department = department

        if is_verified is not None:
            instance.employee_profile.is_verified = is_verified

        if position is not None:
            instance.employee_profile.position = position

        instance.employee_profile.save()

        return instance


class EmployeeSideUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["username", "first_name", "last_name", "email"]


class EmployeeDropdownSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "full_name",
        ]

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip()


class CategoryDropdownSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name"]


class DepartmentDropdownSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ["id", "full_name"]
