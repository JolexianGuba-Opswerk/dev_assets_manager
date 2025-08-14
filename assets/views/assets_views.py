from django.db.models import Prefetch
from django_filters.rest_framework import DjangoFilterBackend
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from assets.filters import AssetFilter
from assets.models import Asset
from django.contrib.auth.models import User
from rest_framework import generics, filters
from assets.permissions import IsOwnerOrReadOnly, IsOwnerAssetsOrReadOnly
from assets.serializers.asset_serializers import (AssetListSerializer, AssetCreateSerializer,
                                                  AssetDetailSerializer, UserAssetListSerializer, UserAssetSerializer)
from rest_framework.permissions import IsAuthenticated, IsAdminUser
import time

# CREATE/GET view for Asset
class AssetListCreateAPIView(generics.ListCreateAPIView):
    queryset = Asset.objects.select_related('category', 'assigned_to').order_by('-id')
    serializer_class = AssetListSerializer
    permission_classes = [IsAuthenticated]

    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter
    ]

    filterset_class = AssetFilter
    ordering_fields = [
        'purchased_date',
        'name'
    ]
    search_fields = [
        'name',
        'serial_number',
        'description'
    ]

    # 15 MINUTES OF CACHING
    @method_decorator(cache_page(60 * 15, key_prefix='asset_list'))
    def list(self, request, *args, **kwargs):
        return super().list(request, request, *args, **kwargs)

    def get_queryset(self):
        time.sleep(2)
        return super().get_queryset()

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return AssetCreateSerializer
        return super().get_serializer_class()

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAdminUser()]
        return [IsAuthenticated()]


# GET/UPDATE/DELETE view for Asset Details
class AssetDetailsView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Asset.objects.select_related('assigned_to','category')
    serializer_class = AssetCreateSerializer
    lookup_field = 'id'

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return AssetDetailSerializer
        return super().get_serializer_class()

    def get_permissions(self):
        if self.request.method == 'GET':
            return [IsAuthenticated()]
        return [IsAdminUser()]


# Getting User's Asset with Details
class UserAssetDetailsView(generics.ListAPIView):
    queryset = (User.objects
                .select_related('employee_profile__department')
                .prefetch_related('assets__category'))
    serializer_class = UserAssetListSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]

    filter_backends = [
        filters.SearchFilter
    ]
    search_fields = ['username','email']


# Getting Own Assets of User
class UserOwnAssetDetailsAPIView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated, IsOwnerAssetsOrReadOnly]
    queryset = User.objects.prefetch_related(
        Prefetch(
            'assets',
            Asset.objects
            .select_related('category')
            .order_by('-purchase_date')
        )
    )
    serializer_class = UserAssetSerializer
    lookup_field = 'id'












def AssetInfoView(request):
    pass
    # def get_queryset(self):
    #     return (Asset.objects.only('id','name', 'serial_number', 'status', 'purchase_date')
    #               .all().order_by('-id'))
    #
    # def get(self, request):
    #     query_set = self.get_queryset()
    #
    #     if not query_set.exists():
    #         return Response({"message": "No assets found"}, status=404)
    #
    #     serialized_data = AssetSerializer(query_set, many=True).data
    #     return Response(serialized_data, status=status.HTTP_200_OK)
    #
    # def post(self, request):
    #     employee = None
    #     category = None
    #     try:
    #         body = request.data
    #
    #         if not body:
    #             return JsonResponse(
    #                 {"error": "No data provided"},
    #                 status=400)
    #
    #         if body.get('assigned_to') and body.get('assigned_to') is not None:
    #             try:
    #                 employee = User.objects.get(id=body.get('assigned_to'))
    #             except User.DoesNotExist:
    #                 return JsonResponse({"error": "Assigned user does not exist"}, status=404)
    #
    #         if body.get('category'):
    #             try:
    #                 category = Category.objects.get(id=body.get('category'))
    #             except Category.DoesNotExist:
    #                 return JsonResponse({"error": "Category does not exist"}, status=404)
    #
    #         asset = Asset.objects.create(
    #             name=body.get('name'),
    #             serial_number=body.get('serial_number'),
    #             status=body.get('status', 'IN_STORAGE'),
    #             purchase_date=body.get('purchase_date'),
    #             description=body.get('description', ''),
    #             category=category if 'category' in body else None,
    #             assigned_to=employee if 'assigned_to' in body else None,
    #         )
    #         if 'assigned_to' in body:
    #             AssetHistory.objects.create(
    #                 asset=asset,
    #                 previous_user=None,
    #                 new_user=employee if 'assigned_to' in body else None,
    #                 notes=body.get('notes', " ")
    #             )
    #         asset.full_clean()
    #         asset.save()
    #         return JsonResponse({"message": "Asset created successfully "}, status=201)
    #     except Exception as e:
    #         return JsonResponse({"error": str(e)}, status=400)


