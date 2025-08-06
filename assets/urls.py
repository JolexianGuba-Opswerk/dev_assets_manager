from .views import assets_list_create, asset_detail, asset_history_list
from django.urls import path


urlpatterns = [
    path('assets/', assets_list_create, name='assets_list_create'),
    path('assets/<int:asset_id>/', asset_detail, name='asset_detail'),
    path('assets-history/', asset_history_list, name='asset_history_list'),
]