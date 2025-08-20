import random
from pprint import pprint

from django.contrib.auth.models import User
from django.db import connection
from faker import Faker

from assets.models import Department, EmployeeProfile

fake = Faker()


def run():
    copy_count = 1
    department = list(Department.objects.all())
    print(department)

    for user in range(copy_count):
        user = User.objects.create_user(
            username=fake.user_name(),
            password=fake.password(),
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            email=fake.email(),
        )

        EmployeeProfile.objects.create(
            user=user, department=random.choice(department), position=fake.job()
        )
        print(
            f"Created user: {user.username} with profile in department ID: {user.employeeprofile.department.id}"
        )

    pprint(connection.queries)
