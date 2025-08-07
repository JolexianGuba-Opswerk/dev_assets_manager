from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from assets.models import Asset, Category, AssetHistory
from django.contrib.auth.models import User
import json

# Get all assets or create a new asset
@csrf_exempt
@require_http_methods(["GET", "POST"])
def assets_list_create(request):
    if request.method == 'GET':
        assets = Asset.objects.all().order_by('-id')
        if not assets:
            return JsonResponse({"message": "No assets found"}, status=404)

        data = [
            {
                "id": a.id,
                "name": a.name,
                "serial_number": a.serial_number,
                "status": a.get_status_display(),
                "purchase_date": a.purchase_date,
            }
            for a in assets
        ]
        return JsonResponse(data, safe=False)

    elif request.method == 'POST':
        employee = None
        category = None
        try:
            body = json.loads(request.body)

            if not body:
                return JsonResponse({"error": "No data provided"}, status=400)

            if body.get('assigned_to') and body.get('assigned_to') is not None:
                try:
                    employee = User.objects.get(id=body.get('assigned_to'))
                except User.DoesNotExist:
                    return JsonResponse({"error": "Assigned user does not exist"}, status=404)

            if body.get('category'):
                try:
                    category = Category.objects.get(id=body.get('category'))
                except Category.DoesNotExist:
                    return JsonResponse({"error": "Category does not exist"}, status=404)

            asset = Asset.objects.create(
                name=body.get('name'),
                serial_number=body.get('serial_number'),
                status=body.get('status', 'IN_STORAGE'),
                purchase_date=body.get('purchase_date'),
                description=body.get('description', ''),
                category=category if 'category' in body else None,
                assigned_to=employee if 'assigned_to' in body else None,
            )
            if 'assigned_to' in body:
                AssetHistory.objects.create(
                    asset=asset,
                    previous_user=None,
                    new_user=employee if 'assigned_to' in body else None,
                    notes=body.get('notes', " ")
                )
            asset.full_clean()
            asset.save()
            return JsonResponse({"message": "Asset created successfully "}, status=201)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)


# Get, update or delete a specific asset by ID
@csrf_exempt
@require_http_methods(["GET", "PATCH", "DELETE"])
def asset_detail(request, asset_id):
    try:
        asset = Asset.objects.get(id=asset_id)

    except Asset.DoesNotExist:
        return JsonResponse({"error": "Asset not found"}, status=404)

    if request.method == 'GET':
        history_entries = asset.assethistory_set.all().order_by('-change_date')
        history_data = [
            {
                "change_date": entry.change_date.strftime('%Y-%m-%d %H:%M:%S'),
                "previous_user": entry.previous_user.get_full_name() if entry.previous_user else "None",
                "new_user": entry.new_user.get_full_name() if entry.new_user else "None",
                "notes": entry.notes,
            }
            for entry in history_entries
        ]

        return JsonResponse({
            "id": asset.id,
            "name": asset.name,
            "serial_number": asset.serial_number,
            "category": asset.category.name if asset.category else None,
            "status": asset.get_status_display(),
            "purchase_date": asset.purchase_date,
            "description": asset.description,
            "assigned_to": {
                "id": asset.assigned_to.id,
                "full_name": asset.assigned_to.get_full_name(),
                "department": (
                    asset.assigned_to.employeeprofile.department.full_name
                    if asset.assigned_to else None
                )
            } if asset.assigned_to else "No user assigned",
            "asset_history": history_data if history_data else "No asset history"
        })

    elif request.method == 'PATCH':
        try:
            body = json.loads(request.body)
            if not body:
                return JsonResponse({"error": "No data provided"}, status=400)

            # Update asset fields based on the provided body
            asset.name = body.get('name', asset.name)
            asset.serial_number = body.get('serial_number', asset.serial_number)
            asset.status = body.get('status', asset.status)
            asset.purchase_date = body.get('purchase_date', asset.purchase_date)
            asset.description = body.get('description', asset.description)
            asset.status = body.get('status', asset.status)

            if 'category' in body:
                try:
                    category = Category.objects.get(id=body['category']) if 'category' in body else asset.category
                    asset.category = category
                except Category.DoesNotExist:
                    return JsonResponse({"error": "Category does not exist"}, status=404)

            if 'assigned_to' in body:
                prev_user = asset.assigned_to
                try:
                    if body['assigned_to'] in [None, '']:
                        AssetHistory.objects.create(
                            asset=asset,
                            previous_user=prev_user,
                            new_user=None,
                            notes=body.get('notes', " ")
                        )
                        asset.assigned_to = None
                    else:
                        user = User.objects.get(id=body['assigned_to']) if 'assigned_to' in body else asset.assigned_to
                        asset.assigned_to = user
                        AssetHistory.objects.create(
                            asset=asset,
                            previous_user=prev_user,
                            new_user=user,
                            notes=body.get('notes', " ")
                        )

                except User.DoesNotExist:
                    return JsonResponse({"error": "Assigned user does not exist"}, status=404)

            asset.full_clean()
            asset.save()

            return JsonResponse({"message": "Asset updated"})

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    elif request.method == 'DELETE':
        asset.delete()
        return JsonResponse({"message": "Asset deleted"})

