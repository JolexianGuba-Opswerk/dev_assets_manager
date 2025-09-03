from django.contrib.auth.models import User
from rest_framework import serializers

from assets.models import Asset, AssetHistory, Category, Department, EmployeeProfile


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "email")


class DepartmentSerializer(serializers.ModelSerializer):
    added_by = UserSerializer(read_only=True)

    class Meta:
        model = Department
        fields = ["name", "full_name", "created_at", "added_by"]


class EmployeeProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    department = DepartmentSerializer(read_only=True)

    class Meta:
        model = EmployeeProfile
        fields = ["user", "department", "position"]


# ASSET SERIALIZERS
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["name"]


class AssetCreateSerializer(serializers.ModelSerializer):
    notes = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = Asset
        fields = [
            "name",
            "serial_number",
            "category",
            "assigned_to",
            "purchase_date",
            "status",
            "description",
            "notes",
        ]

    def create(self, validated_data):
        notes = validated_data.pop("notes", "")
        assigned_to = validated_data.get("assigned_to", None)
        asset = Asset.objects.create(**validated_data)

        if assigned_to:
            AssetHistory.objects.create(
                asset=asset, previous_user=None, new_user=assigned_to, notes=notes
            )
        return asset

    def update(self, instance, validated_data):
        notes = validated_data.pop("notes", None)
        new_user = validated_data.get("assigned_to", None)
        old_user = instance.assigned_to

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()

        if "assigned_to" in validated_data and old_user != new_user:
            AssetHistory.objects.create(
                asset=instance, previous_user=old_user, new_user=new_user, notes=notes
            )

        if notes:
            current_history = (
                AssetHistory.objects.filter(asset=instance)
                .order_by("-change_date")
                .first()
            )
            current_history.notes = notes
            current_history.save()

        return instance


class AssetListSerializer(serializers.ModelSerializer):
    category = serializers.SerializerMethodField()

    class Meta:
        model = Asset
        fields = [
            "id",
            "name",
            "serial_number",
            "category",
            "status",
            "description",
        ]

    def get_category(self, obj):
        return obj.category.name if obj.category else None


class AssetDetailSerializer(serializers.ModelSerializer):
    category = serializers.SerializerMethodField()
    assigned_to = serializers.SerializerMethodField()

    class Meta:
        model = Asset
        fields = [
            "id",
            "name",
            "serial_number",
            "category",
            "assigned_to",
            "purchase_date",
            "status",
            "description",
        ]

    def get_assigned_to(self, obj):
        if obj.assigned_to:
            return {
                "id": obj.assigned_to.id,
                "name": obj.assigned_to.get_full_name(),
                "email": obj.assigned_to.email,
            }
        return None

    def get_category(self, obj):
        if obj.category:
            return {
                "id": obj.category.id,
                "name": obj.category.name,
            }
        return None


# Nested Serializer for our Employee Asset
class UserAssetDetailSerializer(serializers.ModelSerializer):
    category = serializers.SerializerMethodField()

    class Meta:
        model = Asset
        fields = ["id", "name", "serial_number", "category"]

    def get_category(self, obj):
        return obj.category.name if obj.category else None


class UserAssetListSerializer(serializers.ModelSerializer):
    assets = UserAssetDetailSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "assets",
        ]


class AssetHistorySerializer(serializers.ModelSerializer):
    new_user = serializers.StringRelatedField()
    previous_user = serializers.StringRelatedField()
    asset = serializers.SerializerMethodField()

    class Meta:
        model = AssetHistory
        fields = ["previous_user", "new_user", "change_date", "notes", "asset"]

    def get_asset(self, obj):
        return {
            "id": obj.asset.id,
            "name": obj.asset.name,
            "serial_number": obj.asset.serial_number,
        }


class UserAssetSerializer(serializers.ModelSerializer):
    assets = AssetListSerializer(many=True)

    class Meta:
        model = User
        fields = ["username", "email", "assets"]
