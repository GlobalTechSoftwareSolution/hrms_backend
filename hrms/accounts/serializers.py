import re

from rest_framework import serializers
from .models import User, CEO, HR, Manager, Employee, Admin, Leave, Attendance, Report, Project, Notice, Document, Award, Department, Ticket, EmployeeDetails, Holiday, AbsentEmployeeDetails, AppliedJobs, JobPosting, ReleavedEmployee, PettyCash, Shift
from typing import Any, Dict, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from django.db.models.base import ModelBase

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:  # type: ignore
        model = User
        fields = ['email', 'password', 'role']

    def create(self, validated_data: Dict[str, Any]) -> User:
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user

    def update(self, instance: User, validated_data: Dict[str, Any]) -> User:
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance


class UserSerializer(serializers.ModelSerializer):
    class Meta:  # type: ignore
        model = User
        fields = ['email', 'role', 'is_staff']


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:  # type: ignore
        model = Department
        fields = ['id', 'department_name', 'description', 'created_at', 'updated_at']


class CEOSerializer(serializers.ModelSerializer):
    class Meta:  # type: ignore
        model = CEO
        fields = '__all__'


class HRSerializer(serializers.ModelSerializer):
    class Meta:  # type: ignore
        model = HR
        fields = '__all__'


class ManagerSerializer(serializers.ModelSerializer):
    class Meta:  # type: ignore
        model = Manager
        fields = '__all__'


class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:  # type: ignore
        model = Employee
        fields = '__all__'


class EmployeeDetailsSerializer(serializers.ModelSerializer):
    class Meta:  # type: ignore
        model = EmployeeDetails
        fields = '__all__'


class AdminSerializer(serializers.ModelSerializer):
    class Meta:  # type: ignore
        model = Admin
        fields = '__all__'


class SuperUserCreateSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=8)

    def validate_email(self, value: str) -> str:
        from django.contrib.auth import get_user_model
        User = get_user_model()
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already exists.")
        return value

    def create(self, validated_data: Dict[str, Any]) -> User:
        from django.contrib.auth import get_user_model
        User = get_user_model()
        # Type checking workaround for Pyright
        user_manager = User.objects
        # Use type: ignore to bypass Pyright's type checking for this specific case
        if hasattr(user_manager, 'create_superuser'):
            user = user_manager.create_superuser(  # type: ignore
                email=validated_data['email'],
                password=validated_data['password'],
                role='admin'
            )
        else:
            # Fallback in case of type checking issues
            user = User.objects.create_superuser(  # type: ignore
                email=validated_data['email'],
                password=validated_data['password'],
                role='admin'
            )
        return user


class LeaveSerializer(serializers.ModelSerializer):
    class Meta:  # type: ignore
        model = Leave
        fields = '__all__'
        read_only_fields = ['status', 'applied_on']


class AttendanceSerializer(serializers.ModelSerializer):
    email = serializers.StringRelatedField()

    class Meta:  # type: ignore
        model = Attendance
        fields = ['email', 'date', 'check_in', 'check_out']


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:  # type: ignore
        model = User
        fields = ["email", "password", "role"]

    def create(self, validated_data: Dict[str, Any]) -> User:
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user
    

