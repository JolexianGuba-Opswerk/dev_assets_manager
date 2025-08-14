from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
from .models import Asset, Category


@receiver([post_save, post_delete], sender=Asset)
def invalidate_asset_list_cache(sender, instance, **kwargs):
    print("Clearing Asset Cache")
    cache.delete_pattern("*asset_list*")
