from assets.views.assets_views import (
    AssetListCreateAPIView,
    AssetDetailsView,
    UserAssetDetailsView,
    UserOwnAssetDetailsAPIView,
)
from assets.views.assets_history_views import AssetHistoryListAPIView
from assets.views.employee_views import (
    EmployeeListCreateAPIView,
    EmployeeDetailsView,
    EmployeeSideDetailsUpdate,
    AuthEmployeeDetailsVIEW,
)
from assets.views.oidc_views import profile_view, logout_view
