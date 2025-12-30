from django.core.management.base import BaseCommand
from django.db import models
from accounts.models import Attendance, Employee, HR, CEO, Manager, Admin


class Command(BaseCommand):
    help = 'Update existing Attendance records with null fullname/department from user data'

    def handle(self, *args, **options):
        attendances = Attendance.objects.filter(
            models.Q(fullname__isnull=True) | models.Q(department__isnull=True)
        )

        updated_count = 0
        for attendance in attendances:
            if attendance.email:
                # Try to get from Employee first
                try:
                    employee = Employee.objects.get(email=attendance.email)
                    attendance.fullname = employee.fullname
                    attendance.department = employee.department
                    attendance.save(update_fields=['fullname', 'department'])
                    updated_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(f'Updated {attendance.email.email}: {attendance.fullname}, {attendance.department}')
                    )
                except Employee.DoesNotExist:
                    # Try other models
                    for model in [HR, CEO, Manager, Admin]:
                        try:
                            instance = model.objects.get(email=attendance.email)
                            attendance.fullname = instance.fullname
                            if hasattr(instance, 'department'):
                                attendance.department = instance.department
                            attendance.save(update_fields=['fullname', 'department'])
                            updated_count += 1
                            self.stdout.write(
                                self.style.SUCCESS(f'Updated {attendance.email.email}: {attendance.fullname}, {attendance.department}')
                            )
                            break
                        except model.DoesNotExist:
                            continue

        self.stdout.write(
            self.style.SUCCESS(f'Successfully updated {updated_count} attendance records')
        )