def assets_list_create(request):
    pass
    # if request.method == 'GET':
    #     assets = (Asset.objects.only('id','name', 'serial_number', 'status', 'purchase_date')
    #               .all().order_by('-id'))
    #
    #     if not assets.exists():
    #         return JsonResponse({"message": "No assets found"}, status=404)
    #
    #     serialize_data = []
    #     for asset in assets:
    #         serialize_data.append({
    #             "id": asset.id,
    #             "name": asset.name,
    #             "serial_number": asset.serial_number,
    #             "status": asset.get_status_display(),
    #             "purchase_date": asset.purchase_date.strftime('%Y-%m-%d') if asset.purchase_date else None,
    #         })
    #
    #     pprint(connection.queries)
    #     print('Connection Queries:', len(connection.queries))
    #
    #     return JsonResponse(serialize_data, safe=False)
    #
    # elif request.method == 'POST':
    #     employee = None
    #     category = None
    #     try:
    #         body = json.loads(request.body)
    #
    #         if not body:
    #             return JsonResponse({"error": "No data provided"}, status=400)
    #
    #         if body.get('assigned_to') and body.get('assigned_to') is not None:
    #             try:
    #                 employee = User.objects.get(id=body.get('assigned_to'))
    #             except User.DoesNotExist:
    #                 return JsonResponse({"error": "Assigned user does not exist"}, status=404)
    #
    #         if body.get('category'):
    #             try:
    #                 category = Category.objects.get(id=body.get('category'))
    #             except Category.DoesNotExist:
    #                 return JsonResponse({"error": "Category does not exist"}, status=404)
    #
    #         asset = Asset.objects.create(
    #             name=body.get('name'),
    #             serial_number=body.get('serial_number'),
    #             status=body.get('status', 'IN_STORAGE'),
    #             purchase_date=body.get('purchase_date'),
    #             description=body.get('description', ''),
    #             category=category if 'category' in body else None,
    #             assigned_to=employee if 'assigned_to' in body else None,
    #         )
    #         if 'assigned_to' in body:
    #             AssetHistory.objects.create(
    #                 asset=asset,
    #                 previous_user=None,
    #                 new_user=employee if 'assigned_to' in body else None,
    #                 notes=body.get('notes', " ")
    #             )
    #         asset.full_clean()
    #         asset.save()
    #         return JsonResponse({"message": "Asset created successfully "}, status=201)
    #     except Exception as e:
    #         return JsonResponse({"error": str(e)}, status=400)


