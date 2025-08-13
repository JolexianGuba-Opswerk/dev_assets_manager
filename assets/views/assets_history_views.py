from django.db.models import Prefetch
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from rest_framework.permissions import IsAuthenticated
from assets.models import AssetHistory, Asset
from rest_framework import generics, filters
from assets.serializers.asset_serializers import AssetHistorySerializer


# Need to check if there is a django built in model for history like this
class AssetHistoryListAPIView(generics.ListAPIView):
    queryset = (AssetHistory.objects
                .prefetch_related('previous_user','new_user')
                .order_by('-id'))

    serializer_class = AssetHistorySerializer
    permission_classes = [IsAuthenticated]

    filter_backends = [
        filters.SearchFilter
    ]
    search_fields = ['assets__name']


# Asset History Sectiona
@csrf_exempt
@require_http_methods(["GET"])
def asset_history_list(request):
    sort_order = request.GET.get('sort', 'desc')

    if sort_order not in ['asc', 'desc']:
        return JsonResponse({"error": "Invalid sort value. Use 'asc' or 'desc'."}, status=400)

    if sort_order == 'asc':
        history_entries = AssetHistory.objects.select_related('asset', 'previous_user', 'new_user').order_by('change_date')
    else:
        history_entries = AssetHistory.objects.select_related('asset', 'previous_user', 'new_user').order_by('-change_date')

    data = []
    for entry in history_entries:
        data.append({
            "id": entry.id,
            "asset": {
                "id": entry.asset.id,
                "name": entry.asset.name,
                "serial_number": entry.asset.serial_number,
            },
            "previous_user": entry.previous_user.get_full_name() if entry.previous_user else "Unassigned",
            "new_user": entry.new_user.get_full_name() if entry.new_user else "Unassigned",
            "change_date": entry.change_date.strftime("%Y-%m-%d %H:%M:%S"),
            "notes": entry.notes,
        })

    return JsonResponse(data, safe=False)