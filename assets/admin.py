from django.contrib import admin
from .models import Asset, AssetHistory, Department, Category, EmployeeProfile

admin.site.register(Asset)
admin.site.register(AssetHistory)
admin.site.register(Department)
admin.site.register(Category)
admin.site.register(EmployeeProfile)
# Register your models here.
