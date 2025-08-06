from django.db import models
from django.contrib.auth.models import User


class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)
    full_name = models.CharField(max_length=100, null=True, blank=True, default=None)
    created_at = models.DateTimeField(auto_now_add=True)
    added_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    added_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.name


# Employee model
class EmployeeProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    position = models.CharField(max_length=100)



# Asset model
class Asset(models.Model):
    STATUS_CHOICES = [
        ('IN_USE', 'In Use'),
        ('IN_STORAGE', 'In Storage'),
        ('REPAIR', 'Under Repair'),
        ('RETIRED', 'Retired'),
    ]

    name = models.CharField(max_length=100)
    serial_number = models.CharField(max_length=100, unique=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, default=None, null=True, blank=True)
    purchase_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='IN_STORAGE')
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.name} ({self.serial_number})"


# Asset History model (optional but good for tracking)
class AssetHistory(models.Model):
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE)
    previous_user = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name='previous_assets'
    )
    new_user = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name='new_assets'
    )
    change_date = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.asset.name} reassigned on {self.change_date.strftime('%Y-%m-%d')}"
