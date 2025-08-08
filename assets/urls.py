from assets.views import (assets_list_create, asset_detail, asset_history_list,
                          get_users_assets, employee_list, employee_details)
from django.urls import path


urlpatterns = [
    path('assets/', assets_list_create, name='assets_list_create'),
    path('assets/user/', get_users_assets, name='get_users_assets'),
    path('assets/<int:asset_id>/', asset_detail, name='asset_detail'),
    path('assets-history/', asset_history_list, name='asset_history_list'),
    path('employees/<int:employee_id>/', employee_details, name='employee_details'),
    path('employees/', employee_list, name='employee_list'),
]