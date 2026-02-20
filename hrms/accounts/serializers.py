import re
from collections import Counter
import textstat

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
        
        # Only block obvious keyboard patterns
        keyboard_patterns = ['asdf', 'qwer', 'zxcv', 'ghjk', 'bnm', 'qwertyuiop']
        value_lower = value.lower()
        for pattern in keyboard_patterns:
            if pattern in value_lower:
                raise serializers.ValidationError("Project title contains keyboard pattern. Please provide meaningful words.")
        
        # Check for repetitive characters (e.g., 'aaaaaa', 'bbbbbb')
        cleaned_value = value.strip()
        
        # Check for 4+ consecutive same characters
        for i in range(len(cleaned_value) - 3):
            if cleaned_value[i] == cleaned_value[i+1] == cleaned_value[i+2] == cleaned_value[i+3]:
                raise serializers.ValidationError("Project title contains excessive repeating characters. Please use real words.")
        
        # Check for very high frequency of one character
        char_counts = Counter(cleaned_value.lower())
        for char, count in char_counts.items():
            if count > len(cleaned_value) * 0.5:  # If one character is 50%+ of string
                raise serializers.ValidationError("Project title has too many repeated characters. Please use real words.")
        
        # Check if project name contains at least two meaningful words
        words = re.findall(r'[a-zA-Z]+', cleaned_value)
        if len(words) < 2:
            raise serializers.ValidationError("Project title should contain at least two meaningful words.")
        
        # Check if words are too short or look random
        meaningful_word_count = 0
        for word in words:
            if len(word) >= 3:
                # Simple check: word should have vowels and reasonable character distribution
                if any(char in 'aeiou' for char in word):
                    meaningful_word_count += 1
        
        if meaningful_word_count < 1:
            raise serializers.ValidationError("Project title appears to contain random characters. Please use real words.")
        
        # Advanced validation using textstat library
        try:
            # Check readability score - random text usually has very low scores
            readability_score = textstat.flesch_reading_ease(cleaned_value)
            if readability_score < -20:  # Very low readability indicates random text
                raise serializers.ValidationError("Project title appears to be random characters. Please use meaningful words.")
            
            # Check syllable count - random text often has unrealistic syllable patterns
            syllable_count = textstat.syllable_count(cleaned_value)
            word_count = len(words)
            if word_count > 0 and syllable_count / word_count > 10:  # Too many syllables per word
                raise serializers.ValidationError("Project title contains unrealistic word patterns. Please use real words.")
                
        except:
            # If textstat fails, continue with basic validation
            pass
        
        # Check for uniqueness of project name
        if Project.objects.filter(name=cleaned_value).exists():
            raise serializers.ValidationError("A project with this name already exists.")
        
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
    def validate_title(self, value):
        """Validate job title to ensure it contains meaningful content"""
        if not value or not value.strip():
            raise serializers.ValidationError("Job title cannot be empty or just whitespace.")
        
        # Check for minimum length
        if len(value.strip()) < 3:
            raise serializers.ValidationError("Job title must be at least 3 characters long.")
        
        # Check if title contains only special characters or numbers
        if not any(c.isalpha() for c in value):
            raise serializers.ValidationError("Job title must contain at least some alphabetic characters.")
        
        # Very aggressive check for completely random content
        cleaned_value = value.strip().lower()
        words = cleaned_value.split()
        
        # Check each word for randomness
        for word in words:
            if len(word) >= 3:
                # Check if word is a common job title keyword (bypass validation)
                job_title_keywords = ['manager', 'developer', 'engineer', 'analyst', 'designer', 'consultant', 'coordinator', 'specialist', 'supervisor', 'director', 'administrator', 'assistant', 'associate', 'lead', 'architect', 'technician', 'advisor', 'officer', 'executive', 'planner', 'researcher', 'trainer', 'representative', 'agent', 'broker', 'software', 'senior', 'junior', 'principal', 'head', 'chief', 'vp', 'vice', 'president', 'marketing', 'sales', 'finance', 'hr', 'human', 'resources', 'technical', 'product', 'project', 'data', 'science', 'quality', 'assurance', 'operations', 'logistics', 'procurement', 'legal', 'compliance', 'risk', 'audit', 'tax', 'accounting', 'financial', 'business', 'development', 'testing', 'support', 'maintenance', 'security', 'network', 'database', 'web', 'mobile', 'cloud', 'devops', 'agile', 'scrum', 'fullstack', 'frontend', 'backend']
                
                # If word is a common job title, allow it even with fewer vowels
                if word.lower() in job_title_keywords:
                    continue  # Skip validation for this word
                
                # Count vowels vs consonants
                vowels = sum(1 for char in word if char in 'aeiou')
                consonants = len([c for c in word if c.isalpha() and c not in 'aeiou'])
                
                # Only flag as random if very few vowels AND word is long
                if len(word) >= 6 and vowels <= 1:
                    raise serializers.ValidationError("Job title contains random character sequences. Please use real words.")
                
                # Check for character frequency - random typing often has evenly distributed characters
                char_counts = {}
                for char in word:
                    char_counts[char] = char_counts.get(char, 0) + 1
                
                # Only flag as random if most characters appear only once AND word is very long
                unique_chars = len(char_counts)
                if len(word) >= 7 and unique_chars >= len(word) - 1:
                    raise serializers.ValidationError("Job title appears to be randomly typed. Please use real words.")
        
        # Only block obvious keyboard patterns
        keyboard_patterns = ['asdf', 'qwer', 'zxcv', 'ghjk', 'bnm', 'qwertyuiop']
        value_lower = value.lower()
        for pattern in keyboard_patterns:
            if pattern in value_lower:
                raise serializers.ValidationError("Job title contains keyboard pattern. Please provide meaningful words.")
        
        # Check for repetitive characters (e.g., 'aaaaaa', 'bbbbbb')
        for i in range(len(cleaned_value) - 3):
            if cleaned_value[i] == cleaned_value[i+1] == cleaned_value[i+2] == cleaned_value[i+3]:
                raise serializers.ValidationError("Job title contains excessive repeating characters. Please use real words.")
        
        # Check for very high frequency of one character
        char_counts = Counter(cleaned_value.lower())
        for char, count in char_counts.items():
            if count > len(cleaned_value) * 0.5:  # If one character is 50%+ of string
                raise serializers.ValidationError("Job title has too many repeated characters. Please use real words.")
        
        # Check if job title contains at least two meaningful words
        words = re.findall(r'[a-zA-Z]+', cleaned_value)
        if len(words) < 2:
            raise serializers.ValidationError("Job title should contain at least two meaningful words.")
        
        # Advanced validation using textstat library
        try:
            # Check readability score - random text usually has very low scores
            readability_score = textstat.flesch_reading_ease(cleaned_value)
            if readability_score < -20:  # Very low readability indicates random text
                raise serializers.ValidationError("Job title appears to be random characters. Please use meaningful words.")
            
            # Check syllable count - random text often has unrealistic syllable patterns
            syllable_count = textstat.syllable_count(cleaned_value)
            word_count = len(words)
            if word_count > 0 and syllable_count / word_count > 10:  # Too many syllables per word
                raise serializers.ValidationError("Job title contains unrealistic word patterns. Please use real words.")
                
        except:
            # If textstat fails, continue with basic validation
            pass
        
        return value.strip()
    
    def validate_skills(self, value):
        """Validate skills to ensure they contain meaningful content"""
        if not value or not value.strip():
            raise serializers.ValidationError("Skills cannot be empty or just whitespace.")
        
        # Check for minimum length
        if len(value.strip()) < 10:
            raise serializers.ValidationError("Skills must be at least 10 characters long.")
        
        # Check if skills contain only special characters or numbers
        if not any(c.isalpha() for c in value):
            raise serializers.ValidationError("Skills must contain alphabetic characters.")
        
        # Check for random character patterns
        cleaned_value = value.strip()
        words = cleaned_value.split()
        
        # Check for obvious random patterns
        for word in words:
            if len(word) >= 4:
                # Check for 4+ consecutive same characters
                for i in range(len(word) - 3):
                    if word[i] == word[i+1] == word[i+2] == word[i+3]:
                        raise serializers.ValidationError("Skills contain excessive repeating characters. Please use real skills.")
                
                # Check for very high frequency of one character
                char_counts = Counter(word.lower())
                for char, count in char_counts.items():
                    if count > len(word) * 0.6:  # If one character is 60%+ of word
                        raise serializers.ValidationError("Skills contain random character patterns. Please use real skills.")
        
        return value.strip()
    
    def validate_education(self, value):
        """Validate education requirements to ensure they contain meaningful content"""
        if not value or not value.strip():
            raise serializers.ValidationError("Education requirements cannot be empty or just whitespace.")
        
        # Check for minimum length
        if len(value.strip()) < 5:
            raise serializers.ValidationError("Education requirements must be at least 5 characters long.")
        
        # Check if education contains only special characters or numbers
        if not any(c.isalpha() for c in value):
            raise serializers.ValidationError("Education requirements must contain alphabetic characters.")
        
        # Check for common education keywords
        education_keywords = ['bachelor', 'master', 'phd', 'degree', 'diploma', 'certificate', 'high school', 'graduate', 'undergraduate', 'postgraduate', 'btech', 'b.tech', 'mtech', 'm.tech', 'be', 'b.e', 'me', 'm.e', 'bsc', 'b.sc', 'msc', 'm.sc', 'ba', 'ma', 'engineering', 'computer science', 'information technology', 'it', 'cs']
        value_lower = value.lower()
        
        # If no common education keywords found, check for random patterns
        has_education_keyword = any(keyword in value_lower for keyword in education_keywords)
        
        if not has_education_keyword:
            # Check for random character patterns
            words = value_lower.split()
            for word in words:
                if len(word) >= 4:
                    # Count vowels vs consonants
                    vowels = sum(1 for char in word if char in 'aeiou')
                    consonants = len([c for c in word if c.isalpha() and c not in 'aeiou'])
                    
                    # If word has very few vowels compared to length, it's likely random
                    if len(word) >= 4 and vowels <= 1:
                        raise serializers.ValidationError("Education requirements appear to contain random characters. Please use meaningful education requirements.")
                    
                    # Check for character frequency - random typing often has evenly distributed characters
                    char_counts = {}
                    for char in word:
                        char_counts[char] = char_counts.get(char, 0) + 1
                    
                    # If most characters appear only once, likely random typing
                    unique_chars = len(char_counts)
                    if len(word) >= 5 and unique_chars >= len(word) - 1:
                        raise serializers.ValidationError("Education requirements contain random character patterns. Please use meaningful education requirements.")
        
        return value.strip()
    
    def validate_requirements(self, value):
        """Validate job requirements to ensure they contain meaningful content"""
        if not value or not value.strip():
            raise serializers.ValidationError("Job requirements cannot be empty or just whitespace.")
        
        # Check for minimum length
        if len(value.strip()) < 15:
            raise serializers.ValidationError("Job requirements must be at least 15 characters long.")
        
        # Check if requirements contain only special characters or numbers
        if not any(c.isalpha() for c in value):
            raise serializers.ValidationError("Job requirements must contain alphabetic characters.")
        
        # Check for random character patterns (more lenient)
        cleaned_value = value.strip()
        words = cleaned_value.split()
        
        # Check each word for randomness (only for very long words)
        for word in words:
            if len(word) >= 8:  # Only check long words for randomness
                # Count vowels vs consonants
                vowels = sum(1 for char in word if char in 'aeiou')
                consonants = len([c for c in word if c.isalpha() and c not in 'aeiou'])
                
                # Only flag as random if very few vowels AND word is very long
                if len(word) >= 8 and vowels <= 1:
                    raise serializers.ValidationError("Job requirements contain random character sequences. Please use real requirements.")
                
                # Check for character frequency - random typing often has evenly distributed characters
                char_counts = {}
                for char in word:
                    char_counts[char] = char_counts.get(char, 0) + 1
                
                # Only flag as random if most characters appear only once AND word is very long
                unique_chars = len(char_counts)
                if len(word) >= 10 and unique_chars >= len(word) - 1:
                    raise serializers.ValidationError("Job requirements appear to be randomly typed. Please use meaningful requirements.")
        
        return value.strip()
    
    def validate_salary(self, value):
        """Validate salary range to ensure it's in proper format"""
        if not value or not value.strip():
            return value  # Salary is optional
        
        # Check for common salary formats
        salary_patterns = [
            r'\$\d{1,3}(,\d{3})*\s*-\s*\$\d{1,3}(,\d{3})*',  # $50,000 - $70,000
            r'\$\d{1,3}(,\d{3})*\s*to\s*\$\d{1,3}(,\d{3})*',   # $50,000 to $70,000
            r'\d{1,3}(,\d{3})*\s*-\s*\d{1,3}(,\d{3})*',        # 50,000 - 70,000
            r'\$\d{1,3}(,\d{3})*\s*per\s*(year|month|hour)',   # $50,000 per year
        ]
        
        value_lower = value.lower()
        has_valid_format = any(re.search(pattern, value_lower) for pattern in salary_patterns)
        
        if not has_valid_format:
            # Check if it's just random characters
            if not any(c.isdigit() for c in value):
                raise serializers.ValidationError("Salary range must contain numbers or be in proper format (e.g., $50,000 - $70,000).")
        
        return value.strip()
    
        
        # Check if requirements contain only special characters or numbers
        if not any(c.isalpha() for c in value):
            raise serializers.ValidationError("Job requirements must contain alphabetic characters.")
        
        # Check for random character patterns
        cleaned_value = value.strip()
        words = cleaned_value.split()
        
        # Check for obvious random patterns
        for word in words:
            if len(word) >= 4:
                # Check for 4+ consecutive same characters
                for i in range(len(word) - 3):
                    if word[i] == word[i+1] == word[i+2] == word[i+3]:
                        raise serializers.ValidationError("Job requirements contain excessive repeating characters. Please use meaningful requirements.")
                
                # Check for very high frequency of one character
                char_counts = Counter(word.lower())
                for char, count in char_counts.items():
                    if count > len(word) * 0.6:  # If one character is 60%+ of word
                        raise serializers.ValidationError("Job requirements contain random character patterns. Please use meaningful requirements.")
        
        return value.strip()
    
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