class ReportSerializer(serializers.ModelSerializer):
    class Meta:  # type: ignore
        model = Report
        fields = ['id', 'title', 'description', 'date', 'content', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class ProjectSerializer(serializers.ModelSerializer):
    def validate_name(self, value):
        """Validate project title to ensure it contains meaningful content"""
        if not value or not value.strip():
            raise serializers.ValidationError("Project title cannot be empty or just whitespace.")
        
        # Check for minimum length
        if len(value.strip()) < 3:
            raise serializers.ValidationError("Project title must be at least 3 characters long.")
        
        # Check if title contains only special characters or numbers
        if not any(c.isalpha() for c in value):
            raise serializers.ValidationError("Project title must contain at least some alphabetic characters.")
        
        # Check for common random patterns (keyboard walks)
        random_patterns = ['asdf', 'qwer', 'zxcv', 'ghjk', 'bnm', 'qwerty', 'asdfgh', 'qwertyuiop']
        value_lower = value.lower()
        for pattern in random_patterns:
            if pattern in value_lower:
                raise serializers.ValidationError("Project title contains keyboard pattern. Please provide meaningful words.")
        
        # Simple but effective randomness check
        words = value.lower().split()
        for word in words:
            if len(word) >= 4:
                # Count vowels vs consonants
                vowels = sum(1 for char in word if char in 'aeiou')
                consonants = len([c for c in word if c.isalpha() and c not in 'aeiou'])
                
                # If a word has 5+ characters and 0 or 1 vowel, it's likely random
                if len(word) >= 5 and vowels <= 1:
                    raise serializers.ValidationError("Project title contains random character sequences. Please use real words.")
                
                # Check for too many consecutive consonants (common in random typing)
                consecutive_consonants = 0
                max_consecutive = 0
                for char in word:
                    if char.isalpha() and char not in 'aeiou':
                        consecutive_consonants += 1
                    else:
                        max_consecutive = max(max_consecutive, consecutive_consonants)
                        consecutive_consonants = 0
                
                max_consecutive = max(max_consecutive, consecutive_consonants)
                # Only flag as random if 5+ consecutive consonants OR 4+ in a long word
                if max_consecutive >= 5 or (max_consecutive >= 4 and len(word) >= 6):
                    raise serializers.ValidationError("Project title contains random character sequences. Please use real words.")
        
        return value.strip()
    
    def validate_description(self, value):
        """Validate project description to ensure it contains meaningful content"""
        if value and not value.strip():
            raise serializers.ValidationError("Project description cannot be just whitespace if provided.")
        
        if value:
            # Check for minimum length if description is provided
            if len(value.strip()) < 10:
                raise serializers.ValidationError("Project description must be at least 10 characters long if provided.")
            
            # Check if description contains only special characters or numbers
            if not any(c.isalpha() for c in value):
                raise serializers.ValidationError("Project description must contain alphabetic characters.")
        
        return value.strip() if value else value
    
    class Meta:  # type: ignore
        model = Project
        fields = '__all__'
        

class NoticeSerializer(serializers.ModelSerializer):
    class Meta:  # type: ignore
        model = Notice
        fields = '__all__'


class DocumentSerializer(serializers.ModelSerializer):
    class Meta:  # type: ignore
        model = Document
        fields = '__all__'


class AwardSerializer(serializers.ModelSerializer):
    class Meta:  # type: ignore
        model = Award
        fields = '__all__'


class TicketSerializer(serializers.ModelSerializer):
    assigned_by = serializers.SlugRelatedField(
        queryset=User.objects.all(), slug_field='email'
    )
    assigned_to = serializers.SlugRelatedField(
        queryset=User.objects.all(), slug_field='email'
    )
    closed_by = serializers.SlugRelatedField(
        queryset=User.objects.all(), slug_field='email', required=False, allow_null=True
    )
    closed_to = serializers.SlugRelatedField(
        queryset=User.objects.all(), slug_field='email', required=False, allow_null=True
    )

    class Meta:  # type: ignore
        model = Ticket
        fields = '__all__'

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        # On creation: assigned_by must not be equal to assigned_to
        if self.instance is None:
            if attrs['assigned_by'] == attrs['assigned_to']:
                raise serializers.ValidationError("assigned_by and assigned_to cannot be the same.")
        
        # On update: if closed_by or closed_to is set, enforce workflow
        if self.instance is not None:
            # Use type: ignore to bypass Pyright's type checking for these specific cases
            if 'closed_by' in attrs or 'closed_to' in attrs:
                if attrs.get('closed_by') != self.instance.assigned_to:  # type: ignore
                    raise serializers.ValidationError("closed_by must be the assigned_to user (User B).")
                if attrs.get('closed_to') != self.instance.assigned_by:  # type: ignore
                    raise serializers.ValidationError("closed_to must be the assigned_by user (User A).")
        return attrs


class HolidaySerializer(serializers.ModelSerializer):
    class Meta:  # type: ignore
        model = Holiday
        fields = ['id', 'year', 'month', 'country', 'date', 'name', 'type', 'weekday']


class AbsentEmployeeDetailsSerializer(serializers.ModelSerializer):
    class Meta:  # type: ignore
        model = AbsentEmployeeDetails
        fields = ['email', 'fullname', 'department', 'date']


class CareerSerializer(serializers.ModelSerializer):
    class Meta:  # type: ignore
        model = JobPosting
        fields = '__all__'


class AppliedJobSerializer(serializers.ModelSerializer):
    class Meta:  # type: ignore
        model = AppliedJobs
        fields = '__all__'
        read_only_fields = ['resume']


class ReleavedEmployeeSerializer(serializers.ModelSerializer):
    class Meta:  # type: ignore
        model = ReleavedEmployee
        fields = '__all__'

class PettyCashSerializer(serializers.ModelSerializer):
    class Meta:
        model = PettyCash
        fields = '__all__'


class ShiftSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shift
        fields = ['shift_id', 'date', 'start_time', 'end_time', 'emp_email', 'emp_name', 'manager_email', 'manager_name', 'shift']
        read_only_fields = ['emp_name', 'manager_name']

    def create(self, validated_data):
        # Names will be automatically populated in the model's save method
        return Shift.objects.create(**validated_data)
