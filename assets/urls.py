from django.urls import path

from assets.views import (
    AssetDetailsView,
    AssetHistoryListAPIView,
    AssetListCreateAPIView,
    AuthEmployeeDetailsVIEW,
    CategoryDropDown,
    EmployeeDepartmentDropdown,
    EmployeeDetailsView,
    EmployeeDropDown,
    EmployeeListCreateAPIView,
    EmployeeSideDetailsUpdate,
    UserAssetDetailsView,
    UserOwnAssetDetailsAPIView,
)
from assets.views.otp_views import (
    ChangePassword,
    RequestOTPView,
    ResetPasswordView,
    VerifyOTPView,
)

urlpatterns = [
    # Assets Routes
    path("assets/", AssetListCreateAPIView.as_view(), name="asset_list_create"),
    path("assets/<int:id>/", AssetDetailsView.as_view(), name="asset_list_detail"),
    path(
        "assets/employee/<int:id>/",
        UserAssetDetailsView.as_view(),
        name="employee_assets",
    ),
    # Employee Routes
    path(
        "employees/", EmployeeListCreateAPIView.as_view(), name="employee_list_create"
    ),
    path("employees/<int:id>/", EmployeeDetailsView.as_view(), name="employee_details"),
    path(
        "employees-side/<int:id>/",
        EmployeeSideDetailsUpdate.as_view(),
        name="employee_side_details",
    ),
    path(
        "employees-side/asset/<int:id>/",
        UserOwnAssetDetailsAPIView.as_view(),
        name="employee_assets_details",
    ),
    path(
        "employees/drop-downs/",
        EmployeeDropDown.as_view(),
        name="employee_dropdown",
    ),
    path(
        "category/drop-downs/",
        CategoryDropDown.as_view(),
        name="category_dropdown",
    ),
    path(
        "department/drop-downs/",
        EmployeeDepartmentDropdown.as_view(),
        name="department_dropdown",
    ),
    path(
        "assets/history/", AssetHistoryListAPIView.as_view(), name="asset_history_list"
    ),
    # OTP Routes and Auth
    path("auth/me/", AuthEmployeeDetailsVIEW.as_view(), name="auth_employee_details"),
    path("forget-password/", RequestOTPView.as_view(), name="change_password"),
    path("verify-otp/", VerifyOTPView.as_view(), name="asset_history_list"),
    path("reset-password/", ResetPasswordView.as_view(), name="reset_password"),
    path("change-password/", ChangePassword.as_view(), name="change-password"),
]
