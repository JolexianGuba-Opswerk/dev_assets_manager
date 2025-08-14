from assets.views import (AssetListCreateAPIView, AssetDetailsView,
                          UserAssetDetailsView, EmployeeListCreateAPIView, EmployeeDetailsView,
                          EmployeeSideDetailsUpdate, AssetHistoryListAPIView, UserOwnAssetDetailsAPIView)
from django.urls import path

from assets.views.otp_views import RequestOTPView, VerifyOTPView, ResetPasswordView

urlpatterns = [
    # Assets Routes
    path('assets/', AssetListCreateAPIView.as_view(), name='asset_list_create'),
    path('assets/<int:id>/', AssetDetailsView.as_view(), name='asset_list_detail'),
    path('assets/employee/', UserAssetDetailsView.as_view(), name='employee_assets'),
    # Employee Routes
    path('employees/', EmployeeListCreateAPIView.as_view(), name='employee_details'),
    path('employees/<int:id>/', EmployeeDetailsView.as_view(), name='employee_details'),
    path('employees-side/<int:id>/', EmployeeSideDetailsUpdate.as_view(), name='employee_details'),
    path('employees-side/asset/<int:id>/', UserOwnAssetDetailsAPIView.as_view(), name='employee_assets_details'),
    path('assets/history/', AssetHistoryListAPIView.as_view(), name='asset_history_list'),

    # OTP Routes
    path('forget-password/',  RequestOTPView.as_view(), name='change_password'),
    path('verify-otp/', VerifyOTPView.as_view(), name='asset_history_list'),
    path('reset-password/', ResetPasswordView.as_view(), name='reset_password'),
]