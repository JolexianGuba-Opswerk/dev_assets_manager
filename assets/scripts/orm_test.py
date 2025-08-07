from assets.models import Asset, Department, AssetHistory
from pprint import pprint
from django.db import connection
from django.contrib.auth.models import User


def run():
    users = User.objects.prefetch_related('asset_set')
    #users = User.objects.all()

    for user in users:
        for asset in user.asset_set.all():
            print(f"{user.get_full_name()} - {asset.name} ({asset.serial_number})")

    print("Query",len(connection.queries))
