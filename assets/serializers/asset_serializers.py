from rest_framework import serializers
from assets.models import Asset, Department, Category, EmployeeProfile
from django.contrib.auth.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')


class DepartmentSerializer(serializers.ModelSerializer):
    added_by = UserSerializer(read_only=True)

    class Meta:
        model = Department
        fields = ['name', 'full_name', 'created_at', 'added_by']


class EmployeeProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    department = DepartmentSerializer(read_only=True)

    class Meta:
        model = EmployeeProfile
        fields = ['user', 'department', 'position']


# ASSET SERIALIZERS
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['name']


class AssetCreateSerializer(serializers.ModelSerializer):
    notes = serializers.CharField(write_only=True, required=False, allow_blank=True)


    class Meta:
        model = Asset
        fields = ['name', 'serial_number', 'category', 'assigned_to',
                  'purchase_date', 'status', 'description', 'notes']

    def create(self, validated_data):
        notes = validated_data.pop('notes', "")
        assigned_to = validated_data.get('assigned_to', None)
        asset = Asset.objects.create(**validated_data)

        if assigned_to:
            Asset.objects.create(
                asset=asset,
                previous_user=None,
                new_user=assigned_to,
                notes=notes
            )
        return asset


class AssetListSerializer(serializers.ModelSerializer):
    category = serializers.SerializerMethodField()

    class Meta:
        model = Asset
        fields = ['id', 'name', 'serial_number', 'category', 'status', 'description']

    def get_category(self, obj):
        return obj.category.name if obj.category else None


class AssetDetailSerializer(serializers.ModelSerializer):
    category = serializers.SerializerMethodField()
    assigned_to = serializers.SerializerMethodField()

    class Meta:
        model = Asset
        fields = ['id', 'name', 'serial_number', 'category', 'assigned_to', 'purchase_date', 'status', 'description']

    def get_assigned_to(self, obj):
        if obj.assigned_to:
            return {
                'name': obj.assigned_to.get_full_name(),
                'email': obj.assigned_to.email
            }
        return None

    def get_category(self, obj):
        return obj.category.name if obj.category else None


class UserAssetDetailSerializer(serializers.ModelSerializer):
    category = serializers.SerializerMethodField()
    class Meta:
        model = Asset
        fields = ['id', 'name', 'serial_number', 'category']

    def get_category(self, obj):
        return obj.category.name if obj.category else None


class UserAssetListSerializer(serializers.ModelSerializer):
    assets = UserAssetDetailSerializer(many=True, read_only=True)
    employee_profile = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'employee_profile', 'assets']

    def get_employee_profile(self, obj):
        if obj.employee_profile:
            return {
                'department': obj.employee_profile.department.full_name,
                'position': obj.employee_profile.position
            }
        return None

