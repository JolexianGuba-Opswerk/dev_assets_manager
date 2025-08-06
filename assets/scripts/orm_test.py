from assets.models import Department, Category, Employee, Asset, AssetHistory
from pprint import pprint
from django.db import connection

def run():
    # Create 
    department = Department()
    department.name = "FINANCE"
    department.save()
    print("Department created:", department.name)

    # Get all departments
    for dept in Department.objects.all():
        print("-", dept.name)

    # Updating a department 
    department2 = Department.objects.first()
    department2.name = "HR"
    department2.save()
    print("Updated department to:", department2.name)


    pprint(connection.queries)  