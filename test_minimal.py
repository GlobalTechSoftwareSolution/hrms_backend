#!/usr/bin/env python3
import os
import sys
import django

# Add the hrms directory to the path
sys.path.insert(0, '/Users/globaltechsoftwaresolutions/hrms_backend/hrms')

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hrms.settings')
django.setup()

from accounts.serializers import CareerSerializer

# Test minimal validation
test_data = {
    'title': 'Dev',
    'department': 'IT',
    'description': 'Job',
    'responsibilities': ['Code'],
    'requirements': ['Know'],
    'benefits': ['Pay'],
    'skills': ['JS'],
    'location': 'Home',
    'type': 'Full-time',
    'experience': '1 year',
    'posted_date': '2024-02-26',
    'category': 'Tech',
    'education': 'Degree'
}

print("Testing CareerSerializer with minimal input...")
serializer = CareerSerializer(data=test_data)

if serializer.is_valid():
    print("✅ Validation PASSED!")
    print("Validated data:")
    for key, value in serializer.validated_data.items():
        print(f"  {key}: {value}")
else:
    print("❌ Validation FAILED!")
    print("Errors:")
    for field, errors in serializer.errors.items():
        print(f"  {field}: {errors}")
