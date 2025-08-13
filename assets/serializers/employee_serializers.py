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
            'department': obj.employee_profile.department.full_name,
            'position': obj.employee_profile.position
        } if obj.employee_profile else None


class EmployeeCreateSerializer(serializers.ModelSerializer):
    position = serializers.CharField(
        write_only=True,
        required=True,
        allow_blank=False)
    department = serializers.PrimaryKeyRelatedField(
        queryset=Department.objects.all(),
        write_only=True
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name',
                  'email', 'password', 'department', 'position']

        extra_kwargs = {
            'password': {'write_only': True}
        }

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


class EmployeeUpdateSerializer(serializers.ModelSerializer):
    position = serializers.CharField(
        source='employee_profile.position',
        required=True)

    department = serializers.PrimaryKeyRelatedField(
        source='employee_profile.department',
        queryset=Department.objects.all()
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name',
                  'email', 'department', 'position']

        extra_kwargs = {
            'password': {'write_only': True}
        }

    def update(self, instance, validated_data):
        profile_data = validated_data.pop('employee_profile', {})
        department = profile_data.get('department', None)
        position = profile_data.get('position', None)
        password = validated_data.pop('password', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if password:
            instance.set_password(password)
        instance.save()

        if department:
            setattr(instance.employee_profile, 'department', department)
        if position:
            setattr(instance.employee_profile, 'position', position)
        instance.employee_profile.save()

        return instance


class EmployeeSideUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name',
                  'email', 'password']
        write_only_fields = 'password'


