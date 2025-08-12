from rest_framework import serializers
from assets.models import Asset, Department, Category, EmployeeProfile
from django.contrib.auth.models import User


class EmployeeListSerializer(serializers.ModelSerializer):
    employee_profile = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name',
                  'email', 'employee_profile']

    def get_employee_profile(self, obj):
        return {
            'name': obj.employee_profile.department.full_name,
            'position': obj.employee_profile.position
        } if obj.employee_profile else None


class EmployeeCreateSerializer(serializers.ModelSerializer):
    position = serializers.CharField(write_only=True, required=True, allow_blank=False)
    department = serializers.PrimaryKeyRelatedField(
        queryset=Department.objects.all(),
        write_only=True
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name',
                  'email', 'password', 'department', 'position']
        write_only_fields = 'password'

    def create(self, validated_data):
        department = validated_data.pop('department')
        position = validated_data.pop('position', "")

        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()

        EmployeeProfile.objects.create(
            user=user,
            department=Department.objects.get(name=department),
            position=position
        )

        return user


