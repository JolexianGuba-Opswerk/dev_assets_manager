from assets.views import (AssetListCreateAPIView, AssetDetailsView,
                          UserAssetDetailsView, EmployeeListCreateAPIView, EmployeeDetailsView, EmployeeSideDetailsUpdate )
from django.urls import path



urlpatterns = [
    path('assets/', AssetListCreateAPIView.as_view(), name='asset_list_create'),
    path('assets/<int:id>/', AssetDetailsView.as_view(), name='asset_list_detail'),
    path('assets/employee/', UserAssetDetailsView.as_view(), name='employee_assets'),

    # path('assets-history/', asset_history_list, name='asset_history_list'),
    path('employees/', EmployeeListCreateAPIView.as_view(), name='employee_details'),
    path('employees/<int:id>/', EmployeeDetailsView.as_view(), name='employee_details'),
    path('employees-side/<int:id>/', EmployeeSideDetailsUpdate.as_view(), name='employee_details'),

    # path('employees/', employee_list, name='employee_list'),
]