def asset_detail(request, asset_id):
    pass
    # if request.method == 'GET':
    #     try:
    #         asset = Asset.objects.select_related('assigned_to', 'category').get(id=asset_id)
    #     except Asset.DoesNotExist:
    #         return JsonResponse({"error": "Asset not found"}, status=404)
    #
    #     history_entries = asset.assethistory_set.select_related('new_user', 'previous_user').all().order_by(
    #         '-change_date')
    #     history_data = []
    #
    #     for history in history_entries:
    #         history_data.append({
    #             "change_date": history.change_date.strftime('%Y-%m-%d %H:%M:%S'),
    #             "previous_user": history.previous_user.get_full_name() if history.previous_user else "None",
    #             "new_user": history.new_user.get_full_name() if history.new_user else "None",
    #             "notes": history.notes,
    #         })
    #
    #     serialize_data = {
    #         "id": asset.id,
    #         "name": asset.name,
    #         "serial_number": asset.serial_number,
    #         "category": asset.category.name if asset.category else None,
    #         "status": asset.get_status_display(),
    #         "purchase_date": asset.purchase_date,
    #         "description": asset.description,
    #         "assigned_to": {
    #             "id": asset.assigned_to.id,
    #             "full_name": asset.assigned_to.get_full_name(),
    #             "department": (
    #                 asset.assigned_to.employeeprofile.department.full_name
    #                 if asset.assigned_to else None
    #             )
    #         } if asset.assigned_to else "No user assigned",
    #         "asset_history": history_data if history_data else "No asset history"
    #     }
    #
    #     pprint(connection.queries)
    #     print('Connection Queries:', len(connection.queries))
    #
    #     return JsonResponse(serialize_data, status=200)
    #
    # elif request.method == 'PATCH':
    #     try:
    #         asset = Asset.objects.get(id=asset_id)
    #     except Asset.DoesNotExist:
    #         return JsonResponse({"error": "Asset not found"}, status=404)
    #
    #     try:
    #         body = json.loads(request.body)
    #         if not body:
    #             return JsonResponse({"error": "No data provided"}, status=400)
    #
    #         updatetable_fields = ['name', 'serial_number', 'status', 'purchase_date', 'description']
    #
    #         # Update asset fields based on the provided body
    #         for field in updatetable_fields:
    #             if field in body and body[field] not in [None, '']:
    #                 setattr(asset, field, body[field])
    #
    #         if 'category' in body:
    #             try:
    #                 category = Category.objects.get(id=body['category']) if 'category' in body else asset.category
    #                 asset.category = category
    #             except Category.DoesNotExist:
    #                 return JsonResponse({"error": "Category does not exist"}, status=404)
    #
    #         if 'assigned_to' in body:
    #             prev_user = asset.assigned_to
    #             try:
    #                 if body['assigned_to'] in [None, '']:
    #                     AssetHistory.objects.create(
    #                         asset=asset,
    #                         previous_user=prev_user,
    #                         new_user=None,
    #                         notes=body.get('notes', " ")
    #                     )
    #                     asset.assigned_to = None
    #                 else:
    #                     user = User.objects.get(id=body['assigned_to']) if 'assigned_to' in body else asset.assigned_to
    #                     asset.assigned_to = user
    #                     AssetHistory.objects.create(
    #                         asset=asset,
    #                         previous_user=prev_user,
    #                         new_user=user,
    #                         notes=body.get('notes', " ")
    #                     )
    #             except User.DoesNotExist:
    #                 return JsonResponse({"error": "Assigned user does not exist"}, status=404)
    #
    #
    #         asset.full_clean()
    #         asset.save()
    #         return JsonResponse({"message": "Asset updated"},status=200)
    #
    #     except ValidationError as ve:
    #         return JsonResponse({"error": str(ve.message_dict)}, status=400)
    #     except IntegrityError as ie:
    #         return JsonResponse({"error": str(ie)}, status=400)
    #     except Exception as e:
    #         return JsonResponse({"error": str(e)}, status=400)
    #
    # elif request.method == 'DELETE':
    #     try:
    #         asset = Asset.objects.get(id=asset_id)
    #     except Asset.DoesNotExist:
    #         return JsonResponse({"error": "Asset not found"}, status=404)
    #
    #     asset.delete()
    #     return JsonResponse({"message": "Asset deleted"}, status=204)


def get_users_assets(request):
    pass
    # if not request.method == 'GET':
    #     return JsonResponse({"error": "Method not allowed"}, status=405)
    #
    # connection.queries.clear()
    # # users = User.objects.all()
    #
    # users = User.objects.select_related('employeeprofile__department').prefetch_related('asset_set')
    #
    # if not users.exists():
    #     return JsonResponse({"message": "No users found"}, status=404)
    # data = []
    #
    # for user in users:
    #     for asset in user.asset_set.all():
    #         data.append({
    #             "user_id": user.id,
    #             "user_full_name": user.get_full_name(),
    #             "user_department": (
    #                 user.employeeprofile.department.full_name if hasattr(user, 'employeeprofile') else "No department"
    #             ),
    #             "assets":[
    #
    #                 {
    #                     "asset_id": asset.id,
    #                     "asset_name": asset.name,
    #                     "asset_serial_number": asset.serial_number,
    #                     "asset_status": asset.get_status_display(),
    #                     "asset_purchase_date": asset.purchase_date.strftime('%Y-%m-%d'),
    #                 }
    #                 for asset in user.asset_set.all()
    #             ],
    #
    #         })
    #
    # pprint(connection.queries)
    # print(len(connection.queries), " queries executed")
    #
    # return JsonResponse(data, safe=False, status=200)
