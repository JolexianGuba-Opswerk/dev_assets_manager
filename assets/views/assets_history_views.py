import logging
import time

from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework import filters, generics
from rest_framework.permissions import IsAuthenticated

from assets.models import AssetHistory
from assets.serializers.asset_serializer import AssetHistorySerializer

logger = logging.getLogger("assets")


# Need to check if there is a django built in model for history like this
class AssetHistoryListAPIView(generics.ListAPIView):
    queryset = AssetHistory.objects.prefetch_related(
        "previous_user", "new_user"
    ).order_by("-id")

    serializer_class = AssetHistorySerializer
    permission_classes = [IsAuthenticated]

    filter_backends = [filters.SearchFilter]
    search_fields = ["assets__name"]

    @method_decorator(cache_page(60 * 15, key_prefix="asset_history"))
    def list(self, request, *args, **kwargs):
        return super().list(request, request, *args, **kwargs)

    def get_queryset(self):
        time.sleep(2)
        return super().get_queryset()
