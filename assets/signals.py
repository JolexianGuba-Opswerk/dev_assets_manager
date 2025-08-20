from django.contrib.auth.models import User
from django.core.cache import cache
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from .models import Asset, AssetHistory


@receiver([post_save, post_delete], sender=Asset)
def invalidate_asset_list_cache(sender, instance, **kwargs):
    cache.delete_pattern("*asset_list*")


@receiver([post_save, post_delete], sender=User)
def invalidate_employee_list_cache(sender, instance, **kwargs):
    cache.delete_pattern("*employee_list*")


@receiver([post_save, post_delete], sender=AssetHistory)
def invalidate_asset_history_list_cache(sender, instance, **kwargs):
    cache.delete_pattern("*asset_history*")
