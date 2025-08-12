from pprint import pprint
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from assets.models import Department, EmployeeProfile
from django.contrib.auth.models import User
from django.db import connection, IntegrityError
from rest_framework.decorators import api_view
from assets.serializers.employee_serializers import EmployeeListSerializer, EmployeeCreateSerializer
from rest_framework import generics
import json


class EmployeeListCreateAPIView(generics.ListCreateAPIView):
    # queryset = User.objects.select_related('employeeprofile', 'employeeprofile__department').filter(
    #             employeeprofile__department__name__exact=department_name.upper()).order_by('-id')

    queryset = User.objects.select_related('employee_profile','employee_profile__department').order_by('-id')
    serializer_class = EmployeeListSerializer

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return EmployeeCreateSerializer
        return super().get_serializer_class()



api_view(['GET', 'POST', 'PATCH'])
def employee_list(request):
    if request.method == 'GET':
        department_name = request.query_params.get('department')
        if department_name:
            employees = User.objects.select_related('employeeprofile', 'employeeprofile__department').filter(
                employeeprofile__department__name__exact=department_name.upper()).order_by('-id')
        else:
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
            

        print("SQL Queries:",len(connection.queries))
        pprint(connection.queries)
        return JsonResponse(serialized_data, safe=False, status=200)

    elif request.method == 'PATCH':
        try:
            body = json.loads(request.body)
            employee_id = body.get('id')
            if not employee_id:
                return JsonResponse({"error": "Employee ID is required"}, status=400)

            try:
                employee = User.objects.get(id=employee_id)
            except User.DoesNotExist:
                return JsonResponse({"error": "Employee does not exist"}, status=404)

            if 'department' in body:
                try:
                    department = Department.objects.get(id=body['department'])
                    employee.employeeprofile.department = department
                except Department.DoesNotExist:
                    return JsonResponse({"error": "Department does not exist"}, status=404)

            if 'position' in body:
                employee.employeeprofile.position = body['position']

            employee.full_clean()
            employee.save()

            return JsonResponse({"message": "Employee updated successfully"}, status=200)

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON data"}, status=400)
        except ValidationError as e:
            return JsonResponse({"error": str(e.message_dict)}, status=400)


def create_employee_profile(request):
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


@csrf_exempt
@require_http_methods(["PATCH", "DELETE"])
def employee_details(request, employee_id):
    if request.method == 'PATCH':
        try:
            employee = User.objects.select_related('employeeprofile','employeeprofile__department').get(id=employee_id)
            body = json.loads(request.body)
            if not body:
                return JsonResponse({"error": "No data provided"}, status=400)

            if 'department' in body and body['department'] is not None:
                try:
                    department = Department.objects.get(id=body['department'])
                    employee.employeeprofile.department = department
                except Department.DoesNotExist:
                    return JsonResponse({"error": "Department does not exist"}, status=404)

            updatable_fields = ['first_name', 'last_name', 'email', 'username', 'position']

            # Update the fields that are needed
            for field in updatable_fields:
                if field in body and body[field] not in [None, ""]:
                    setattr(employee, field, body[field])

            employee.full_clean()
            employee.save()
            pprint(connection.queries)
            return JsonResponse({"message": "Employee updated successfully"}, status=200)

        except User.DoesNotExist:
            return JsonResponse({"error": "Employee not found"}, status=404)
        except ValidationError as ve:
            return JsonResponse({"error": str(ve.message_dict)}, status=400)
        except IntegrityError as ie:
            return JsonResponse({"error": str(ie)}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    elif request.method == 'DELETE':
        try:
            employee = User.objects.get(id=employee_id)
            employee.delete()
            return JsonResponse({"message": "Employee deleted successfully"}, status=204)
        except User.DoesNotExist:
            return JsonResponse({"error": "Employee not found"}, status=404)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)