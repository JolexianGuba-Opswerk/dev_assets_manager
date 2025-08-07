from pprint import pprint

from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from assets.models import Asset, Category, AssetHistory, Department, EmployeeProfile
from django.contrib.auth.models import User
from django.db import connection, IntegrityError
import json


@csrf_exempt
@require_http_methods(["GET", "POST"])
def employee_list(request):
    if request.method == 'GET':
        employees = User.objects.select_related('employeeprofile', 'employeeprofile__department').order_by('-id')

        if not employees.exists():
            return JsonResponse({"message": "No employees found"}, status=404)

        serialized_data = []
        for employee in employees:
            serialized_data.append({
                "id": employee.id,
                "username": employee.username,
                "first_name": employee.first_name,
                "last_name": employee.last_name,
                "email": employee.email,
                "department": employee.employeeprofile.department.name if hasattr(employee,
                                                                                  'employeeprofile') else None,
                "position": employee.employeeprofile.position if hasattr(employee, 'employeeprofile') else None,
            })

        pprint(connection.queries)
        return JsonResponse(serialized_data, safe=False, status=200)

    elif request.method == 'POST':
        try:
            body = json.loads(request.body)

            if not body:
                return JsonResponse({"error": "No data provided"}, status=400)

            department_id = body.get('department')
            position = body.get('position')

            if department_id and position:
                try:
                    department = Department.objects.get(id=department_id)
                except Department.DoesNotExist:
                    return JsonResponse({"error": "Department does not exist"}, status=404)
            else:
                return JsonResponse({"error": "Department ID and position is required "}, status=400)

            try:
                user = User.objects.create_user(
                    username=body.get('username'),
                    password=body.get('password'),
                    first_name=body.get('first_name'),
                    last_name=body.get('last_name'),
                    email=body.get('email')
                )
                user.full_clean()

                if not user:
                    return JsonResponse({"error": "User creation failed"}, status=400)

                employeeprofile = EmployeeProfile.objects.create(
                    user=user,
                    department=department,
                    position=position
                )
                employeeprofile.full_clean()

            except ValidationError as e:
                return JsonResponse({"error": str(e.message_dict)}, status=400)
            except IntegrityError as e:
                return JsonResponse({"error": str(e)}, status=400)
            except Exception as e:
                return JsonResponse({"error": str(e)}, status=400)

            return JsonResponse({
                "message": "Employee created successfully",
                "employee_id": user.id
            }, status=201)

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON data"}, status=400)
